"""Step 5 analysis of the Step 4 judge run. Unit of pairing = (item, answer order)."""
import json, re, pathlib, sys, collections, random, itertools
import numpy as np, pandas as pd
from scipy.stats import binomtest
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns
import statsmodels.api as sm, statsmodels.formula.api as smf

ROOT = pathlib.Path(__file__).resolve().parents[1]
S4, OUT = ROOT / "results" / "step4", ROOT / "results" / "step5"
OUT.mkdir(parents=True, exist_ok=True)
V = ["en", "hi_deva", "hi_roman", "hi_cm"]
VN = {"en": "English", "hi_deva": "Hindi (Devanagari)", "hi_roman": "Romanized Hindi", "hi_cm": "Hinglish"}
J = ["gpt-oss-120b", "llama-3.3-70b", "gemma-4-26b", "qwen3-30b", "claude-haiku-4-5", "llama-3.1-8b"]
B = 2000
rng = np.random.default_rng(0)

def load(paths):
    last = {}
    for p in paths:
        if p.exists():
            for l in open(p):
                r = json.loads(l)
                last[(r["id"], r["variant"], r["order"], r["judge"], r.get("run", 0))] = r
    rows = []
    for r in last.values():
        m = re.findall(r"Output \((a|b)\)", r.get("raw") or "")
        rows.append({"id": r["id"], "subset": r["subset"], "variant": r["variant"], "order": r["order"],
                     "judge": r["judge"], "run": r.get("run", 0), "valid": bool(r["valid"]),
                     "pick": r["pick"], "correct": bool(r["correct"]) if r["valid"] else False,
                     "letter": (m[-1] if (m and r["valid"]) else None)})
    return pd.DataFrame(rows)

core = [l.strip() for l in open(ROOT / "data/core_ids.txt") if l.strip()]
rep100 = [l.strip() for l in open(ROOT / "data/repeat100.txt") if l.strip()]
gold = {json.loads(l)["id"]: json.loads(l)["label"] for l in open(ROOT / "data/llmbar_en.jsonl")}
df = load([S4 / "judgments.jsonl", S4 / "run1.jsonl", S4 / "run2.jsonl"])
df = df[df.id.isin(core)]
main = df[df.run == 0].copy()
assert len(main) == len(core) * 4 * 2 * 6, len(main)

# code-heavy items (devanagari_low in hi_deva) for sensitivity
deva = {json.loads(l)["id"]: json.loads(l) for l in open(ROOT / "data/final/hi_deva.jsonl")}
code_heavy = {i for i in core if "check:devanagari_low" in (deva[i].get("auto_reasons") or [])}
fixed_items = set()
for v in V[1:]:
    for l in open(ROOT / f"data/final/{v}.jsonl"):
        r = json.loads(l)
        if r.get("human_fixed"): fixed_items.add(r["id"])

def wide(d, col):
    """pivot to (judge, id, order) x variant"""
    return d.pivot_table(index=["judge", "id", "order"], columns="variant", values=col, aggfunc="first")

def boot_ci(ids, f):
    ids = np.array(sorted(ids)); vals = []
    for _ in range(B):
        vals.append(f(rng.choice(ids, len(ids))))
    return np.percentile(vals, [2.5, 97.5])

def holm(ps):
    order = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0
    for k, i in enumerate(order):
        run = max(run, min(1, (m - k) * ps[i])); adj[i] = run
    return adj

