"""Pilot BAB VI pada seed validasi (100-104), skenario S2, k = 4.
Tujuan: memeriksa bahwa MAS-QA-pi berjalan, mengukur konvergensi, dan memilih rho0 SEBELUM
evaluasi pada seed 42-71 (seed evaluasi tidak disentuh di sini). Resumable per (seed, metode).
Keluaran: ../../data/chapter6/pilot_rows.csv dan pilot_trace.csv"""
import os, sys, time, json
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mas_price as M
import masqa_lib as L
import r2lib as R

OUT = os.path.join(HERE, "..", "..", "data", "chapter6"); os.makedirs(OUT, exist_ok=True)
ROWS, TRACE = os.path.join(OUT, "pilot_rows.csv"), os.path.join(OUT, "pilot_trace.csv")
SEEDS = [int(s) for s in os.environ.get("SEEDS", "100,101,102,103,104").split(",")]
SCEN = os.environ.get("SCEN", "S2")

CONFIGS = {
    "Greedy-only":            None,
    "MAS-QA-v2 (mu=0)":       dict(kind="v2", mu=0.0),
    "MAS-QA-v2 (mu=20)":      dict(kind="v2", mu=20.0),
    "MAS-QA-pi off (mu_f)":   dict(kind="pi", T_max=1, rho0=0.0, mu_mode="analytic"),
    "MAS-QA-pi rho0=10":      dict(kind="pi", T_max=8, rho0=10.0, mu_mode="analytic"),
    "MAS-QA-pi rho0=40":      dict(kind="pi", T_max=8, rho0=40.0, mu_mode="analytic"),
    "MAS-QA-pi rho0=10 mu=20": dict(kind="pi", T_max=8, rho0=10.0, mu_mode="const", mu_const=20.0),
    "MAS-QA-pi-Lex rho0=10":  dict(kind="lex", T_max=5, rho0=10.0, mu_mode="analytic"),
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
        t0 = time.perf_counter(); info, trace = {}, []
        if cfg is None:
            final = L.coordinate({}, flows)
        elif cfg["kind"] == "v2":
            final, info = R.pod_solve(flows, seed, D, cc, R.LAM, cfg["mu"], "sqa", R.TUNED)
            info = dict(work=info["pod_work"], rounds=1, pods_seq_s=info["pod_sequential_s"])
        else:
            kw = {k: v for k, v in cfg.items() if k != "kind"}
            fn = M.run_mas_price if cfg["kind"] == "pi" else M.run_mas_price_lex
            final, info, trace = fn(flows, seed, D, cc, **kw)
        m = R.metrics(flows, final, D)
        row = dict(scenario=SCEN, seed=seed, method=name, wall_s=time.perf_counter() - t0,
                   **{k: v for k, v in m.items()}, **{k: info.get(k) for k in ["rounds", "work", "pods_seq_s", "pods_par_s"]})
        pd.DataFrame([row]).to_csv(ROWS, mode="a", header=not os.path.exists(ROWS), index=False)
        if trace:
            pd.DataFrame([dict(seed=seed, method=name, **r) for r in trace]).to_csv(
                TRACE, mode="a", header=not os.path.exists(TRACE), index=False)
        print(f"{SCEN} seed={seed} {name:26s} PL={m['PL_flow']:5.1f} EF={m['PL_EF']:5.1f} "
              f"rounds={info.get('rounds')} t={row['wall_s']:.1f}s", flush=True)
print("SELESAI")
