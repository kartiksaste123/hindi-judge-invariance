# hindi-judge-invariance

**Language-Switching Invariance of LLM-as-a-Judge for Hindi Scripts and Hinglish: Evidence from Controlled Pairwise Meta-Evaluation**

Does an LLM judge pick a different answer when the *same* question and the *same* two candidate answers are written in English, Hindi (Devanagari), Romanized Hindi, or code-mixed Hinglish?

## Design
- **Data:** [LLMBar](https://github.com/princeton-nlp/LLMBar) (419 pairwise items with gold labels, MIT license), translated into 3 Hindi variants by `gemini-2.5-pro`. Each translation was automatically verified by `claude-sonnet-4-5`, repaired, and human-validated by two bilingual raters (251 cells).
- **Final core:** 387 items. 31 items whose evaluation depends on English (rhyme, spelling, grammar) are excluded, and 1 item is excluded because the translator's safety filter blocked it.
- **Judges (6):** GPT-OSS-120B, Llama-3.3-70B, Llama-3.1-8B, Qwen3-30B, Gemma-4-26B (Cloudflare Workers AI), Claude Haiku 4.5. Gemini is not a judge, because it produced the translations.
- **Run:** 387 items × 4 languages × 2 answer orders × 6 judges = 18,576 judgments. Repeat runs: the same setup re-run twice on a fixed 100-item subset (9,600 judgments) to measure the re-run noise floor. Temperature 0, gateway cache off.
- **Analysis:** accuracy vs gold, verdict flip rate vs English, position consistency, exact McNemar (Holm-corrected), item-clustered bootstrap CIs, item-clustered GEE logistic model, and a same-prompt re-run noise floor.

## Headline result
Pooled accuracy: English 78.9%, Devanagari 74.1%, Hinglish 73.3%, Romanized 70.3%. Each of the 18 judge × language drops is significant after Holm correction. Romanized Hindi is the hardest (GEE OR 0.60 [0.54, 0.67] vs English). Full report: `results/step5/Step4_Results_Report.pdf`.

## Layout
```
prompts/            judge, translation, verification and repair prompts
src/                pipeline code (see below)
data/llmbar_en.jsonl          normalized LLMBar source
data/trans/*.jsonl            all translation attempts (last record per id is active)
data/final/*.jsonl            finalized cells with status + human-validation metadata
data/core_ids.txt             387-item final core;  data/repeat100.txt  repeat subset (seed 2027)
data/human_check_v2/          original rater workbooks (unchanged)
data/human_adjudication/      extracted ratings, agreement stats, exact fixes applied
data/pre_repair/, data/pre_human/   snapshots before repair / human fixes
results/step4/                raw judgments: judgments.jsonl (run 0), run1.jsonl, run2.jsonl
results/step5/                metrics CSVs, figures, report (PDF/HTML/DOCX)
results/llm_calls.jsonl       every API call: model, prompt hash, usage, latency, raw response
results/v1/, results/judgments.jsonl   pilot runs (exploratory, not used in final results)
```

## Reproduce
```bash
pip install -r requirements.txt   # report export also needs pandoc
export CLOUDFLARE_ACCOUNT_ID=...  CLOUDFLARE_API_TOKEN=...   # AI Gateway named llm-judge-hinglish
python data/fetch_llmbar.py                    # optional: data/llmbar_en.jsonl is already included
python src/translate.py --variants hi_deva,hi_roman,hi_cm --ids <ids>   # then src/verify.py, src/repair.py
python src/finalize.py                          # statuses + core_ids
python src/judge.py --variants en,hi_deva,hi_roman,hi_cm --ids data/core_ids.txt --run 0 --out results/step4/judgments.jsonl
python src/judge.py --variants en,hi_deva,hi_roman,hi_cm --ids data/repeat100.txt --run 1 --out results/step4/run1.jsonl
python src/judge.py --variants en,hi_deva,hi_roman,hi_cm --ids data/repeat100.txt --run 2 --out results/step4/run2.jsonl
python src/judge.py ... --retry-invalid          # retry unreadable verdicts (max 3 attempts)
python src/check_step4.py                        # completeness check
python src/step5_analysis.py && python src/build_report.py && python src/export_report.py
```
Analysis needs no API access: all raw judgments are included.

## License
Code is MIT (see `LICENSE`). LLMBar is MIT, © Princeton NLP. Translations and human annotations are released for research use; please cite this work and LLMBar.
