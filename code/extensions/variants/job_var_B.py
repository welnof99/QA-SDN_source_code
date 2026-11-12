from common_var import *
rows=[]; N, D = L.SCENARIOS['S2']
for seed in E.MAIN_SEEDS:
    flows = L.gen_traffic(N, D, seed)
    cc = {k: sum(f["demand"] for f in flows if f["cls"]==k) for k in ["EF","AF","BE"]}
    for cap_name, capset in [('homogeneous', lambda: L.set_homogeneous()), ('heterogeneous', lambda: L.set_hetero_core(25.0))]:
        for wname, wflag in [('demand-weighted H_bw', False), ('priority-weighted H_bw', True)]:
            capset(); L.BW_WEIGHTED = wflag
            set_sqa(0.5,1.0); set_budget(sqa_reads=10,sqa_sweeps=5000,trotter=16)
            raw, rep, ex = L.run_mono(flows, seed, D, cc, L.LAMBDA, method='sqa')
            rows.append(dict(seed=seed, capacity=cap_name, objective=wname, method='SQA-mono+coord', **E.metrics2(flows, rep, D)))
    L.set_homogeneous(); L.BW_WEIGHTED=False
    print('seed', seed, flush=True); pd.DataFrame(rows).to_csv('var_objective_S2.csv', index=False)
print('DONE', flush=True)
