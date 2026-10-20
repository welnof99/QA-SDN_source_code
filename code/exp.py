"""Experiments mapped to reviewer comments. Usage: python3 exp.py <part> [args]
parts: tune | main <scenarios comma> | opt | scale | timing | stats"""
import sys, json, time, math
import numpy as np, pandas as pd
from scipy import stats
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import lil_matrix
import masqa_lib as L

OUT = "results"
import os; os.makedirs(OUT, exist_ok=True)
MAIN_SEEDS = list(range(42, 72))          # n = 30 (reviewer: n≥30 for power)

# ---------- helpers ----------
def metrics2(flows, served, Dtot):
    m = L.metrics(flows, served, Dtot)
    srv = [f for f in flows if served[f["id"]] is not None]
    lat = [f["pdelay"][served[f["id"]]] for f in srv]
    m["latency_p95_ms"] = float(np.percentile(lat, 95)) if lat else float("nan")   # tail latency
    for k in ["EF", "AF", "BE"]:                                                    # class-specific loss
        fk = [f for f in flows if f["cls"] == k]
        m[f"PL_{k}"] = 100.0 * sum(served[f["id"]] is None for f in fk) / max(1, len(fk))
    return m

def run_mas2(flows, seed, Dtot, cc, lam, method="sqa"):
    """Pods (parallel-ready) then coordinator. Returns pod-level assignment, final assignment, timing and work."""
    pod_assign, pod_times, nvars, work = {}, [], [], 0.0
    for q in range(4):
        sub = [f for f in flows if f["pod"] == q]
        if not sub: continue
        t0 = time.perf_counter()
        qb = L.build_qubo(sub, L.TOPO, np.zeros(len(L.TOPO["links"])), Dtot, cc, lam)
        smp = L.solve(qb, method, L.B["pod_reads"], L.B["pod_sweeps"], seed * 10 + q)
        pod_assign.update(L.decode(qb, smp, sub))
        pod_times.append(time.perf_counter() - t0)
        nvars.append(len(qb.idx)); work += len(qb.idx) * L.B["pod_sweeps"] * L.B["pod_reads"]
    t1 = time.perf_counter()
    final = L.coordinate(pod_assign, flows)
    return pod_assign, final, dict(pod_parallel_s=max(pod_times), pod_sequential_s=sum(pod_times),
                                   coord_s=time.perf_counter() - t1, pod_vars=sum(nvars), pod_work=work)

def run_mono_matched(flows, seed, Dtot, cc, lam, pod_work):
    """Monolithic SQA with sweeps chosen so that nvars * sweeps * reads == total pod work (equal annealing work)."""
    qb = L.build_qubo(flows, L.TOPO, np.zeros(len(L.TOPO["links"])), Dtot, cc, lam)
    nv = len(qb.idx)
    sweeps = max(1, int(round(pod_work / (nv * L.B["sqa_reads"]))))
    t0 = time.perf_counter()
    smp = L.solve(qb, "sqa", L.B["sqa_reads"], sweeps, seed)
    assign = L.decode(qb, smp, flows)
    return L.loss_on_overload(flows, assign), L.coordinate(assign, flows), dict(mono_vars=nv, matched_sweeps=sweeps,
                                                                              solve_s=time.perf_counter() - t0)

def load_tuned():
    p = os.path.join(OUT, "tuned_lambda.json")
    return json.load(open(p))["lam"] if os.path.exists(p) else None

LAM_PAPER = dict(L.LAMBDA)

# ---------- part: validation tuning (reviewer: tune on separate validation workload) ----------
def part_tune():
    rows = []
    for name, lam in L.LAMBDA_GRID.items():
        for seed in L.VALID_SEEDS:
            N, Dtot = L.SCENARIOS["S2"]
            flows = L.gen_traffic(N, Dtot, seed)
            cc = {k: sum(f["demand"] for f in flows if f["cls"] == k) for k in ["EF", "AF", "BE"]}
            _, final, _ = run_mas2(flows, seed, Dtot, cc, lam)
            m = metrics2(flows, final, Dtot); m.update(config=name, seed=seed, lam=json.dumps(lam))
            rows.append(m); print("tune", name, seed, round(m["PL_flow"], 2), flush=True)
    df = pd.DataFrame(rows); df.to_csv(f"{OUT}/tune_validation.csv", index=False)
    agg = df.groupby(["config", "lam"])[["PL_flow", "JFI"]].mean().reset_index().sort_values(["PL_flow", "JFI"], ascending=[True, False])
    best = agg.iloc[0]
    json.dump({"config": best.config, "lam": json.loads(best.lam)}, open(f"{OUT}/tuned_lambda.json", "w"), indent=2)
    print(agg.to_string(), flush=True)

