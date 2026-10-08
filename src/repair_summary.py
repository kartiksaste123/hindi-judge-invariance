import json, collections, random, sys
sys.path.insert(0, str(__file__).rsplit("/", 2)[0] + "/src")
from analyse import PRICES
from llm import ROOT

VARIANTS = ["hi_deva", "hi_roman", "hi_cm"]
en = {json.loads(l)["id"]: json.loads(l) for l in open(ROOT / "data/llmbar_en.jsonl")}
rng = random.Random(5)

pre = collections.defaultdict(collections.Counter)
post = collections.defaultdict(collections.Counter)
for l in open(ROOT / "data/pre_repair/status.jsonl"):
    r = json.loads(l); pre[r["variant"]][r["status"]] += 1
for l in open(ROOT / "data/status.jsonl"):
    r = json.loads(l); post[r["variant"]][r["status"]] += 1
core_b = len(open(ROOT / "data/pre_repair/core_ids.txt").read().split())
core_a = len(open(ROOT / "data/core_ids.txt").read().split())

# reason breakdown after
reasons = collections.defaultdict(collections.Counter)
for l in open(ROOT / "data/status.jsonl"):
    r = json.loads(l)
    for x in r["reasons"]:
        reasons[r["variant"]][x.split("=")[0] if not x.startswith("verifier:")
                             else "verifier:" + x.split(":")[1].split("=")[0]] += 1

# examples
ex = []
for v in VARIANTS:
    chosen = {}
    for l in open(ROOT / f"data/trans/{v}.jsonl"):
        r = json.loads(l); chosen[r["id"]] = r
    prev = {json.loads(l)["id"]: json.loads(l)
            for l in open(ROOT / f"data/pre_repair/trans/{v}.jsonl")}
    st = {(r["id"], r["variant"]): r["status"]
          for r in (json.loads(l) for l in open(ROOT / "data/status.jsonl"))}
    good = [i for i, t in chosen.items() if t.get("repaired") and st.get((i, v)) == "pass"]
    i = rng.choice(good)
    ex.append((i, v, prev[i]["texts"]["input"][:400], chosen[i]["texts"]["input"][:400]))

# sanity: gold vs non-gold length ratios among repaired
import statistics as stt
ratios = collections.defaultdict(list)
for v in VARIANTS:
    chosen = {}
    for l in open(ROOT / f"data/trans/{v}.jsonl"):
        r = json.loads(l); chosen[r["id"]] = r
    for i, t in chosen.items():
        if not t.get("repaired") or "texts" not in t:
            continue
        g = en[i]["label"]; og = 3 - g
        ratios["gold"].append(len(t["texts"][f"output_{g}"]) / max(1, len(en[i][f"output_{g}"])))
        ratios["nongold"].append(len(t["texts"][f"output_{og}"]) / max(1, len(en[i][f"output_{og}"])))

calls = [json.loads(l) for l in open(ROOT / "results/llm_calls.jsonl")]
cost = n = errs = 0
for c in calls:
    if not c["tag"].startswith("repair:"):
        continue
    n += 1; errs += bool(c.get("error"))
    u = c.get("usage") or {}
    pr = PRICES.get(c["model"], {"in": 3.0, "out": 15.0})
    cost += (u.get("prompt_tokens", 0) * pr["in"] + u.get("completion_tokens", 0) * pr["out"]) / 1e6

md = ["# Repair pass summary", "",
      "| variant | pass before→after | needs_review before→after | exclude_langdep before→after |",
      "|---|---|---|---|"]
for v in VARIANTS:
    md.append(f"| {v} | {pre[v]['pass']} → {post[v]['pass']} | "
              f"{pre[v]['needs_review']} → {post[v]['needs_review']} | "
              f"{pre[v]['exclude_langdep']} → {post[v]['exclude_langdep']} |")
md += ["", f"**core_ids: {core_b} → {core_a}**",
       f"Newly excluded as language_dependent during repair: "
       f"{open(ROOT/'data/repair_langdep.txt').read().split()}",
       "", "## Reason breakdown after repair"]
for v in VARIANTS:
    md.append(f"### {v}")
    for r, c in reasons[v].most_common():
        md.append(f"- {r}: {c}")
md += ["", "## Before/after examples (input field ≤400 chars)"]
for i, v, b, a in ex:
    md += [f"### {i} [{v}]", f"before: `{b}`", f"after: `{a}`", ""]
md += ["## Sanity check: do repairs favour the gold output?",
       f"Char-length ratio vs English among 116 repaired cells:",
       f"- gold output: mean {stt.mean(ratios['gold']):.3f}, median {stt.median(ratios['gold']):.3f}, "
       f"longer(>1.05) {sum(1 for x in ratios['gold'] if x>1.05)}, shorter(<0.95) {sum(1 for x in ratios['gold'] if x<0.95)}",
       f"- non-gold output: mean {stt.mean(ratios['nongold']):.3f}, median {stt.median(ratios['nongold']):.3f}, "
       f"longer(>1.05) {sum(1 for x in ratios['nongold'] if x>1.05)}, shorter(<0.95) {sum(1 for x in ratios['nongold'] if x<0.95)}",
       "", "## Cost",
       f"{n} repair-tagged calls, {errs} errors, ~${cost:.2f} token-estimated "
       f"(exact neuron billing in llm_calls.jsonl)."]
(ROOT / "results/repair_summary.md").write_text("\n".join(md))
print("written")
