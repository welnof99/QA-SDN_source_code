"""Figures 1-8, 10 and 6 of the manuscript, generated from data/. Run: python code/figures_main.py"""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from scipy import stats
import os, sys
ROOT = os.environ.get("MASQA_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(ROOT, "data") + os.sep
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8,
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
                     "savefig.dpi": 300, "axes.linewidth": 0.7})
# Okabe-Ito palette (colour-blind safe)
OI = {"blue": "#0072B2", "orange": "#E69F00", "green": "#009E73", "sky": "#56B4E9", "verm": "#D55E00",
      "purple": "#CC79A7", "yellow": "#F0E442", "grey": "#7F7F7F", "black": "#000000"}
COL = {"ECMP+adm": OI["grey"], "Greedy-only": "#BBBBBB", "SA-mono-m+repair": OI["sky"], "SA-mono-mt+repair": OI["blue"],
       "MAS+SA-m": OI["green"], "SQA-mono-v2+repair": OI["verm"], "MAS-QA-v2": OI["orange"], "ECMP-hash": "#444444"}
LAB = {"ECMP+adm": "ECMP+adm", "Greedy-only": "Greedy", "SA-mono-m+repair": "SA (default)", "SA-mono-mt+repair": "SA (tuned)",
       "MAS+SA-m": "MAS+SA", "SQA-mono-v2+repair": "SQA (mono)", "MAS-QA-v2": "MAS-QA (proposed)", "ECMP-hash": "ECMP-hash"}
import matplotlib.axes as _axm, matplotlib.figure as _figm
_orig_set_title = _axm.Axes.set_title
def _no_fig_title(self, label, *a, **k):
    if str(label).startswith("Figure"):
        return None
    return _orig_set_title(self, label, *a, **k)
_axm.Axes.set_title = _no_fig_title
_figm.Figure.suptitle = lambda self, *a, **k: None
SAVE = os.path.join(ROOT, "figures") + os.sep
os.makedirs(SAVE, exist_ok=True)
# manuscript figure numbers (file names follow the numbering used in the article)
NAME = {"Fig01_pipeline": "fig01_pipeline", "Fig02_topology": "fig02_topology", "Fig03_validation_tuning": "fig03_validation_tuning",
        "Fig04_main_distributions": "fig04_main_distributions", "Fig05_paired_differences": "fig05_paired_differences",
        "Fig06_repair_ablation": "fig07_repair_ablation", "Fig07_scale": "fig10_scale", "Fig08_class_loss": "fig08_class_loss",
        "Fig10_iteration_change": "fig06_iteration_change"}
def save(fig, name):
    name = NAME.get(name, name)
    fig.savefig(SAVE + name + ".png", bbox_inches="tight"); fig.savefig(SAVE + name + ".pdf", bbox_inches="tight"); plt.close(fig)

m = pd.read_csv(R + "matched_all.csv")
sa = pd.read_csv(R + "eval_sa_mono_tuned.csv"); sa["method"] = "SA-mono-mt+repair"
D = pd.concat([m, sa]); D = D[D.scenario.isin(["S1", "S2", "S3"])]
S = pd.read_csv(R + "scale_full.csv")
MAIN = pd.concat([pd.read_csv(R + "main_S1_S2.csv"), pd.read_csv(R + "main_S3.csv")])
def ser(df, keycol, val, meth, col="PL_flow"):
    return df[(df[keycol] == val) & (df.method == meth)].sort_values("seed")[col].values
def ci95(x):
    x = np.asarray(x, float); return 1.96 * x.std(ddof=1) / np.sqrt(len(x))
def paired(x, y):
    dd = x - y; n = len(dd); se = dd.std(ddof=1) / np.sqrt(n); t = stats.t.ppf(.975, n - 1)
    return dd.mean(), dd.mean() - t * se, dd.mean() + t * se, stats.ttest_rel(x, y).pvalue

