import argparse, json, pathlib, sys, collections, random
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from llm import ROOT, JUDGES

from scipy.stats import binomtest

VARIANTS = ["en", "hi_deva", "hi_roman", "hi_cm"]

# per-1M-token USD. Sources:
# Workers AI (REST API neuron-based billing, token equivalents from pricing page):
#   https://developers.cloudflare.com/workers-ai/platform/pricing/
# Gemini API: https://ai.google.dev/gemini-api/docs/pricing
PRICES = {
    "workers-ai/@cf/meta/llama-3.3-70b-instruct-fp8-fast": {"in": 0.293, "out": 2.253, "src": "https://developers.cloudflare.com/workers-ai/platform/pricing/"},
    "workers-ai/@cf/openai/gpt-oss-120b": {"in": 0.35, "out": 0.75, "src": "https://developers.cloudflare.com/workers-ai/platform/pricing/"},
    "workers-ai/@cf/qwen/qwen3-30b-a3b-fp8": {"in": 0.20, "out": 0.60, "src": "https://developers.cloudflare.com/workers-ai/platform/pricing/"},
    "workers-ai/@cf/google/gemma-4-26b-a4b-it": {"in": 0.30, "out": 0.90, "src": "estimate — not listed; gemma-class assumed"},
    "workers-ai/@cf/meta/llama-3.1-8b-instruct-fp8": {"in": 0.045, "out": 0.384, "src": "https://developers.cloudflare.com/workers-ai/platform/pricing/"},
    "google-ai-studio/gemini-2.5-pro": {"in": 1.25, "out": 10.00, "src": "https://ai.google.dev/gemini-api/docs/pricing"},
    "google-ai-studio/gemini-2.5-flash": {"in": 0.30, "out": 2.50, "src": "https://ai.google.dev/gemini-api/docs/pricing"},
}


def load():
    rows = [json.loads(l) for l in open(ROOT / "results" / "judgments.jsonl")]
    calls = [json.loads(l) for l in open(ROOT / "results" / "llm_calls.jsonl")] \
        if (ROOT / "results" / "llm_calls.jsonl").exists() else []
    return rows, calls


def metrics(rows):
    by = collections.defaultdict(list)
    for r in rows:
        by[(r["judge"], r["variant"])].append(r)
    out = {}
    for (j, v), rs in sorted(by.items()):
        n = len(rs)
        valid = [r for r in rs if r["valid"]]
        ab = {r["id"]: r["pick"] for r in valid if r["order"] == "AB"}
        ba = {r["id"]: r["pick"] for r in valid if r["order"] == "BA"}
        consistent = sum(1 for i in ab if i in ba and ab[i] == ba[i]) / max(1, len(ab))
        acc = sum(1 for r in valid if r["correct"]) / max(1, len(valid))
        firstpos = sum(1 for r in valid if r["raw"] and r["raw"].strip().endswith("(a)")
                     for _ in [0]) / max(1, len(valid)) if False else \
                   sum(1 for r in valid if r.get("_letter") == "a")
        out[(j, v)] = {"n": n, "invalid_rate": 1 - len(valid) / max(1, n),
                       "accuracy": acc, "pos_consistency": consistent,
                       "picks": {(r["id"], r["order"]): r["pick"] for r in valid},
                       "correct": {(r["id"], r["order"]): r["correct"] for r in valid},
                       "valid_rs": valid}
    return out


