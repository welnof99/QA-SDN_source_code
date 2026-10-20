"""Shared data loading and statistics for the MAS-QA-SDN article.

All numbers in the manuscript tables that are computed from data are produced here.
Paths are relative to the repository root (see ROOT below)."""
import os
import numpy as np
import pandas as pd
from scipy import stats

ROOT = os.environ.get("MASQA_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
FIG = os.path.join(ROOT, "figures")

SQA, SAT, SAD, MAS = "SQA-mono-v2+repair", "SA-mono-mt+repair", "SA-mono-m+repair", "MAS-QA-v2"
SCEN = ["S1", "S2", "S3"]

def read(name):
    return pd.read_csv(os.path.join(DATA, name))

def load_main():
    """Main-scenario runs (S1-S3, seeds 42-71) plus the tuned-SA re-evaluation."""
    return pd.concat([read("matched_all.csv"), read("eval_sa_mono_tuned.csv")], ignore_index=True)

def load_earlier():
    """Earlier protocol (initial SQA setting, beta = 5, Gamma = 3): controls and the equal-work runs."""
    return pd.concat([read("main_S1_S2.csv"), read("main_S3.csv")], ignore_index=True)

def load_scale():
    return read("scale_full.csv")

def load_small():
    return read("small_v2_all.csv")

def ser(df, keycol, val, meth, col="PL_flow"):
    return df[(df[keycol] == val) & (df.method == meth)].sort_values("seed")[col].values

def paired(x, y):
    """Paired difference x - y with 95% t-interval, two-sided paired t-test and exact Wilcoxon p."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    dd = x - y
    n = len(dd)
    mu = dd.mean()
    se = dd.std(ddof=1) / np.sqrt(n)
    t = stats.t.ppf(0.975, n - 1)
    try:
        wp = stats.wilcoxon(x, y).pvalue
    except ValueError:  # all differences zero
        wp = 1.0
    return dict(n=n, dbar=mu, lo=mu - t * se, hi=mu + t * se, p=stats.ttest_rel(x, y).pvalue, p_wilcoxon=wp)

def pv(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"

def mean_ci(x):
    x = np.asarray(x, float)
    h = stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
    return x.mean(), x.mean() - h, x.mean() + h

# ---------- tables ----------
def table2(m):
    """Table 2: PL_flow mean +- SD per method and main scenario."""
    meths = ["ECMP+adm", "Greedy-only", "SA-mono-m+repair", "SA-mono-mt+repair", "MAS+SA-m", SQA, MAS, "ITER-SQA-v2-R3"]
    out = {}
    for meth in meths:
        out[meth] = {s: f"{ser(m, 'scenario', s, meth).mean():.1f} ± {ser(m, 'scenario', s, meth).std(ddof=1):.1f}" for s in SCEN}
    return pd.DataFrame(out).T

PAIRS = [(SQA, SAT), (SQA, SAD), (MAS, SAT), (MAS, "MAS+SA-m"), (MAS, SQA), (MAS, "Greedy-only"), (MAS, "ECMP+adm"), ("ITER-SQA-v2-R3", MAS)]

def table3(m):
    """Table 3: paired PL_flow differences (A - B), 24 comparisons, Bonferroni m = 24."""
    rows = []
    for s in SCEN:
        for a, b in PAIRS:
            r = paired(ser(m, "scenario", s, a), ser(m, "scenario", s, b))
            rows.append(dict(setting=s, A=a, B=b, dbar=r["dbar"], lo=r["lo"], hi=r["hi"], p=r["p"], p_adj=min(1, r["p"] * len(PAIRS) * len(SCEN))))
    return pd.DataFrame(rows)

def headline(m, scale):
    """Table 4 / Figure 5a / Figure 13: tuned SQA minus tuned SA in main and scale settings (m = 7)."""
    rows = []
    for s in SCEN:
        r = paired(ser(m, "scenario", s, SQA), ser(m, "scenario", s, SAT))
        rows.append(dict(setting=s, **r))
    for N in [50, 100, 200, 300]:
        r = paired(ser(scale, "N", N, SQA), ser(scale, "N", N, SAT))
        rows.append(dict(setting=f"N={N}", **r))
    df = pd.DataFrame(rows)
    df["p_adj_m7"] = np.minimum(1, df.p * len(df))
    return df

def equal_work(earlier):
    """Equal-work control (initial settings): monolithic SQA at matched work minus MAS-QA (earlier protocol)."""
    return {s: paired(ser(earlier, "scenario", s, "SQA-mono-matched+repair"), ser(earlier, "scenario", s, "MAS-QA")) for s in SCEN}

def table6(m):
    """Table 6: class losses, JFI, CoV and latency means over 30 seeds."""
    meths = [("ECMP+adm", "ECMP+adm"), ("Greedy-only", "Greedy"), (SAT, "SA (tuned)"), (SQA, "SQA (mono)"), (MAS, "MAS-QA-v2")]
    rows = []
    for s in SCEN:
        for k, lab in meths:
            d = m[(m.scenario == s) & (m.method == k)]
            rows.append(dict(scenario=s, method=lab, PL_EF=d.PL_EF.mean(), PL_AF=d.PL_AF.mean(), PL_BE=d.PL_BE.mean(),
                             JFI=d.JFI.mean(), CoV=d.CoV.mean(), lat_mean=d.latency_ms.mean(), lat_p95=d.latency_p95_ms.mean()))
    return pd.DataFrame(rows)

def table7(scale):
    """Table 7: scale study PL_flow means (constant per-flow demand)."""
    meths = ["ECMP+adm", "Greedy-only", SAT, SQA, MAS]
    out = {}
    for N in [50, 100, 200, 300]:
        out[N] = {k: ser(scale, "N", N, k).mean() for k in meths}
    return pd.DataFrame(out).T

def table8(scale):
    """Table 8: SQA minus tuned SA, and MAS-QA minus ECMP+adm, per scale size."""
    rows = []
    for N in [50, 100, 200, 300]:
        a = paired(ser(scale, "N", N, SQA), ser(scale, "N", N, SAT))
        b = paired(ser(scale, "N", N, MAS), ser(scale, "N", N, "ECMP+adm"))
        rows.append(dict(N=N, sqa_minus_sa=a["dbar"], sqa_ci_lo=a["lo"], sqa_ci_hi=a["hi"], sqa_p=a["p"],
                         mas_minus_ecmp=b["dbar"], mas_ci_lo=b["lo"], mas_ci_hi=b["hi"], mas_p=b["p"]))
    return pd.DataFrame(rows)

def table9(small):
    """Table 9: small instances, PL_flow and BWL means over 20 seeds."""
    return small.groupby(["N", "ratio", "method"]).agg(PL_flow=("PL_flow", "mean"), BWL=("BWL", "mean")).round(2)

def small_gaps(small):
    """Per-seed gap to the count optimum (pp), averaged over seeds, with the number of seeds that miss the optimum."""
    rows = []
    for (N, r), sub in small.groupby(["N", "ratio"]):
        piv = sub.pivot_table(index="seed", columns="method", values="PL_flow")
        for k in piv.columns:
            if k == "OPT-count":
                continue
            g = (piv[k] - piv["OPT-count"]).values
            mu, lo, hi = mean_ci(g)
            rows.append(dict(N=N, ratio=r, method=k, gap_mean=mu, ci_lo=lo, ci_hi=hi, seeds_missed=int((g > 1e-9).sum()), seeds=len(g)))
    return pd.DataFrame(rows)

def contrasts_fig13(m, scale, earlier):
    """Rows of Figure 13 (summary of paired contrasts discussed in Section 4.10)."""
    rows = []
    for s in SCEN:
        r = paired(ser(m, "scenario", s, SQA), ser(m, "scenario", s, SAT)); rows.append(("Headline (tuned)", f"{s}: SQA − SA tuned", r))
    for N in [50, 100, 200, 300]:
        r = paired(ser(scale, "N", N, SQA), ser(scale, "N", N, SAT)); rows.append(("Headline (tuned)", f"N = {N}: SQA − SA tuned", r))
    for s in SCEN:
        r = paired(ser(m, "scenario", s, SAD), ser(m, "scenario", s, SAT)); rows.append(("SA schedule", f"{s}: SA default − SA tuned", r))
    for s, r in equal_work(earlier).items():
        rows.append(("Equal-work control", f"{s}: SQA (equal work) − pipeline", r))
    for s in SCEN:
        r = paired(ser(m, "scenario", s, MAS), ser(m, "scenario", s, SQA)); rows.append(("Pipeline vs monolithic", f"{s}: pipeline − SQA (tuned)", r))
    return pd.DataFrame([dict(group=g, label=l, **r) for g, l, r in rows])

CONTROLS = [("ECMP-hash", "ECMP-hash"), ("ECMP+adm", "ECMP+adm"), ("Greedy-only", "Greedy-only (repair, no solver)"),
            ("MAS-decomp-only", "MAS-decomp-only (no repair)"), ("SQA-mono raw", "SQA-mono raw (no repair)"),
            ("SA-mono raw", "SA-mono raw (no repair)"), ("SQA-mono+repair", "SQA-mono + repair (initial settings)"),
            ("SQA-mono-matched+repair", "SQA-mono, equal work + repair (initial settings)"), ("MAS-QA", "MAS-QA + repair (initial settings)")]

def table5(earlier):
    """Table 5: controls from the earlier protocol (initial SQA setting), PL_flow means over 30 seeds."""
    out = {}
    for key, label in CONTROLS:
        out[label] = {s: ser(earlier, "scenario", s, key).mean() for s in SCEN}
    return pd.DataFrame(out).T.round(1)