# ---------- Fig 1: pipeline schematic ----------
def box(ax, xy, w, h, text, fc, ec="#333333", fs=6.6):
    ax.add_patch(FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.02,rounding_size=0.05", fc=fc, ec=ec, lw=0.7))
    ax.text(xy[0] + w / 2, xy[1] + h / 2, text, ha="center", va="center", fontsize=fs, linespacing=1.25)
def arrow(ax, a_, b_, ls="-", col="#333333", rad=0.0):
    ax.add_patch(FancyArrowPatch(a_, b_, arrowstyle="-|>", mutation_scale=7, lw=0.8, color=col, linestyle=ls, connectionstyle=f"arc3,rad={rad}"))
fig, ax = plt.subplots(figsize=(7.3, 3.4)); ax.set_xlim(-0.1, 10.4); ax.set_ylim(-0.2, 4.2); ax.axis("off")
W, H_, Y = 1.86, 1.35, 1.7
xs = [0.0, 2.1, 4.2, 6.3, 8.4]
box(ax, (xs[0], Y), W, H_, "Traffic\n50 / 100 / 150 flows\n12.8 Mbps per flow", "#F2F2F2")
box(ax, (xs[1], Y), W, H_, "Fat-Tree, k = 4\n16 hosts\n96 directed arcs\n(50 Mbps each)", "#F2F2F2")
box(ax, (xs[2], Y), W, H_, "Decompose by\nsource pod\n4 subproblems, b = 0", "#DCEBF7")
box(ax, (xs[3], Y), W, H_, "Solver per\nsubproblem:\nSQA (P = 16) or SA", "#FBE3D6")
box(ax, (xs[4], Y), W, H_, "Coordinator:\npriority repair,\nthen greedy fill", "#E2F0D9")
for i in range(4):
    arrow(ax, (xs[i] + W, Y + H_ / 2), (xs[i + 1], Y + H_ / 2))
# iterative loop: solver back to decomposition (drawn above the boxes)
ax.add_patch(FancyArrowPatch((xs[3] + W / 2, Y + H_ + 0.02), (xs[2] + W / 2, Y + H_ + 0.02), arrowstyle="-|>", mutation_scale=7, lw=0.8, color=OI["purple"], linestyle="--", connectionstyle="arc3,rad=-0.6"))
ax.text((xs[2] + xs[3] + W) / 2, Y + H_ + 0.55, "iterative variant: re-solve with other pods' loads (3 rounds)", fontsize=5.8, color=OI["purple"], ha="center")
box(ax, (xs[4], 0.0), W, 0.95, "Scoring, identical for all methods:\nPL_flow, BWL, class loss,\nJFI / CoV, latency", "#FFF2CC", fs=6.0)
arrow(ax, (xs[4] + W / 2, Y), (xs[4] + W / 2, 0.95))
box(ax, (0.0, 0.0), 7.9, 0.95, "Tuning (validation seeds 100–104 for SQA β, Γ and SA schedule; check on fresh seeds 105–114)\nEvaluation: seeds 42–71 (main scenarios), seeds 42–66 (scale study); exact MILP reference on N = 8, 12", "#F7F7F7", fs=6.0)
ax.set_title("Figure 1. Study pipeline and experimental protocol", loc="left", fontsize=8.5, pad=2)
save(fig, "Fig01_pipeline")

# ---------- Fig 2: Fat-Tree topology ----------
fig, ax = plt.subplots(figsize=(7.0, 3.8)); ax.set_xlim(-0.8, 8.6); ax.set_ylim(-1.35, 3.9); ax.axis("off")
podcol = [OI["sky"], OI["orange"], OI["green"], OI["purple"]]
core_x = [1.5, 3.2, 4.8, 6.5]; core_y = 3.4
for i, x in enumerate(core_x):
    ax.add_patch(plt.Rectangle((x - 0.18, core_y - 0.18), 0.36, 0.36, fc="#444444", ec="none"))
    ax.text(x, core_y + 0.32, f"C{i+1}", ha="center", fontsize=6.5)
for p in range(4):
    x0 = p * 2.0 + 0.2
    agg_x = [x0 + 0.35, x0 + 1.15]; edge_x = [x0 + 0.35, x0 + 1.15]
    for j, ax_x in enumerate(agg_x):
        ax.add_patch(plt.Rectangle((ax_x - 0.2, 2.2 - 0.16), 0.4, 0.32, fc=podcol[p], ec="#333333", lw=0.5))
        for k in range(2):  # agg j connects to core group j
            c = core_x[2 * j + k]
            ax.plot([ax_x, c], [2.2 + 0.16, core_y - 0.18], color="#999999", lw=0.6)
    for j, ex in enumerate(edge_x):
        ax.add_patch(plt.Rectangle((ex - 0.2, 0.9 - 0.16), 0.4, 0.32, fc=podcol[p], ec="#333333", lw=0.5, alpha=0.6))
        for a in agg_x: ax.plot([ex, a], [0.9 + 0.16, 2.2 - 0.16], color="#999999", lw=0.6)
        for h in range(2):
            hx = ex - 0.15 + h * 0.3
            ax.add_patch(plt.Circle((hx, -0.25), 0.07, fc="white", ec="#333333", lw=0.6))
            ax.plot([hx, ex], [-0.25 + 0.07, 0.9 - 0.16], color="#999999", lw=0.5)
    ax.text(x0 + 0.75, 3.0 - 0.9 + 0.0, f"Pod {p+1}", ha="center", fontsize=7, color="#222222",
            bbox=dict(fc="white", ec="none", pad=0.5)) if False else None
    ax.text(x0 + 0.75, -0.7, f"Pod {p+1}", ha="center", fontsize=7, color="#222222")
    ax.text(x0 - 0.05, 1.55, "", fontsize=6)
ax.text(-0.5, 3.4, "Core", fontsize=7, va="center"); ax.text(-0.5, 2.2, "Aggregation", fontsize=7, va="center")
ax.text(-0.5, 0.9, "Edge", fontsize=7, va="center"); ax.text(-0.5, -0.25, "Hosts", fontsize=7, va="center")
ax.text(-0.7, -1.2, "Link delays: host–edge U[1, 3] ms; edge–agg U[0.5, 1.5] ms; agg–core U[0.1, 0.5] ms", fontsize=6.2, va="center", ha="left")
ax.set_title("Figure 2. Fat-Tree (k = 4): 4 core, 8 aggregation, 8 edge switches, 16 hosts, 48 physical links", loc="left", fontsize=8, pad=2)
save(fig, "Fig02_topology")

# ---------- Fig 3: validation tuning ----------
a = pd.read_csv(R + "diagB_validation.csv"); b = pd.read_csv(R + "diagB_validation_low.csv")
g = pd.concat([a, b]).groupby(["beta", "gamma"]).PL_flow.mean().reset_index()
betas = sorted(g.beta.unique()); gammas = sorted(g.gamma.unique())
M = np.full((len(gammas), len(betas)), np.nan)
for _, r in g.iterrows(): M[gammas.index(r.gamma), betas.index(r.beta)] = r.PL_flow
fig = plt.figure(figsize=(7.3, 3.2))
ax1 = fig.add_subplot(1, 3, 1)
im = ax1.imshow(M, cmap="viridis_r", aspect="auto", origin="lower")
for i in range(len(gammas)):
    for j in range(len(betas)):
        if not np.isnan(M[i, j]): ax1.text(j, i, f"{M[i,j]:.1f}", ha="center", va="center", fontsize=6, color="white" if M[i, j] > 42 else "black")
ax1.set_xticks(range(len(betas))); ax1.set_xticklabels([str(x) for x in betas], fontsize=6.5)
ax1.set_yticks(range(len(gammas))); ax1.set_yticklabels([str(x) for x in gammas], fontsize=6.5)
ax1.set_xlabel("β (inverse temperature)"); ax1.set_ylabel("Γ (transverse field)")
bi, gi = betas.index(0.5), gammas.index(1.0)
ax1.add_patch(plt.Rectangle((bi - 0.5, gi - 0.5), 1, 1, fill=False, ec=OI["verm"], lw=1.6))
ax1.set_title("(a) SQA grid, seeds 100–104\n(selected: β = 0.5, Γ = 1.0)", loc="left", fontsize=7.5)
cb = fig.colorbar(im, ax=ax1, fraction=0.05, pad=0.03); cb.set_label("PL_flow (%)", fontsize=6.5); cb.ax.tick_params(labelsize=6)
ax2 = fig.add_subplot(1, 3, 2)
t = pd.read_csv(R + "tune_sa_mono_matched.csv"); t["cand"] = t.apply(lambda r: "default" if pd.isna(r.beta_min) else f"[{r.beta_min:g}, {r.beta_max:g}]", axis=1)
order = ["default", "[0.1, 3]", "[0.1, 10]", "[1, 10]"]
for i, c in enumerate(order):
    v = t[t.cand == c].PL_flow.values
    ax2.bar(i, v.mean(), 0.6, color=OI["blue"] if c == "[0.1, 10]" else "#BDBDBD", yerr=ci95(v), capsize=2, error_kw={"lw": 0.7})
    ax2.scatter(np.full(len(v), i) + np.random.default_rng(0).uniform(-0.12, 0.12, len(v)), v, s=6, color="black", zorder=3)
ax2.set_xticks(range(4)); ax2.set_xticklabels(order, fontsize=6.5, rotation=0)
ax2.set_xlabel("SA schedule β ∈ [β_min, β_max]"); ax2.set_ylabel("PL_flow (%)"); ax2.set_ylim(38, 46)
ax2.set_title("(b) SA candidates, seeds 100–104\n(selected: [0.1, 10])", loc="left", fontsize=7.5)
ax3 = fig.add_subplot(1, 3, 3)
v2 = pd.read_csv(R + "val2_sqa_mono.csv")
cfg = [(5.0, 3.0, "default (5, 3)"), (0.25, 1.0, "(0.25, 1)"), (0.5, 0.5, "(0.5, 0.5)"), (0.5, 1.0, "(0.5, 1) selected"), (0.5, 2.0, "(0.5, 2)"), (1.0, 1.0, "(1, 1)")]
for i, (be, ga, lab) in enumerate(cfg):
    v = v2[(v2.beta == be) & (v2.gamma == ga)].PL_flow.values
    ax3.bar(i, v.mean(), 0.6, color=OI["verm"] if (be, ga) == (0.5, 1.0) else "#BDBDBD", yerr=ci95(v), capsize=2, error_kw={"lw": 0.7})
ax3.set_xticks(range(len(cfg))); ax3.set_xticklabels([c[2].replace("\n", " ") for c in cfg], fontsize=5.8, rotation=35, ha="right")
ax3.set_ylabel("PL_flow (%)"); ax3.set_ylim(34, 47)
ax3.set_title("(c) SQA settings on fresh seeds 105–114\n(10 seeds, mean ± 95% CI)", loc="left", fontsize=7.5)
fig.suptitle("Figure 3. Solver tuning on validation seeds only; evaluation seeds 42–71 were not used for selection", x=0.01, ha="left", fontsize=8.5, y=1.02)
fig.tight_layout(w_pad=1.4); save(fig, "Fig03_validation_tuning")

# ---------- Fig 4: per-seed distributions in the main scenarios ----------
meths = ["ECMP+adm", "Greedy-only", "SA-mono-m+repair", "SA-mono-mt+repair", "MAS+SA-m", "SQA-mono-v2+repair", "MAS-QA-v2"]
fig, axes = plt.subplots(1, 3, figsize=(7.3, 3.2), sharey=False)
for ax, s, lab in zip(axes, ["S1", "S2", "S3"], ["S1: 50 flows", "S2: 100 flows", "S3: 150 flows"]):
    data = [ser(D, "scenario", s, k) for k in meths]
    bp = ax.boxplot(data, widths=0.55, patch_artist=True, showfliers=False, medianprops=dict(color="black", lw=0.8), whiskerprops=dict(lw=0.6), capprops=dict(lw=0.6), boxprops=dict(lw=0.6))
    for patch, k in zip(bp["boxes"], meths): patch.set_facecolor(COL[k]); patch.set_alpha(0.55)
    for i, v in enumerate(data):
        ax.scatter(np.full(len(v), i + 1) + np.random.default_rng(i).uniform(-0.15, 0.15, len(v)), v, s=4, color="black", zorder=3, alpha=0.6)
    ax.set_xticks(range(1, len(meths) + 1)); ax.set_xticklabels(["ECMP", "Greedy", "SA\ndef.", "SA\ntuned", "MAS\n+SA", "SQA\nmono", "MAS-QA"], fontsize=6, rotation=0)
    ax.set_title(lab, loc="left"); ax.grid(axis="y", lw=0.3, alpha=0.5)
axes[0].set_ylabel("PL_flow (%) per seed (n = 30)")
fig.suptitle("Figure 4. Per-seed flow loss by method (box: IQR and median; dots: individual seeds)", x=0.01, ha="left", fontsize=8.5, y=1.0)
fig.tight_layout(); save(fig, "Fig04_main_distributions")

# ---------- Fig 5: paired differences ----------
rows_a = []
for s in ["S1", "S2", "S3"]:
    rows_a.append((f"Main {s} (n=30)", *paired(ser(D, "scenario", s, "SQA-mono-v2+repair"), ser(D, "scenario", s, "SA-mono-mt+repair"))))
for N in [50, 100, 200, 300]:
    rows_a.append((f"Scale N={N} (n={25 if N<300 else 24})", *paired(ser(S, "N", N, "SQA-mono-v2+repair"), ser(S, "N", N, "SA-mono-mt+repair"))))
rows_b = []
for s in ["S1", "S2", "S3"]:
    for a_, b_, lab in [("MAS-QA-v2", "ECMP+adm", "MAS-QA − ECMP+adm"), ("MAS-QA-v2", "Greedy-only", "MAS-QA − Greedy"),
                        ("MAS-QA-v2", "SQA-mono-v2+repair", "MAS-QA − SQA mono"), ("MAS-QA-v2", "SA-mono-mt+repair", "MAS-QA − SA tuned")]:
        rows_b.append((f"{s}: {lab}", *paired(ser(D, "scenario", s, a_), ser(D, "scenario", s, b_))))
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.3, 3.9), gridspec_kw={"width_ratios": [1, 1.25]})
for y, (lab, mu, lo, hi, p) in enumerate(rows_a):
    c = OI["verm"] if hi < 0 else OI["grey"]
    ax1.plot([lo, hi], [y, y], color=c, lw=1.6); ax1.plot(mu, y, "o", color=c, ms=4)
