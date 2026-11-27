"""Analisis evaluasi ringan BAB VI: rata-rata, uji berpasangan per seed (t-test dan Wilcoxon),
koreksi Bonferroni per famili yang ditetapkan di Subbab 6.5.11.
Keluaran: ../../data/chapter6/analysis_light_means.csv dan analysis_light_paired.csv"""
import os
import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "data")
OUT = os.path.join(DATA, "chapter6")

frames = [pd.read_csv(os.path.join(OUT, f)) for f in ["eval_light_A.csv", "eval_light_B.csv"]
          if os.path.exists(os.path.join(OUT, f))]
d = pd.concat(frames, ignore_index=True)
# SA monolitik tuned dari data artikel (k = 4), dipakai ulang
sa = pd.read_csv(os.path.join(DATA, "eval_sa_mono_tuned.csv"))
sa = sa[sa.seed.between(42, 71)].assign(tier="A", method="SA-mono tuned (artikel)")
d = pd.concat([d, sa[["tier", "scenario", "seed", "method", "PL_flow", "PL_EF", "PL_AF", "PL_BE", "JFI"]]],
              ignore_index=True)

means = d.groupby(["scenario", "method"], sort=False).agg(
    n=("seed", "nunique"), PL_flow=("PL_flow", "mean"), PL_flow_sd=("PL_flow", "std"),
    PL_EF=("PL_EF", "mean"), PL_AF=("PL_AF", "mean"), PL_BE=("PL_BE", "mean"),
    prio_utility=("prio_utility", "mean"), work_M=("work", lambda x: x.mean() / 1e6),
    wall_s=("wall_s", "mean")).reset_index()
means.to_csv(os.path.join(OUT, "analysis_light_means.csv"), index=False)


def paired(sc, a, b, metric="PL_flow"):
    x = d[(d.scenario == sc) & (d.method == a)].set_index("seed")[metric]
    y = d[(d.scenario == sc) & (d.method == b)].set_index("seed")[metric]
    s = x.index.intersection(y.index)
    diff = (x[s] - y[s]).astype(float)
    n = len(diff)
    if n < 2:
        return None
    m, se = diff.mean(), diff.std(ddof=1) / np.sqrt(n)
    ci = stats.t.ppf(0.975, n - 1) * se
    p_t = stats.ttest_rel(x[s], y[s]).pvalue if diff.std() > 0 else (0.0 if m != 0 else 1.0)
    p_w = stats.wilcoxon(diff).pvalue if (diff != 0).any() else 1.0
    return dict(scenario=sc, metric=metric, A=a, B=b, n=n, mean_diff=m, ci_lo=m - ci, ci_hi=m + ci,
                p_t=p_t, p_wilcoxon=p_w, wins_A=int((diff < 0).sum()), ties=int((diff == 0).sum()))


rows = []
scA = ["S1", "S2", "S3"]
fam = {
    "RQ6.1": [(sc, a, "MAS-QA-v2", "PL_flow") for sc in scA for a in ["MAS-QA-mu_f", "MAS-QA-v2 mu=20"]],
    "RQ6.2": [(sc, "MAS-QA-mu_f-Lex", "MAS-QA-mu_f", m) for sc in scA for m in ["PL_EF", "PL_flow"]],
    "RQ6.4": [(sc, a, "MAS-QA-v2", "PL_flow") for sc in scA
              for a in ["MAS-QA-v2 2x250", "MAS-QA-v2 4x125", "MAS-QA-v2 8x62"]],
    "tanpa koreksi": [("k6-S2", a, "MAS-QA-v2", m) for a, m in
                      [("MAS-QA-mu_f", "PL_flow"), ("MAS-QA-mu_f-Lex", "PL_EF"), ("MAS-QA-mu_f-Lex", "PL_flow"),
                       ("MAS-QA-v2 4x125", "PL_flow"), ("IP-count", "PL_flow")]]
                     + [(sc, "MAS-QA-v2", b, "PL_flow") for sc in scA for b in ["IP-count", "SA-mono tuned (artikel)"]],
}
for f, items in fam.items():
    res = [r for r in (paired(*it) for it in items) if r]
    m = len(res)
    for r in res:
        r["family"] = f
        r["p_bonf"] = min(1.0, r["p_t"] * m) if f != "tanpa koreksi" else float("nan")
        rows.append(r)
pt = pd.DataFrame(rows)
pt.to_csv(os.path.join(OUT, "analysis_light_paired.csv"), index=False)

pd.set_option("display.width", 200)
print(means.round(2).to_string(index=False))
print()
print(pt[["family", "scenario", "metric", "A", "B", "n", "mean_diff", "ci_lo", "ci_hi", "p_t", "p_bonf",
          "p_wilcoxon", "wins_A", "ties"]].round(4).to_string(index=False))
