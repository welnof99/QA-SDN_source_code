# Topology-validity runs: Fat-Tree(k) with intensity-matched traffic. Usage: run_k.py k N D seeds_a seeds_b methods out.csv
import sys, time, json; sys.path.insert(0,'.')
import numpy as np, pandas as pd, openjij as oj
import fattree_k as F
import masqa_lib as L
from masqa_lib import LAMBDA
k, N, D = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
s0, s1 = int(sys.argv[4]), int(sys.argv[5]); methods = sys.argv[6].split(','); out = sys.argv[7]
# tuned SQA: beta=0.5, gamma=1.0 (manuscript); SA tuned schedule beta in [0.1, 10]
ORIG = L.solve
def solve(q, method, reads, sweeps, seed):
    if method == 'sqa':
        ss = oj.SQASampler().sample_qubo(q.Q, num_reads=reads, num_sweeps=sweeps, trotter=L.B['trotter'], beta=0.5, gamma=1.0, seed=seed)
    else:
        ss = oj.SASampler().sample_qubo(q.Q, num_reads=reads, num_sweeps=sweeps, beta_min=0.1, beta_max=10.0, seed=seed)
    return {int(a): int(b) for a, b in ss.first.sample.items()}
L.solve = solve
T = F.build_fat_tree_k(k); L.TOPO = T
rows = []
for seed in range(s0, s1):
    flows = F.gen_traffic_k(T, N, D, seed)
    cc = {c: sum(f['demand'] for f in flows if f['cls']==c) for c in ['EF','AF','BE']}
    def add(m, served, extra=None, t=0.0):
        r = dict(k=k, N=N, D=D, seed=seed, method=m, wall_s=t, **L.metrics(flows, served, D))
        for c in ['EF','AF','BE']:
            fc=[f for f in flows if f['cls']==c]; r[f'PL_{c}']=100*sum(served[f['id']] is None for f in fc)/max(1,len(fc))
        if extra: r.update(extra)
        rows.append(r); print(k, seed, f'{m:24s}', round(r['PL_flow'],2), round(r['wall_s'],1), flush=True)
        pd.DataFrame(rows).to_csv(out, index=False)
    for m in methods:
        t0 = time.perf_counter()
        if m == 'ECMP-hash': add(m, L.ecmp_hash(flows, seed), t=time.perf_counter()-t0)
        elif m == 'ECMP+adm': add(m, L.ecmp_admission(flows, seed), t=time.perf_counter()-t0)
        elif m == 'Greedy-only': add(m, L.coordinate({}, flows), t=time.perf_counter()-t0)
        elif m in ('MAS-QA','MAS-decomp-only'):
            L.B.update(pod_reads=10, pod_sweeps=500, trotter=16)
            asg, fin, ex = F.run_mas_k(T, flows, seed, D, cc, LAMBDA, 'sqa')
            add('MAS-QA' if m=='MAS-QA' else m, fin if m=='MAS-QA' else L.loss_on_overload(flows, asg), ex, time.perf_counter()-t0)
        elif m in ('SQA-mono','SA-mono'):
            meth = 'sqa' if m=='SQA-mono' else 'sa'
            L.B.update(sqa_reads=10, sqa_sweeps=5000, sa_reads=10, sa_sweeps=80000, trotter=16)
            qb = L.build_qubo(flows, T, np.zeros(len(T['links'])), D, cc, LAMBDA)
            reads, sweeps = (10,5000) if meth=='sqa' else (10,80000)
            smp = solve(qb, meth, reads, sweeps, seed); asg = L.decode(qb, smp, flows)
            add(m+' raw', L.loss_on_overload(flows, asg), t=time.perf_counter()-t0)
            add(m+'+repair', L.coordinate(asg, flows), t=time.perf_counter()-t0)
print('DONE', flush=True)