def table(d, tag):
    P, C = wide(d, "pick"), wide(d, "correct").astype(float)
    Vd = wide(d, "valid").astype(float)
    rows = []
    for j in J:
        pj, cj = P.loc[j], C.loc[j]
        sub = d[d.judge == j]
        for v in V:
            s = sub[sub.variant == v]; sv = s[s.valid]
            ab = s[s.order == "AB"].set_index("id").pick; ba = s[s.order == "BA"].set_index("id").pick
            both = ab.notna() & ba.notna()
            r = {"judge": j, "variant": v, "n": len(s), "invalid_rate": 1 - s.valid.mean(),
                 "accuracy": s.correct.mean(),  # invalid counted as incorrect
                 "accuracy_valid_only": sv.correct.mean(),
                 "pos_consistency": (ab[both] == ba[both]).mean(),
                 "first_pos_rate": (sv.letter == "a").mean()}
            if v != "en":
                ok = pj["en"].notna() & pj[v].notna()
                flips = (pj["en"][ok] != pj[v][ok]).astype(float)
                bb = int(((cj["en"] == 1) & (cj[v] == 0)).sum()); cc = int(((cj["en"] == 0) & (cj[v] == 1)).sum())
                r.update({"flip_rate": flips.mean(), "acc_delta": cj[v].mean() - cj["en"].mean(),
                          "en_right_v_wrong": bb, "en_wrong_v_right": cc,
                          "mcnemar_p": binomtest(min(bb, cc), bb + cc, 0.5).pvalue if bb + cc else 1.0})
                fl = flips.groupby(level="id").mean(); dl = (cj[v] - cj["en"]).groupby(level="id").mean()
                r["flip_ci"] = boot_ci(fl.index, lambda ids: fl.loc[ids].mean())
                r["acc_delta_ci"] = boot_ci(dl.index, lambda ids: dl.loc[ids].mean())
            rows.append(r)
    t = pd.DataFrame(rows)
    m = t.variant != "en"
    t.loc[m, "mcnemar_p_holm"] = holm(t.loc[m, "mcnemar_p"].values)
    for k in ("flip_ci", "acc_delta_ci"):
        t.loc[m, k + "_lo"] = [x[0] for x in t.loc[m, k]]; t.loc[m, k + "_hi"] = [x[1] for x in t.loc[m, k]]
    t = t.drop(columns=["flip_ci", "acc_delta_ci"])
    t.to_csv(OUT / f"metrics_{tag}.csv", index=False)
    return t

T = table(main, "main")
T_nocode = table(main[~main.id.isin(code_heavy)], "no_codeheavy")
T_nofix = table(main[~main.id.isin(fixed_items)], "no_humanfixed")

# repeat-run noise floor on repeat100: self-flip between runs within the same variant
rp = df[df.id.isin(rep100)]
noise = []
for j in J:
    for v in V:
        s = rp[(rp.judge == j) & (rp.variant == v)].pivot_table(index=["id", "order"], columns="run", values="pick", aggfunc="first")
        pairs = [(a, b) for a, b in itertools.combinations([0, 1, 2], 2) if a in s and b in s]
        sf = np.mean([(s[a][s[a].notna() & s[b].notna()] != s[b][s[a].notna() & s[b].notna()]).mean() for a, b in pairs])
        allsame = (s.nunique(axis=1) == 1).mean()
        # cross-language flip on the same 100 items, run 0
        noise.append({"judge": j, "variant": v, "self_flip_rate": sf, "all3_identical": allsame})
N = pd.DataFrame(noise)
x100 = T.set_index(["judge", "variant"])  # full-set flips
sub100 = table(main[main.id.isin(rep100)], "repeat100_subset")
N = N.merge(sub100[["judge", "variant", "flip_rate"]], on=["judge", "variant"], how="left")
N["excess_flip"] = N.flip_rate - N.self_flip_rate
N.to_csv(OUT / "repeat_noise.csv", index=False)

# confusion matrices: gold vs pick, per judge x variant (valid only)
cm = {}
for j in J:
    for v in V:
        s = main[(main.judge == j) & (main.variant == v) & main.valid]
        g = s.id.map(gold)
        cm[(j, v)] = pd.crosstab(g, s.pick).reindex(index=[1, 2], columns=[1, 2], fill_value=0).values.tolist()

# GEE logistic: correct ~ variant + judge + order, clustered by item (exchangeable)
g = main.copy(); g["correct"] = g.correct.astype(int)
g["variant"] = pd.Categorical(g.variant, V); g["judge"] = pd.Categorical(g.judge, J)
gee = smf.gee("correct ~ C(variant) + C(judge) + C(order)", groups="id", data=g,
              family=sm.families.Binomial(), cov_struct=sm.cov_struct.Exchangeable()).fit()
