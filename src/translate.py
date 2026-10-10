import argparse, asyncio, json, re, unicodedata, pathlib, sys

import httpx

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from llm_client import TRANSLATOR, REASONING, chat, ROOT

FIELDS = ["input", "output_1", "output_2"]
DEVA = re.compile(r"[ऀ-ॿ]")
URL_RE = re.compile(r"https?://[^\s)\]>\"']+")
CODE_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
PROMPT_FILES = ["translate_system.txt", "translate_user.txt", "variants.json"]

import hashlib
PROMPT_VERSION = "v2:" + hashlib.sha1(
    "".join((ROOT / "prompts" / f).read_text() for f in PROMPT_FILES).encode()
).hexdigest()[:12]


def strip_non_prose(text):
    text = CODE_RE.sub(" ", text)
    text = INLINE_CODE_RE.sub(" ", text)
    text = URL_RE.sub(" ", text)
    return text


def deva_ratio(text):
    letters = [c for c in strip_non_prose(text) if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if DEVA.match(c)) / len(letters)


def check_item(src, out, variant):
    fails = {}
    joined = "".join(out[f] for f in FIELDS)
    dr = deva_ratio(joined)
    fails["devanagari_ratio"] = round(dr, 4)
    if variant == "hi_deva" and dr < 0.6:
        fails["devanagari_low"] = round(dr, 4)
    if variant in ("hi_roman", "hi_cm") and dr != 0:
        fails["devanagari_nonzero"] = round(dr, 4)
    for f in FIELDS:
        en, tr = src[f], out[f]
        if not (tr or "").strip():
            fails[f"empty:{f}"] = True
            continue
        lr = len(tr) / max(1, len(en))
        if not (0.5 <= lr <= 2.0):
            fails[f"len_ratio:{f}"] = round(lr, 3)
        for u in URL_RE.findall(en):
            if u not in tr:
                fails.setdefault(f"missing_url:{f}", []).append(u)
        src_blocks = CODE_RE.findall(en)
        tr_blocks = CODE_RE.findall(tr)
        if len(src_blocks) != len(tr_blocks):
            fails[f"codeblock_count:{f}"] = [len(src_blocks), len(tr_blocks)]
        else:
            for k, (sb, tb) in enumerate(zip(src_blocks, tr_blocks)):
                if sb != tb:
                    fails.setdefault(f"codeblock_mismatch:{f}", []).append(k)
    failed = any(k != "devanagari_ratio" for k in fails)
    return fails, failed


# failures that trigger a re-translation (everything except a low
# devanagari_ratio, which is informational and handled downstream)
NONRETRY_KEYS = {"devanagari_ratio", "devanagari_low"}


def deterministic_failed(checks):
    return any(k.split(":")[0] not in NONRETRY_KEYS for k in checks)


async def _attempt(client, sem, item, variant, system, user, tag):
    text, resp, err = await chat(client, sem, TRANSLATOR, system, user,
                                 max_tokens=8192, json_mode=True, tag=tag)
    if err:
        return None, err
    try:
        parsed = json.loads(text)
        if set(parsed.keys()) != set(FIELDS) or not all(isinstance(parsed[f], str) for f in FIELDS):
            return None, "json_parse_failed"
        return parsed, None
    except Exception:
        return None, "json_parse_failed"


async def one(client, sem, item, variant, vspec, sys_tpl, usr_tpl):
    payload = json.dumps({f: item[f] for f in FIELDS}, ensure_ascii=False)
    system = sys_tpl.format(variant_name=vspec["name"], variant_rules=vspec["rules"])
    user = usr_tpl.format(payload_json=payload)
    tag = f"trans:{item['id']}:{variant}"
    rec = {"id": item["id"], "subset": item["subset"], "variant": variant,
           "prompt_version": PROMPT_VERSION}
    last = None
    for attempt in range(1, 4):
        parsed, err = await _attempt(client, sem, item, variant, system, user,
                                     tag if attempt == 1 else f"{tag}:r{attempt}")
        rec["attempts"] = attempt
        if err:
            if err != "json_parse_failed":
                rec["error"] = err
                return rec
            last = {"error": "json_parse_failed", "raw_text": ""}
            continue
        checks, failed = check_item(item, parsed, variant)
        last = {"texts": parsed, "checks": checks, "failed_checks": failed}
        if not deterministic_failed(checks):
            break  # first passing attempt
    rec.update(last)
    return rec


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", required=True)
    ap.add_argument("--ids", required=True)
    args = ap.parse_args()

    variants = json.load(open(ROOT / "prompts" / "variants.json"))
    sys_tpl = (ROOT / "prompts" / "translate_system.txt").read_text()
    usr_tpl = (ROOT / "prompts" / "translate_user.txt").read_text()
    want_ids = [l.strip() for l in open(args.ids) if l.strip()]
    items = {r["id"]: r for r in
             (json.loads(l) for l in open(ROOT / "data" / "llmbar_en.jsonl"))}

    trans_dir = ROOT / "data" / "raw" / "translation_attempts"
    trans_dir.mkdir(parents=True, exist_ok=True)
    sem = asyncio.Semaphore(8)
    async with httpx.AsyncClient() as client:
        for variant in args.variants.split(","):
            path = trans_dir / f"{variant}.jsonl"
            done = {json.loads(l)["id"] for l in open(path)} if path.exists() else set()
            todo = [items[i] for i in want_ids if i in items and i not in done]
            print(f"{variant}: {len(todo)} to translate, {len(done)} cached")
            if not todo:
                continue
            results = await asyncio.gather(*(
                one(client, sem, it, variant, variants[variant], sys_tpl, usr_tpl)
                for it in todo))
            with open(path, "a") as f:
                for r in results:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            nf = sum(1 for r in results if r.get("error") or r.get("failed_checks"))
            print(f"{variant}: wrote {len(results)}, flagged {nf}")


if __name__ == "__main__":
    asyncio.run(main())
