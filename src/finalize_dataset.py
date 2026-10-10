import json, csv, collections, pathlib, sys, random, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from llm_client import ROOT, read_api_calls
from translate import check_item

VARIANTS = ["hi_deva", "hi_roman", "hi_cm"]
FIELDS = ["input", "output_1", "output_2"]

en = {json.loads(l)["id"]: json.loads(l) for l in open(ROOT / "data/llmbar_en.jsonl")}
trans, verify = {}, {}
for v in VARIANTS:
    trans[v] = {json.loads(l)["id"]: json.loads(l) for l in open(ROOT / f"data/raw/translation_attempts/{v}.jsonl")}
    verify[v] = {json.loads(l)["id"]: json.loads(l) for l in open(ROOT / f"data/raw/verification_attempts/{v}.jsonl")}

# per-item language_dependent (any variant)
langdep = {}
for i in en:
    langdep[i] = any((verify[v].get(i, {}).get("verdict") or {}).get("language_dependent") for v in VARIANTS)

status = {}
reasons = collections.defaultdict(collections.Counter)
for i, item in en.items():
    if langdep[i]:
        for v in VARIANTS:
            status[(i, v)] = ("exclude_langdep", ["language_dependent"])
            reasons[v]["language_dependent"] += 1
        continue
    for v in VARIANTS:
        t, vv = trans[v].get(i), verify[v].get(i)
        rs = []
        if not t or "texts" not in t:
            rs.append("no_translation")
        elif t.get("failed_checks"):
            rs += [f"check:{k}" for k in t["checks"] if k != "devanagari_ratio"]
        verdict = (vv or {}).get("verdict") or {}
        for k in ("meaning_input", "meaning_output_1", "meaning_output_2"):
            if verdict.get(k) == "changed":
                rs.append(f"verifier:{k}=changed")
        if verdict.get("label_preserved") is False:
            rs.append("verifier:label_preserved")
        if verdict.get("form_ok") is False:
            rs.append("verifier:form_ok")
        if not vv or "verdict" not in vv:
            rs.append("no_verdict")
        status[(i, v)] = ("needs_review" if rs else "pass", rs)
        if rs:
            for r in rs:
                if r.startswith("verifier:"):
                    key = r.split(":", 1)[1].split("=")[0]
                    reasons[v][f"verifier:{key}"] += 1
                else:
                    reasons[v][r] += 1

# --- human adjudication layer (step 3) ---
ratings_path = ROOT / "data" / "human_validation" / "ratings.jsonl"
ratings = {}
if ratings_path.exists():
    for l in open(ratings_path):
        r = json.loads(l)
        ratings[(r["id"], r["variant"])] = r

human_validated = {}
for i, item in en.items():
    if langdep[i]:
        continue
    # item-level drop if any variant has no texts in last trans record
    if any("texts" not in (trans[v].get(i) or {}) for v in VARIANTS):
        for v in VARIANTS:
            status[(i, v)] = ("dropped_no_translation",
                              status.get((i, v), (None, []))[1])
        continue
    for v in VARIANTS:
        key = (i, v)
        if key not in ratings:
            continue
        a, b = ratings[key]["A"], ratings[key]["B"]
        t = trans[v].get(i) or {}
        # devanagari_low is a heuristic for untranslated prose; for human-validated
        # cells, low ratio from verbatim code/notation (rules 4-6) does not block.
        det_ok = "texts" in t and not any(
            k not in ("devanagari_ratio", "devanagari_low") for k in (t.get("checks") or {}))
        no_meaning_no = a.get("meaning") != "No" and b.get("meaning") != "No"
        old_status, old_reasons = status[key]
        if no_meaning_no and det_ok:
            status[key] = ("pass", old_reasons)
            human_validated[key] = True
        else:
            status[key] = ("needs_review", old_reasons)
            human_validated[key] = False

# write status.jsonl + final/
with open(ROOT / "data" / "item_status.jsonl", "w") as f:
    for (i, v), (s, rs) in sorted(status.items()):
        f.write(json.dumps({"id": i, "variant": v, "status": s, "reasons": rs},
                           ensure_ascii=False) + "\n")
final_dir = ROOT / "data" / "translations"
final_dir.mkdir(exist_ok=True)
for v in VARIANTS:
    with open(final_dir / f"{v}.jsonl", "w") as f:
        for i, t in sorted(trans[v].items()):
            s, rs = status[(i, v)]
            rec = {**t, "status": s, "auto_reasons": rs}
            if (i, v) in human_validated:
                rec["human_validated"] = human_validated[(i, v)]
            if t.get("human_fixed"):
                rec["post_fix_verdict"] = (verify[v].get(i) or {}).get("verdict")
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

core = [i for i in en if all(status[(i, v)][0] == "pass" for v in VARIANTS) and not langdep[i]]
(ROOT / "data" / "splits" / "core_387.txt").write_text("\n".join(core) + "\n")

# crosstab: langdep vs v2 low-deva flag
xtab = collections.Counter()
for i in en:
    low_deva = any(((trans["hi_deva"].get(i) or {}).get("checks") or {}).get("devanagari_low")
                   is not None for _ in [0]) if trans["hi_deva"].get(i) else False
    ld = langdep[i]
    xtab[(ld, low_deva)] += 1

# examples per failure reason
rng = random.Random(3)
ex = collections.defaultdict(list)
for (i, v), (s, rs) in status.items():
    for r in rs:
        ex[r].append((i, v))
examples = {r: rng.sample(v, min(3, len(v))) for r, v in ex.items()}

# cost from call log (step-2 tags only)
calls = list(read_api_calls())
tot = {"trans:r": 0, "trans:": 0, "verify:": 0}
calls_n = err_n = 0
lat = 0.0
for c in calls:
    if c["tag"].startswith("trans:") or c["tag"].startswith("verify:"):
        calls_n += 1
        lat += c.get("latency_s") or 0
        if c.get("error"):
            err_n += 1

# summary md
cnt = collections.defaultdict(collections.Counter)
for (i, v), (s, rs) in status.items():
    cnt[v][s] += 1
print(json.dumps({v: dict(cnt[v]) for v in VARIANTS}))
print("core_ids:", len(core), "| langdep items:", sum(langdep.values()))
