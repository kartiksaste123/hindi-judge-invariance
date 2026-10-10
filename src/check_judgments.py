import json, collections, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from llm_client import ROOT, JUDGES

VARIANTS = ["en", "hi_deva", "hi_roman", "hi_cm"]
JUDGE_KEYS = list(JUDGES)
FILES = {0: ROOT / "results/judgments/main_run.jsonl",
         1: ROOT / "results/judgments/repeat_run1.jsonl",
         2: ROOT / "results/judgments/repeat_run2.jsonl"}

core = [l.strip() for l in open(ROOT / "data/splits/core_387.txt") if l.strip()]
rep = [l.strip() for l in open(ROOT / "data/splits/repeat_100.txt") if l.strip()]
IDS = {0: core, 1: rep, 2: rep}

# current last trans record per cell
def last_trans(v):
    d = {}
    p = ROOT / "data" / "raw" / "translation_attempts" / f"{v}.jsonl"
    for l in open(p):
        r = json.loads(l); d[r["id"]] = r
    return d
TRANS = {v: last_trans(v) for v in VARIANTS if v != "en"}

expected = {(i, v, o, j, run)
            for run, ids in IDS.items() for i in ids
            for v in VARIANTS for o in ("AB", "BA") for j in JUDGE_KEYS}

seen = collections.defaultdict(list)
unexpected = []
for run, path in FILES.items():
    if not path.exists():
        continue
    for l in open(path):
        r = json.loads(l)
        k = (r["id"], r["variant"], r["order"], r["judge"], r.get("run", 0))
        seen[k].append(r)
        if k not in expected:
            unexpected.append(k)

present = set(seen)
valid = {k for k, rs in seen.items() if rs[-1].get("valid")}
invalid = present - valid
missing = expected - present

cnt = collections.Counter()
for k in expected:
    st = ("missing" if k not in present
          else "valid" if k in valid else "invalid")
    cnt[(k[3], k[1], k[4], st)] += 1

print(f"expected {len(expected)} | present {len(present & expected)} "
      f"| valid {len(valid & expected)} | invalid {len(invalid & expected)} "
      f"| missing {len(missing)} | unexpected {len(unexpected)}")
print("\njudge | variant | run | valid | invalid | missing")
for j in JUDGE_KEYS:
    for v in VARIANTS:
        for run in (0, 1, 2):
            row = {s: cnt.get((j, v, run, s), 0) for s in ("valid", "invalid", "missing")}
            if any(row.values()):
                print(f"{j:15s} {v:8s} {run}   {row['valid']:5d} {row['invalid']:5d} {row['missing']:5d}")

# error type breakdown on last records
eb = collections.Counter()
for k in invalid & expected:
    e = (seen[k][-1].get("error") or "?")
    eb[e.split(":")[0][:80]] += 1
print("\nerror breakdown (last records, invalid):", dict(eb.most_common(10)))

# trans_version mismatch check
mism = []
for k in present & expected:
    i, v, o, j, run = k
    if v == "en":
        continue
    cur = TRANS[v].get(i) or {}
    pv = cur.get("prompt_version", "?") + ("|human_fixed" if cur.get("human_fixed") else "")
    rv = seen[k][-1].get("trans_version")
    if rv != pv:
        mism.append((k, rv, pv))
print("\ntrans_version mismatches:", len(mism), mism[:10])
