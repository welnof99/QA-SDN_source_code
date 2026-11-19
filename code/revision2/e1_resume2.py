"""E1 (resumable per seed): equal-work with tuned settings, S2 then S3, seeds 42-71."""
import os
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "revision2")
import csv, os
import r2lib as R
OUT = os.path.join(OUT_DIR, "e1_equalwork_tuned_S23.csv")
FIELDS = ["scenario","seed","method","sweeps","work","PL_flow","BWL","PL_EF","PL_AF","PL_BE","total_s"]
rows = []
if os.path.exists(OUT):
    rows = list(csv.DictReader(open(OUT)))
done = {(r["scenario"], int(r["seed"])) for r in rows if r["method"] == "SQA-mono-tuned-equal-work"}
for scen in ["S2", "S3"]:
    N, Dtot = R.SCEN[scen]
    for seed in R.MAIN_SEEDS:
        if (scen, seed) in done:
            continue
        flows = R.L.gen_traffic(N, Dtot, seed); cc = R.cc_of(flows)
        fin, info = R.pod_solve(flows, seed, Dtot, cc, R.LAM, 0, "sqa", R.TUNED)
        m = R.metrics(flows, fin, Dtot)
        rows.append(dict(scenario=scen, seed=seed, method="MAS-QA-tuned", sweeps=R.TUNED["pod_sweeps"], work=info["pod_work"], PL_flow=m["PL_flow"], BWL=m["BWL"], PL_EF=m["PL_EF"], PL_AF=m["PL_AF"], PL_BE=m["PL_BE"], total_s=info["total_s"]))
        raw, fin2, i2, _, _ = R.mono_solve(flows, seed, Dtot, cc, R.LAM, 0, "sqa", R.TUNED["sqa_reads"], R.TUNED["sqa_sweeps"], R.TUNED)
        m2 = R.metrics(flows, fin2, Dtot)
        rows.append(dict(scenario=scen, seed=seed, method="SQA-mono-tuned-5000", sweeps=R.TUNED["sqa_sweeps"], work=i2["mono_work"], PL_flow=m2["PL_flow"], BWL=m2["BWL"], PL_EF=m2["PL_EF"], PL_AF=m2["PL_AF"], PL_BE=m2["PL_BE"], total_s=i2["total_s"]))
        nv = i2["mono_vars"]
        sw = max(1, round(info["pod_work"] / (nv * R.P * R.TUNED["sqa_reads"])))
        raw3, fin3, i3, _, _ = R.mono_solve(flows, seed, Dtot, cc, R.LAM, 0, "sqa", R.TUNED["sqa_reads"], sw, R.TUNED)
        m3 = R.metrics(flows, fin3, Dtot)
        rows.append(dict(scenario=scen, seed=seed, method="SQA-mono-tuned-equal-work", sweeps=sw, work=i3["mono_work"], PL_flow=m3["PL_flow"], BWL=m3["BWL"], PL_EF=m3["PL_EF"], PL_AF=m3["PL_AF"], PL_BE=m3["PL_BE"], total_s=i3["total_s"]))
        with open(OUT, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
        print(scen, seed, "done", flush=True)
print("ALL DONE", flush=True)
