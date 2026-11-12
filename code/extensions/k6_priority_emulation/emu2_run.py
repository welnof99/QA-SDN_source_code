import os
# Kernel-forwarding emulation of methods' served sets (k=4, S2). Usage: emu2_run.py seed_a seed_b out.csv
import sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
import numpy as np, pandas as pd, openjij as oj
import fattree_k as F, masqa_lib as L, emu2
from mininet.log import setLogLevel; setLogLevel('error')
SCALE = 0.1; DUR = 10
s0, s1, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
L.B.update(pod_reads=10, pod_sweeps=500, trotter=16)
def solve(q, method, reads, sweeps, seed):
    if method == 'sqa':
        ss = oj.SQASampler().sample_qubo(q.Q, num_reads=reads, num_sweeps=sweeps, trotter=L.B['trotter'], beta=0.5, gamma=1.0, seed=seed)
    else:
        ss = oj.SASampler().sample_qubo(q.Q, num_reads=reads, num_sweeps=sweeps, beta_min=0.1, beta_max=10.0, seed=seed)
    return {int(a): int(b) for a, b in ss.first.sample.items()}
L.solve = solve
T = F.build_fat_tree_k(4); L.TOPO = T
N, D = L.SCENARIOS['S2']
rows = []
for seed in range(s0, s1):
    flows = F.gen_traffic_k(T, N, D, seed)
    cc = {c: sum(f['demand'] for f in flows if f['cls']==c) for c in ['EF','AF','BE']}
    rng = np.random.default_rng(seed + 7)
    hash_assign = {f['id']: int(rng.integers(len(f['paths']))) for f in flows}
    adm = L.ecmp_admission(flows, seed)
    greedy = L.coordinate({}, flows)
    _, mas, _ = F.run_mas_k(T, flows, seed, D, cc, L.LAMBDA, 'sqa')
    methods = {'ECMP-hash': (hash_assign, set(range(N))),
               'ECMP+adm': (adm, {i for i, p in adm.items() if p is not None}),
               'Greedy-only': (greedy, {i for i, p in greedy.items() if p is not None}),
               'MAS-QA': (mas, {i for i, p in mas.items() if p is not None})}
    for m, (asg, sel) in methods.items():
        e = emu2.Emu(T, SCALE)
        addr = e.install(flows, asg, sel)
        res = e.run(flows, addr, SCALE, DUR)
        e.stop()
        offered = sum(flows[i]['demand'] for i in sel) * SCALE * 1e6
        delivered = sum(0 if np.isnan(res[i]['bps']) else res[i]['bps'] for i in sel)
        losses = [res[i]['lost_pct'] for i in sel if not np.isnan(res[i]['lost_pct'])]
        rows.append(dict(seed=seed, method=m, n_sent=len(sel), n_loss_gt1pct=sum(l > 1.0 for l in losses),
                         mean_loss_pct=float(np.mean(losses)) if losses else float('nan'),
                         delivered_frac=delivered / offered if offered else float('nan'),
                         n_nan=sum(np.isnan(res[i]['lost_pct']) for i in sel)))
        print(seed, m, rows[-1], flush=True)
        pd.DataFrame(rows).to_csv(out, index=False)
print('DONE', flush=True)
