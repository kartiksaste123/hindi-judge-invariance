import argparse, asyncio, json, pathlib, sys

import httpx

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from llm import chat, ROOT

VERIFIER = "anthropic/claude-sonnet-4-5"
FIELDS = ["input", "output_1", "output_2"]
EXPECTED_KEYS = {"meaning_input", "meaning_output_1", "meaning_output_2",
                 "label_preserved", "language_dependent", "form_ok", "issues"}


async def one(client, sem, item, variant, texts, sys_tpl, usr_tpl, vname):
    en_json = json.dumps({f: item[f] for f in FIELDS}, ensure_ascii=False)
    tr_json = json.dumps(texts, ensure_ascii=False)
    user = usr_tpl.format(variant_name=vname, gold=str(item["label"]),
                          en_json=en_json, tr_json=tr_json)
    tag = f"verify:{item['id']}:{variant}"
    rec = {"id": item["id"], "subset": item["subset"], "variant": variant}
    for attempt in range(2):
        text, resp, err = await chat(client, sem, VERIFIER, sys_tpl, user,
                                     max_tokens=600, json_mode=True,
                                     tag=tag if attempt == 0 else tag + ":retry")
        if err:
            rec["error"] = err
            return rec
        try:
            cleaned = text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1].rsplit("```", 1)[0]
            v = json.loads(cleaned)
            if set(v.keys()) == EXPECTED_KEYS:
                rec["verdict"] = v
                return rec
        except Exception:
            pass
    rec["error"] = "json_parse_failed"
    rec["raw_text"] = text[:2000]
    return rec


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", default="hi_deva,hi_roman,hi_cm")
    args = ap.parse_args()

    variants = json.load(open(ROOT / "prompts" / "variants.json"))
    sys_tpl = (ROOT / "prompts" / "verify_system.txt").read_text()
    usr_tpl = (ROOT / "prompts" / "verify_user.txt").read_text()
    items = {r["id"]: r for r in
             (json.loads(l) for l in open(ROOT / "data" / "llmbar_en.jsonl"))}
    out_dir = ROOT / "data" / "verify"
    out_dir.mkdir(exist_ok=True)

    sem = asyncio.Semaphore(8)
    async with httpx.AsyncClient() as client:
        for variant in args.variants.split(","):
            trans_path = ROOT / "data" / "trans" / f"{variant}.jsonl"
            trans = {json.loads(l)["id"]: json.loads(l)
                     for l in open(trans_path)}
            path = out_dir / f"{variant}.jsonl"
            done = {json.loads(l)["id"] for l in open(path)
                    if "verdict" in json.loads(l)} if path.exists() else set()
            todo = []
            for i, t in trans.items():
                if i in done or "texts" not in t:
                    continue
                todo.append((items[i], t["texts"]))
            print(f"{variant}: {len(todo)} to verify, {len(done)} cached")
            if not todo:
                continue
            results = await asyncio.gather(*(
                one(client, sem, it, variant, txts, sys_tpl, usr_tpl,
                    variants[variant]["name"]) for it, txts in todo))
            with open(path, "a") as f:
                for r in results:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            print(f"{variant}: wrote {len(results)}, "
                  f"errors {sum(1 for r in results if r.get('error'))}")


if __name__ == "__main__":
    asyncio.run(main())
