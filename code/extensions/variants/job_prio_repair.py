import sys
from common import *
scen = sys.argv[1]
def coordinate_prio(assign, flows):
    cap = L.LINK_CAP
    order_asc = sorted(flows, key=lambda f: (f['w'], f['demand']), reverse=False)
    order_desc = sorted(flows, key=lambda f: (-f['w'], -f['demand']))
    load = {}
    for f in flows:
        p = assign.get(f['id'])
        if p is None: continue
        for l in f['paths'][p]: load[l]=load.get(l,0.0)+f['demand']
    final = {f['id']: assign.get(f['id']) for f in flows}
    for f in order_asc:           # lowest priority first
        p = final[f['id']]
        if p is None: continue
        if any(load.get(l,0.0) > cap+1e-9 for l in f['paths'][p]):
            for l in f['paths'][p]: load[l]-=f['demand']
            final[f['id']] = None
    for f in order_desc:          # greedy refill of all rejected flows, priority order
        if final[f['id']] is None:
            for p2 in range(len(f['paths'])):
                if all(load.get(l,0.0)+f['demand']<=cap+1e-9 for l in f['paths'][p2]):
                    for l in f['paths'][p2]: load[l]=load.get(l,0.0)+f['demand']
                    final[f['id']]=p2; break
    return final
N, D = L.SCENARIOS[scen]
rows=[]
for seed in E.MAIN_SEEDS:
    flows = L.gen_traffic(N, D, seed)
    cc = {k: sum(f["demand"] for f in flows if f["cls"]==k) for k in ["EF","AF","BE"]}
    set_sqa(0.5,1.0); set_budget(sqa_reads=10,sqa_sweeps=5000,trotter=16)
    qb = L.build_qubo(flows, L.TOPO, np.zeros(96), D, cc, L.LAMBDA)
    s = L.solve(qb,'sqa',10,5000,seed)
    assign = L.decode(qb, s, flows)
    rows.append(dict(scenario=scen, seed=seed, method='SQA-mono + current coordinator', **E.metrics2(flows, L.coordinate(assign, flows), D)))
    rows.append(dict(scenario=scen, seed=seed, method='SQA-mono + priority-first repair', **E.metrics2(flows, coordinate_prio(assign, flows), D)))
    print('seed', seed, flush=True)
    pd.DataFrame(rows).to_csv(f'prio_repair_{scen}.csv', index=False)
print('DONE', flush=True)
