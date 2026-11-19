import os
"""Round-2 experiment library. Imports the released model code (masqa_lib) and exposes every solver
parameter explicitly. Defaults equal the manuscript's tuned settings (SQA beta=0.5, gamma=1.0, P=16;
tuned SA beta in [0.1, 10]; pods 10 reads x 500 sweeps; monolithic SQA 10 x 5000; monolithic SA 10 x 80000).
Work is counted as spin updates: nvars * sweeps * reads, multiplied by P for SQA."""
import sys, time
import numpy as np
import openjij as oj
RELEASE_CODE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, RELEASE_CODE)
import masqa_lib as L

P = 16
TUNED = dict(sqa_beta=0.5, sqa_gamma=1.0, sa_bmin=0.1, sa_bmax=10.0,
             pod_reads=10, pod_sweeps=500, sqa_reads=10, sqa_sweeps=5000, sa_reads=10, sa_sweeps=80000)
SCEN = L.SCENARIOS
MAIN_SEEDS = list(range(42, 72))
VALID_SEEDS = list(range(100, 105))
LAM = dict(L.LAMBDA)

def sample_sqa(qb, reads, sweeps, seed, beta=TUNED["sqa_beta"], gamma=TUNED["sqa_gamma"]):
    ss = oj.SQASampler().sample_qubo(qb.Q, num_reads=reads, num_sweeps=sweeps, trotter=P,
                                     beta=beta, gamma=gamma, seed=seed)
    return {int(k): int(v) for k, v in ss.first.sample.items()}

def sample_sa(qb, reads, sweeps, seed, bmin=TUNED["sa_bmin"], bmax=TUNED["sa_bmax"]):
    ss = oj.SASampler().sample_qubo(qb.Q, num_reads=reads, num_sweeps=sweeps, seed=seed,
                                    beta_min=bmin, beta_max=bmax)
    return {int(k): int(v) for k, v in ss.first.sample.items()}

def add_bonus(qb, flows, mu):
    """Admission bonus: adds -mu * y_f for each flow (linear reward for admitting a flow)."""
    if mu:
        for f in flows:
            y = qb.idx[("y", f["id"])]
            qb.add(y, y, -mu)
    return qb

def energy(qb, sample):
    """QUBO energy of a binary sample (constant offset omitted, identical for all states)."""
    e = 0.0
    for (i, j), v in qb.Q.items():
        e += v * sample.get(i, 0) * sample.get(j, 0)
    return e

def all_rejected_sample(qb, flows):
    """All y_f = 0 and x = 0; slack bits at their maximum (the state the manuscript describes)."""
    s = {}
    for key, idx in qb.idx.items():
        s[idx] = 1 if key[0] == "s" else 0
    return s

def cc_of(flows, Dtot=None):
    return {k: sum(f["demand"] for f in flows if f["cls"] == k) for k in ["EF", "AF", "BE"]}

def metrics(flows, served, Dtot):
    m = L.metrics(flows, served, Dtot)
    srv = [f for f in flows if served[f["id"]] is not None]
    lat = [f["pdelay"][served[f["id"]]] for f in srv]
    m["latency_p95_ms"] = float(np.percentile(lat, 95)) if lat else float("nan")
    for k in ["EF", "AF", "BE"]:
        fk = [f for f in flows if f["cls"] == k]
        m[f"PL_{k}"] = 100.0 * sum(served[f["id"]] is None for f in fk) / max(1, len(fk))
    return m

def pod_solve(flows, seed, Dtot, cc, lam, mu, solver, prm):
    """Four source-pod subproblems (sequential), then the coordinator. Returns (final, info)."""
    assign, nvars, work, pod_t = {}, 0, 0.0, []
    for q in range(4):
        sub = [f for f in flows if f["pod"] == q]
        if not sub:
            continue
        t0 = time.perf_counter()
        qb = add_bonus(L.build_qubo(sub, L.TOPO, np.zeros(len(L.TOPO["links"])), Dtot, cc, lam), sub, mu)
        if solver == "sqa":
            smp = sample_sqa(qb, prm["pod_reads"], prm["pod_sweeps"], seed * 10 + q, prm["sqa_beta"], prm["sqa_gamma"])
            work += len(qb.idx) * P * prm["pod_sweeps"] * prm["pod_reads"]
        else:
            smp = sample_sa(qb, prm["pod_reads"], prm["pod_sweeps"], seed * 10 + q, prm["sa_bmin"], prm["sa_bmax"])
            work += len(qb.idx) * prm["pod_sweeps"] * prm["pod_reads"]
        assign.update(L.decode(qb, smp, sub))
        nvars += len(qb.idx); pod_t.append(time.perf_counter() - t0)
    t1 = time.perf_counter()
    final = L.coordinate(assign, flows)
    return final, dict(pod_vars=nvars, pod_work=work, pod_sequential_s=sum(pod_t),
                       coord_s=time.perf_counter() - t1, total_s=sum(pod_t) + (time.perf_counter() - t1))

def mono_solve(flows, seed, Dtot, cc, lam, mu, solver, reads, sweeps, prm, want_energy=False):
    """One monolithic solve over all flows. Returns (raw_assignment, final, info, qb, sample)."""
    t0 = time.perf_counter()
    qb = add_bonus(L.build_qubo(flows, L.TOPO, np.zeros(len(L.TOPO["links"])), Dtot, cc, lam), flows, mu)
    t_build = time.perf_counter() - t0
    t1 = time.perf_counter()
    if solver == "sqa":
        smp = sample_sqa(qb, reads, sweeps, seed, prm["sqa_beta"], prm["sqa_gamma"])
        work = len(qb.idx) * P * sweeps * reads
    else:
        smp = sample_sa(qb, reads, sweeps, seed, prm["sa_bmin"], prm["sa_bmax"])
        work = len(qb.idx) * sweeps * reads
    t_solve = time.perf_counter() - t1
    t2 = time.perf_counter()
    raw = L.decode(qb, smp, flows)
    final = L.coordinate(raw, flows)
    t_coord = time.perf_counter() - t2
    info = dict(mono_vars=len(qb.idx), mono_work=work, build_s=t_build, solve_s=t_solve,
                coord_s=t_coord, total_s=t_build + t_solve + t_coord)
    return raw, final, info, qb, smp
