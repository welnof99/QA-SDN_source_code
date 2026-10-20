"""Exact reference on small instances (Section 3.9, 4.6): MILP optimum (HiGHS via SciPy) and heuristics.
Total demand: D_tot = r * 12.8 * N Mbps. Writes data/small_v2_all.csv. Runtime: about 20 minutes on 2 cores.
Run from the repository root:  python code/small_instances.py
"""
import os, sys
ROOT = os.environ.get("MASQA_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "code"))
import numpy as np, pandas as pd, openjij as oj
import masqa_lib as L
from exp import metrics2, LAM_PAPER, milp_optimum, run_mas2

def main(out_csv=os.path.join(ROOT, "data", "small_v2_all.csv")):
    rows = []
    for N in [8, 12]:
        for r in [0.8, 1.6]:
            Dtot = r * 12.8 * N
            for seed in range(42, 62):
                f = L.gen_traffic(N, Dtot, seed)
                cc = {k: sum(x["demand"] for x in f if x["cls"] == k) for k in ["EF", "AF", "BE"]}
                mo = {"OPT-count": milp_optimum(f, "count"), "OPT-bw": milp_optimum(f, "bw")}
                _, mas, _ = run_mas2(f, seed, Dtot, cc, LAM_PAPER, "sqa"); mo["MAS-QA"] = mas
                mo["Greedy-only"] = L.coordinate({}, f)
                mo["ECMP+adm"] = L.ecmp_admission(f, seed)
                qm = L.build_qubo(f, L.TOPO, np.zeros(96), Dtot, cc, LAM_PAPER)
                s1 = oj.SQASampler().sample_qubo(qm.Q, num_reads=10, num_sweeps=5000, trotter=16, beta=0.5, gamma=1.0, seed=seed)
                s2 = oj.SASampler().sample_qubo(qm.Q, num_reads=10, num_sweeps=80000, seed=seed, beta_min=0.1, beta_max=10.0)
                mo["SQA-mono-v2+repair"] = L.coordinate(L.decode(qm, {int(k): int(v) for k, v in s1.first.sample.items()}, f), f)
                mo["SA-mono-mt+repair"] = L.coordinate(L.decode(qm, {int(k): int(v) for k, v in s2.first.sample.items()}, f), f)
                for name, asg in mo.items():
                    m = metrics2(f, asg, Dtot)
                    rows.append(dict(N=N, ratio=r, seed=seed, method=name, PL_flow=m["PL_flow"], BWL=m["BWL"]))
            print("done N", N, "r", r, flush=True)
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print("written", out_csv)

if __name__ == "__main__":
    main()