def main():
    rows, calls = load()
    # attach pick-letter for first-position rate: recompute from raw
    for r in rows:
        import re
        m = re.findall(r"Output \((a|b)\)", r.get("raw") or "")
        r["_letter"] = m[-1] if m else None
    M = metrics(rows)
    for k in M:
        v = M[k]["valid_rs"]
        M[k]["first_pos_rate"] = sum(1 for r in v if r["_letter"] == "a") / max(1, len(v))

    rng = random.Random(0)
    lines, csvrows = [], []
    hdr = ("judge,variant,n,invalid_rate,accuracy,pos_consistency,first_pos_rate,"
           "flip_rate,acc_delta,mcnemar_p,flip_ci_lo,flip_ci_hi,accd_ci_lo,accd_ci_hi")
    csvrows.append(hdr)

    judges = sorted({k[0] for k in M})
    variants = sorted({k[1] for k in M}, key=VARIANTS.index)
    for j in judges:
        en = M.get((j, "en"), {"picks": {}, "correct": {}, "valid_rs": [],
                               "n": 0, "invalid_rate": 1, "accuracy": 0,
                               "pos_consistency": 0, "first_pos_rate": 0})
        for v in variants:
            m = M.get((j, v))
            if not m:
                continue
            flip = accd = p = flo = fhi = dlo = dhi = ""
            if v != "en":
                cells = set(en["picks"]) & set(m["picks"])
                per_order = {}
                for order in ("AB", "BA"):
                    oc = [i for (i, o) in cells if o == order]
                    per_order[order] = sum(1 for i in oc
                                           if en["picks"][(i, order)] != m["picks"][(i, order)]) / max(1, len(oc))
                flip = sum(per_order.values()) / 2
                accd = m["accuracy"] - en["accuracy"]
                # McNemar on paired item×order correctness
                b = sum(1 for c in cells if en["correct"].get(c) and not m["correct"].get(c))
                c = sum(1 for c in cells if not en["correct"].get(c) and m["correct"].get(c))
                p = binomtest(min(b, c), b + c, 0.5).pvalue if (b + c) else 1.0
                # item-clustered bootstrap for flip & acc_delta CIs
                ids = sorted({i for (i, o) in cells})
                def stats(sample_ids):
                    s = set(sample_ids)
                    fl, da = [], []
                    for order in ("AB", "BA"):
                        oc = [i for i in s if (i, order) in cells]
                        fl.append(sum(1 for i in oc if en["picks"][(i, order)] != m["picks"][(i, order)]) / max(1, len(oc)))
                    ev = [r for r in en["valid_rs"] if r["id"] in s]
                    mv = [r for r in m["valid_rs"] if r["id"] in s]
                    acc_e = sum(1 for r in ev if r["correct"]) / max(1, len(ev))
                    acc_v = sum(1 for r in mv if r["correct"]) / max(1, len(mv))
                    return sum(fl) / 2, acc_v - acc_e
                fs, ds = [], []
                for _ in range(2000):
                    smp = [rng.choice(ids) for _ in ids]
                    f_, d_ = stats(smp)
                    fs.append(f_); ds.append(d_)
                fs.sort(); ds.sort()
                flo, fhi = fs[50], fs[1949]
                dlo, dhi = ds[50], ds[1949]
            row = (f"{j},{v},{m['n']},{m['invalid_rate']:.3f},{m['accuracy']:.3f},"
                   f"{m['pos_consistency']:.3f},{m['first_pos_rate']:.3f},"
                   + (f"{flip:.3f},{accd:.3f},{p:.4f},{flo:.3f},{fhi:.3f},{dlo:.3f},{dhi:.3f}"
                      if v != "en" else ",,,,,"))
            csvrows.append(row)

    (ROOT / "results" / "pilot_summary.csv").write_text("\n".join(csvrows) + "\n")

    # cost
    cost = calls_n = errors = 0
    tot_cost = 0.0
    for c in calls:
        calls_n += 1
        if c.get("error"):
            errors += 1
        u = c.get("usage") or {}
        pr = PRICES.get(c["model"], {"in": 0, "out": 0})
        tot_cost += (u.get("prompt_tokens", 0) * pr["in"] +
                     u.get("completion_tokens", 0) * pr["out"]) / 1e6

    md = ["# Pilot summary (50 items × 4 variants × 2 orders)", "",
          "| judge | variant | n | invalid | acc | pos_cons | first_pos | flip | Δacc | McNemar p | flip 95% CI | Δacc 95% CI |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for row in csvrows[1:]:
        f = row.split(",")
        md.append("| " + " | ".join(f[:7]) + " | " +
                  (" | ".join([f[7], f[8], f[9], f"{f[10]}–{f[11]}", f"{f[12]}–{f[13]}"]) if f[7] else "— | — | — | — | —") + " |")
    md += ["", f"## Cost", f"API calls: {calls_n} ({errors} errors)",
           f"Estimated total cost: **${tot_cost:.4f}** (token-based; Workers AI actually bills in neurons — raw `neurons` logged per call)",
           "", "PRICES used:", "```json", json.dumps(PRICES, indent=1), "```"]
    (ROOT / "results" / "pilot_summary.md").write_text("\n".join(md))
    print("\n".join(csvrows[:3]), f"\n... wrote {len(csvrows)-1} rows; cost ${tot_cost:.4f}; calls {calls_n}, errors {errors}")


if __name__ == "__main__":
    main()
