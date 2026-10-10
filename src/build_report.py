import base64, json, pathlib, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]
M = ROOT / "results" / "metrics"; F = ROOT / "results" / "figures"
B = ROOT / "build"; B.mkdir(exist_ok=True)
class _O:  # shim so existing O/... expressions still work
    def __truediv__(self, n): return F / n
O = _O()
VN = {"en": "English", "hi_deva": "Hindi (Devanagari)", "hi_roman": "Romanized Hindi", "hi_cm": "Hinglish"}
J = ["gpt-oss-120b", "llama-3.3-70b", "gemma-4-26b", "qwen3-30b", "claude-haiku-4-5", "llama-3.1-8b"]
T = pd.read_csv(M / "metrics_main.csv"); N = pd.read_csv(M / "repeat_noise.csv"); S = json.load(open(M / "stats.json"))
G = pd.read_csv(M / "gee_odds_ratios.csv", index_col=0)
def img(n, cap): return f'<figure><img src="data:image/png;base64,{base64.b64encode((F/n).read_bytes()).decode()}"><figcaption>{cap}</figcaption></figure>'
def pct(x): return f"{100*x:.1f}"
rows = ""
for j in J:
    for v in VN:
        r = T[(T.judge == j) & (T.variant == v)].iloc[0]
        if v == "en":
            rows += f"<tr class=en><td>{j}</td><td>{VN[v]}</td><td>{pct(r.accuracy)}</td><td>—</td><td>—</td><td>{pct(r.pos_consistency)}</td><td>{pct(r.first_pos_rate)}</td><td>—</td></tr>"
        else:
            rows += (f"<tr><td>{j}</td><td>{VN[v]}</td><td>{pct(r.accuracy)}</td><td>{100*r.acc_delta:+.1f} [{100*r.acc_delta_ci_lo:+.1f}, {100*r.acc_delta_ci_hi:+.1f}]</td>"
                     f"<td>{pct(r.flip_rate)} [{pct(r.flip_ci_lo)}, {pct(r.flip_ci_hi)}]</td><td>{pct(r.pos_consistency)}</td><td>{pct(r.first_pos_rate)}</td><td>{r.mcnemar_p_holm:.2g}</td></tr>")
nrows = "".join(f"<tr><td>{r.judge}</td><td>{VN[r.variant]}</td><td>{pct(r.self_flip_rate)}</td><td>{pct(r.all3_identical)}</td><td>{'—' if pd.isna(r.flip_rate) else pct(r.flip_rate)}</td><td>{'—' if pd.isna(r.excess_flip) else f'{100*r.excess_flip:+.1f}'}</td></tr>" for r in N.itertuples())
grows = "".join(f"<tr><td>{VN[k.split('T.')[1].rstrip(']')]}</td><td>{r.OR:.3f}</td><td>[{r.lo:.3f}, {r.hi:.3f}]</td><td>{r.p:.1e}</td></tr>" for k, r in G[G.index.str.startswith('C(variant)')].iterrows())
sens = ""
for tag, name in [("main", "All 387 items"), ("no_codeheavy", "Without 12 code-heavy items (375)"), ("no_humanfixed", "Without 34 human-fixed items (353)")]:
    d = pd.read_csv(M / f"metrics_{tag}.csv"); d = d[d.variant != "en"]; m = d.groupby("variant").acc_delta.mean()
    sens += f"<tr><td>{name}</td>" + "".join(f"<td>{100*m[v]:+.1f}</td>" for v in ["hi_deva", "hi_roman", "hi_cm"]) + f"<td>{(d.mcnemar_p_holm<.05).sum()}/18</td></tr>"
