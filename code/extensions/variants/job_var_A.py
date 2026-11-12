from common_var import *
rows=[]; N, D = L.SCENARIOS['S2']
L.set_hetero_core(25.0); L.BW_WEIGHTED=False
for seed in E.MAIN_SEEDS:
    flows = L.gen_traffic(N, D, seed)
    cc = {k: sum(f["demand"] for f in flows if f["cls"]==k) for k in ["EF","AF","BE"]}
    rows.append(dict(seed=seed, method='ECMP+adm', **E.metrics2(flows, L.ecmp_admission(flows, seed), D)))
    rows.append(dict(seed=seed, method='Greedy-only', **E.metrics2(flows, L.coordinate({}, flows), D)))
    rows.append(dict(seed=seed, method='Least-loaded greedy', **E.metrics2(flows, L.least_loaded(flows), D)))
    set_sqa(0.5,1.0); set_budget(sqa_reads=10,sqa_sweeps=5000,trotter=16,pod_reads=10,pod_sweeps=500)
    raw, rep, ex = L.run_mono(flows, seed, D, cc, L.LAMBDA, method='sqa')
    rows.append(dict(seed=seed, method='SQA-mono+coord', **E.metrics2(flows, rep, D)))
    _, fin, _ = E.run_mas2(flows, seed, D, cc, L.LAMBDA, "sqa")
    rows.append(dict(seed=seed, method='MAS-QA pipeline', **E.metrics2(flows, fin, D)))
    set_sa_tuned(0.1,10.0); set_budget(sa_reads=10,sa_sweeps=80000)
    raw, rep, ex = L.run_mono(flows, seed, D, cc, L.LAMBDA, method='sa')
    rows.append(dict(seed=seed, method='SA-mono+coord (tuned)', **E.metrics2(flows, rep, D)))
    print('seed', seed, flush=True); pd.DataFrame(rows).to_csv('var_hetero_S2.csv', index=False)
print('DONE', flush=True)
