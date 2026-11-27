"""Aset naskah BAB VI: Gambar 6.1 (arsitektur MAS-QA multi-agen) dan persamaan (6.1)-(6.5) sebagai PNG.
Pemakaian: python3 assets_naskah.py  -> figures/chapter6/gambar6_1_arsitektur.(png|pdf), figures/chapter6/persamaan/*.png"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "..", "figures", "chapter6")
EQ = os.path.join(FIG, "persamaan"); os.makedirs(EQ, exist_ok=True)
INK, INK2, EDGE, ACC = "#1f1f1f", "#5c5c5c", "#8a8a8a", "#257de0"
plt.rcParams.update({"font.family": "DejaVu Sans", "mathtext.fontset": "cm"})

# ---------------- Gambar 6.1: arsitektur
fig, ax = plt.subplots(figsize=(10, 6.2)); ax.set_xlim(0, 760); ax.set_ylim(460, 0); ax.axis("off")


def box(cx, cy, w, h, name, line, accent=False):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0,rounding_size=8",
                                fc=(0.145, 0.49, 0.878, 0.12) if accent else "white",
                                ec=ACC if accent else EDGE, lw=2 if accent else 1.2))
    ax.text(cx, cy - 7, name, ha="center", va="center", fontsize=10, fontweight="bold", color=INK)
    ax.text(cx, cy + 11, line, ha="center", va="center", fontsize=8.5, color=INK2)


def arrow(x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color=EDGE, lw=1.2))


def seg(xs, ys):
    ax.plot(xs, ys, color=EDGE, lw=1.2)


box(380, 70, 320, 56, "Agen koordinator", "harga π_l per arc bersama (studi pendahuluan)", accent=True)
pods = [102, 279, 457, 634]
seg([380, 380], [98, 135]); seg([102, 634], [135, 135])
for i, x in enumerate(pods):
    arrow(x, 135, x, 172)
    box(x, 200, 160, 56, f"Agen pod {i + 1}", "QUBO lokal, μ_f, SQA")
    seg([x, x], [228, 252])
seg([102, 634], [252, 252]); arrow(380, 252, 380, 290)
ax.text(392, 125, "harga π_l", fontsize=8.5, color=INK2)
ax.text(392, 275, "keputusan admisi dan jalur per pod", fontsize=8.5, color=INK2)
seg([716, 716], [200, 70]); arrow(716, 70, 540, 70); seg([714, 716], [200, 200])
ax.text(722, 135, "beban arc\nbersama", fontsize=8.5, color=INK2, va="center")
box(380, 318, 300, 56, "Repair bersama", "koordinator global, prioritas EF → AF → BE")
arrow(380, 346, 380, 382)
box(380, 410, 220, 52, "Admisi akhir", "flow yang diterima dan jalurnya")
ax.text(380, 452, s="Lex: alur dijalankan untuk EF, lalu AF, lalu BE; kapasitas tahap sebelumnya dikunci.",
        fontsize=9, color=INK2, ha="center")
for ext in ("png", "pdf"):
    fig.savefig(os.path.join(FIG, f"gambar6_1_arsitektur.{ext}"), dpi=300, bbox_inches="tight")
plt.close(fig)

# ---------------- persamaan
EQS = {
    "pers6_1": r"$\Delta E_f=\lambda_l\,\Delta H_{bal}+\lambda_t\,w_f\,\frac{D_p}{D_{max}}+\lambda_f\,\Delta H_{fair}+\lambda_c\,\varepsilon_{cap}-\lambda_b\,\frac{d_f}{D_{tot}}-\mu_f$",
    "pers6_2": r"$\Delta H_{bal}=2a_f\sum_{l\in p}\left(u_l-\bar{u}\right)+h\,a_f^{2}\left(1-\frac{h}{|E|}\right)$",
    "pers6_3": r"$\mu_f^{min}=\min_{p}\left[\lambda_l\,\Delta H_{bal}+\lambda_t\,w_f\,\frac{D_p}{D_{max}}+\lambda_f\,\Delta H_{fair}^{max}+\lambda_c\,\varepsilon_{cap}\right]-\lambda_b\,\frac{d_f}{D_{tot}}$",
    "pers6_4": r"$\mu_f=(1+\epsilon)\,\max\left(\mu_f^{min},\ 0\right)$",
    "pers6_5": r"$H_q(\pi)=H_q^{lokal}+\sum_{l\in L_s}\frac{\pi_l}{c}\sum_{f\in F_q}d_f\sum_{p\ni l}x_{f,p}$",
    "pers6_6": r"$\pi_l^{(t+1)}=\max\left(0,\ \pi_l^{(t)}+\rho_t\,\frac{\bar{L}_l^{(t)}-c}{c}\right),\quad \bar{L}_l^{(t)}=(1-\alpha)\,\bar{L}_l^{(t-1)}+\alpha\,L_l^{(t)}$",
}
for name, tex in EQS.items():
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, tex, fontsize=13, color="black")
    fig.savefig(os.path.join(EQ, f"{name}.png"), dpi=300, bbox_inches="tight", pad_inches=0.04, transparent=False, facecolor="white")
    plt.close(fig)
print("selesai:", sorted(os.listdir(EQ)))
