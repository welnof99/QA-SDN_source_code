import os
# Priority constraint evaluation on k=4 S2. Usage: run_prio.py lam_p seeds_a seeds_b out.csv
import sys, time; sys.path.insert(0,'.'); sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
import numpy as np, pandas as pd, openjij as oj
import masqa_lib as L
from masqa_lib import LAMBDA
import prio as P
lam_p = float(sys.argv[1]); s0, s1 = int(sys.argv[2]), int(sys.argv[3]); out = sys.argv[4]
def solve(q, method, reads, sweeps, seed):
    if method == 'sqa':
        ss = oj.SQASampler().sample_qubo(q.Q, num_reads=reads, num_sweeps=sweeps, trotter=L.B['trotter'], beta=0.5, gamma=1.0, seed=seed)
    else:
        ss = oj.SASampler().sample_qubo(q.Q, num_reads=reads, num_sweeps=sweeps, beta_min=0.1, beta_max=10.0, seed=seed)
    return {int(a): int(b) for a, b in ss.first.sample.items()}
L.solve = solve
L.B.update(pod_reads=10, pod_sweeps=500, sqa_reads=10, sqa_sweeps=5000, trotter=16)
T = L.TOPO; N, D = L.SCENARIOS['S2']
rows = []
def cls_pl(flows, served):
    r = {}
    for c in ['EF','AF','BE']:
        fc=[f for f in flows if f['cls']==c]; r[f'PL_{c}']=100*sum(served[f['id']] is None for f in fc)/max(1,len(fc))
    return r
for seed in range(s0, s1):
    flows = L.gen_traffic(N, D, seed)
    cc = {c: sum(f['demand'] for f in flows if f['cls']==c) for c in ['EF','AF','BE']}
    # monolithic SQA with the priority penalty
    qb = P.build_qubo_prio(flows, T, np.zeros(len(T['links'])), D, cc, LAMBDA, lam_p)
    smp = solve(qb, 'sqa', L.B['sqa_reads'], L.B['sqa_sweeps'], seed); asg = L.decode(qb, smp, flows)
    for name, served in [('SQA-mono raw', L.loss_on_overload(flows, asg)), ('SQA-mono+repair', L.coordinate(asg, flows))]:
        r = dict(lam_p=lam_p, seed=seed, method=name, n_pairs=qb.n_prio_pairs, **L.metrics(flows, served, D), **cls_pl(flows, served))
        rows.append(r)
    # MAS pipeline with the penalty inside each pod
    assign = {}
    for q in range(4):
        sub = [f for f in flows if f['pod']==q]
        if not sub: continue
        qb2 = P.build_qubo_prio(sub, T, np.zeros(len(T['links'])), D, cc, LAMBDA, lam_p)
        s2 = solve(qb2, 'sqa', L.B['pod_reads'], L.B['pod_sweeps'], seed*10+q)
        assign.update(L.decode(qb2, s2, sub))
    fin = L.coordinate(assign, flows)
    rows.append(dict(lam_p=lam_p, seed=seed, method='MAS-QA', n_pairs=-1, **L.metrics(flows, fin, D), **cls_pl(flows, fin)))
    pd.DataFrame(rows).to_csv(out, index=False); print('seed', seed, 'done', flush=True)
print('DONE', flush=True)
