"""Evaluasi ringan BAB VI (dapat dijalankan pada laptop/PC dua core).

Tingkat A  : Fat-Tree k = 4, skenario S1-S3, seed evaluasi 42-71 (sama dengan artikel).
Tingkat B  : Fat-Tree k = 6, intensitas setara S2 (338 flow), seed 42-51.
Tidak ada  : k = 8 dan evaluasi koordinasi harga (cukup hasil pilot, Subbab 6.5.7-6.5.10).
Dipakai ulang tanpa dijalankan ulang: SA monolitik tuned (data/eval_sa_mono_tuned.csv, k = 4).

Pemakaian:  python3 eval_light.py A [seed,seed,...] [S1,S2,S3]
            python3 eval_light.py B [seed,seed,...]
Keluaran   : ../../data/chapter6/eval_light_A.csv, eval_light_B.csv (resumable per skenario, seed, metode)."""
import os, sys, time
import numpy as np
import pandas as pd
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import lil_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "extensions", "k6_priority_emulation"))
import mas_price as M
import masqa_lib as L
import r2lib as R
import fattree_k as F

TIER = sys.argv[1] if len(sys.argv) > 1 else "A"
IP_LIMIT = float(os.environ.get("IP_LIMIT", "60"))


def ip_count(flows, time_limit=IP_LIMIT):
    """Acuan eksak: maksimalkan jumlah flow diterima (satu jalur per flow, kapasitas per arc).
    Mengembalikan (assign, info) dengan status, waktu, dan MIP gap bila batas waktu tercapai."""
    cols = [(f["id"], p) for f in flows for p in range(len(f["paths"]))]
    fidx = {f["id"]: f for f in flows}
    nL = len(L.TOPO["links"])
    rows, lb, ub = [], [], []
    for f in flows:
        rows.append({j: 1.0 for j, (fid, _) in enumerate(cols) if fid == f["id"]}); lb.append(0.0); ub.append(1.0)
    arc = {l: {} for l in range(nL)}
    for j, (fid, p) in enumerate(cols):
        for l in fidx[fid]["paths"][p]:
            arc[l][j] = fidx[fid]["demand"]
    for l in range(nL):
        if arc[l]:
            rows.append(arc[l]); lb.append(0.0); ub.append(L.LINK_CAP)
    A = lil_matrix((len(rows), len(cols)))
    for i, r in enumerate(rows):
        for j, v in r.items():
            A[i, j] = v
    t0 = time.perf_counter()
    res = milp(c=-np.ones(len(cols)), constraints=LinearConstraint(A.tocsr(), lb, ub),
               integrality=np.ones(len(cols)), bounds=Bounds(0, 1), options=dict(time_limit=time_limit))
    dt = time.perf_counter() - t0
    adm = {f["id"]: None for f in flows}
    if res.x is not None:
        x = np.round(res.x).astype(int)
        for j, (fid, p) in enumerate(cols):
            if x[j] == 1:
                adm[fid] = p
    gap = getattr(res, "mip_gap", float("nan"))
    return adm, dict(ip_status=int(res.status), ip_optimal=bool(res.status == 0), ip_gap=gap, solve_s=dt)


def methods_for(tier):
    m = {
        "Greedy-only":            lambda fl, s, D, cc: (L.coordinate({}, fl), {}),
        "ECMP+adm":               lambda fl, s, D, cc: (L.ecmp_admission(fl, s), {}),
        "MAS-QA-v2":              lambda fl, s, D, cc: M.run_v2_k(fl, s, D, cc),
        "MAS-QA-mu_f":            lambda fl, s, D, cc: _pi1(M.run_mas_price, fl, s, D, cc),
        "MAS-QA-mu_f-Lex":        lambda fl, s, D, cc: _pi1(M.run_mas_price_lex, fl, s, D, cc),
        "MAS-QA-v2 4x125":        lambda fl, s, D, cc: M.run_v2_restarts(fl, s, D, cc, 4, prm=dict(R.TUNED, pod_sweeps=125)),
        "IP-count":               lambda fl, s, D, cc: ip_count(fl),
    }
    if tier == "A":
        m["MAS-QA-v2 mu=20"] = lambda fl, s, D, cc: M.run_v2_k(fl, s, D, cc, mu=20.0)
        m["MAS-QA-v2 2x250"] = lambda fl, s, D, cc: M.run_v2_restarts(fl, s, D, cc, 2, prm=dict(R.TUNED, pod_sweeps=250))
        m["MAS-QA-v2 8x62"] = lambda fl, s, D, cc: M.run_v2_restarts(fl, s, D, cc, 8, prm=dict(R.TUNED, pod_sweeps=62))
    return m


def _pi1(fn, fl, s, D, cc):
    """Satu putaran tanpa koordinasi harga: QUBO pod dengan mu_f analitis, kapasitas lokal saja."""
    out = fn(fl, s, D, cc, T_max=1, rho0=0.0, mu_mode="analytic")
    final, info = out[0], out[1]
    info.pop("last_final", None)
    return final, info


if TIER == "A":
    T = L.TOPO
    SCEN = (sys.argv[3].split(",") if len(sys.argv) > 3 else ["S1", "S2", "S3"])
    SEEDS = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 and sys.argv[2] else list(range(42, 72))
    jobs = [(sc,) + L.SCENARIOS[sc] for sc in SCEN]
    gen = lambda N, D, s: L.gen_traffic(N, D, s)
else:
    T = F.build_fat_tree_k(6)
    SEEDS = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 and sys.argv[2] else list(range(42, 52))
    jobs = [("k6-S2", 338, 4313.5)]
    gen = lambda N, D, s: F.gen_traffic_k(T, N, D, s)
M.set_topology(T)

OUT = os.path.join(HERE, "..", "..", "data", "chapter6"); os.makedirs(OUT, exist_ok=True)
ROWS = os.path.join(OUT, f"eval_light_{TIER}.csv")
done = set()
if os.path.exists(ROWS):
    d = pd.read_csv(ROWS); done = set(zip(d.scenario, d.seed, d.method))
METHODS = methods_for(TIER)
for sc, N, D in jobs:
    for seed in SEEDS:
        flows = gen(N, D, seed); cc = R.cc_of(flows)
        for name, fn in METHODS.items():
            if (sc, seed, name) in done:
                continue
            t0 = time.perf_counter()
            final, info = fn(flows, seed, D, cc)
            m = R.metrics(flows, final, D)
            wprio = sum(f["w"] * f["demand"] for f in flows if final[f["id"]] is not None) / sum(f["w"] * f["demand"] for f in flows)
            row = dict(tier=TIER, scenario=sc, N=N, seed=seed, method=name, wall_s=time.perf_counter() - t0, **m,
                       prio_utility=100.0 * wprio,
                       **{k: info.get(k) for k in ["work", "rounds", "pods_seq_s", "pods_par_s",
                                                   "ip_status", "ip_optimal", "ip_gap", "solve_s"]})
            pd.DataFrame([row]).to_csv(ROWS, mode="a", header=not os.path.exists(ROWS), index=False)
            print(f"{TIER} {sc} seed={seed} {name:18s} PL={m['PL_flow']:5.1f} EF={m['PL_EF']:5.1f} t={row['wall_s']:.1f}s", flush=True)
print("SELESAI", flush=True)