gee_or = pd.DataFrame({"OR": np.exp(gee.params), "lo": np.exp(gee.conf_int()[0]),
                       "hi": np.exp(gee.conf_int()[1]), "p": gee.pvalues})
gee_or.to_csv(OUT / "gee_odds_ratios.csv")
gee_x = smf.gee("correct ~ C(variant) * C(judge) + C(order)", groups="id", data=g,
                family=sm.families.Binomial(), cov_struct=sm.cov_struct.Exchangeable()).fit()
# Wald test that all variant x judge interactions are zero
names = [n for n in gee_x.params.index if ":" in n]
R = np.zeros((len(names), len(gee_x.params)))
for k, n in enumerate(names): R[k, list(gee_x.params.index).index(n)] = 1
wald = gee_x.wald_test(R, scalar=True)

# per-subset accuracy (pooled over judges)
subacc = main.groupby(["subset", "variant"]).correct.mean().unstack()[V]
subacc.to_csv(OUT / "subset_accuracy.csv")

# ---------- figures ----------
sns.set_theme(style="whitegrid", font_scale=0.95)
def save(f, name): f.tight_layout(); f.savefig(OUT / name, dpi=200); plt.close(f)
A = T.pivot(index="judge", columns="variant", values="accuracy").loc[J, V].rename(columns=VN)
f, ax = plt.subplots(figsize=(7.5, 4)); sns.heatmap(A * 100, annot=True, fmt=".1f", cmap="RdYlGn", vmin=40, vmax=95, ax=ax, cbar_kws={"label": "accuracy %"})
ax.set_title("Fig. 1  Judge accuracy against LLMBar gold (387 items × 2 orders)"); ax.set_xlabel(""); ax.set_ylabel(""); save(f, "fig1_accuracy_heatmap.png")

def bars(col, lo, hi, title, ylabel, name, pct=True):
    t = T[T.variant != "en"]; f, ax = plt.subplots(figsize=(8.5, 4)); w = 0.27
    for k, v in enumerate(V[1:]):
        s = t[t.variant == v].set_index("judge").loc[J]; x = np.arange(len(J)) + (k - 1) * w
        ax.bar(x, s[col] * 100, w, label=VN[v], yerr=[(s[col] - s[lo]) * 100, (s[hi] - s[col]) * 100], capsize=3)
    ax.axhline(0, color="k", lw=0.8); ax.set_xticks(np.arange(len(J))); ax.set_xticklabels(J, rotation=20)
    ax.set_ylabel(ylabel); ax.set_title(title); ax.legend(fontsize=8); save(f, name)
bars("acc_delta", "acc_delta_ci_lo", "acc_delta_ci_hi", "Fig. 2  Accuracy change vs English (95% item-clustered bootstrap CI)", "Δ accuracy (pp)", "fig2_acc_delta.png")
bars("flip_rate", "flip_ci_lo", "flip_ci_hi", "Fig. 3  Verdict flip rate vs English (95% CI)", "flip rate %", "fig3_flip_rate.png")

f, ax = plt.subplots(figsize=(8.5, 4)); w = 0.27
for k, v in enumerate(V[1:]):
    s = N[N.variant == v].set_index("judge").loc[J]; x = np.arange(len(J)) + (k - 1) * w
    ax.bar(x, s.flip_rate * 100, w, label=f"{VN[v]}: cross-language flip", alpha=0.85)
    ax.scatter(x, s.self_flip_rate * 100, color="k", marker="_", s=200, zorder=3, label="same-prompt re-run flip" if k == 0 else None)
ax.set_xticks(np.arange(len(J))); ax.set_xticklabels(J, rotation=20); ax.set_ylabel("%")
ax.set_title("Fig. 4  Cross-language flips vs re-run noise floor (repeat-100 subset)"); ax.legend(fontsize=7); save(f, "fig4_noise_floor.png")

