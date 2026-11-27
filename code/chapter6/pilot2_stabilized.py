"""Pilot 2 BAB VI: loop harga yang distabilkan vs kontrol 'terbaik dari K restart'.
Seed validasi 100-104, S2, k = 4. Keluaran: ../../data/chapter6/pilot2_rows.csv, pilot2_trace.csv"""
import os, sys, time
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mas_price as M
import masqa_lib as L
import r2lib as R

OUT = os.path.join(HERE, "..", "..", "data", "chapter6"); os.makedirs(OUT, exist_ok=True)
ROWS, TRACE = os.path.join(OUT, "pilot2_rows.csv"), os.path.join(OUT, "pilot2_trace.csv")
SEEDS = [int(s) for s in os.environ.get("SEEDS", "100,101,102,103,104").split(",")]
SCEN = os.environ.get("SCEN", "S2")
STAB = dict(kappa=2.0, alpha=0.5, fixed_seed=True)

CONFIGS = {
    "MAS-QA-v2":                         dict(kind="v2", K=1),
    "MAS-QA-v2 terbaik dari 2 restart":  dict(kind="v2", K=2),
    "pi acak rho0=10 (8x250)":           dict(kind="pi", T_max=8, rho0=10.0, pod_sweeps=250),
    "pi stabil rho0=40 (8x250)":         dict(kind="pi", T_max=8, rho0=40.0, pod_sweeps=250, **STAB),
    "pi benih tetap saja rho0=40 (8x250)": dict(kind="pi", T_max=8, rho0=40.0, pod_sweeps=250, fixed_seed=True),
    "pi-Lex stabil rho0=40 (5x250)":     dict(kind="lex", T_max=5, rho0=40.0, pod_sweeps=250, **STAB),
}

done = set()
if os.path.exists(ROWS):
    d = pd.read_csv(ROWS); done = set(zip(d.seed, d.method))
N, D = L.SCENARIOS[SCEN]
for seed in SEEDS:
    flows = L.gen_traffic(N, D, seed); cc = R.cc_of(flows)
    for name, cfg in CONFIGS.items():
        if (seed, name) in done:
            continue
        t0 = time.perf_counter(); trace = []; last = None
        if cfg["kind"] == "v2":
            final, info = M.run_v2_restarts(flows, seed, D, cc, cfg["K"])
        else:
            kw = {k: v for k, v in cfg.items() if k != "kind"}
            if cfg["kind"] == "pi":
                final, info, trace = M.run_mas_price(flows, seed, D, cc, **kw)
                last = info.pop("last_final")
            else:
                final, info, trace = M.run_mas_price_lex(flows, seed, D, cc, **kw)
        m = R.metrics(flows, final, D)
        row = dict(scenario=SCEN, seed=seed, method=name, wall_s=time.perf_counter() - t0, **m,
                   PL_flow_last=(R.metrics(flows, last, D)["PL_flow"] if last else float("nan")),
                   **{k: info.get(k) for k in ["rounds", "work", "pods_seq_s", "pods_par_s"]})
        pd.DataFrame([row]).to_csv(ROWS, mode="a", header=not os.path.exists(ROWS), index=False)
        if trace:
            pd.DataFrame([dict(seed=seed, method=name, **r) for r in trace]).to_csv(
                TRACE, mode="a", header=not os.path.exists(TRACE), index=False)
        print(f"seed={seed} {name:38s} PL={m['PL_flow']:5.1f} EF={m['PL_EF']:5.1f} t={row['wall_s']:.1f}s", flush=True)
print("SELESAI")
