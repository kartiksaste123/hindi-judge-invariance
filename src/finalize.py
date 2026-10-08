import json, csv, collections, pathlib, sys, random, time
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from llm import ROOT
from translate import check_item

VARIANTS = ["hi_deva", "hi_roman", "hi_cm"]
FIELDS = ["input", "output_1", "output_2"]

en = {json.loads(l)["id"]: json.loads(l) for l in open(ROOT / "data/llmbar_en.jsonl")}
trans, verify = {}, {}
for v in VARIANTS:
    trans[v] = {json.loads(l)["id"]: json.loads(l) for l in open(ROOT / f"data/trans/{v}.jsonl")}
    verify[v] = {json.loads(l)["id"]: json.loads(l) for l in open(ROOT / f"data/verify/{v}.jsonl")}

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

# write status.jsonl + final/
with open(ROOT / "data" / "status.jsonl", "w") as f:
    for (i, v), (s, rs) in sorted(status.items()):
        f.write(json.dumps({"id": i, "variant": v, "status": s, "reasons": rs},
                           ensure_ascii=False) + "\n")
final_dir = ROOT / "data" / "final"
final_dir.mkdir(exist_ok=True)
for v in VARIANTS:
    with open(final_dir / f"{v}.jsonl", "w") as f:
        for i, t in sorted(trans[v].items()):
            s, rs = status[(i, v)]
            f.write(json.dumps({**t, "status": s, "reasons": rs}, ensure_ascii=False) + "\n")

core = [i for i in en if all(status[(i, v)][0] == "pass" for v in VARIANTS) and not langdep[i]]
(ROOT / "data" / "core_ids.txt").write_text("\n".join(core) + "\n")

# human check sheets (all non-excluded items), UTF-8 BOM
hc_dir = ROOT / "data" / "human_check"
hc_dir.mkdir(exist_ok=True)
for v in VARIANTS:
    with open(hc_dir / f"sheet_{v}.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "subset", "field", "english", "converted", "auto_status",
                    "auto_issues", "repaired", "meaning(Yes/Partly/No)",
                    "label(Yes/No)", "naturalness(1-5)", "notes"])
        for i in sorted(en):
            if langdep[i]:
                continue
            s, rs = status[(i, v)]
            texts = (trans[v].get(i) or {}).get("texts") or {}
            issues = "; ".join(rs) + (" | " + str((verify[v].get(i, {}).get("verdict") or {}).get("issues", "")) if rs else "")
            for fld in FIELDS:
                w.writerow([i, en[i]["subset"], fld, en[i][fld],
                            texts.get(fld, ""), s if fld == "input" else "",
                            issues if fld == "input" else "",
                            str((trans[v].get(i) or {}).get("repaired", "")) if fld == "input" else "",
                            "", "", "", ""])

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
calls = [json.loads(l) for l in open(ROOT / "results" / "llm_calls.jsonl")]
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
md = ["# Step 2 summary — full 419-item translation + verification", "",
      "| variant | pass | needs_review | exclude_langdep |",
      "|---|---|---|---|"]
for v in VARIANTS:
    md.append(f"| {v} | {cnt[v]['pass']} | {cnt[v]['needs_review']} | {cnt[v]['exclude_langdep']} |")
md += ["", f"**core_ids: {len(core)}**", "",
       "## Reason breakdown (per variant)"]
for v in VARIANTS:
    md.append(f"### {v}")
    for r, n in reasons[v].most_common():
        md.append(f"- {r}: {n}")
md += ["", "## language_dependent × v1-style low-Devanagari flag (item-level)", "",
       f"- langdep & low-deva: {xtab[(True, True)]}",
       f"- langdep & not low-deva: {xtab[(True, False)]}",
       f"- not langdep & low-deva: {xtab[(False, True)]}",
       f"- neither: {xtab[(False, False)]}",
       "", "## Random examples per failure reason (field text ≤400 chars)"]
for r, ivs in sorted(examples.items()):
    md.append(f"### {r}")
    for i, v in ivs:
        tr = (trans[v].get(i) or {}).get("texts", {}).get("input", "")
        md.append(f"- `{i}` [{v}]: {tr[:400]!r}")
md += ["", f"## Calls", f"{calls_n} translation+verification calls logged total "
       f"(cumulative incl. pilot), {err_n} errors, "
       f"~{lat/60:.0f} min summed latency. See llm_calls.jsonl for per-call usage."]
(ROOT / "results" / "step2_summary.md").write_text("\n".join(md))
print(json.dumps({v: dict(cnt[v]) for v in VARIANTS}))
print("core_ids:", len(core), "| langdep items:", sum(langdep.values()))
