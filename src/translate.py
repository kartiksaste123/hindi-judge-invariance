import argparse, asyncio, json, re, unicodedata, pathlib, sys

import httpx

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from llm import TRANSLATOR, REASONING, chat, ROOT

FIELDS = ["input", "output_1", "output_2"]
DEVA = re.compile(r"[ऀ-ॿ]")
URL_RE = re.compile(r"https?://[^\s)\]>\"']+")
CODE_RE = re.compile(r"```.*?```", re.S)


def deva_ratio(text):
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if DEVA.match(c)) / len(letters)


def check_item(src, out, variant):
    fails = {}
    joined = "".join(out[f] for f in FIELDS)
    dr = deva_ratio(joined)
    fails["devanagari_ratio"] = dr
    if variant == "hi_deva" and dr < 0.6:
        fails["devanagari_low"] = dr
    if variant in ("hi_roman", "hi_cm") and dr != 0:
        fails["devanagari_nonzero"] = dr
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
                fails.setdefault("missing_url", []).append(u)
        for cb in CODE_RE.findall(en):
            if cb not in tr:
                fails.setdefault("missing_codeblock", []).append(cb[:60])
    failed = any(k != "devanagari_ratio" for k in fails)
    return fails, failed


async def one(client, sem, item, variant, vspec, sys_tpl, usr_tpl):
    payload = json.dumps({f: item[f] for f in FIELDS}, ensure_ascii=False)
    system = sys_tpl.format(variant_name=vspec["name"], variant_rules=vspec["rules"])
    user = usr_tpl.format(payload_json=payload)
    tag = f"trans:{item['id']}:{variant}"
    text, resp, err = await chat(client, sem, TRANSLATOR, system, user,
                                 max_tokens=8192, json_mode=True, tag=tag)
    rec = {"id": item["id"], "subset": item["subset"], "variant": variant}
    if err:
        rec["error"] = err
        return rec
    parsed = None
    try:
        parsed = json.loads(text)
        if set(parsed.keys()) != set(FIELDS) or not all(isinstance(parsed[f], str) for f in FIELDS):
            parsed = None
    except Exception:
        pass
    if parsed is None:
        # one retry
        text, resp, err = await chat(client, sem, TRANSLATOR, system, user,
                                     max_tokens=8192, json_mode=True, tag=tag + ":retry")
        try:
            parsed = json.loads(text)
            if set(parsed.keys()) != set(FIELDS):
                parsed = None
        except Exception:
            parsed = None
    if parsed is None:
        rec["error"] = "json_parse_failed"
        rec["raw_text"] = text[:2000]
        return rec
    checks, failed = check_item(item, parsed, variant)
    rec["texts"] = parsed
    rec["checks"] = checks
    rec["failed_checks"] = failed
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

    trans_dir = ROOT / "data" / "trans"
    trans_dir.mkdir(exist_ok=True)
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