P = S["pooled"]
html = f"""<!doctype html><html><head><meta charset=utf-8><title>Step 4–5 Results</title>
<script>MathJax={{tex:{{inlineMath:[['\\\\(','\\\\)']]}},svg:{{fontCache:'global'}}}};</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
<style>body{{font-family:Georgia,serif;max-width:900px;margin:auto;padding:20px;line-height:1.45;font-size:13px}}h1{{font-size:21px}}h2{{font-size:17px;border-bottom:1px solid #ccc;margin-top:26px}}
table{{border-collapse:collapse;font-size:11px;margin:8px 0}}td,th{{border:1px solid #bbb;padding:3px 6px;text-align:center}}th{{background:#eee}}tr.en td{{background:#f6f6f6;font-weight:bold}}
figure{{margin:12px 0;page-break-inside:avoid}}img{{max-width:100%}}figcaption{{font-size:11px;color:#444}}pre{{background:#f5f5f5;padding:10px;font-size:11px;white-space:pre-wrap}}.box{{background:#eef5ff;padding:10px;border-left:4px solid #47c}}</style></head><body>
<h1>Language-Switching Invariance of LLM-as-a-Judge for Hindi Scripts and Hinglish — Step 4 run and results</h1>
<p>Data: LLMBar (419 pairwise items) → 387-item human-validated core, rendered in English, Hindi (Devanagari), Romanized Hindi and code-mixed Hinglish. Six judges, two answer orders, temperature 0, Cloudflare AI Gateway (cache off).</p>
<div class=box><b>Main findings.</b><ol>
<li>All six judges were less accurate in every Hindi-language condition than in English, and each of the 18 judge × language drops is significant after Holm correction (paired McNemar, p<sub>Holm</sub> ≤ 0.02).</li>
<li>Pooled accuracy: English {pct(P['en'])}%, Devanagari {pct(P['hi_deva'])}%, Hinglish {pct(P['hi_cm'])}%, Romanized {pct(P['hi_roman'])}%. <b>Romanized Hindi is the hardest condition</b>: an item-clustered GEE gives odds ratio 0.60 [0.54, 0.67] for a correct verdict, compared with English.</li>
<li>Judges flip their verdict on 8–25% of identical item/order pairs when only the language/script changes. That is well above their own same-prompt re-run flip rate (0–11%).</li>
<li>Judges are affected differently (variant × judge interaction Wald χ²={S['interaction_wald']['stat']:.1f}, df={S['interaction_wald']['df']}, p={S['interaction_wald']['p']:.3f}). GPT-OSS-120B is the most robust (−3 pp); Llama-3.3-70B and Claude Haiku 4.5 lose 11–13 pp on Romanized Hindi.</li>
<li>The effect remains when the 12 code-heavy items or the 34 human-fixed items are removed (Table 4).</li></ol></div>

<h2>1. Step 4 run completeness</h2>
<table><tr><th>Run</th><th>Design</th><th>Expected</th><th>Present</th><th>Valid</th></tr>
<tr><td>Main (run 0)</td><td>387 items × 4 languages × 2 orders × 6 judges</td><td>18,576</td><td>18,576</td><td>18,570</td></tr>
<tr><td>Repeat 1, 2</td><td>100 fixed items (seed 2027) × 4 × 2 × 6, twice</td><td>9,600</td><td>9,600</td><td>9,600</td></tr></table>
<p>The 6 unreadable judgments remained unreadable after 3 attempts each: 3 Qwen3 outputs where reasoning was cut off at the token limit, and 3 Llama-3.1-8B refusals. They are kept in the logs and <b>counted as incorrect</b> (a conservative choice). The run made 32,010 API calls, including retries of HTTP 429 rate-limit errors, at an estimated cost of $11.53 (token-based estimate). Every record stores the prompt hash, returned model, translation version, timestamp, token usage and raw response.</p>

<h2>2. Method (algorithm)</h2>
<pre>Algorithm 1: Controlled language-switching meta-evaluation
Input: items D = {{(x, y1, y2, g)}}, languages L = {{en, deva, roman, cm}}, judges J, orders O = {{AB, BA}}
1  for each item d in D, language l in L:  (x, y1, y2)_l ← validated translation T_l(d)   # human-checked
2  for each judge j, item d, language l, order o:
3      prompt ← fixed LLMBar judge template filled with (x_l, first, second) per o
4      r ← j(prompt; temperature=0, no cache);   parse last "Output (a|b)" → pick p ∈ {{1,2}}
5      if unparseable or API error: retry (≤3 attempts) else store (p, raw, usage, hashes)
6  repeat lines 2–5 for runs k = 1, 2 on a fixed 100-item subset (noise floor)
7  compute accuracy, flip rate, position consistency per (j, l); pair cells on (d, o)
8  test l vs en: exact McNemar per judge (Holm across 18 tests); item-clustered bootstrap CIs (B=2000)
9  pooled model: GEE logistic correct ~ language + judge + order, clustered by item</pre>

<h2>3. Metrics and equations</h2>
<p>For judge \\(j\\), language \\(\\ell\\), item \\(i\\), order \\(o\\): the pick is \\(p_{{j\\ell io}}\\in\\{{1,2\\}}\\) and the gold label is \\(g_i\\).</p>
<p>Accuracy: \\[\\mathrm{{Acc}}_{{j\\ell}} = \\frac{{1}}{{2|D|}}\\sum_{{i\\in D}}\\sum_{{o\\in\\{{AB,BA\\}}}} \\mathbb{{1}}[p_{{j\\ell io}}=g_i]\\]</p>
<p>Language-switch flip rate (relative to English): \\[\\mathrm{{Flip}}_{{j\\ell}} = \\frac{{1}}{{2|D|}}\\sum_{{i,o}} \\mathbb{{1}}[p_{{j\\ell io}}\\neq p_{{j,\\mathrm{{en}},io}}]\\]</p>
<p>Accuracy gap: \\(\\Delta_{{j\\ell}}=\\mathrm{{Acc}}_{{j\\ell}}-\\mathrm{{Acc}}_{{j,\\mathrm{{en}}}}\\). Position consistency: \\(\\mathrm{{PC}}_{{j\\ell}}=\\frac{{1}}{{|D|}}\\sum_i \\mathbb{{1}}[p_{{j\\ell i,AB}}=p_{{j\\ell i,BA}}]\\).</p>
<p>Re-run noise floor: across runs \\(k&lt;k'\\) on the subset \\(D_{{100}}\\), \\(\\mathrm{{SelfFlip}}_{{j\\ell}}=\\binom{{3}}{{2}}^{{-1}}\\sum_{{k&lt;k'}}\\frac{{1}}{{2|D_{{100}}|}}\\sum_{{i,o}}\\mathbb{{1}}[p^{{(k)}}_{{j\\ell io}}\\neq p^{{(k')}}_{{j\\ell io}}]\\), and \\(\\mathrm{{Excess}}_{{j\\ell}}=\\mathrm{{Flip}}_{{j\\ell}}-\\mathrm{{SelfFlip}}_{{j\\ell}}\\).</p>
<p>Exact McNemar test on the paired cells, with \\(b\\) = right in English and wrong in \\(\\ell\\), \\(c\\) = the reverse: \\[p = P\\big(X\\le\\min(b,c)\\big)\\cdot 2,\\quad X\\sim\\mathrm{{Bin}}(b+c,\\tfrac12)\\]</p>
<p>GEE logistic model with exchangeable within-item correlation: \\[\\operatorname{{logit}} P(y_{{ij\\ell o}}=1)=\\beta_0+\\beta_\\ell+\\gamma_j+\\delta_o,\\qquad \\mathrm{{OR}}_\\ell=e^{{\\beta_\\ell}}\\]</p>
<p>Confidence intervals come from 2000 bootstrap resamples of items (the clusters), so the two orders and the paired cells of an item are resampled together.</p>

<h2>4. Results</h2>
{img('fig1_accuracy_heatmap.png','Figure 1. Accuracy (%) of each judge in each language condition.')}
<p><b>Table 1.</b> Per-judge results. Δacc and flip are relative to English; 95% item-clustered bootstrap CIs in brackets; p is Holm-adjusted McNemar.</p>
<table><tr><th>Judge</th><th>Language</th><th>Acc %</th><th>Δacc pp [95% CI]</th><th>Flip % [95% CI]</th><th>Pos. consistency %</th><th>First-pos %</th><th>p (Holm)</th></tr>{rows}</table>
{img('fig2_acc_delta.png','Figure 2. Accuracy change vs English with 95% CIs. All 18 bars exclude 0.')}
{img('fig3_flip_rate.png','Figure 3. Fraction of identical item/order pairs whose verdict changes when only the language changes.')}
{img('fig4_noise_floor.png','Figure 4. Cross-language flips (bars) vs the same-prompt re-run flip rate (black ticks) on the 100-item repeat subset.')}
<p><b>Table 2.</b> Repeat-run stability on the 100-item subset (3 runs).</p>
<table><tr><th>Judge</th><th>Language</th><th>Self-flip %</th><th>All 3 runs identical %</th><th>Cross-language flip % (subset)</th><th>Excess pp</th></tr>{nrows}</table>
<p>Llama-3.3-70B, Claude Haiku and Llama-3.1-8B are almost deterministic (self-flip ≤1%), so almost all of their cross-language flips are caused by the language change. Gemma-4 and Qwen3 have a re-run noise floor of 7–11%. For Gemma on Hinglish, the excess is about 0, so most of its Hinglish flips there are noise.</p>
<p><b>Table 3.</b> GEE logistic model (387 item clusters, n=18,576), odds ratio of a correct verdict vs English, adjusted for judge and order.</p>
<table><tr><th>Language</th><th>OR</th><th>95% CI</th><th>p</th></tr>{grows}</table>
{img('fig9_gee_or.png','Figure 9. GEE odds ratios with 95% CIs.')}
{img('fig5_position_bias.png','Figure 5. Position consistency and first-position preference. Switching away from English lowers consistency for most judges.')}
{img('fig6_confusion_gold.png','Figure 6. Confusion matrices (gold better output vs judge pick), valid judgments only. Llama-3.1-8B is near chance in English and anti-correlated with gold in Hindi conditions.')}
{img('fig7_mcnemar_tables.png','Figure 7. Paired correctness tables (English vs each language) used for the McNemar tests. The off-diagonal asymmetry (EN✓→✗ ≫ EN✗→✓) is the effect.')}
{img('fig8_subset_accuracy.png','Figure 8. Accuracy by LLMBar subset, pooled over judges.')}

<h2>5. Robustness</h2>
<p><b>Table 4.</b> Mean Δacc (pp) across the six judges, and the number of judge × language cells significant after Holm correction.</p>
<table><tr><th>Item set</th><th>Devanagari</th><th>Romanized</th><th>Hinglish</th><th>Significant</th></tr>{sens}</table>
<p>The full per-judge tables for each subset are in metrics_no_codeheavy.csv and metrics_no_humanfixed.csv. Counting the 6 unreadable judgments as incorrect vs dropping them changes accuracy by at most 0.2 pp (Table 1 shows only the conservative version; both are in the CSV).</p>

<h2>6. Limitations (to state in the paper)</h2>
<ul><li>Translations were made by machine (Gemini 2.5 Pro), checked by Claude Sonnet 4.5, and human-validated by two raters on 251 cells (raw meaning agreement 91%, Gwet's AC1 0.91). A drop in accuracy may partly reflect residual translation quality rather than judge bias, although the effect holds after removing human-fixed items.</li>
<li>One benchmark (LLMBar), one prompt template, and six judges accessed through Cloudflare/Anthropic APIs at a fixed date. Results are a measurement for these settings, not a universal claim.</li>
<li>Claude Haiku 4.5 belongs to the same family as the verifier model (Claude Sonnet 4.5), not the translator.</li>
<li>Cost is a token-based estimate; the exact billing is in the AI Gateway logs.</li></ul>
<p style=font-size:10px;color:#666>Code: src/run_judges.py, src/check_judgments.py, src/analyze_results.py, src/build_report.py. Raw data: results/judgments/*.jsonl.</p>
</body></html>"""
(B / "report.html").write_text(html)