PC = T.pivot(index="judge", columns="variant", values="pos_consistency").loc[J, V].rename(columns=VN)
FP = T.pivot(index="judge", columns="variant", values="first_pos_rate").loc[J, V].rename(columns=VN)
f, axs = plt.subplots(1, 2, figsize=(11, 4))
sns.heatmap(PC * 100, annot=True, fmt=".1f", cmap="Blues", ax=axs[0]); axs[0].set_title("Position consistency % (same pick in both orders)")
sns.heatmap(FP * 100, annot=True, fmt=".1f", cmap="coolwarm", center=50, ax=axs[1]); axs[1].set_title("First-position pick rate % (50 = no bias)")
for a in axs: a.set_xlabel(""); a.set_ylabel("")
f.suptitle("Fig. 5  Position bias by judge and language"); save(f, "fig5_position_bias.png")

f, axs = plt.subplots(len(J), 4, figsize=(10, 2.3 * len(J)))
for r_, j in enumerate(J):
    for c_, v in enumerate(V):
        m = np.array(cm[(j, v)]); ax = axs[r_, c_]
        sns.heatmap(m, annot=True, fmt="d", cbar=False, cmap="Purples", ax=ax, xticklabels=["pick 1", "pick 2"], yticklabels=["gold 1", "gold 2"])
        if r_ == 0: ax.set_title(VN[v], fontsize=9)
        if c_ == 0: ax.set_ylabel(j, fontsize=8)
f.suptitle("Fig. 6  Confusion matrices: gold better output vs judge pick (valid judgments)"); save(f, "fig6_confusion_gold.png")

f, axs = plt.subplots(len(J), 3, figsize=(8, 2.3 * len(J)))
C = wide(main, "correct").astype(float)
for r_, j in enumerate(J):
    cj = C.loc[j]
    for c_, v in enumerate(V[1:]):
        m = pd.crosstab(cj["en"], cj[v]).reindex(index=[1.0, 0.0], columns=[1.0, 0.0], fill_value=0).values
        ax = axs[r_, c_]; sns.heatmap(m, annot=True, fmt="d", cbar=False, cmap="Oranges", ax=ax,
                                       xticklabels=[f"{v} ✓", f"{v} ✗"], yticklabels=["EN ✓", "EN ✗"])
        if r_ == 0: ax.set_title(VN[v], fontsize=9)
        if c_ == 0: ax.set_ylabel(j, fontsize=8)
f.suptitle("Fig. 7  Paired English-vs-variant correctness (McNemar tables)"); save(f, "fig7_mcnemar_tables.png")

f, ax = plt.subplots(figsize=(7.5, 3.8)); sns.heatmap(subacc.rename(columns=VN) * 100, annot=True, fmt=".1f", cmap="RdYlGn", ax=ax)
ax.set_title("Fig. 8  Accuracy by LLMBar subset (pooled over 6 judges)"); ax.set_xlabel(""); ax.set_ylabel(""); save(f, "fig8_subset_accuracy.png")

go = gee_or[gee_or.index.str.startswith("C(variant)")]
f, ax = plt.subplots(figsize=(6, 2.8)); y = np.arange(len(go))
ax.errorbar(go.OR, y, xerr=[go.OR - go.lo, go.hi - go.OR], fmt="o", capsize=4); ax.axvline(1, color="k", lw=0.8)
ax.set_yticks(y); ax.set_yticklabels([VN[n.split("T.")[1].rstrip("]")] for n in go.index]); ax.set_xlabel("odds ratio of a correct verdict vs English")
ax.set_title("Fig. 9  GEE logistic model (item-clustered), adjusted for judge & order"); save(f, "fig9_gee_or.png")

json.dump({"n_items": len(core), "n_main": len(main), "n_repeat_rows": int((df.run > 0).sum()),
           "code_heavy": sorted(code_heavy), "human_fixed_items": len(fixed_items),
           "confusion_gold": {f"{j}|{v}": m for (j, v), m in cm.items()},
           "gee_variant_OR": go.to_dict(orient="index"),
           "interaction_wald": {"stat": float(np.squeeze(wald.statistic)), "df": int(wald.df_denom) if hasattr(wald, "df_denom") and wald.df_denom else len(names), "p": float(wald.pvalue)},
           "pooled": main.groupby("variant").correct.mean().to_dict()},
          open(OUT / "stats.json", "w"), indent=1, default=float)
print(T.round(3).to_string()); print(N.round(3).to_string()); print(go.round(3)); print("interaction p", float(wald.pvalue))
