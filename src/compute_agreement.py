import json, collections, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from llm_client import ROOT

VARIANTS = ["hi_deva", "hi_roman", "hi_cm"]

ratings = [json.loads(l) for l in open(ROOT / "data/human_validation/ratings.jsonl")]
fixes = json.load(open(ROOT / "data/human_validation/fixes.json"))


def cohen_kappa(a, b, cats):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa = collections.Counter(a); pb = collections.Counter(b)
    pe = sum((pa[c] / n) * (pb[c] / n) for c in cats)
    return po, (po - pe) / (1 - pe) if pe < 1 else 0.0


def gwet_ac1(a, b, cats):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa = collections.Counter(a); pb = collections.Counter(b)
    Q = len(cats)
    pe = sum(((pa[c] + pb[c]) / (2 * n)) * (1 - (pa[c] + pb[c]) / (2 * n))
             for c in cats) / (Q - 1)
    return (po - pe) / (1 - pe) if pe < 1 else 0.0


def quad_kappa(a, b, cats):
    n = len(a)
    idx = {c: k for k, c in enumerate(cats)}
    Q = len(cats)
    obs = collections.Counter(zip(a, b))
    pa = collections.Counter(a); pb = collections.Counter(b)
    num = den = 0.0
    for x in cats:
        for y in cats:
            w = (idx[x] - idx[y]) ** 2 / (Q - 1) ** 2
            o = obs.get((x, y), 0) / n
            e = (pa[x] / n) * (pb[y] / n)
            num += w * o
            den += w * e
    return 1 - num / den if den else 0.0


def stats(field, cats, rows):
    a = [r["A"][field] for r in rows]
    b = [r["B"][field] for r in rows]
    pairs = [(x, y) for x, y in zip(a, b) if x and y]
    a, b = [p[0] for p in pairs], [p[1] for p in pairs]
    n = len(pairs)
    po = sum(x == y for x, y in pairs) / n
    _, kap = cohen_kappa(a, b, cats)
    return {"n": n, "raw": round(po, 3), "kappa": round(kap, 3),
            "AC1": round(gwet_ac1(a, b, cats), 3), "PABAK": round(2 * po - 1, 3)}


def nat_stats(rows):
    a = [r["A"]["naturalness"] for r in rows]
    b = [r["B"]["naturalness"] for r in rows]
    pairs = [(int(x), int(y)) for x, y in zip(a, b) if x and y]
    n = len(pairs)
    exact = sum(x == y for x, y in pairs) / n
    within1 = sum(abs(x - y) <= 1 for x, y in pairs) / n
    return {"n": n, "exact": round(exact, 3), "within1": round(within1, 3),
            "quad_kappa_observed": round(quad_kappa([p[0] for p in pairs], [p[1] for p in pairs],
                                                  sorted({x for p in pairs for x in p})), 3),
            "quad_kappa_1to5": round(quad_kappa([p[0] for p in pairs], [p[1] for p in pairs],
                                              [1, 2, 3, 4, 5]), 3),
            "mean_A": round(sum(p[0] for p in pairs) / n, 2),
            "mean_B": round(sum(p[1] for p in pairs) / n, 2)}


def per_variant(rows):
    out = {}
    for v in VARIANTS:
        rs = [r for r in rows if r["variant"] == v]
        if rs:
            out[v] = {"meaning": stats("meaning", ["Yes", "Partly", "No"], rs),
                      "label": stats("label", ["Yes", "No"], rs),
                      "naturalness": nat_stats(rs)}
    return out


result = {
    "overall": {"meaning": stats("meaning", ["Yes", "Partly", "No"], ratings),
                "label": stats("label", ["Yes", "No"], ratings),
                "naturalness": nat_stats(ratings)},
    "per_variant": per_variant(ratings),
}
(ROOT / "data/human_validation/agreement.json").write_text(
    json.dumps(result, indent=1, ensure_ascii=False))
print(json.dumps(result["overall"], indent=1))

# disagreements table
dis = [r for r in ratings
       if r["A"]["meaning"] != r["B"]["meaning"] or r["A"]["label"] != r["B"]["label"]]
md = ["# Human validation — rater agreement", "",
      f"cells rated by both: {len(ratings)}", "",
      "## Overall agreement", "```json", json.dumps(result["overall"], indent=1), "```",
      "## Per variant", "```json", json.dumps(result["per_variant"], indent=1), "```",
      "## Meaning/Label disagreements", "",
      "| variant | id | type | A(m/l) | B(m/l) | B notes |",
      "|---|---|---|---|---|---|"]
for r in dis:
    md.append(f"| {r['variant']} | {r['id']} | {r['type']} | "
              f"{r['A']['meaning']}/{r['A']['label']} | {r['B']['meaning']}/{r['B']['label']} | "
              f"{(r['B']['notes'] or '')[:120]} |")
md += ["", "## B Label=No items (source-label disagreements with LLMBar gold; not blocking)", ""]
for r in ratings:
    if r["B"]["label"] == "No":
        md.append(f"- {r['id']} [{r['variant']}]: {(r['B']['notes'] or '')[:150]}")
md += ["", "## Fixes applied", ""]
cnt = collections.Counter((f["variant"], f["source"]) for f in fixes["fixes"])
for (v, s), c in sorted(cnt.items()):
    md.append(f"- {v} / source {s}: {c}")
md += ["", "## Rejected fixes", ""]
for r in fixes["rejected"]:
    md.append(f"- {r['variant']} {r['id']} {r['field']} (src {r['source']}): {r['rationale']}")

# final status counts
st = collections.Counter()
for l in open(ROOT / "data/item_status.jsonl"):
    r = json.loads(l)
    st[(r["variant"], r["status"])] += 1
md += ["", "## Final status counts", "", "| variant | status | n |", "|---|---|---|"]
for (v, s), c in sorted(st.items()):
    md.append(f"| {v} | {s} | {c} |")
md.append(f"\n**core_ids: {len(open(ROOT/'data/splits/core_387.txt').read().split())}**")
(ROOT / "docs" / "human_validation.md").parent.mkdir(exist_ok=True)
(ROOT / "docs" / "human_validation.md").write_text("\n".join(md))
print("disagreements:", len(dis))
