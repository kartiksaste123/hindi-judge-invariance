import argparse, asyncio, json, re, pathlib, sys

import httpx

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from llm import JUDGES, REASONING, chat, ROOT

PICK_RE = re.compile(r"Output \((a|b)\)")
FIELDS = ["input", "output_1", "output_2"]
RESULTS = ROOT / "results" / "judgments.jsonl"


def load_variant(variant):
    if variant == "en":
        return {json.loads(l)["id"]: json.loads(l)
                for l in open(ROOT / "data" / "llmbar_en.jsonl")}
    p = ROOT / "data" / "trans" / f"{variant}.jsonl"
    out = {}
    if p.exists():
        for l in open(p):
            r = json.loads(l)
            out[r["id"]] = r
    return out


def get_fields(item, variant, trans):
    if variant == "en":
        return {f: item[f] for f in FIELDS}, None
    t = trans.get(item["id"])
    if not t or "texts" not in t:
        return None, "missing_translation"
    return t["texts"], None


async def one(client, sem, item, variant, order, judge, texts, sys_tpl, usr_tpl):
    if order == "AB":
        a, b = texts["output_1"], texts["output_2"]
    else:
        a, b = texts["output_2"], texts["output_1"]
    user = usr_tpl.format(instruction=texts["input"], output_a=a, output_b=b)
    max_tok = 1024 if judge in REASONING else 16
    effort = "low" if judge in ("gpt-oss-120b", "qwen3-30b", "gemma-4-26b") else None
    tag = f"judge:{item['id']}:{variant}:{order}:{judge}"
    raw, resp, err = await chat(client, sem, JUDGES[judge], sys_tpl, user,
                                max_tokens=max_tok, reasoning_effort=effort, tag=tag)
    rec = {"id": item["id"], "subset": item["subset"], "variant": variant,
           "order": order, "judge": judge, "raw": raw[:500],
           "usage": (resp or {}).get("usage"),
           "neurons": ((resp or {}).get("usage") or {}).get("neurons")}
    if err:
        rec.update({"valid": False, "pick": None, "correct": None, "error": err})
        return rec
    m = PICK_RE.findall(raw)
    if not m:
        rec.update({"valid": False, "pick": None, "correct": None,
                    "error": "unparseable"})
        return rec
    letter = m[-1]
    pick = {"AB": {"a": 1, "b": 2}, "BA": {"a": 2, "b": 1}}[order][letter]
    rec.update({"valid": True, "pick": pick, "correct": pick == item["label"],
                "error": None})
    return rec


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", required=True)
    ap.add_argument("--ids", required=True)
    ap.add_argument("--judges", default="all")
    args = ap.parse_args()

    variants = args.variants.split(",")
    judges = list(JUDGES) if args.judges == "all" else args.judges.split(",")
    sys_tpl = (ROOT / "prompts" / "judge_system.txt").read_text()
    usr_tpl = (ROOT / "prompts" / "judge_user.txt").read_text()
    want_ids = [l.strip() for l in open(args.ids) if l.strip()]
    items = {r["id"]: r for r in
             (json.loads(l) for l in open(ROOT / "data" / "llmbar_en.jsonl"))}
    trans = {v: load_variant(v) for v in variants}

    done = set()
    if RESULTS.exists():
        for l in open(RESULTS):
            r = json.loads(l)
            done.add((r["id"], r["variant"], r["order"], r["judge"]))
    todo = []
    for i in want_ids:
        if i not in items:
            continue
        for v in variants:
            texts, terr = get_fields(items[i], v, trans[v])
            for order in ("AB", "BA"):
                for j in judges:
                    if (i, v, order, j) in done:
                        continue
                    todo.append((items[i], v, order, j, texts, terr))
    print(f"{len(todo)} judgments to run ({len(done)} cached)")
    sem = asyncio.Semaphore(8)
    async with httpx.AsyncClient() as client:
        async def go(t):
            item, v, order, j, texts, terr = t
            if terr:
                return {"id": item["id"], "subset": item["subset"], "variant": v,
                        "order": order, "judge": j, "raw": "", "usage": None,
                        "valid": False, "pick": None, "correct": None, "error": terr}
            return await one(client, sem, item, v, order, j, texts, sys_tpl, usr_tpl)
        results = []
        BATCH = 200
        for k in range(0, len(todo), BATCH):
            batch = await asyncio.gather(*(go(t) for t in todo[k:k+BATCH]))
            with open(RESULTS, "a") as f:
                for r in batch:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            results += batch
            print(f"  {k+len(batch)}/{len(todo)} done")
    print("done:", len(results), "invalid:", sum(1 for r in results if not r["valid"]))


if __name__ == "__main__":
    asyncio.run(main())