# ---------- part: main experiment (n = 30; reviewer 1: n≥30; reviewer 2: common policy, decomposition-only, coordinator-only, matched budget) ----------
def part_main(scen_list):
    tuned = load_tuned()
    path = f"{OUT}/main_{'_'.join(scen_list)}.csv"
    rows = []
    for scen in scen_list:
        N, Dtot = L.SCENARIOS[scen]
        for seed in MAIN_SEEDS:
            flows = L.gen_traffic(N, Dtot, seed)
            cc = {k: sum(f["demand"] for f in flows if f["cls"] == k) for k in ["EF", "AF", "BE"]}
            def add(method, served, extra=None):
                t = {} if extra is None else extra
                r = dict(scenario=scen, seed=seed, method=method, **metrics2(flows, served, Dtot), **t)
                rows.append(r); print(scen, seed, f"{method:20s}", round(r["PL_flow"], 2), flush=True)
            add("ECMP-hash", L.ecmp_hash(flows, seed))
            add("ECMP+adm", L.ecmp_admission(flows, seed))
            pod_assign, final, ex = run_mas2(flows, seed, Dtot, cc, LAM_PAPER, "sqa")
            add("MAS-QA", final, ex)
            add("MAS-decomp-only", L.loss_on_overload(flows, pod_assign), ex)     # decomposition, no coordinator
            add("Greedy-only", L.coordinate({}, flows))                           # coordinator alone, no QUBO
            _, final_sa, ex_sa = run_mas2(flows, seed, Dtot, cc, LAM_PAPER, "sa")
            add("MAS+SA", final_sa, ex_sa)                                       # same decomposition + coordinator, SA pods
            if tuned is not None:
                _, final_t, ex_t = run_mas2(flows, seed, Dtot, cc, tuned, "sqa")
                add("MAS-QA-tuned", final_t, ex_t)
            for meth in ["sa", "sqa"]:
                qb = L.build_qubo(flows, L.TOPO, np.zeros(len(L.TOPO["links"])), Dtot, cc, LAM_PAPER)
                reads, sweeps = (L.B["sa_reads"], L.B["sa_sweeps"]) if meth == "sa" else (L.B["sqa_reads"], L.B["sqa_sweeps"])
                t0 = time.perf_counter(); smp = L.solve(qb, meth, reads, sweeps, seed)
                asg = L.decode(qb, smp, flows); el = time.perf_counter() - t0
                name = "SA-mono" if meth == "sa" else "SQA-mono"
                add(name + " raw", L.loss_on_overload(flows, asg), dict(solve_s=el))
                add(name + "+repair", L.coordinate(asg, flows), dict(solve_s=el))
            mraw, mrep, exm = run_mono_matched(flows, seed, Dtot, cc, LAM_PAPER, ex["pod_work"])
            add("SQA-mono-matched raw", mraw, exm)
            add("SQA-mono-matched+repair", mrep, exm)
            pd.DataFrame(rows).to_csv(path, index=False)   # incremental save
    print("saved", path, flush=True)

# ---------- part: exact optimum on small instances (reviewer 1: near-optimality needs an exact reference) ----------
def milp_optimum(flows, objective):
    """objective='count' maximizes admitted flows; 'bw' maximizes admitted demand. Capacity per directed arc."""
    cols = [(f["id"], p) for f in flows for p in range(len(f["paths"]))]
    nL = len(L.TOPO["links"])
    c = np.array([-1.0 if objective == "count" else -flows[f]["demand"] for f, _ in cols])
    A_rows = []; lb = []; ub = []
    fidx = {f["id"]: f for f in flows}
    # one-of per flow
    for f in flows:
        row = {}
        for j, (fid, p) in enumerate(cols):
            if fid == f["id"]: row[j] = 1.0
        A_rows.append(row); lb.append(0.0); ub.append(1.0)
    # capacity per arc
    arc_rows = {l: {} for l in range(nL)}
    for j, (fid, p) in enumerate(cols):
        for l in fidx[fid]["paths"][p]:
            arc_rows[l][j] = fidx[fid]["demand"]
    for l in range(nL):
        if arc_rows[l]:
            A_rows.append(arc_rows[l]); lb.append(0.0); ub.append(L.LINK_CAP)
    A = lil_matrix((len(A_rows), len(cols)))
    for i, row in enumerate(A_rows):
        for j, v in row.items(): A[i, j] = v
    res = milp(c=c, constraints=LinearConstraint(A.tocsr(), lb, ub), integrality=np.ones(len(cols)),
               bounds=Bounds(0, 1), options=dict(time_limit=120))
    assert res.success, res.message
    x = np.round(res.x).astype(int)
    adm = {f["id"]: None for f in flows}
    for j, (fid, p) in enumerate(cols):
        if x[j] == 1: adm[fid] = p
    return adm

