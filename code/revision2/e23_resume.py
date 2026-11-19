"""E2 + E3 (resumable per seed), S2, seeds 42-71, baseline weights, run ALONE.
Each row is one configuration on one seed with measured build / solve / coordinator time."""
import os
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "revision2")
import csv, os, time
import numpy as np
import r2lib as R
OUT = os.path.join(OUT_DIR, "e23_timing_curves.csv")
FIELDS = ["seed","method","budget","PL_flow","BWL","build_s","solve_s","coord_s","total_s","vars","work"]
rows = []
if os.path.exists(OUT):
    rows = list(csv.DictReader(open(OUT)))
done = {(int(r["seed"]), r["method"], r["budget"]) for r in rows}
N, Dtot = R.SCEN["S2"]
def save(seed, method, budget, m, build, solve, coord, vars_, work):
    rows.append(dict(seed=seed, method=method, budget=budget, PL_flow=m["PL_flow"], BWL=m["BWL"], build_s=build, solve_s=solve, coord_s=coord,
                     total_s=build + solve + coord, vars=vars_, work=work))
for seed in R.MAIN_SEEDS:
    if (seed, "Greedy-only", "-") not in done:
        flows = R.L.gen_traffic(N, Dtot, seed)
        t0 = time.perf_counter(); g = R.L.coordinate({}, flows); tg = time.perf_counter() - t0
        save(seed, "Greedy-only", "-", R.metrics(flows, g, Dtot), 0.0, 0.0, tg, 0, 0)
    flows = R.L.gen_traffic(N, Dtot, seed); cc = R.cc_of(flows)
    for ps in [100, 500, 1000]:
        if (seed, "MAS-QA-pods-SQA", str(ps)) in done: continue
        fin, info = R.pod_solve(flows, seed, Dtot, cc, R.LAM, 0, "sqa", dict(R.TUNED, pod_sweeps=ps))
        save(seed, "MAS-QA-pods-SQA", str(ps), R.metrics(flows, fin, Dtot), float("nan"), info["pod_sequential_s"], info["coord_s"], info["pod_vars"], info["pod_work"])
    for sw in [500, 2000, 5000]:
        if (seed, "SQA-mono", str(sw)) in done: continue
        raw, fin, info, _, _ = R.mono_solve(flows, seed, Dtot, cc, R.LAM, 0, "sqa", 10, sw, R.TUNED)
        save(seed, "SQA-mono", str(sw), R.metrics(flows, fin, Dtot), info["build_s"], info["solve_s"], info["coord_s"], info["mono_vars"], info["mono_work"])
    for sw in [5000, 20000, 80000]:
        if (seed, "SA-mono", str(sw)) in done: continue
        raw, fin, info, _, _ = R.mono_solve(flows, seed, Dtot, cc, R.LAM, 0, "sa", 10, sw, R.TUNED)
        save(seed, "SA-mono", str(sw), R.metrics(flows, fin, Dtot), info["build_s"], info["solve_s"], info["coord_s"], info["mono_vars"], info["mono_work"])
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    done = {(int(r["seed"]), r["method"], r["budget"]) for r in rows}
    print(seed, "done", flush=True)
print("ALL DONE", flush=True)
