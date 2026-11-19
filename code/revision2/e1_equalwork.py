"""E1: equal-work comparison with TUNED settings (S1-S3, seeds 42-71).
MAS-QA pods (SQA, tuned) vs monolithic SQA at full budget (10x5000, tuned) vs monolithic SQA with the
sweep count chosen so that total spin-update work equals the four pod solves (P included)."""
import os
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "revision2")
import csv, sys, time
import r2lib as R
OUT = os.path.join(OUT_DIR, "e1_equalwork_tuned.csv")
rows = []
t_start = time.time()
for scen, (N, Dtot) in R.SCEN.items():
    for seed in R.MAIN_SEEDS:
        flows = R.L.gen_traffic(N, Dtot, seed); cc = R.cc_of(flows)
        fin, info = R.pod_solve(flows, seed, Dtot, cc, R.LAM, 0, "sqa", R.TUNED)
        m = R.metrics(flows, fin, Dtot)
        rows.append(dict(scenario=scen, seed=seed, method="MAS-QA-tuned", sweeps=R.TUNED["pod_sweeps"],
                         work=info["pod_work"], PL_flow=m["PL_flow"], BWL=m["BWL"], PL_EF=m["PL_EF"], PL_AF=m["PL_AF"],
                         PL_BE=m["PL_BE"], total_s=info["total_s"]))
        # monolithic SQA, full tuned budget
        raw, fin2, i2, _, _ = R.mono_solve(flows, seed, Dtot, cc, R.LAM, 0, "sqa",
                                           R.TUNED["sqa_reads"], R.TUNED["sqa_sweeps"], R.TUNED)
        m2 = R.metrics(flows, fin2, Dtot)
        rows.append(dict(scenario=scen, seed=seed, method="SQA-mono-tuned-5000", sweeps=R.TUNED["sqa_sweeps"],
                         work=i2["mono_work"], PL_flow=m2["PL_flow"], BWL=m2["BWL"], PL_EF=m2["PL_EF"], PL_AF=m2["PL_AF"],
                         PL_BE=m2["PL_BE"], total_s=i2["total_s"]))
        # monolithic SQA with equal total work (P included): sweeps = pod_work / (nv * P * reads)
        nv = i2["mono_vars"]
        sweeps_eq = max(1, round(info["pod_work"] / (nv * R.P * R.TUNED["sqa_reads"])))
        raw3, fin3, i3, _, _ = R.mono_solve(flows, seed, Dtot, cc, R.LAM, 0, "sqa",
                                            R.TUNED["sqa_reads"], sweeps_eq, R.TUNED)
        m3 = R.metrics(flows, fin3, Dtot)
        rows.append(dict(scenario=scen, seed=seed, method="SQA-mono-tuned-equal-work", sweeps=sweeps_eq,
                         work=i3["mono_work"], PL_flow=m3["PL_flow"], BWL=m3["BWL"], PL_EF=m3["PL_EF"], PL_AF=m3["PL_AF"],
                         PL_BE=m3["PL_BE"], total_s=i3["total_s"]))
    print("done", scen, round(time.time() - t_start), flush=True)
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("written", OUT, len(rows), flush=True)