def part_opt():
    rows = []
    for N in [8, 12]:
        for r in [0.8, 1.6]:
            Dtot = r * 800.0 * N / 100.0 if False else r * 800.0 * (N / 100.0) * 2.0   # demand scaled to N (see notebook note)
            for seed in range(42, 62):
                flows = L.gen_traffic(N, Dtot, seed)
                cc = {k: sum(f["demand"] for f in flows if f["cls"] == k) for k in ["EF", "AF", "BE"]}
                opt_c = milp_optimum(flows, "count"); opt_b = milp_optimum(flows, "bw")
                mo = {"OPT-count": opt_c, "OPT-bw": opt_b}
                _, mas, _ = run_mas2(flows, seed, Dtot, cc, LAM_PAPER, "sqa"); mo["MAS-QA"] = mas
                mo["Greedy-only"] = L.coordinate({}, flows)
                mo["ECMP+adm"] = L.ecmp_admission(flows, seed)
                for name, asg in mo.items():
                    m = metrics2(flows, asg, Dtot)
                    rows.append(dict(N=N, ratio=r, seed=seed, method=name, PL_flow=m["PL_flow"], BWL=m["BWL"]))
                print("opt", N, r, seed, flush=True)
    df = pd.DataFrame(rows); df.to_csv(f"{OUT}/optimum_small.csv", index=False)
    print(df.groupby(["N", "ratio", "method"])[["PL_flow", "BWL"]].mean().round(2).to_string(), flush=True)

# ---------- part: scalability in number of flows (reviewer 2: scale, runtime) ----------
def part_scale():
    rows = []
    for N in [50, 100, 200, 300]:
        Dtot = 1.6 * 800.0
        for seed in range(42, 47):
            flows = L.gen_traffic(N, Dtot, seed)
            cc = {k: sum(f["demand"] for f in flows if f["cls"] == k) for k in ["EF", "AF", "BE"]}
            _, final, ex = run_mas2(flows, seed, Dtot, cc, LAM_PAPER, "sqa")
            rows.append(dict(N=N, seed=seed, method="MAS-QA", **metrics2(flows, final, Dtot), **ex))
            rows.append(dict(N=N, seed=seed, method="Greedy-only", **metrics2(flows, L.coordinate({}, flows), Dtot)))
            rows.append(dict(N=N, seed=seed, method="ECMP+adm", **metrics2(flows, L.ecmp_admission(flows, seed), Dtot)))
            print("scale", N, seed, flush=True)
    pd.DataFrame(rows).to_csv(f"{OUT}/scale.csv", index=False)

# ---------- part: measured pod concurrency (reviewer 1: report measured concurrency, not inferred) ----------
_FLOWS_G = None
def _pod_job(args):
    q, seed, Dtot, cc = args
    sub = [f for f in _FLOWS_G if f["pod"] == q]
    t0 = time.perf_counter()
    qb = L.build_qubo(sub, L.TOPO, np.zeros(len(L.TOPO["links"])), Dtot, cc, LAM_PAPER)
    L.solve(qb, "sqa", L.B["pod_reads"], L.B["pod_sweeps"], seed * 10 + q)
    return time.perf_counter() - t0, t0, time.perf_counter()