ax1.axvline(0, color="black", lw=0.7, ls="--")
ax1.set_yticks(range(len(rows_a))); ax1.set_yticklabels([r[0] for r in rows_a], fontsize=6.8); ax1.invert_yaxis()
ax1.set_xlabel("SQA − SA (tuned), pp"); ax1.set_title("(a) Headline comparison (7 settings)", loc="left", fontsize=7.5)
ax1.text(0.02, -0.14, "Orange: 95% CI below zero. Bonferroni m = 7:\nsignificant for S2, S3 and N = 100, 200, 300", transform=ax1.transAxes, fontsize=6, va="top")
for y, (lab, mu, lo, hi, p) in enumerate(rows_b):
    c = OI["green"] if hi < 0 else (OI["verm"] if lo > 0 else OI["grey"])
    ax2.plot([lo, hi], [y, y], color=c, lw=1.6); ax2.plot(mu, y, "o", color=c, ms=3.5)
ax2.axvline(0, color="black", lw=0.7, ls="--")
ax2.set_yticks(range(len(rows_b))); ax2.set_yticklabels([r[0] for r in rows_b], fontsize=6.3); ax2.invert_yaxis()
ax2.set_xlabel("Difference in PL_flow, pp (negative: MAS-QA loses fewer flows)")
ax2.set_title("(b) Pipeline comparisons (n = 30 per scenario)", loc="left", fontsize=7.5)
fig.suptitle("Figure 5. Paired differences with 95% confidence intervals (paired by seed)", x=0.01, ha="left", fontsize=8.5, y=1.0)
fig.tight_layout(); save(fig, "Fig05_paired_differences")

