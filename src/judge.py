import argparse, asyncio, hashlib, json, re, pathlib, sys, time

import httpx

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from llm import JUDGES, REASONING, chat, ROOT

PICK_RE = re.compile(r"Output \((a|b)\)")
FIELDS = ["input", "output_1", "output_2"]


def load_variant(variant):
    """Last line per id wins."""
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
        return {f: item[f] for f in FIELDS}, "en", None
    t = trans.get(item["id"])
    if not t or "texts" not in t:
        return None, None, "missing_translation"
    pv = t.get("prompt_version", "?")
    if t.get("human_fixed"):
        pv += "|human_fixed"
    return t["texts"], pv, None


async def one(client, sem, item, variant, order, judge, texts, trans_version,
              run, attempt_no, sys_tpl, usr_tpl):
    if order == "AB":
        a, b = texts["output_1"], texts["output_2"]
    else:
        a, b = texts["output_2"], texts["output_1"]
    user = usr_tpl.format(instruction=texts["input"], output_a=a, output_b=b)
    max_tok = 1024 if judge in REASONING else 16
    effort = "low" if judge in ("gpt-oss-120b", "qwen3-30b", "gemma-4-26b") else None
    tag = f"judge:{item['id']}:{variant}:{order}:{judge}:run{run}:a{attempt_no}"
    phash = hashlib.sha1((sys_tpl + "|" + user).encode()).hexdigest()[:12]
    raw, resp, err = await chat(client, sem, JUDGES[judge], sys_tpl, user,
                                max_tokens=max_tok, reasoning_effort=effort, tag=tag)
    rec = {"id": item["id"], "subset": item["subset"], "variant": variant,
           "order": order, "judge": judge, "run": run, "attempt_no": attempt_no,
           "ts": time.time(), "returned_model": (resp or {}).get("model"),
           "prompt_hash": phash, "trans_version": trans_version,
           "raw": raw[:500],
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
    ap.add_argument("--out", default=str(ROOT / "results" / "judgments.jsonl"))
    ap.add_argument("--run", type=int, default=0)
    ap.add_argument("--retry-invalid", action="store_true")
    ap.add_argument("--max-attempts", type=int, default=3)
    ap.add_argument("--concurrency", type=int, default=8)
    args = ap.parse_args()

    out_path = pathlib.Path(args.out)
    variants = args.variants.split(",")
    judges = list(JUDGES) if args.judges == "all" else args.judges.split(",")
    sys_tpl = (ROOT / "prompts" / "judge_system.txt").read_text()
    usr_tpl = (ROOT / "prompts" / "judge_user.txt").read_text()
    want_ids = [l.strip() for l in open(args.ids) if l.strip()]
    items = {r["id"]: r for r in
             (json.loads(l) for l in open(ROOT / "data" / "llmbar_en.jsonl"))}
    trans = {v: load_variant(v) for v in variants}

    # assert every requested non-en id has texts
    missing = []
    for i in want_ids:
        for v in variants:
            if v == "en":
                continue
            if "texts" not in (trans[v].get(i) or {}):
                missing.append((i, v))
    if missing:
        print("ABORT: ids without texts:", missing[:20])
        sys.exit(1)

    # cache: records per key (id,variant,order,judge,run), last wins
    recs_by_key = {}
    if out_path.exists():
        for l in open(out_path):
            r = json.loads(l)
            k = (r["id"], r["variant"], r["order"], r["judge"], r.get("run", 0))
            recs_by_key.setdefault(k, []).append(r)

    todo = []
    for i in want_ids:
        if i not in items:
            continue
        for v in variants:
            texts, tver, terr = get_fields(items[i], v, trans[v])
            for order in ("AB", "BA"):
                for j in judges:
                    k = (i, v, order, j, args.run)
                    prev = recs_by_key.get(k, [])
                    if not prev:
                        attempt_no = 1
                    elif not args.retry_invalid:
                        continue
                    else:
                        last = prev[-1]
                        if last.get("valid") or len(prev) >= args.max_attempts:
                            continue
                        attempt_no = len(prev) + 1
                    todo.append((items[i], v, order, j, texts, tver, attempt_no))
    print(f"{len(todo)} judgments to run ({len(recs_by_key)} keys cached, "
          f"retry-invalid={args.retry_invalid})")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sem = asyncio.Semaphore(args.concurrency)
    async with httpx.AsyncClient() as client:
        results = []
        BATCH = 200
        for k in range(0, len(todo), BATCH):
            batch = await asyncio.gather(*(
                one(client, sem, item, v, order, j, texts, tver, args.run,
                    att, sys_tpl, usr_tpl)
                for item, v, order, j, texts, tver, att in todo[k:k+BATCH]))
            with open(out_path, "a") as f:
                for r in batch:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            results += batch
            print(f"  {k+len(batch)}/{len(todo)} done")
    print("done:", len(results), "invalid:", sum(1 for r in results if not r["valid"]))


if __name__ == "__main__":
    asyncio.run(main())