def part_timing():
    import multiprocessing as mp
    global _FLOWS_G
    rows = []
    for seed in [42, 43, 44]:
        N, Dtot = L.SCENARIOS["S2"]
        _FLOWS_G = L.gen_traffic(N, Dtot, seed)
        cc = {k: sum(f["demand"] for f in _FLOWS_G if f["cls"] == k) for k in ["EF", "AF", "BE"]}
        jobs = [(q, seed, Dtot, cc) for q in range(4)]
        t0 = time.perf_counter(); seq = [_pod_job(j) for j in jobs]; seq_wall = time.perf_counter() - t0
        with mp.get_context("fork").Pool(2) as pool:
            t0 = time.perf_counter(); par = pool.map(_pod_job, jobs); par_wall = time.perf_counter() - t0
        rows.append(dict(seed=seed, sequential_wall_s=seq_wall, parallel_wall_s=par_wall,
                         sum_pod_s=sum(s[0] for s in seq), max_pod_s=max(s[0] for s in seq),
                         cores=os.cpu_count(), workers=2))
        print(rows[-1], flush=True)
    pd.DataFrame(rows).to_csv(f"{OUT}/timing_concurrency.csv", index=False)

# ---------- part: statistics (paired, Bonferroni, TOST equivalence with a pre-specified margin) ----------
def paired_all(df, ref, metric):
    out = []
    comps = [(s, m) for s in df.scenario.unique() for m in df.method.unique() if m != ref]
    k = len(comps)
    for s, m in comps:
        a = df[(df.scenario == s) & (df.method == ref)].sort_values("seed")
        b = df[(df.scenario == s) & (df.method == m)].sort_values("seed")
        mm = a.merge(b, on="seed", suffixes=("_a", "_b"))
        if len(mm) < 3: continue
        d = mm[f"{metric}_a"].values - mm[f"{metric}_b"].values
        n = len(d); dbar = d.mean(); sd = d.std(ddof=1) if n > 1 else float("nan")
        t, p = stats.ttest_1samp(d, 0.0) if sd > 0 else (float("nan"), float("nan"))
        try: pw = stats.wilcoxon(d, method="exact").pvalue if np.any(d != 0) else float("nan")
        except Exception: pw = float("nan")
        h = stats.t.ppf(0.975, n - 1) * sd / math.sqrt(n) if sd == sd else float("nan")
        h90 = stats.t.ppf(0.95, n - 1) * sd / math.sqrt(n) if sd == sd else float("nan")
        # TOST with pre-specified margin ±1 pp (PL) — equivalence only if the 90% CI lies inside the margin
        tost_eq = (dbar - h90 > -1.0) and (dbar + h90 < 1.0) if metric == "PL_flow" else None
        out.append(dict(metric=metric, scenario=s, reference=ref, comparator=m, n=n, dbar=dbar, sd_d=sd,
                        t=t, p_nom=p, p_bonf=min(1.0, k * p) if p == p else p, p_wilcoxon=pw,
                        ci95=f"[{dbar-h:.2f}, {dbar+h:.2f}]", cohen_d=dbar / sd if sd and sd > 0 else float("nan"),
                        sig_bonf_0_05=(min(1.0, k * p) <= 0.05) if p == p else False,
                        equivalent_within_1pp_TOST=tost_eq, m_tests=k))
    return pd.DataFrame(out)

def part_stats():
    import glob
    df = pd.concat([pd.read_csv(f) for f in glob.glob(f"{OUT}/main_*.csv")], ignore_index=True)
    res = []
    for metric in ["PL_flow", "BWL", "latency_p95_ms", "JFI", "PL_EF", "PL_AF", "PL_BE"]:
        res.append(paired_all(df, "MAS-QA", metric))
    res = pd.concat(res, ignore_index=True)
    res.to_csv(f"{OUT}/stats_main.csv", index=False)
    summ = df.groupby(["scenario", "method"])[["PL_flow", "BWL", "latency_ms", "latency_p95_ms", "JFI", "CoV"]].agg(["mean", "std"]).round(2)
    summ.to_csv(f"{OUT}/summary_main.csv")
    print(summ.to_string()); print(res[res.metric == "PL_flow"][["scenario", "comparator", "dbar", "p_bonf", "sig_bonf_0_05", "equivalent_within_1pp_TOST"]].round(3).to_string())

if __name__ == "__main__":
    part = sys.argv[1]
    if part == "tune": part_tune()
    elif part == "main": part_main(sys.argv[2].split(","))
    elif part == "opt": part_opt()
    elif part == "scale": part_scale()
    elif part == "timing": part_timing()
    elif part == "stats": part_stats()
    else: raise SystemExit(part)
