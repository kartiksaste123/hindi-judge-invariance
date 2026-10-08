import json, random, subprocess, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = ROOT / "data" / "llmbar_repo"
if not REPO.exists():
    subprocess.run(["git", "clone", "https://github.com/princeton-nlp/LLMBar", str(REPO)], check=True)
sha = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
(ROOT / "data" / "SOURCE.txt").write_text(f"https://github.com/princeton-nlp/LLMBar commit {sha}\n")

SUBSETS = ["Natural", "Adversarial/Neighbor", "Adversarial/GPTInst", "Adversarial/GPTOut", "Adversarial/Manual"]
EXPECT = {"Natural": 100, "Adversarial/Neighbor": 134, "Adversarial/GPTInst": 92,
          "Adversarial/GPTOut": 47, "Adversarial/Manual": 46}

rows = []
for sub in SUBSETS:
    data = json.load(open(REPO / "Dataset" / "LLMBar" / sub / "dataset.json"))
    short = sub.split("/")[-1]
    assert len(data) == EXPECT[sub], (sub, len(data))
    for i, r in enumerate(data):
        rows.append({"id": f"{short}-{i:03d}", "subset": short,
                     "input": r["input"], "output_1": r["output_1"],
                     "output_2": r["output_2"], "label": r["label"]})
assert len(rows) == 419, len(rows)

with open(ROOT / "data" / "llmbar_en.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

# pilot: 10 per subset, seed 42
rng = random.Random(42)
pilot = []
for sub in ["Natural", "Neighbor", "GPTInst", "GPTOut", "Manual"]:
    ids = [r["id"] for r in rows if r["subset"] == sub]
    pilot += rng.sample(ids, 10)
(ROOT / "data" / "pilot50.txt").write_text("\n".join(pilot) + "\n")
print("rows", len(rows), "pilot", len(pilot), "sha", sha[:12])
