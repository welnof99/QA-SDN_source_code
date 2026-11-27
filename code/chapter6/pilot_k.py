"""Pilot BAB VI pada Fat-Tree k = 6 dan k = 8 (seed validasi), intensitas per host setara S2.
Pemakaian: python3 pilot_k.py <k> <seed,seed,...> <konfig,konfig,...>
Keluaran: ../../data/chapter6/pilot_k<k>_rows.csv dan pilot_k<k>_trace.csv (resumable per seed, metode)."""
import os, sys, time
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "extensions", "k6_priority_emulation"))
import mas_price as M
import masqa_lib as L
import r2lib as R
import fattree_k as F

K = int(sys.argv[1])
SEEDS = [int(s) for s in sys.argv[2].split(",")]
WANT = sys.argv[3].split(",")
S2_N, S2_D = L.SCENARIOS["S2"]
HOSTS = K ** 3 // 4
N = int(-(-S2_N * HOSTS // 16))                 # dibulatkan ke atas: 338 (k=6), 800 (k=8)
D = {6: 4313.5}.get(K, S2_D * HOSTS / 16)        # k=6 memakai nilai artikel
T = F.build_fat_tree_k(K); M.set_topology(T)
STAB = dict(kappa=2.0, alpha=0.5, fixed_seed=True)
CONFIGS = {
    "greedy":    ("Greedy-only", None),
    "v2":        ("MAS-QA-v2", dict(kind="v2", K=1)),
    "v2r2":      ("MAS-QA-v2 terbaik dari 2 restart", dict(kind="v2", K=2)),
    "piacak":    ("pi acak rho0=10", dict(kind="pi", T_max=6, rho0=10.0, pod_sweeps=250)),
    "pistabil":  ("pi stabil rho0=40", dict(kind="pi", T_max=6, rho0=40.0, pod_sweeps=250, **STAB)),
    "lex":       ("pi-Lex stabil rho0=40", dict(kind="lex", T_max=4, rho0=40.0, pod_sweeps=250, **STAB)),
    # 6.5.10: langkah konstan berskala median mu_f, 10 putaran x 150 sweeps (kerja setara 6 x 250)
    "adapt3":    ("pi adaptif 3x mu (10x150)", dict(kind="pi", T_max=10, pod_sweeps=150, step="const", rho_mu_mult=3.0, **STAB)),
    "adapt10":   ("pi adaptif 10x mu (10x150)", dict(kind="pi", T_max=10, pod_sweeps=150, step="const", rho_mu_mult=10.0, **STAB)),
}
OUT = os.path.join(HERE, "..", "..", "data", "chapter6"); os.makedirs(OUT, exist_ok=True)
ROWS, TRACE = os.path.join(OUT, f"pilot_k{K}_rows.csv"), os.path.join(OUT, f"pilot_k{K}_trace.csv")
done = set()
if os.path.exists(ROWS):
    d = pd.read_csv(ROWS); done = set(zip(d.seed, d.method))
print(f"k={K} host={HOSTS} N={N} D={D:.1f} arc={M.NL}", flush=True)
for seed in SEEDS:
    flows = F.gen_traffic_k(T, N, D, seed); cc = R.cc_of(flows)
    for key in WANT:
        name, cfg = CONFIGS[key]
        if (seed, name) in done:
            continue
        t0 = time.perf_counter(); trace = []; last = None; info = {}
        if cfg is None:
            final = L.coordinate({}, flows)
        elif cfg["kind"] == "v2":
            final, info = M.run_v2_restarts(flows, seed, D, cc, cfg["K"])
        else:
            kw = {k: v for k, v in cfg.items() if k != "kind"}
            if cfg["kind"] == "pi":
                final, info, trace = M.run_mas_price(flows, seed, D, cc, **kw)
                last = info.pop("last_final")
            else:
                final, info, trace = M.run_mas_price_lex(flows, seed, D, cc, **kw)
        m = R.metrics(flows, final, D)
        row = dict(k=K, N=N, seed=seed, method=name, wall_s=time.perf_counter() - t0, **m,
                   PL_flow_last=(R.metrics(flows, last, D)["PL_flow"] if last else float("nan")),
                   **{c: info.get(c) for c in ["rounds", "work", "pods_seq_s", "pods_par_s"]})
        pd.DataFrame([row]).to_csv(ROWS, mode="a", header=not os.path.exists(ROWS), index=False)
        if trace:
            pd.DataFrame([dict(seed=seed, method=name, **r) for r in trace]).to_csv(
                TRACE, mode="a", header=not os.path.exists(TRACE), index=False)
        print(f"k={K} seed={seed} {name:34s} PL={m['PL_flow']:5.1f} EF={m['PL_EF']:5.1f} t={row['wall_s']:.0f}s", flush=True)
print("SELESAI", flush=True)
