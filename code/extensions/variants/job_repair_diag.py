from common import *
rows=[]
N, D = L.SCENARIOS['S2']
for seed in E.MAIN_SEEDS:
    flows = L.gen_traffic(N, D, seed)
    cc = {k: sum(f["demand"] for f in flows if f["cls"]==k) for k in ["EF","AF","BE"]}
    set_sqa(0.5,1.0); set_budget(sqa_reads=10,sqa_sweeps=5000,trotter=16)
    qb = L.build_qubo(flows, L.TOPO, np.zeros(96), D, cc, L.LAMBDA)
    s = L.solve(qb, 'sqa', 10, 5000, seed)
    assign = L.decode(qb, s, flows)
    fmap = {f['id']: f for f in flows}
    order = sorted(flows, key=lambda f: (-f['w'], -f['demand']))
    # load from all solver-admitted flows (as in coordinate pass 1)
    load = {}
    for f in order:
        p = assign.get(f['id'])
        if p is None: continue
        for l in f['paths'][p]: load[l] = load.get(l,0.0)+f['demand']
    cap = L.LINK_CAP
    # arc load from flows with priority >= f (incl. f) for overload attribution
    for cls in ['EF','AF','BE']:
        rows.append(dict(seed=seed, cls=cls, solver_admitted=sum(1 for f in flows if f['cls']==cls and assign.get(f['id']) is not None)))
    removed = {'EF':0,'AF':0,'BE':0}; avoidable = {'EF':0,'AF':0,'BE':0}
    cur = dict(load)
    final = {f['id']: assign.get(f['id']) for f in flows}
    for f in order:
        p = final.get(f['id'])
        if p is None: continue
        if any(cur.get(l,0.0) > cap+1e-9 for l in f['paths'][p]):
            # attribution: load from flows with w >= w_f only
            hp = {}
            for g in flows:
                if g['w'] >= f['w'] and assign.get(g['id']) is not None and g['id'] in final and final[g['id']] is not None or (g['w']>=f['w'] and assign.get(g['id']) is not None and g is f):
                    gp = assign.get(g['id'])
                    if gp is None: continue
                    for l in g['paths'][gp]: hp[l] = hp.get(l,0.0)+g['demand']
            if max(hp.get(l,0.0) for l in f['paths'][p]) <= cap+1e-9:
                avoidable[f['cls']] += 1
            removed[f['cls']] += 1
            for l in f['paths'][p]: cur[l] -= f['demand']
            alt=None
            for p2 in range(len(f['paths'])):
                if p2!=p and all(cur.get(l,0.0)+f['demand']<=cap+1e-9 for l in f['paths'][p2]): alt=p2; break
            final[f['id']] = alt
            if alt is not None:
                for l in f['paths'][alt]: cur[l]=cur.get(l,0.0)+f['demand']
    for cls in ['EF','AF','BE']:
        rows.append(dict(seed=seed, cls=cls, pass1_removed=removed[cls], removed_caused_only_by_lower=avoidable[cls]))
    print('seed', seed, removed, avoidable, flush=True)
    pd.DataFrame(rows).to_csv('repair_diag_S2.csv', index=False)
print('DONE', flush=True)