# ---------- Fig 6: repair ablation (initial settings) ----------
abl = [("ECMP-hash", "ECMP-hash\n(no check)"), ("MAS-decomp-only", "Decomposition\nno repair"), ("SQA-mono raw", "SQA mono\nno repair"),
       ("SA-mono raw", "SA mono\nno repair"), ("SQA-mono+repair", "SQA mono\n+ repair"), ("MAS-QA", "MAS-QA\n+ repair"), ("Greedy-only", "Greedy\n(repair only)"), ("ECMP+adm", "ECMP+adm\n(admission)")]
fig, ax = plt.subplots(figsize=(7.3, 3.2))
w = 0.26
for i, (s, c) in enumerate(zip(["S1", "S2", "S3"], [OI["sky"], OI["blue"], OI["black"]])):
    for j, (k, _) in enumerate(abl):
        v = ser(MAIN, "scenario", s, k)
        ax.bar(j + (i - 1) * w, v.mean(), w, color=c, yerr=ci95(v), capsize=1.5, error_kw={"lw": 0.6}, label=s if j == 0 else None)
ax.set_xticks(range(len(abl))); ax.set_xticklabels([l for _, l in abl], fontsize=6.4)
ax.set_ylabel("PL_flow (%), mean ± 95% CI"); ax.set_ylim(0, 118)
ax.legend(title="Scenario", fontsize=7, title_fontsize=7, loc="upper right", ncol=3)
ax.axvspan(-0.5, 3.5, color="#F5F5F5", zorder=0); ax.text(1.5, 108, "no repair: solver outputs infeasible", ha="center", fontsize=6.5, color="#555555")
ax.text(5.5, 108, "with repair", ha="center", fontsize=6.5, color="#555555")
fig.suptitle("Figure 6. Effect of the repair step (initial SQA setting β = 5, Γ = 3; 30 seeds per scenario)", x=0.01, ha="left", fontsize=8.5, y=1.0)
fig.tight_layout(); save(fig, "Fig06_repair_ablation")

