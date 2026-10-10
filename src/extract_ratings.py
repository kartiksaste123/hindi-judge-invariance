import json, pathlib, sys, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from llm_client import ROOT
import openpyxl

SHEETS = {"Hindi (Devanagari)": "hi_deva", "Romanized Hindi": "hi_roman",
          "Hinglish (code-mixed)": "hi_cm"}
FILES = {"A": ROOT / "data/human_validation/rater_A.xlsx",
         "B": ROOT / "data/human_validation/rater_B.xlsx"}
COLS = {"type": 1, "id": 2, "meaning": 11, "label": 12, "naturalness": 13,
        "fix": 14, "notes": 15}


def read(fn):
    wb = openpyxl.load_workbook(fn, read_only=True)
    out = {}
    for sheet, variant in SHEETS.items():
        ws = wb[sheet]
        for row in ws.iter_rows(2, values_only=True):
            if not row[COLS["id"]]:
                continue
            iid = str(row[COLS["id"]]).strip()
            out[(variant, iid)] = {
                "type": row[COLS["type"]],
                "meaning": row[COLS["meaning"]],
                "label": row[COLS["label"]],
                "naturalness": row[COLS["naturalness"]],
                "fix": row[COLS["fix"]],
                "notes": row[COLS["notes"]],
            }
    return out


def clean(v):
    return v if v not in ("", None) else None


def main():
    ra, rb = read(FILES["A"]), read(FILES["B"])
    keys = sorted(set(ra) & set(rb))
    recs = []
    for k in keys:
        a, b = ra[k], rb[k]
        recs.append({"variant": k[0], "id": k[1], "type": a["type"] or b["type"],
                     "A": {f: clean(a[f]) for f in ("meaning", "label", "naturalness", "fix", "notes")},
                     "B": {f: clean(b[f]) for f in ("meaning", "label", "naturalness", "fix", "notes")}})
    out = ROOT / "data/human_validation/ratings.jsonl"
    with open(out, "w") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(len(recs), "cells;", collections.Counter(r["variant"] for r in recs))


if __name__ == "__main__":
    main()
