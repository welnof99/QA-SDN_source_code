"""Figures 9, 11, 12 and 13 of the manuscript, generated from data/ via analysis.py.
Figure numbers appear only in the manuscript captions, not inside the images."""
import os
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import analysis as A

OI = {"blue": "#0072B2", "orange": "#E69F00", "green": "#009E73", "sky": "#56B4E9", "verm": "#D55E00",
      "purple": "#CC79A7", "grey": "#7F7F7F"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
                     "legend.frameon": False, "axes.linewidth": 0.7, "savefig.dpi": 300})

def save(fig, name):
    os.makedirs(A.FIG, exist_ok=True)
    fig.savefig(os.path.join(A.FIG, name + ".png"), bbox_inches="tight")
    fig.savefig(os.path.join(A.FIG, name + ".pdf"), bbox_inches="tight")
    plt.close(fig)

def fig09(m):
    """Fairness (JFI) and p95 latency per seed, by method and scenario (Section 4.4)."""
    METHODS = [("ECMP+adm", "ECMP+adm", OI["grey"]), ("Greedy-only", "Greedy", "#BBBBBB"),
               (A.SAT, "SA (tuned)", OI["blue"]), (A.SQA, "SQA (mono)", OI["verm"]), (A.MAS, "MAS-QA (proposed)", OI["green"])]
    fig, axes = plt.subplots(1, 2, figsize=(7.3, 3.4), sharey=True)
    for ax, col, title, xlab in [(axes[0], "JFI", "(a) Jain's fairness index", "JFI (per seed, mean ± 95% CI)"),
                                 (axes[1], "latency_p95_ms", "(b) 95th-percentile latency", "p95 latency, ms (mean ± 95% CI)")]:
        y, yt, yl = 0, [], []
        for s in A.SCEN:
            for k, lab, c in METHODS:
                mu, lo, hi = A.mean_ci(A.ser(m, "scenario", s, k, col))
                ax.plot([lo, hi], [y, y], color=c, lw=1.4); ax.plot(mu, y, "o", color=c, ms=3.5)
                yt.append(y); yl.append(f"{s}  {lab}"); y += 1
            y += 0.8
        ax.set_yticks(yt); ax.set_yticklabels(yl, fontsize=5.6); ax.invert_yaxis()
        ax.set_xlabel(xlab); ax.set_title(title, loc="left", fontsize=7.5)
    fig.tight_layout(); save(fig, "fig09_fairness_latency")

def fig11(small):
    """Small instances: per-seed gap to the exact count optimum (Section 4.6)."""
    g = A.small_gaps(small)
    MK = [("ECMP+adm", "ECMP+adm"), ("Greedy-only", "Greedy"), (A.SAT, "SA (tuned)"), (A.SQA, "SQA (mono)"), ("MAS-QA", "MAS-QA")]
    fig, axes = plt.subplots(1, 2, figsize=(7.3, 2.9), sharey=True)
    for ax, N in zip(axes, [8, 12]):
        for j, (k, lab) in enumerate(MK):
            for r_, off, c in [(0.8, -0.2, OI["sky"]), (1.6, 0.2, OI["verm"])]:
                row = g[(g.N == N) & (g.ratio == r_) & (g.method == k)].iloc[0]
                h = row.ci_hi - row.gap_mean
                ax.bar(j + off, row.gap_mean, 0.38, color=c, yerr=h, capsize=1.5, error_kw={"lw": 0.6},
                       label=f"load r = {r_}" if (j == 0 and N == 8) else None)
                ax.text(j + off, row.gap_mean + h + 0.15, f"{row.gap_mean:.2f}", ha="center", fontsize=5.8)
        ax.set_xticks(range(len(MK))); ax.set_xticklabels([l for _, l in MK], fontsize=6.5)
        ax.set_title(f"N = {N} flows (reference: count optimum)", loc="left", fontsize=7.5); ax.grid(axis="y", lw=0.3, alpha=0.5)
    axes[0].set_ylabel("PL_flow above exact optimum (pp)"); axes[0].legend(fontsize=6.8, loc="upper right")
    fig.tight_layout(); save(fig, "fig11_small_instances")