# ---------- Fig 7: scale study ----------
Ns = [50, 100, 200, 300]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.3, 3.0))
for k in ["ECMP+adm", "Greedy-only", "SA-mono-mt+repair", "SQA-mono-v2+repair", "MAS-QA-v2"]:
    mu = [ser(S, "N", N, k).mean() for N in Ns]; e = [ci95(ser(S, "N", N, k)) for N in Ns]
    ax1.errorbar(Ns, mu, yerr=e, marker="o", ms=3.5, capsize=2, lw=1.0, elinewidth=0.6, color=COL[k], label=LAB[k])
ax1.set_xlabel("Number of flows N (12.8 Mbps per flow)"); ax1.set_ylabel("PL_flow (%)"); ax1.set_xticks(Ns)
ax1.legend(fontsize=6.2, loc="upper left"); ax1.set_title("(a) Flow loss, mean ± 95% CI", loc="left", fontsize=7.5)
for k, lab, c in [("SQA-mono-v2+repair", "SQA − SA (tuned)", OI["verm"]), ("MAS-QA-v2", "MAS-QA − ECMP+adm", OI["orange"])]:
    base = "SA-mono-mt+repair" if k.startswith("SQA") else "ECMP+adm"
    res = [paired(ser(S, "N", N, k), ser(S, "N", N, base)) for N in Ns]
    mu = [r[0] for r in res]; lo = [r[1] for r in res]; hi = [r[2] for r in res]
    ax2.errorbar(np.array(Ns) + (-4 if k.startswith("SQA") else 4), mu, yerr=[np.array(mu) - lo, np.array(hi) - mu], fmt="o-", ms=3.5, capsize=2, lw=1.0, elinewidth=0.6, color=c, label=lab)
