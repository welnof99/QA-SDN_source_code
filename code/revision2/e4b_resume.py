"""E4b (resumable): mu*=20 evaluation, order S2, S1, S3; skips (scenario, seed) already in OUT."""
import os
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "revision2")
import csv, os, sys
import r2lib as R
MU = 20.0
OUT = os.path.join(OUT_DIR, "e4b_mu20_eval.csv")
rows = []
if os.path.exists(OUT):
    with open(OUT) as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        for k in ("seed",):
            r[k] = int(r[k])
        for k in ("PL_flow", "BWL", "work", "vars"):
            r[k] = float(r[k])
done = {(r["scenario"], r["seed"]) for r in rows if r["method"].startswith("SA-mono")}
for scen in ["S2", "S1", "S3"]:
    N, Dtot = R.SCEN[scen]
    for seed in R.MAIN_SEEDS:
        if (scen, seed) in done:
            continue
        flows = R.L.gen_traffic(N, Dtot, seed); cc = R.cc_of(flows)
        fin, info = R.pod_solve(flows, seed, Dtot, cc, R.LAM, MU, "sqa", R.TUNED)
        m = R.metrics(flows, fin, Dtot)
        rows.append(dict(scenario=scen, seed=seed, method="MAS-QA-tuned-mu20", PL_flow=m["PL_flow"], BWL=m["BWL"], work=info["pod_work"], vars=info["pod_vars"]))
        raw, fin, info, _, _ = R.mono_solve(flows, seed, Dtot, cc, R.LAM, MU, "sqa", 10, 5000, R.TUNED)
        m = R.metrics(flows, fin, Dtot)
        rows.append(dict(scenario=scen, seed=seed, method="SQA-mono-tuned-5000-mu20", PL_flow=m["PL_flow"], BWL=m["BWL"], work=info["mono_work"], vars=info["mono_vars"]))
        raw, fin, info, _, _ = R.mono_solve(flows, seed, Dtot, cc, R.LAM, MU, "sa", 10, 80000, R.TUNED)
        m = R.metrics(flows, fin, Dtot)
        rows.append(dict(scenario=scen, seed=seed, method="SA-mono-tuned-80000-mu20", PL_flow=m["PL_flow"], BWL=m["BWL"], work=info["mono_work"], vars=info["mono_vars"]))
        with open(OUT, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["scenario", "seed", "method", "PL_flow", "BWL", "work", "vars"]); w.writeheader(); w.writerows(rows)
        print(scen, seed, "done", flush=True)
print("ALL DONE", flush=True)