def fig12(m):
    """Effect of the SA schedule on the SQA headline (Section 4.8)."""
    rows = []
    for s in A.SCEN:
        sa_def = A.ser(m, "scenario", s, A.SAD); sa_tun = A.ser(m, "scenario", s, A.SAT); sqa = A.ser(m, "scenario", s, A.SQA)
        for lab, d, c in [("SA default − SA tuned", sa_def - sa_tun, OI["sky"]), ("SQA − SA default", sqa - sa_def, OI["purple"]),
                          ("SQA − SA tuned", sqa - sa_tun, OI["verm"])]:
            mu, lo, hi = A.mean_ci(d)
            from scipy import stats
            rows.append((f"{s}: {lab}", mu, lo, hi, stats.ttest_1samp(d, 0).pvalue, c))
    fig, ax = plt.subplots(figsize=(4.6, 3.8))
    ypos = [-i - (i // 3) * 0.6 for i in range(len(rows))]
    for yy, (lab, mu, lo, hi, p, c) in zip(ypos, rows):
        ax.plot([lo, hi], [yy, yy], color=c, lw=1.5); ax.plot(mu, yy, "o", color=c, ms=3.8)
        ax.text(hi + 0.12, yy, f"p = {p:.3f}" if p >= 0.001 else "p < 0.001", va="center", fontsize=5.8)
    ax.axvline(0, color="black", lw=0.7, ls="--")
    ax.set_yticks(ypos); ax.set_yticklabels([r[0] for r in rows], fontsize=6.2)
    ax.set_xlabel("Difference in PL_flow, pp (mean ± 95% CI; positive: first method loses more flows)")
    ax.set_title("Paired by seed, n = 30 per scenario (unadjusted p)", loc="left", fontsize=7.5)
    fig.tight_layout(); save(fig, "fig12_sa_schedule")

def fig13(m, scale, earlier):
    """Summary of the paired contrasts discussed in Section 4.10."""
    out = A.contrasts_fig13(m, scale, earlier)
    fig, ax = plt.subplots(figsize=(6.6, 5.2))
    ypos, ylab, groups = [], [], []
    y = 0
    for g in out.group.unique():
        groups.append((g, y))
        for _, r in out[out.group == g].iterrows():
            c = OI["verm"] if r.hi < 0 else (OI["sky"] if r.lo > 0 else OI["grey"])
            ax.plot([r.lo, r.hi], [y, y], color=c, lw=1.5); ax.plot(r.dbar, y, "o", color=c, ms=3.6)
            ax.text(max(r.hi, 0) + 0.25, y, ("p < 0.001" if r.p < 0.001 else f"p = {r.p:.3f}"), va="center", fontsize=5.6)
            ypos.append(y); ylab.append(r.label); y += 1
        y += 0.9
    ax.axvline(0, color="black", lw=0.7, ls="--")
    ax.set_yticks(ypos); ax.set_yticklabels(ylab, fontsize=6.2); ax.invert_yaxis()
    for g, yy in groups:
        ax.text(-0.02, yy - 0.75, g, transform=ax.get_yaxis_transform(), ha="right", va="bottom", fontsize=6.6, fontweight="bold")
    ax.set_xlabel("Paired difference in PL_flow, pp (mean with 95% CI; negative favours the first method)")
    ax.set_xlim(-6.5, 4.2)
    fig.tight_layout(); save(fig, "fig13_summary_contrasts")
    return out

if __name__ == "__main__":
    m = A.load_main(); scale = A.load_scale(); small = A.load_small(); earlier = A.load_earlier()
    fig09(m); fig11(small); fig12(m); out = fig13(m, scale, earlier)
    print("extra figures written to", A.FIG)