ax2.axhline(0, color="black", lw=0.7, ls="--"); ax2.set_xticks(Ns); ax2.set_xlabel("Number of flows N")
ax2.set_ylabel("Paired difference (pp)"); ax2.legend(fontsize=6.5, loc="lower left")
ax2.set_title("(b) Paired differences, 95% CI", loc="left", fontsize=7.5)
fig.suptitle("Figure 7. Scale study with constant per-flow demand (24–25 seeds per size, seeds 42–66)", x=0.01, ha="left", fontsize=8.5, y=1.0)
fig.tight_layout(); save(fig, "Fig07_scale")

# ---------- Fig 8: class-specific loss ----------
cls = [("PL_EF", "EF"), ("PL_AF", "AF"), ("PL_BE", "BE")]
meth8 = ["ECMP+adm", "Greedy-only", "SA-mono-mt+repair", "SQA-mono-v2+repair", "MAS-QA-v2"]
fig, axes = plt.subplots(1, 3, figsize=(7.3, 2.9), sharey=True)
for ax, s in zip(axes, ["S1", "S2", "S3"]):
    for i, k in enumerate(meth8):
        mu = [D[(D.scenario == s) & (D.method == k)][c].mean() for c, _ in cls]
        ax.bar(np.arange(3) + (i - 2) * 0.16, mu, 0.16, color=COL[k], label=LAB[k] if s == "S1" else None)
    ax.set_xticks(range(3)); ax.set_xticklabels([n for _, n in cls]); ax.set_title({"S1": "S1 (50 flows)", "S2": "S2 (100 flows)", "S3": "S3 (150 flows)"}[s], loc="left")
    ax.grid(axis="y", lw=0.3, alpha=0.5)
