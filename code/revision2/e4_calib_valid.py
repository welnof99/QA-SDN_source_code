"""E4a: calibrate the admission bonus mu on VALIDATION seeds 100-104 (S2 workload), monolithic tuned SQA
and pod pipeline. Also records the energy comparison the reviewer asked for: energy of the raw solver sample
versus the all-rejected state, per seed."""
import os
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "revision2")
import csv, time
import r2lib as R
OUT = os.path.join(OUT_DIR, "e4a_mu_validation.csv")
N, Dtot = R.SCEN["S2"]
rows = []
for mu in [0.0, 5.0, 10.0, 20.0, 40.0, 80.0]:
    for seed in R.VALID_SEEDS:
        flows = R.L.gen_traffic(N, Dtot, seed); cc = R.cc_of(flows)
        raw, fin, info, qb, smp = R.mono_solve(flows, seed, Dtot, cc, R.LAM, mu, "sqa",
                                               R.TUNED["sqa_reads"], R.TUNED["sqa_sweeps"], R.TUNED)
        m = R.metrics(flows, fin, Dtot)
        e_sample = R.energy(qb, smp)
        e_empty = R.energy(qb, R.all_rejected_sample(qb, flows))
        n_adm_raw = sum(1 for f in flows if raw[f["id"]] is not None)
        rows.append(dict(mu=mu, seed=seed, PL_flow=m["PL_flow"], BWL=m["BWL"], PL_EF=m["PL_EF"],
                         energy_sample=e_sample, energy_all_rejected=e_empty,
                         sample_below_empty=int(e_sample < e_empty), admitted_raw=n_adm_raw))
    print("mu", mu, flush=True)
with open(OUT, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("written", OUT, flush=True)
