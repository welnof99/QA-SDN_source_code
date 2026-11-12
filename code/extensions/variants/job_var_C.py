from common_var import *
rows=[]; N, D = L.SCENARIOS['S2']
L.set_homogeneous(); L.BW_WEIGHTED=True
for seed in E.MAIN_SEEDS:
    flows = L.gen_traffic(N, D, seed)
    cc = {k: sum(f["demand"] for f in flows if f["cls"]==k) for k in ["EF","AF","BE"]}
    for lb in [2.0, 10.0, 20.0]:
        lam = dict(L.LAMBDA); lam['b']=lb
        set_sqa(0.5,1.0); set_budget(sqa_reads=10,sqa_sweeps=5000,trotter=16)
        raw, rep, ex = L.run_mono(flows, seed, D, cc, lam, method='sqa')
        rows.append(dict(seed=seed, lambda_b=lb, method='SQA-mono+coord (priority-weighted H_bw)', **E.metrics2(flows, rep, D)))
    print('seed', seed, flush=True); pd.DataFrame(rows).to_csv('var_lambdab_S2.csv', index=False)
L.BW_WEIGHTED=False
print('DONE', flush=True)
