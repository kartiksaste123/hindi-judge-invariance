import asyncio, copy, json, pathlib, sys

import httpx

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from llm import chat, ROOT
from translate import check_item, FIELDS
from verify import one as verify_one

FIXES = json.load(open(ROOT / "data/human_adjudication/fixes.json"))
VARIANTS = ["hi_deva", "hi_roman", "hi_cm"]


def load_last(variant):
    d = {}
    for l in open(ROOT / "data" / "trans" / f"{variant}.jsonl"):
        r = json.loads(l)
        d[r["id"]] = r
    return d


def main_sync():
    en = {json.loads(l)["id"]: json.loads(l)
          for l in open(ROOT / "data/llmbar_en.jsonl")}
    last = {v: load_last(v) for v in VARIANTS}
    # idempotency: skip ops whose new text is already present in a human_fixed record
    todo = []
    for idx, op in enumerate(FIXES["fixes"]):
        rec = last[op["variant"]].get(op["id"]) or {}
        cur = (rec.get("texts") or {}).get(op["field"], "")
        if rec.get("human_fixed") and op["new"] in cur:
            continue
        todo.append((idx, op))
    # dry-run count assertions on CURRENT last records
    errors = []
    staged = {}
    for idx, op in todo:
        v, iid, fld = op["variant"], op["id"], op["field"]
        base = staged.get((v, iid)) or last[v][iid]
        text = base["texts"][fld]
        cnt = text.count(op["old"])
        exp = op["expected_count"]
        ok = cnt == exp if isinstance(exp, int) else cnt >= 1
        if not ok:
            errors.append((idx, op["variant"], op["id"], op["field"], cnt, exp))
            continue
        nb = copy.deepcopy(base)
        nb["texts"] = dict(nb["texts"])
        nb["texts"][fld] = nb["texts"][fld].replace(op["old"], op["new"])
        nb.setdefault("human_fix_ops", []).append(idx)
        nb["human_fixed"] = True
        nb["prompt_version"] = "human_fix"
        staged[(v, iid)] = nb
    if errors:
        print("ABORT — count mismatches:")
        for e in errors:
            print(" ", e)
        sys.exit(1)
    # append new records
    appended = []
    for (v, iid), rec in sorted(staged.items()):
        checks, failed = check_item(en[iid], rec["texts"], v)
        rec["checks"] = checks
        rec["failed_checks"] = failed
        rec["repaired"] = True
        rec["repair_round"] = 3  # human pass
        with open(ROOT / "data" / "trans" / f"{v}.jsonl", "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        appended.append((v, iid, rec))
    print(f"applied {len(todo)} ops; appended {len(appended)} cell records")
    if not appended:
        return []

    async def reverify():
        sys_tpl = (ROOT / "prompts" / "verify_system.txt").read_text()
        usr_tpl = (ROOT / "prompts" / "verify_user.txt").read_text()
        vspec = json.load(open(ROOT / "prompts" / "variants.json"))
        sem = asyncio.Semaphore(8)
        results = []
        async with httpx.AsyncClient() as client:
            async def go(v, iid, rec):
                r = await verify_one(client, sem, en[iid], v, rec["texts"],
                                     sys_tpl, usr_tpl, vspec[v]["name"])
                r["post_fix"] = True
                return v, r
            results = await asyncio.gather(*(go(v, i, r) for v, i, r in appended))
        byv = {}
        for v, r in results:
            byv.setdefault(v, []).append(r)
        for v, rs in byv.items():
            with open(ROOT / "data" / "verify" / f"{v}.jsonl", "a") as f:
                for r in rs:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print("reverified", len(results),
              "errors:", sum(1 for _, r in results if r.get("error")))
        return results

    return asyncio.run(reverify())


if __name__ == "__main__":
    main_sync()