axes[0].set_ylabel("Class flow loss (%)")
fig.legend(loc="upper center", ncol=5, fontsize=6.8, bbox_to_anchor=(0.5, 1.04))
fig.suptitle("Figure 8. Class-specific flow loss (means over 30 seeds)", x=0.01, ha="left", fontsize=8.5, y=1.12)
fig.tight_layout(); save(fig, "Fig08_class_loss")

# ---------- Fig 10: iteration/convergence ----------
y = pd.read_csv(R + "diagA_jacobi.csv")
import json
fig, ax = plt.subplots(figsize=(3.6, 2.9))
for meth, c, lab in [("sqa", OI["verm"], "SQA (default β = 5, Γ = 3)"), ("sa", OI["blue"], "SA (default schedule)")]:
    arr = np.array([json.loads(s) for s in y[y.method == meth].change])
    mu = arr.mean(0) * 100; e = arr.std(0, ddof=1) / np.sqrt(len(arr)) * 100 * 1.96
    rr = np.arange(1, 1 + arr.shape[1])
    ax.errorbar(rr, mu, yerr=e, marker="o", ms=3.5, capsize=2, lw=1.0, color=c, label=lab)
ax.set_xlabel("Re-solve round (after round r)"); ax.set_ylabel("Decision variables changed (%)")
ax.set_xticks(range(1, 6)); ax.legend(fontsize=6.3, loc="upper right"); ax.set_title("(10 seeds; mean ± 95% CI)", loc="left", fontsize=7)
ax.set_ylim(0, 40)
fig.suptitle("Figure 10. Round-to-round change in the iterated pod solves", x=0.01, ha="left", fontsize=8, y=1.02)
fig.tight_layout(); save(fig, "Fig10_iteration_change")
print("main figures written to", SAVE)
