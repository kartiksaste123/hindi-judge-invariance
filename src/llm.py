"""Shared async client for the Cloudflare AI Gateway OpenAI-compatible endpoint."""
import asyncio, hashlib, json, os, time, pathlib

import httpx

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG = ROOT / "results" / "llm_calls.jsonl"
ACCT = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
GW_ID = "llm-judge-hinglish"
URL = f"https://gateway.ai.cloudflare.com/v1/{ACCT}/{GW_ID}/compat/chat/completions"

JUDGES = {
    "llama-3.3-70b": "workers-ai/@cf/meta/llama-3.3-70b-instruct-fp8-fast",
    "gpt-oss-120b": "workers-ai/@cf/openai/gpt-oss-120b",
    "qwen3-30b": "workers-ai/@cf/qwen/qwen3-30b-a3b-fp8",
    "gemma-4-26b": "workers-ai/@cf/google/gemma-4-26b-a4b-it",
    "llama-3.1-8b": "workers-ai/@cf/meta/llama-3.1-8b-instruct-fp8",
    "gemini-2.5-flash": "google-ai-studio/gemini-2.5-flash",
}
TRANSLATOR = "google-ai-studio/gemini-2.5-pro"

# models that emit reasoning_content and need a larger token budget
REASONING = {"gpt-oss-120b", "qwen3-30b", "gemma-4-26b", "gemini-2.5-flash", "translator"}

_log_lock = asyncio.Lock()


def _token():
    t = os.environ.get("CLOUDFLARE_API_TOKEN")
    if t:
        return t
    return pathlib.Path(os.path.expanduser("~/.secrets/cf_gw_token")).read_text().strip()


async def _log(rec):
    async with _log_lock:
        LOG.parent.mkdir(exist_ok=True)
        with open(LOG, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def extract_text(resp):
    """Final message content (falls back to reasoning_content if content empty)."""
    try:
        msg = resp["choices"][0]["message"] or {}
    except Exception:
        return ""
    return msg.get("content") or msg.get("reasoning_content") or msg.get("reasoning") or ""


async def chat(client, sem, model, system, user, *, max_tokens=16, temperature=0.0,
               json_mode=False, reasoning_effort=None, timeout=120, tag=""):
    body = {"model": model, "temperature": temperature, "max_tokens": max_tokens,
            "messages": ([{"role": "system", "content": system}] if system else [])
                        + [{"role": "user", "content": user}]}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    if reasoning_effort:
        body["reasoning_effort"] = reasoning_effort
    phash = hashlib.sha1((system + "|" + user).encode()).hexdigest()[:12]
    headers = {"Authorization": f"Bearer {_token()}",
               "cf-aig-skip-cache": "true", "Content-Type": "application/json"}
    rec = {"ts": time.time(), "model": model, "tag": tag, "prompt_hash": phash}
    t0 = time.monotonic()
    last_err = None
    for attempt in range(3):
        try:
            async with sem:
                r = await client.post(URL, json=body, headers=headers, timeout=timeout)
            if r.status_code in (429, 500, 502, 503, 504, 529):
                last_err = f"HTTP {r.status_code}: {r.text[:200]}"
                await asyncio.sleep(2 ** attempt * 2)
                continue
            if r.status_code == 400 and json_mode and "response_format" in r.text:
                body.pop("response_format", None)
                continue  # retry without JSON mode
            r.raise_for_status()
            resp = r.json()
            rec.update({"latency_s": round(time.monotonic() - t0, 2),
                        "returned_model": resp.get("model"),
                        "usage": resp.get("usage"),
                        "neurons": (resp.get("usage") or {}).get("neurons"),
                        "raw": resp, "error": None, "attempt": attempt + 1})
            await _log(rec)
            return extract_text(resp), resp, None
        except Exception as e:
            last_err = f"{type(e).__name__}: {str(e)[:300]}"
            await asyncio.sleep(2 ** attempt * 2)
    rec.update({"latency_s": round(time.monotonic() - t0, 2),
                "error": last_err, "raw": None, "usage": None})
    await _log(rec)
    return "", None, last_err
