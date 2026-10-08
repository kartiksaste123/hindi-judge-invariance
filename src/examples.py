import json, random, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from llm import ROOT

VARIANTS = ["hi_deva", "hi_roman", "hi_cm"]
FIELDS = ["input", "output_1", "output_2"]
TRUNC = 600

en = {json.loads(l)["id"]: json.loads(l) for l in open(ROOT / "data/llmbar_en.jsonl")}
trans = {v: {json.loads(l)["id"]: json.loads(l) for l in open(ROOT / f"data/trans/{v}.jsonl")} for v in VARIANTS}
pilot = [l.strip() for l in open(ROOT / "data/pilot50.txt") if l.strip()]

rng = random.Random(7)
sample = rng.sample(pilot, 5)
failed = [(v, r) for v in VARIANTS for r in trans[v].values()
          if r.get("error") or r.get("failed_checks")]

def t(s):
    s = s or ""
    return s[:TRUNC] + (" …[truncated]" if len(s) > TRUNC else "")

md = ["# Translation examples\n"]
for i in sample:
    md.append(f"## {i} ({en[i]['subset']}) — gold label {en[i]['label']}\n")
    for f in FIELDS:
        md.append(f"### `{f}`\n**en:**\n```\n{t(en[i][f])}\n```")
        for v in VARIANTS:
            tt = (trans[v].get(i) or {}).get("texts", {}).get(f, "*missing*")
            md.append(f"**{v}:**\n```\n{t(tt)}\n```")
md.append("\n# Items that failed automatic checks\n")
for v, r in failed:
    md.append(f"- **{r['id']} [{v}]**: " +
              (f"error={r['error']}" if r.get("error") else f"checks={r['checks']}"))
md.append("")
(ROOT / "results" / "translation_examples.md").write_text("\n".join(md))
print("wrote", len(sample), "examples,", len(failed), "failures")
