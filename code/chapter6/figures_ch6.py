"""Gambar BAB VI dari CSV di data/chapter6. Keluaran PNG (300 dpi) dan PDF di figures/chapter6/.
Pemakaian: python3 figures_ch6.py"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "..", "data", "chapter6")
FIG = os.path.join(HERE, "..", "..", "figures", "chapter6"); os.makedirs(FIG, exist_ok=True)

# palet kategorikal tervalidasi (slot 1-3) + abu-abu untuk acuan; bentuk penanda sebagai pengode kedua
BLUE, ORANGE, AQUA, GRAY = "#257de0", "#f47230", "#00b894", "#8a8a8a"
INK, INK2, GRID = "#1f1f1f", "#5c5c5c", "#e6e6e6"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
    "axes.edgecolor": "#bdbdbd", "axes.linewidth": 0.8, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.axisbelow": True, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
    "savefig.dpi": 300, "savefig.bbox": "tight"})

A = pd.read_csv(os.path.join(D, "eval_light_A.csv"))
Bk = pd.read_csv(os.path.join(D, "eval_light_B.csv"))
EV = pd.concat([A, Bk], ignore_index=True)
SC = ["S1", "S2", "S3", "k6-S2"]
SCL = {"S1": "k=4 S1\n(50 flow)", "S2": "k=4 S2\n(100 flow)", "S3": "k=4 S3\n(150 flow)", "k6-S2": "k=6\n(338 flow)"}


def pdiff(df, sc, a, b, metric="PL_flow"):
    x = df[(df.scenario == sc) & (df.method == a)].set_index("seed")[metric]
    y = df[(df.scenario == sc) & (df.method == b)].set_index("seed")[metric]
    s = x.index.intersection(y.index)
    d = (x[s] - y[s]).astype(float)
    h = stats.t.ppf(0.975, len(d) - 1) * d.std(ddof=1) / np.sqrt(len(d))
    return d.mean(), h


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"))
    plt.close(fig)


def zero(ax):
    ax.axhline(0, color=INK2, lw=0.9, zorder=1)


# ---------------- Gambar 6.1: reward admisi (RQ6.1)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.0), gridspec_kw=dict(width_ratios=[1.6, 1]))
x = np.arange(len(SC))
for off, meth, col, mk, lab in [(-0.12, "MAS-QA-mu_f", BLUE, "o", "μ_f analitis"),
                                (0.12, "MAS-QA-v2 mu=20", ORANGE, "s", "μ = 20 empiris")]:
    pts = [(i, *pdiff(EV, sc, meth, "MAS-QA-v2")) for i, sc in enumerate(SC)
           if ((EV.scenario == sc) & (EV.method == meth)).any()]
    xi, m, h = zip(*pts)
    a1.errorbar(np.array(xi) + off, m, yerr=h, fmt=mk, ms=6, color=col, ecolor=col, elinewidth=1.4, capsize=3, label=lab, zorder=3)
zero(a1)
a1.set_xticks(x, [SCL[s] for s in SC]); a1.set_ylabel("Selisih PL_flow terhadap MAS-QA-v2 (pp)")
a1.set_title("(a) Kualitas: negatif = lebih sedikit flow hilang", loc="left")
a1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2)
w = EV[EV.method.isin(["MAS-QA-v2", "MAS-QA-mu_f"])].groupby(["scenario", "method"]).work.mean().unstack()
ratio = [100 * w.loc[s, "MAS-QA-mu_f"] / w.loc[s, "MAS-QA-v2"] for s in SC]
bars = a2.bar(x, ratio, width=0.55, color=BLUE, edgecolor="white", linewidth=2)
for xi, r in zip(x, ratio):
    a2.text(xi, r + 2, f"{r:.0f}%", ha="center", va="bottom", fontsize=8.5, color=INK)
a2.axhline(100, color=GRAY, lw=1, ls="--"); a2.text(3.35, 101.5, "MAS-QA-v2 = 100%", ha="right", fontsize=8, color=INK2)
a2.set_ylim(0, 115); a2.set_xticks(x, ["k=4\nS1", "k=4\nS2", "k=4\nS3", "k=6"])
a2.set_ylabel("Kerja annealing μ_f / MAS-QA-v2 (%)"); a2.set_title("(b) Kerja annealing", loc="left")
fig.tight_layout(); save(fig, "gambar6_2_reward_admisi")

# ---------------- Gambar 6.2: proteksi prioritas (RQ6.2)
fig, axs = plt.subplots(1, 4, figsize=(7.4, 2.9), sharey=True)
cls = ["PL_EF", "PL_AF", "PL_BE"]; cl = ["EF", "AF", "BE"]
g = EV.groupby(["scenario", "method"])[cls].mean()
for ax, sc in zip(axs, SC):
    xi = np.arange(3)
    for off, meth, col, lab, hatch in [(-0.19, "MAS-QA-mu_f", BLUE, "MAS-QA-μ_f", None),
                                        (0.19, "MAS-QA-mu_f-Lex", ORANGE, "MAS-QA-μ_f-Lex", "////")]:
        ax.bar(xi + off, g.loc[(sc, meth)].values, width=0.36, color=col, edgecolor="white", linewidth=2,
               hatch=hatch, label=lab)
    ef_m, ef_l = g.loc[(sc, "MAS-QA-mu_f"), "PL_EF"], g.loc[(sc, "MAS-QA-mu_f-Lex"), "PL_EF"]
    ax.text(0.19, ef_l + 2, f"{ef_l:.0f}", ha="center", fontsize=8); ax.text(-0.19, ef_m + 2, f"{ef_m:.0f}", ha="center", fontsize=8)
    ax.set_xticks(xi, cl); ax.set_title(SCL[sc].replace("\n", " "), fontsize=8.5)
axs[0].set_ylabel("Kehilangan flow per kelas (%)"); axs[0].set_ylim(0, 92)
h, l = axs[0].get_legend_handles_labels(); fig.legend(h, l, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.06))
fig.tight_layout(); save(fig, "gambar6_3_proteksi_prioritas")

# ---------------- Gambar 6.4: alokasi anggaran (RQ6.4)
fig, ax = plt.subplots(figsize=(5.2, 3.2))
K = [1, 2, 4, 8]; MK = {1: "MAS-QA-v2", 2: "MAS-QA-v2 2x250", 4: "MAS-QA-v2 4x125", 8: "MAS-QA-v2 8x62"}
for (sc, col, mk, dx) in [("S1", BLUE, "o", -0.06), ("S2", ORANGE, "s", 0.0), ("S3", AQUA, "^", 0.06)]:
    m, h = zip(*[(0.0, 0.0)] + [pdiff(EV, sc, MK[k], "MAS-QA-v2") for k in K[1:]])
    xs = np.log2(K) + dx
    ax.errorbar(xs, m, yerr=h, fmt=f"-{mk}", ms=6, lw=2, color=col, capsize=3, elinewidth=1.2, label=SCL[sc].replace("\n", " "))
m6, h6 = pdiff(EV, "k6-S2", MK[4], "MAS-QA-v2")
ax.errorbar([2 + 0.12], [m6], yerr=[h6], fmt="D", ms=6, color=GRAY, capsize=3, label="k=6 (338 flow), hanya 4 sampel")
zero(ax)
ax.set_xticks(np.log2(K), ["1 × 500", "2 × 250", "4 × 125", "8 × 62"])
ax.set_xlabel("Jumlah sampel × sweeps per sampel (kerja total sama)")
ax.set_ylabel("Selisih PL_flow terhadap 1 × 500 (pp)")
ax.legend(loc="lower left", fontsize=8)
fig.tight_layout(); save(fig, "gambar6_5_alokasi_anggaran")

# ---------------- Gambar 6.5: IP eksak (RQ6.5)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.0))
gm = EV.groupby(["scenario", "method"]).agg(PL=("PL_flow", "mean"), t=("wall_s", "mean"), ts=("solve_s", "mean"))
x = np.arange(len(SC))
for off, meth, col, mk, lab in [(-0.1, "MAS-QA-v2", BLUE, "o", "MAS-QA-v2"), (0.1, "IP-count", ORANGE, "s", "IP eksak (batas 60 detik)")]:
    a1.plot(x + off, [gm.loc[(s, meth), "PL"] for s in SC], mk, ms=7, color=col, label=lab)
for i, s in enumerate(SC):
    a1.annotate("", xy=(i + 0.1, gm.loc[(s, "IP-count"), "PL"]), xytext=(i - 0.1, gm.loc[(s, "MAS-QA-v2"), "PL"]),
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=1))
    d = gm.loc[(s, "IP-count"), "PL"] - gm.loc[(s, "MAS-QA-v2"), "PL"]
    a1.text(i + 0.18, (gm.loc[(s, "IP-count"), "PL"] + gm.loc[(s, "MAS-QA-v2"), "PL"]) / 2, f"{d:+.1f}", fontsize=8, va="center")
a1.set_xticks(x, [SCL[s] for s in SC], fontsize=7.5); a1.set_ylabel("PL_flow (%)"); a1.set_xlim(-0.4, 3.6)
a1.set_title("(a) Flow yang hilang", loc="left"); a1.legend(loc="lower right", fontsize=8)
tv = [gm.loc[(s, "MAS-QA-v2"), "t"] for s in SC]; ti = [gm.loc[(s, "IP-count"), "ts"] for s in SC]
a2.plot(x, tv, "-o", lw=2, ms=6, color=BLUE, label="MAS-QA-v2 (berurutan, 1 core)")
a2.plot(x, ti, "-s", lw=2, ms=6, color=ORANGE, label="IP eksak")
a2.axhline(60, color=GRAY, ls="--", lw=1); a2.text(0.05, 85, "batas waktu IP 60 detik", fontsize=8, color=INK2)
a2.set_yscale("log"); a2.set_ylim(0.03, 200)
a2.set_xticks(x, [SCL[s] for s in SC], fontsize=7.5); a2.set_ylabel("Waktu per instans (detik, skala log)")
a2.set_title("(b) Waktu penyelesaian", loc="left"); a2.legend(loc="lower right", fontsize=8)
fig.tight_layout(); save(fig, "gambar6_6_ip_eksak")

# ---------------- Gambar 6.3: koordinasi harga (RQ6.3, data pilot seed validasi)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.0))
tr = [("k=4", "pilot2_trace.csv", "pi stabil rho0=40 (8x250)", BLUE, "o"),
      ("k=6", "pilot_k6_trace.csv", "pi stabil rho0=40", ORANGE, "s"),
      ("k=8", "pilot_k8_trace.csv", "pi stabil rho0=40", AQUA, "^")]
for lab, f, meth, col, mk in tr:
    t = pd.read_csv(os.path.join(D, f)); t = t[t.method == meth].groupby("round").max_overload_shared.mean()
    a1.plot(t.index, 100 * t.values, f"-{mk}", lw=2, ms=5, color=col, label=lab)
a1.axhline(0, color=INK2, lw=0.9)
a1.set_xlabel("Putaran koordinasi"); a1.set_ylabel("Kelebihan beban maks. arc bersama (%)")
a1.set_title("(a) Harga menurunkan kelebihan beban", loc="left"); a1.legend(fontsize=8)
rows = [("k=4", "pilot2_rows.csv", "pi stabil rho0=40 (8x250)"), ("k=6", "pilot_k6_rows.csv", "pi stabil rho0=40"),
        ("k=8", "pilot_k8_rows.csv", "pi stabil rho0=40")]
for i, (lab, f, meth) in enumerate(rows):
    r = pd.read_csv(os.path.join(D, f)); r = r.assign(scenario="x")
    for off, ref, col, mk, ll in [(-0.1, "MAS-QA-v2", BLUE, "o", "vs MAS-QA-v2"), (0.1, "MAS-QA-v2 terbaik dari 2 restart", ORANGE, "s", "vs terbaik dari 2 restart")]:
        m, h = pdiff(r, "x", meth, ref)
        a2.errorbar(i + off, m, yerr=h, fmt=mk, ms=6, color=col, capsize=3, elinewidth=1.2, label=ll if i == 0 else None)
zero(a2)
a2.set_xticks(range(3), ["k=4 (5 seed)", "k=6 (5 seed)", "k=8 (3 seed)"])
a2.set_ylabel("Selisih PL_flow harga stabil (pp)")
a2.set_title("(b) ... tetapi tidak menambah flow", loc="left"); a2.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2)
fig.tight_layout(); save(fig, "gambar6_4_koordinasi_harga")
print("selesai:", sorted(os.listdir(FIG)))
