"""Aset naskah BAB I-III (bahasa Indonesia): gambar konsep, alur, pipeline, topologi, penyetelan, dan persamaan bab III.
Pemakaian: python3 code/bab1_3/assets_bab123.py  -> figures/bab1_3/*.png|pdf dan figures/bab1_3/persamaan/*.png"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "figures", "bab1_3")
EQ = os.path.join(OUT, "persamaan")
os.makedirs(EQ, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "cm", "font.size": 9,
                     "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 300})
OI = {"blue": "#0072B2", "orange": "#E69F00", "green": "#009E73", "sky": "#56B4E9", "verm": "#D55E00",
      "purple": "#CC79A7", "grey": "#7F7F7F"}
INK, INK2, EDGE = "#1f1f1f", "#4d4d4d", "#6b6b6b"


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), bbox_inches="tight", facecolor="white")
    plt.close(fig)


def box(ax, x, y, w, h, title, body="", fc="white", ec=EDGE, fs_t=9.5, fs_b=8.2, lw=1.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.12", fc=fc, ec=ec, lw=lw))
    if body:
        ax.text(x + w / 2, y + h - 0.22, title, ha="center", va="top", fontsize=fs_t, fontweight="bold", color=INK)
        ax.text(x + w / 2, y + h - 0.62, body, ha="center", va="top", fontsize=fs_b, color=INK2, linespacing=1.35)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=fs_t, color=INK, linespacing=1.3)


def arrow(ax, a, b, col=EDGE, ls="-", rad=0.0, lw=1.1):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=10, lw=lw, color=col, linestyle=ls,
                                 connectionstyle=f"arc3,rad={rad}"))


# ---------------------------------------------------------------- Gambar 1.1 peta jalan penelitian
fig, ax = plt.subplots(figsize=(10, 4.9)); ax.set_xlim(0, 15); ax.set_ylim(0, 7.35); ax.axis("off")
cols = [(0.1, "Tahap 1 · BAB IV", "Studi eksploratif",
         "QUBO penempatan flow ke server\n(1.600 variabel, Fat-Tree k = 4)\nSQA vs DQN, ACO, GA\n1 seed utama + 5 seed\n\nTemuan: QUBO + SQA dapat\nditerapkan dan kompetitif\npada sebagian metrik, tetapi\nperbandingan belum setara", "#EEF4FB"),
        (5.1, "Tahap 2 · BAB V", "Studi terkontrol",
         "QUBO admisi flow + pemilihan jalur\n(96 arc berarah, S1–S3, 30 seed)\nSQA vs SA disetel, anggaran setara,\nrepair sama, uji berpasangan\n\nTemuan: keunggulan SQA\nbergantung objektif; repair\ndominan; EF tidak terlindungi", "#FDF1E3"),
        (10.1, "Tahap 3 · BAB VI", "Pengembangan multi-agen",
         "MAS-QA: agen per pod + repair\nReward admisi analitis μ_f,\npentahapan prioritas (Lex),\nkoordinasi harga, alokasi anggaran,\nperbandingan IP eksak (k = 4, 6, 8)\n\nTemuan: μ_f dan Lex bermanfaat;\nkoordinasi harga tidak menambah\nkualitas di atas repair", "#EAF5EE")]
for x, t1, t2, body, fc in cols:
    ax.add_patch(FancyBboxPatch((x, 2.55), 4.8, 4.75, boxstyle="round,pad=0,rounding_size=0.15", fc=fc, ec=EDGE, lw=1.0))
    ax.text(x + 2.4, 7.0, t1, ha="center", va="top", fontsize=10.5, fontweight="bold", color=INK)
    ax.text(x + 2.4, 6.55, t2, ha="center", va="top", fontsize=9.5, style="italic", color=INK2)
    ax.text(x + 2.4, 6.05, body, ha="center", va="top", fontsize=8.6, color=INK, linespacing=1.4)
arrow(ax, (4.9, 4.9), (5.1, 4.9)); arrow(ax, (9.9, 4.9), (10.1, 4.9))
ax.text(5.0, 2.4, "Mendorong protokol terkontrol:\npenyetelan, anggaran, admisi, repair", ha="center", va="top", fontsize=8.2, color=OI["blue"])
ax.text(10.0, 2.4, "Mendorong perbaikan objektif,\nproteksi prioritas, dan koordinasi", ha="center", va="top", fontsize=8.2, color=OI["verm"])
ax.add_patch(FancyBboxPatch((0.6, 0.1), 13.8, 0.95, boxstyle="round,pad=0,rounding_size=0.12", fc="#F4F4F4", ec=EDGE, lw=1.0))
ax.text(7.5, 0.575, "BAB VII · Sintesis: nilai MAS-QA terletak pada dekomposisi dan proteksi prioritas yang murah,\nbukan pada keunggulan kualitas solver atau koordinasi antar-agen",
        ha="center", va="center", fontsize=8.6, color=INK, linespacing=1.35)
save(fig, "gambar1_1_peta_penelitian")

# ---------------------------------------------------------------- Gambar 2.1 kerangka konseptual
fig, ax = plt.subplots(figsize=(10, 5.1)); ax.set_xlim(0, 15); ax.set_ylim(0.55, 8.0); ax.axis("off")
xs = [0.1, 3.05, 6.0, 8.95, 11.9]; W, H, Y = 2.75, 2.2, 3.4
items = [("Masalah", "admisi flow +\npemilihan jalur;\nkapasitas arc 50 Mbps;\nkelas EF/AF/BE"),
         ("Formulasi QUBO", "one-hot, kapasitas\ndengan slack biner,\nbalance, latensi,\nbandwidth, fairness"),
         ("Solver", "SQA (integral lintasan)\natau SA; monolitik\natau per pod (MAS-QA)"),
         ("Repair", "koordinator\ndeterministik:\nurutan prioritas,\nlalu pengisian greedy"),
         ("Evaluasi", "PL_flow, BWL,\nkehilangan per kelas,\nJFI/CoV, latensi,\nkerja annealing")]
fcs = ["#F2F2F2", "#DCEBF7", "#FBE3D6", "#E2F0D9", "#FFF2CC"]
for (t, b), x, fc in zip(items, xs, fcs):
    box(ax, x, Y, W, H, t, b, fc=fc, fs_b=8.0)
for i in range(4):
    arrow(ax, (xs[i] + W, Y + H / 2), (xs[i + 1], Y + H / 2))
ax.add_patch(FancyBboxPatch((0.1, 0.75), 14.55, 2.0, boxstyle="round,pad=0,rounding_size=0.12", fc="white", ec=OI["blue"], lw=1.2, ls="--"))
ax.text(0.35, 2.5, "Empat faktor yang dikendalikan agar selisih dapat diatribusikan ke solver (BAB V)", fontsize=9, fontweight="bold", color=OI["blue"], va="top")
fac = ["(1) Kekuatan pembanding:\nkedua solver disetel pada\nseed validasi", "(2) Aturan admisi:\nhimpunan flow dinilai\ndengan aturan yang sama",
       "(3) Anggaran komputasi:\ndisetarakan dalam\nspin-update", "(4) Repair:\nkoordinator yang sama\nuntuk setiap metode"]
for i, f in enumerate(fac):
    ax.text(0.35 + i * 3.6 + 1.6, 1.85, f, ha="center", va="top", fontsize=8.1, color=INK, linespacing=1.35)
ax.add_patch(FancyBboxPatch((3.05, 6.25), 11.6, 1.55, boxstyle="round,pad=0,rounding_size=0.12", fc="white", ec=OI["verm"], lw=1.2, ls="--"))
ax.text(3.3, 7.6, "Pengembangan pada BAB VI", fontsize=9, fontweight="bold", color=OI["verm"], va="top")
dev = [(4.4, "reward admisi\nanalitis μ_f"), (7.35, "koordinasi harga\nantar-agen pod"), (10.3, "pentahapan\nprioritas (Lex)"), (13.25, "acuan IP eksak\n(HiGHS)")]
for x, t in dev:
    ax.text(x, 7.15, t, ha="center", va="top", fontsize=8.1, color=INK, linespacing=1.3)
for x, tgt in [(4.4, xs[1] + W / 2), (7.35, xs[2] + W / 2), (10.3, xs[3] + W / 2), (13.25, xs[4] + W / 2)]:
    arrow(ax, (x, 6.25), (tgt, Y + H + 0.02), col=OI["verm"], lw=0.9)
save(fig, "gambar2_1_kerangka_konseptual")

# ---------------------------------------------------------------- Gambar 3.1 alur penelitian
fig, ax = plt.subplots(figsize=(9, 7.7)); ax.set_xlim(0, 12.6); ax.set_ylim(0.7, 10.5); ax.axis("off")
steps = [("Studi literatur dan perumusan masalah", "SDN, Fat-Tree, ECMP, QUBO, SQA/SA, metaheuristik, DRL (BAB II)", "#F2F2F2"),
         ("Tahap 1 – Studi eksploratif (BAB IV)", "QUBO penempatan flow ke server; SQA vs DQN, ACO, GA; Google Colab T4", "#EEF4FB"),
         ("Evaluasi kritis Tahap 1", "anggaran tidak setara, satu seed, tanpa repair dan uji berpasangan", "#FFFFFF"),
         ("Tahap 2 – Studi terkontrol (BAB V)", "QUBO admisi + jalur; penyetelan pada seed validasi; anggaran setara;\nrepair sama; uji berpasangan dan koreksi Bonferroni; IP eksak; k = 6; Mininet", "#FDF1E3"),
         ("Tahap 3 – Pengembangan multi-agen (BAB VI)", "reward admisi analitis, pentahapan prioritas, koordinasi harga (studi pendahuluan\ndengan aturan keputusan), alokasi anggaran, IP eksak pada k = 4, 6, 8", "#EAF5EE"),
         ("Sintesis dan kesimpulan (BAB VII)", "jawaban rumusan masalah, batas klaim, dan arah penelitian lanjutan", "#F2F2F2")]
y = 10.3
for i, (t, b, fc) in enumerate(steps):
    h = 1.45 if "\n" in b else 1.15
    ec = OI["verm"] if i == 2 else EDGE
    ax.add_patch(FancyBboxPatch((1.2, y - h), 9.6, h, boxstyle="round,pad=0,rounding_size=0.12", fc=fc, ec=ec, lw=1.0, ls="--" if i == 2 else "-"))
    ax.text(6.0, y - 0.2, t, ha="center", va="top", fontsize=10, fontweight="bold", color=INK)
    ax.text(6.0, y - 0.62, b, ha="center", va="top", fontsize=8.4, color=INK2, linespacing=1.35)
    if i < len(steps) - 1:
        arrow(ax, (6.0, y - h), (6.0, y - h - 0.38))
    y = y - h - 0.38
ax.text(11.0, 6.0, "Seed validasi 100–104\n(cek 105–114) untuk\npenyetelan; seed\nevaluasi 42–71\ntidak dipakai memilih\npengaturan", fontsize=7.8, color=OI["blue"], va="center", ha="left", linespacing=1.3)
save(fig, "gambar3_1_alur_penelitian")

# ---------------------------------------------------------------- Gambar 3.2 pipeline
fig, ax = plt.subplots(figsize=(7.3, 3.4)); ax.set_xlim(-0.1, 10.4); ax.set_ylim(-0.2, 4.2); ax.axis("off")
W, H_, Y = 1.86, 1.35, 1.7
xs = [0.0, 2.1, 4.2, 6.3, 8.4]
def sbox(xy, w, h, text, fc, fs=6.6):
    ax.add_patch(FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.02,rounding_size=0.05", fc=fc, ec="#333333", lw=0.7))
    ax.text(xy[0] + w / 2, xy[1] + h / 2, text, ha="center", va="center", fontsize=fs, linespacing=1.25)
sbox((xs[0], Y), W, H_, "Trafik\n50 / 100 / 150 flow\n±12,8 Mbps per flow", "#F2F2F2")
sbox((xs[1], Y), W, H_, "Fat-Tree k = 4\n16 host\n96 arc berarah\n(50 Mbps)", "#F2F2F2")
sbox((xs[2], Y), W, H_, "Dekomposisi\nmenurut pod sumber\n4 subproblem, b = 0", "#DCEBF7")
sbox((xs[3], Y), W, H_, "Solver per\nsubproblem:\nSQA (P = 16) atau SA", "#FBE3D6")
sbox((xs[4], Y), W, H_, "Koordinator:\nrepair berurutan\nprioritas, lalu\npengisian greedy", "#E2F0D9")
for i in range(4):
    ax.add_patch(FancyArrowPatch((xs[i] + W, Y + H_ / 2), (xs[i + 1], Y + H_ / 2), arrowstyle="-|>", mutation_scale=7, lw=0.8, color="#333333"))
ax.add_patch(FancyArrowPatch((xs[3] + W / 2, Y + H_ + 0.02), (xs[2] + W / 2, Y + H_ + 0.02), arrowstyle="-|>", mutation_scale=7, lw=0.8,
                             color=OI["purple"], linestyle="--", connectionstyle="arc3,rad=-0.6"))
ax.text((xs[2] + xs[3] + W) / 2, Y + H_ + 0.62, "varian iteratif: selesaikan ulang dengan beban pod lain (3 putaran)", fontsize=5.8, color=OI["purple"], ha="center")
sbox((xs[4], 0.0), W, 0.95, "Penilaian, sama untuk\nsemua metode:\nPL_flow, BWL, kelas,\nJFI/CoV, latensi", "#FFF2CC", fs=5.9)
ax.add_patch(FancyArrowPatch((xs[4] + W / 2, Y), (xs[4] + W / 2, 0.95), arrowstyle="-|>", mutation_scale=7, lw=0.8, color="#333333"))
sbox((0.0, 0.0), 8.1, 0.95, "Penyetelan: seed validasi 100–104 untuk β, Γ (SQA) dan jadwal SA; pemeriksaan pada seed baru 105–114\nEvaluasi: seed 42–71 (skenario utama), seed 42–66 (studi skala); acuan MILP eksak pada N = 8 dan 12", "#F7F7F7", fs=6.0)
save(fig, "gambar3_2_pipeline")

# ---------------------------------------------------------------- Gambar 3.3 topologi Fat-Tree k = 4
fig, ax = plt.subplots(figsize=(7.0, 3.8)); ax.set_xlim(-0.8, 8.6); ax.set_ylim(-1.35, 3.9); ax.axis("off")
podcol = [OI["sky"], OI["orange"], OI["green"], OI["purple"]]
core_x = [1.5, 3.2, 4.8, 6.5]; core_y = 3.4
for i, x in enumerate(core_x):
    ax.add_patch(plt.Rectangle((x - 0.18, core_y - 0.18), 0.36, 0.36, fc="#444444", ec="none"))
    ax.text(x, core_y + 0.32, f"C{i+1}", ha="center", fontsize=6.5)
for p in range(4):
    x0 = p * 2.0 + 0.2
    agg_x = [x0 + 0.35, x0 + 1.15]; edge_x = [x0 + 0.35, x0 + 1.15]
    for j, axx in enumerate(agg_x):
        ax.add_patch(plt.Rectangle((axx - 0.2, 2.2 - 0.16), 0.4, 0.32, fc=podcol[p], ec="#333333", lw=0.5))
        for k in range(2):
            ax.plot([axx, core_x[2 * j + k]], [2.2 + 0.16, core_y - 0.18], color="#999999", lw=0.6)
    for ex in edge_x:
        ax.add_patch(plt.Rectangle((ex - 0.2, 0.9 - 0.16), 0.4, 0.32, fc=podcol[p], ec="#333333", lw=0.5, alpha=0.6))
        for a in agg_x:
            ax.plot([ex, a], [0.9 + 0.16, 2.2 - 0.16], color="#999999", lw=0.6)
        for h in range(2):
            hx = ex - 0.15 + h * 0.3
            ax.add_patch(plt.Circle((hx, -0.25), 0.07, fc="white", ec="#333333", lw=0.6))
            ax.plot([hx, ex], [-0.25 + 0.07, 0.9 - 0.16], color="#999999", lw=0.5)
    ax.text(x0 + 0.75, -0.7, f"Pod {p+1}", ha="center", fontsize=7, color="#222222")
ax.text(-0.5, 3.4, "Inti", fontsize=7, va="center"); ax.text(-0.5, 2.2, "Agregasi", fontsize=7, va="center")
ax.text(-0.5, 0.9, "Edge", fontsize=7, va="center"); ax.text(-0.5, -0.25, "Host", fontsize=7, va="center")
ax.text(-0.7, -1.2, "Delay tautan: host–edge U[1, 3] ms; edge–agregasi U[0,5; 1,5] ms; agregasi–inti U[0,1; 0,5] ms",
        fontsize=6.2, va="center", ha="left")
save(fig, "gambar3_3_topologi")

# ---------------------------------------------------------------- Gambar 3.4 penyetelan solver
def ci95(x):
    x = np.asarray(x, float); return 1.96 * x.std(ddof=1) / np.sqrt(len(x))
plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8})
a = pd.read_csv(os.path.join(DATA, "diagB_validation.csv")); b = pd.read_csv(os.path.join(DATA, "diagB_validation_low.csv"))
g = pd.concat([a, b]).groupby(["beta", "gamma"]).PL_flow.mean().reset_index()
betas = sorted(g.beta.unique()); gammas = sorted(g.gamma.unique())
M = np.full((len(gammas), len(betas)), np.nan)
for _, r in g.iterrows():
    M[gammas.index(r.gamma), betas.index(r.beta)] = r.PL_flow
fig = plt.figure(figsize=(7.3, 3.2))
ax1 = fig.add_subplot(1, 3, 1)
im = ax1.imshow(M, cmap="viridis_r", aspect="auto", origin="lower")
for i in range(len(gammas)):
    for j in range(len(betas)):
        if not np.isnan(M[i, j]):
            ax1.text(j, i, f"{M[i,j]:.1f}".replace(".", ","), ha="center", va="center", fontsize=6, color="white" if M[i, j] > 42 else "black")
ax1.set_xticks(range(len(betas))); ax1.set_xticklabels([f"{x:g}".replace(".", ",") for x in betas], fontsize=6.5)
ax1.set_yticks(range(len(gammas))); ax1.set_yticklabels([f"{x:g}".replace(".", ",") for x in gammas], fontsize=6.5)
ax1.set_xlabel("β (suhu invers)"); ax1.set_ylabel("Γ (medan transversal)")
bi, gi = betas.index(0.5), gammas.index(1.0)
ax1.add_patch(plt.Rectangle((bi - 0.5, gi - 0.5), 1, 1, fill=False, ec=OI["verm"], lw=1.6))
ax1.set_title("(a) Grid SQA, seed 100–104\n(terpilih: β = 0,5; Γ = 1,0)", loc="left", fontsize=7.5)
cb = fig.colorbar(im, ax=ax1, fraction=0.05, pad=0.03); cb.set_label("PL_flow (%)", fontsize=6.5); cb.ax.tick_params(labelsize=6)
ax2 = fig.add_subplot(1, 3, 2)
t = pd.read_csv(os.path.join(DATA, "tune_sa_mono_matched.csv"))
t["cand"] = t.apply(lambda r: "default" if pd.isna(r.beta_min) else f"[{r.beta_min:g}; {r.beta_max:g}]".replace(".", ","), axis=1)
order = ["default", "[0,1; 3]", "[0,1; 10]", "[1; 10]"]
for i, c in enumerate(order):
    v = t[t.cand == c].PL_flow.values
    ax2.bar(i, v.mean(), 0.6, color=OI["blue"] if c == "[0,1; 10]" else "#BDBDBD")
    ax2.scatter(np.full(len(v), i) + np.random.default_rng(0).uniform(-0.12, 0.12, len(v)), v, s=6, color="black", zorder=3)
ax2.set_xticks(range(4)); ax2.set_xticklabels(order, fontsize=6.3)
ax2.set_xlabel("Jadwal SA β ∈ [β_min; β_max]"); ax2.set_ylabel("PL_flow (%)"); ax2.set_ylim(38, 46)
ax2.set_title("(b) Kandidat SA, seed 100–104\n(terpilih: [0,1; 10]; titik = seed)", loc="left", fontsize=7.5)
ax3 = fig.add_subplot(1, 3, 3)
v2 = pd.read_csv(os.path.join(DATA, "val2_sqa_mono.csv"))
cfg = [(5.0, 3.0, "awal (5; 3)"), (0.25, 1.0, "(0,25; 1)"), (0.5, 0.5, "(0,5; 0,5)"), (0.5, 1.0, "(0,5; 1) terpilih"), (0.5, 2.0, "(0,5; 2)"), (1.0, 1.0, "(1; 1)")]
for i, (be, ga, lab) in enumerate(cfg):
    v = v2[(v2.beta == be) & (v2.gamma == ga)].PL_flow.values
    ax3.bar(i, v.mean(), 0.6, color=OI["verm"] if (be, ga) == (0.5, 1.0) else "#BDBDBD", yerr=ci95(v), capsize=2, error_kw={"lw": 0.7})
ax3.set_xticks(range(len(cfg))); ax3.set_xticklabels([c[2] for c in cfg], fontsize=5.8, rotation=35, ha="right")
ax3.set_ylabel("PL_flow (%)"); ax3.set_ylim(34, 47)
ax3.set_title("(c) SQA pada seed baru 105–114\n(10 seed, rata-rata ± IK 95%)", loc="left", fontsize=7.5)
fig.tight_layout(w_pad=1.4)
save(fig, "gambar3_4_penyetelan")

# ---------------------------------------------------------------- persamaan BAB III
EQS = {
    "pers3_1": r"$H=\lambda_A H_A+\lambda_c H_{cap}+\lambda_l H_{bal}+\lambda_t H_{lat}+\lambda_b H_{bw}+\lambda_f H_{fair}$",
    "pers3_2": r"$H_A=\sum_{f}\left(\sum_{p}x_{f,p}-y_f\right)^{2}$",
    "pers3_3": r"$H_{cap}=\sum_{l}\left(\frac{\sum_{f}d_f\sum_{p\ni l}x_{f,p}+\sum_{k=0}^{K-1}\delta\,2^{k}s_{l,k}+b_l-c}{c}\right)^{2},\quad \delta=\frac{c}{2^{K}-1}$",
    "pers3_4": r"$u_l=\frac{b_l+\sum_{f}d_f\sum_{p\ni l}x_{f,p}}{c},\qquad H_{bal}=\sum_{l}u_l^{2}-\frac{1}{|E|}\left(\sum_{l}u_l\right)^{2}$",
    "pers3_5": r"$H_{lat}=\sum_{f}\sum_{p}w_f\,\frac{D_p}{D_{max}}\,x_{f,p}$",
    "pers3_6": r"$H_{bw}=-\sum_{f}\frac{d_f}{D_{tot}}\,y_f$",
    "pers3_7": r"$\rho_k=\frac{1}{D_k}\sum_{f\in k}d_f\,y_f,\qquad H_{fair}=\sum_{k<k'}\left(\rho_k-\rho_{k'}\right)^{2}$",
    "pers3_8": r"$H_{\mu}=H-\mu\sum_{f}y_f$",
    "pers3_9": r"$H_{p}=\lambda_p\sum_{(g,f)}y_f\,(1-y_g)$",
    "pers3_10": r"$\max\ \sum_{f}\sum_{p}x_{f,p}\quad \mathrm{s.t.}\quad \sum_{p}x_{f,p}\leq 1\ \ \forall f,\qquad \sum_{(f,p):\,l\in p}d_f\,x_{f,p}\leq c\ \ \forall l$",
    "pers3_11": r"$W=n_{var}\cdot P\cdot n_{sweep}\cdot n_{read}$",
    "pers3_12": r"$PL_{flow}=100\left(1-\frac{|A|}{N}\right),\qquad BWL=100\left(1-\frac{\sum_{f\in A}d_f}{D_{tot}}\right)$",
    "pers3_13": r"$JFI=\frac{\left(\sum_{i=1}^{n}x_i\right)^{2}}{n\sum_{i=1}^{n}x_i^{2}},\qquad CoV=\frac{\sigma_x}{\bar{x}}\times 100\%$",
    "pers3_14": r"$\bar{d}=\frac{1}{n}\sum_{s=1}^{n}\left(A_s-B_s\right),\qquad \bar{d}\pm t_{0.975,\,n-1}\frac{s_d}{\sqrt{n}},\qquad p_{adj}=\min(1,\ m\,p)$",
}
# ---------------------------------------------------------------- Gambar arsitektur SDN tiga lapisan
plt.rcParams.update({"font.size": 9})
fig, ax = plt.subplots(figsize=(8, 5.0)); ax.set_xlim(0, 12); ax.set_ylim(0, 7.6); ax.axis("off")
layers = [(5.4, "Lapisan Aplikasi", "rekayasa trafik · penyeimbangan beban · keamanan · pemantauan", "#EEF4FB"),
          (3.0, "Lapisan Kontrol", "pengendali SDN: pandangan global topologi dan beban tautan", "#FDF1E3"),
          (0.6, "Lapisan Infrastruktur", "switch dan router yang meneruskan paket sesuai tabel flow", "#EAF5EE")]
for y, t, b, fc in layers:
    ax.add_patch(FancyBboxPatch((1.0, y), 10.0, 1.6, boxstyle="round,pad=0,rounding_size=0.12", fc=fc, ec=EDGE, lw=1.0))
    ax.text(6.0, y + 1.15, t, ha="center", fontsize=10.5, fontweight="bold", color=INK)
    ax.text(6.0, y + 0.55, b, ha="center", fontsize=8.8, color=INK2)
for y0, y1, lab in [(5.4, 4.6, "API northbound"), (3.0, 2.2, "API southbound (mis. OpenFlow)")]:
    arrow(ax, (5.2, y0), (5.2, y1)); arrow(ax, (6.8, y1), (6.8, y0))
    ax.text(7.1, (y0 + y1) / 2, lab, fontsize=8.4, color=OI["blue"], va="center")
save(fig, "gambar2_1_arsitektur_sdn")

# ---------------------------------------------------------------- Gambar fishbone
fig, ax = plt.subplots(figsize=(10.5, 4.8)); ax.set_xlim(-1.2, 16); ax.set_ylim(0, 8); ax.axis("off")
ax.plot([0.6, 12.4], [4, 4], color=INK, lw=2.2)
ax.add_patch(FancyBboxPatch((12.5, 3.0), 3.35, 2.0, boxstyle="round,pad=0,rounding_size=0.12", fc="#FDF1E3", ec=OI["verm"], lw=1.4))
ax.text(14.17, 4.0, "Kehilangan flow\n(PL_flow) dan\nproteksi kelas EF", ha="center", va="center", fontsize=9.5, fontweight="bold", color=INK)
bones = [(1.7, True, "Objektif QUBO", ["bobot λ", "reward admisi μ / μ_f", "suku prioritas λ_p"]),
         (6.05, True, "Pemecah", ["SQA: β, Γ, P", "SA: jadwal β", "jumlah sampel (reads)"]),
         (10.4, True, "Anggaran", ["sweep × read × P", "dekomposisi per pod", "batas waktu IP"]),
         (1.7, False, "Repair", ["urutan EF → AF → BE", "pengisian ulang greedy", "beban terkunci (Lex)"]),
         (6.05, False, "Trafik", ["jumlah flow (S1–S3)", "Pareto, 12,8 Mbps/flow", "komposisi kelas"]),
         (10.4, False, "Topologi", ["Fat-Tree k = 4, 6, 8", "kapasitas arc 50 Mbps", "kandidat jalur terpendek"])]
for x, up, title, items in bones:
    y_end = 7.0 if up else 1.0
    ax.plot([x, x + 1.9], [y_end, 4.0], color=EDGE, lw=1.4)
    ax.text(x - 0.1, y_end + (0.35 if up else -0.35), title, ha="center", va="center", fontsize=9.5, fontweight="bold", color=OI["blue"])
    for i, it in enumerate(items):
        t = (i + 1) / 4.0
        yy = y_end + (4.0 - y_end) * t; xx = x + 1.9 * t
        ax.plot([xx - 0.5, xx], [yy, yy], color="#B0B0B0", lw=0.9)
        ax.text(xx - 0.55, yy, it, ha="right", va="center", fontsize=7.4, color=INK2)
save(fig, "gambar3_5_fishbone")

# ---------------------------------------------------------------- Gambar integrasi QA ke SDN dan MAS
fig, ax = plt.subplots(figsize=(9.5, 5.6)); ax.set_xlim(0, 15); ax.set_ylim(0, 8.6); ax.axis("off")
ax.add_patch(FancyBboxPatch((0.2, 5.2), 14.6, 3.2, boxstyle="round,pad=0,rounding_size=0.12", fc="#F7F7F7", ec=EDGE, lw=1.0, ls="--"))
ax.text(0.45, 8.15, "Lapisan aplikasi/kontrol SDN: modul MAS-QA", fontsize=9, fontweight="bold", color=INK, va="top")
box(ax, 0.5, 5.5, 2.6, 2.1, "Status jaringan", "permintaan flow,\nkelas, topologi,\nkapasitas arc", fc="#F2F2F2", fs_b=7.8)
box(ax, 3.5, 5.5, 4.4, 2.1, "Agen pod 1 … q", "QUBO lokal per pod sumber\n(μ_f, tanpa slack arc bersama)\ndiselesaikan SQA; paralel", fc="#DCEBF7", fs_b=7.8)
box(ax, 8.3, 5.5, 3.0, 2.1, "Repair bersama", "koordinator global:\nEF → AF → BE,\npengisian greedy", fc="#E2F0D9", fs_b=7.8)
box(ax, 11.7, 5.5, 2.9, 2.1, "Keputusan", "flow diterima\ndan jalurnya", fc="#FFF2CC", fs_b=7.8)
for a_, b_ in [((3.1, 6.55), (3.5, 6.55)), ((7.9, 6.55), (8.3, 6.55)), ((11.3, 6.55), (11.7, 6.55))]:
    arrow(ax, a_, b_)
ax.text(7.5, 5.05, "(opsional) harga π_l pada arc bersama — tidak dipertahankan (BAB VI)", fontsize=7.4, color=OI["verm"], ha="center", va="top")
ax.add_patch(FancyBboxPatch((0.2, 0.3), 14.6, 3.6, boxstyle="round,pad=0,rounding_size=0.12", fc="#EAF5EE", ec=EDGE, lw=1.0))
ax.text(0.45, 3.65, "Lapisan infrastruktur: Fat-Tree (k = 4: 16 host, 96 arc berarah 50 Mbps)", fontsize=9, fontweight="bold", color=INK, va="top")
for p in range(4):
    x0 = 1.2 + p * 3.4
    ax.add_patch(FancyBboxPatch((x0, 0.7), 2.6, 1.9, boxstyle="round,pad=0,rounding_size=0.1", fc="white", ec=EDGE, lw=0.8))
    ax.text(x0 + 1.3, 1.65, f"Pod {p+1}\n2 agregasi · 2 edge\n4 host", ha="center", va="center", fontsize=7.8, color=INK2)
ax.text(7.5, 3.05, "4 switch inti", ha="center", fontsize=8, color=INK2)
arrow(ax, (13.15, 5.5), (13.15, 3.9)); ax.text(13.3, 4.3, "pasang aturan\nflow", fontsize=7.6, color=OI["blue"], va="center")
arrow(ax, (1.8, 3.9), (1.8, 5.5)); ax.text(1.95, 4.3, "statistik beban\ndan permintaan", fontsize=7.6, color=OI["blue"], va="center")
save(fig, "gambar3_6_integrasi")

EQS.update({
    "pers2_ising": r"$H_P=\sum_{i}h_i\,s_i+\sum_{i<j}J_{ij}\,s_i\,s_j,\qquad s_i\in\{-1,+1\}$",
    "pers2_aco": r"$p_{ij}^{(a)}=\frac{\tau_{ij}^{\alpha}\,\eta_{ij}^{\beta}}{\sum_{m\in N_i}\tau_{im}^{\alpha}\,\eta_{im}^{\beta}},\qquad \tau_{ij}\leftarrow(1-\rho)\,\tau_{ij}+\sum_{a}\Delta\tau_{ij}^{(a)}$",
    "pers2_dqn": r"$L(\theta)=\mathbb{E}\left[\left(r+\gamma\max_{a'}Q(s',a';\theta^{-})-Q(s,a;\theta)\right)^{2}\right]$",
    "pers2_thr": r"$\mathrm{Throughput}=\sum_{f\in A}d_f,\qquad D_f=\sum_{e\in p_f}d_e,\qquad \mathrm{Jitter}=\frac{1}{n-1}\sum_{i=2}^{n}\left|D_i-D_{i-1}\right|$",
})
EQS.update({
    "pers2_1": r"$\min_{x\in\{0,1\}^{n}}\ x^{\top}Qx=\sum_{i}Q_{ii}x_i+\sum_{i<j}Q_{ij}x_ix_j,\qquad s_i=2x_i-1\in\{-1,+1\}$",
    "pers2_2": r"$\hat{H}(t)=-A(t)\sum_{i}\hat{\sigma}_i^{x}+B(t)\,\hat{H}_P,\qquad t\in[0,T]$",
    "pers2_3": r"$P_{\mathrm{terima}}=\min\left(1,\ e^{-\beta\,\Delta E}\right)$",
    "pers2_4": r"$\beta H_{eff}=\frac{\beta}{P}\sum_{k=1}^{P}H_P\left(s^{(k)}\right)-J_{\perp}\sum_{k=1}^{P}\sum_{i}s_i^{(k)}s_i^{(k+1)},\qquad J_{\perp}=\frac{1}{2}\ln\coth\frac{\beta\Gamma}{P}$",
    "pers2_5": r"$L(x,\pi)=f(x)+\sum_{l}\pi_l\left(g_l(x)-c_l\right),\qquad \pi_l\leftarrow\max\left(0,\ \pi_l+\rho\,(g_l(x)-c_l)\right)$",
})
for name, tex in EQS.items():
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, tex, fontsize=13, color="black")
    fig.savefig(os.path.join(EQ, f"{name}.png"), dpi=300, bbox_inches="tight", pad_inches=0.04, facecolor="white")
    plt.close(fig)
print("selesai:", sorted(os.listdir(OUT)), sorted(os.listdir(EQ)))
