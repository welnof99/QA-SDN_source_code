# masqa_lib: functions of the MAS-QA notebook (no experiment runs at import)
# ===== CELL: config =====
import os, time, math, itertools, json
import numpy as np, pandas as pd
import openjij as oj
from scipy import stats

# Budget presets. PAPER follows the manuscript where it states values; SMOKE is for a quick test.
BUDGETS = {
    "smoke": dict(pod_reads=2, pod_sweeps=50, trotter=16, sa_reads=2, sa_sweeps=200, sqa_reads=2, sqa_sweeps=200),
    "paper": dict(pod_reads=10, pod_sweeps=500, trotter=16, sa_reads=100, sa_sweeps=5000, sqa_reads=10, sqa_sweeps=5000),
}
BUDGET = os.environ.get("MASQA_BUDGET", "paper")   # set to "smoke" for a quick check
B = BUDGETS[BUDGET]

SCENARIOS = {  # name: (N_F, D_total in Mbps)  — from Table 3 of the manuscript
    "S1": (50, 640.0),
    "S2": (100, 1278.3),
    "S3": (150, 1920.0),
}
EVAL_SEEDS = list(range(42, 52))          # evaluation seeds (n = 10)
VALID_SEEDS = list(range(100, 105))       # separate validation seeds for tuning λ
LINK_CAP = 50.0                           # Mbps per directed arc (full-duplex physical link)
SERVER_CAP = 50.0
D_MAX = 2 * (3.0 + 1.5 + 0.5)             # 10.0 ms: bound from the delay intervals (corrected)
LAMBDA = dict(A=10.0, c=10.0, l=5.0, t=3.0, b=2.0, f=1.0)   # one-hot, capacity, balance, delay, bandwidth, fairness
SLACK_BITS = 6
PRIO_W = {"EF": 3, "AF": 2, "BE": 1}
print("budget preset:", BUDGET, B)

# ===== CELL: Fat-Tree k=4 topology and candidate paths =====
def build_fat_tree(topo_seed=42):
    """k=4 Fat-Tree: 4 pods, 2 edge + 2 agg per pod, 4 cores, 16 hosts, 48 physical links."""
    rng = np.random.default_rng(topo_seed)
    links = {}          # (u,v) sorted -> link id
    delay = []          # link id -> sampled delay (ms), class-dependent intervals
    def add_link(u, v, lo, hi):
        """Physical full-duplex link -> two directed arcs (u->v, v->u), each with capacity LINK_CAP."""
        if (u, v) not in links:
            d_ = rng.uniform(lo, hi)
            for a, b in [(u, v), (v, u)]:
                links[(a, b)] = len(delay)
                delay.append(d_)
        return links[(u, v)]
    hosts = []          # (pod, edge, idx, name)
    E = {}; A = {}; C = [f"c{i}" for i in range(4)]
    for p in range(4):
        for j in range(2):
            E[(p, j)] = f"e{p}{j}"; A[(p, j)] = f"a{p}{j}"
            for h in range(2):
                hosts.append((p, j, h, f"h{p}{j}{h}"))
    for p in range(4):
        for j in range(2):
            for h in range(2):
                add_link(f"h{p}{j}{h}", E[(p, j)], 1.0, 3.0)      # host-edge, edge interval [1.0, 3.0]
            for a in range(2):
                add_link(E[(p, j)], A[(p, a)], 0.5, 1.5)          # edge-agg, interval [0.5, 1.5]
        for a in range(2):
            for t in range(2):
                add_link(A[(p, a)], C[2 * a + t], 0.1, 0.5)       # agg-core, interval [0.1, 0.5]
    assert len(links) == 96 and len(delay) == 96, len(links)   # 48 physical links = 96 directed arcs
    return dict(links=links, delay=np.array(delay), hosts=hosts, E=E, A=A, C=C)

TOPO = build_fat_tree(42)
print("links:", len(TOPO["links"]), "| hosts:", len(TOPO["hosts"]))

def link_id(topo, u, v):
    """Directed arc id for traversal u -> v."""
    return topo["links"][(u, v)]

def candidate_paths(topo, s, d):
    """Return candidate paths (list of link-id lists and delays), sorted by delay."""
    ps, es, hs, sn = s; pd, ed, hd, dn = d
    E, A, C = topo["E"], topo["A"], topo["C"]
    lk = lambda u, v: link_id(topo, u, v)
    paths = []
    if (ps, es) == (pd, ed):
        paths.append([lk(sn, E[(ps, es)]), lk(E[(pd, ed)], dn)])
    elif ps == pd:
        for a in range(2):
            paths.append([lk(sn, E[(ps, es)]), lk(E[(ps, es)], A[(ps, a)]), lk(A[(ps, a)], E[(pd, ed)]), lk(E[(pd, ed)], dn)])
    else:
        for a in range(2):
            for t in range(2):
                c = C[2 * a + t]
                paths.append([lk(sn, E[(ps, es)]), lk(E[(ps, es)], A[(ps, a)]), lk(A[(ps, a)], c),
                              lk(c, A[(pd, a)]), lk(A[(pd, a)], E[(pd, ed)]), lk(E[(pd, ed)], dn)])
    out = [(pl, float(sum(topo["delay"][l] for l in pl))) for pl in paths]
    out.sort(key=lambda t: t[1])
    return [p for p, _ in out], [dl for _, dl in out]

# ===== CELL: traffic generation =====
def gen_traffic(N, D_total, seed, topo=TOPO):
    rng = np.random.default_rng(seed)
    hosts = topo["hosts"]
    flows = []
    raw = 2.0 * (1.0 + rng.pareto(2.0, size=N))        # Pareto(a=2), x_min = 2 Mbps
    dem = raw * (D_total / raw.sum())                    # scale so that total demand = D_total (Table 3)
    n_ef, n_af = int(round(0.1 * N)), int(round(0.3 * N))
    classes = np.array(["EF"] * n_ef + ["AF"] * n_af + ["BE"] * (N - n_ef - n_af))
    rng.shuffle(classes)
    for f in range(N):
        i, j = rng.choice(len(hosts), size=2, replace=False)
        s, d = hosts[i], hosts[j]
        pl, dl = candidate_paths(topo, s, d)
        flows.append(dict(id=f, src=s[3], dst=d[3], pod=s[0], demand=float(dem[f]), cls=str(classes[f]),
                          w=PRIO_W[str(classes[f])], paths=pl, pdelay=dl))
    return flows

# ===== CELL: QUBO builder (corrected formulation; see manuscript Section 3.2) =====
class QUBO:
    def __init__(self):
        self.Q = {}; self.idx = {}
    def var(self, key):
        if key not in self.idx:
            self.idx[key] = len(self.idx)
        return self.idx[key]
    def add(self, i, j, v):
        if i > j: i, j = j, i
        self.Q[(i, j)] = self.Q.get((i, j), 0.0) + v
    def add_sq(self, lin, c0, scale=1.0):
        """Add scale * (sum_i a_i z_i + c0)^2 using z^2 = z. lin: dict var-index -> a_i."""
        items = list(lin.items())
        for i, a in items:
            self.add(i, i, scale * (a * a + 2 * c0 * a))
        for x in range(len(items)):
            for y in range(x + 1, len(items)):
                i, a = items[x]; j, b = items[y]
                self.add(i, j, scale * 2 * a * b)

def build_qubo(flows_sub, topo, bg_load, Dtot, class_counts, lam=LAMBDA):
    # class_counts: {"EF": D_EF, "AF": D_AF, "BE": D_BE} = global demand per class (Mbps)
    """H = λA·H_A + λc·H_cap + λl·H_bal + λt·H_lat + λb·H_bw + λf·H_fair (all in utilization units).
       flows_sub: list of flow dicts; bg_load: array (48) of fixed background load (Mbps) from other pods."""
    q = QUBO(); nL = len(topo["links"])
    link_terms = {l: {} for l in range(nL)}     # link -> {var: demand coefficient}
    for f in flows_sub:
        fid = f["id"]
        y = q.var(("y", fid))
        xs = []
        for p, pl in enumerate(f["paths"]):
            xv = q.var(("x", fid, p)); xs.append(xv)
            for l in pl:
                link_terms[l][xv] = f["demand"]
            # H_lat: priority-weighted normalized delay
            q.add(xv, xv, lam["t"] * f["w"] * (f["pdelay"][p] / D_MAX))
        # H_A: one path per admitted flow
        lin = {xv: 1.0 for xv in xs}; lin[y] = -1.0
        q.add_sq(lin, 0.0, lam["A"])
        # H_bw: unserved bandwidth (d/Dtot)(1 - y) -> linear term in y
        q.add(y, y, -lam["b"] * f["demand"] / Dtot)
    # H_cap (hard, utilization units) with binary slack: (sum d x + sum δ2^k s - cap')/c, cap' = c - bg
    used_links = [l for l in range(nL) if link_terms[l]]
    for l in used_links:
        c = LINK_CAP
        delta = c / (2 ** SLACK_BITS - 1)
        lin = {}
        for v, a in link_terms[l].items():
            lin[v] = a / c
        for k in range(SLACK_BITS):
            sv = q.var(("s", l, k)); lin[sv] = delta * (2 ** k) / c
        q.add_sq(lin, -(c - bg_load[l]) / c, lam["c"])
    # H_bal: |E|·Var(u) = Σ u_l^2 - (1/|E|)(Σ u_l)^2, with u_l = (bg_l + Σ d x)/c
    total_lin = {}; total_c0 = 0.0
    for l in range(nL):
        lin = {v: a / LINK_CAP for v, a in link_terms[l].items()}
        c0 = bg_load[l] / LINK_CAP
        if lin or c0:
            q.add_sq(lin, c0, lam["l"])
        for v, a in lin.items(): total_lin[v] = total_lin.get(v, 0.0) + a
        total_c0 += c0
    if total_lin:
        q.add_sq(total_lin, total_c0, -lam["l"] / nL)
    # H_fair: parity of served-bandwidth share across classes.
    #   rho_k = (1/D_k) * sum_{f in class k} d_f * y_f,  D_k = global demand of class k (class_demand).
    #   H_fair = sum_{k<k'} (rho_k - rho_k')^2. Zero when nothing is served, so rejecting all flows is not favoured.
    cls_sub = {}
    for f in flows_sub:
        cls_sub.setdefault(f["cls"], []).append((q.var(("y", f["id"])), f["demand"]))
    keys = ["EF", "AF", "BE"]
    for k1, k2 in itertools.combinations(keys, 2):
        lin = {}
        for v, dmd in cls_sub.get(k1, []): lin[v] = lin.get(v, 0.0) + dmd / class_counts[k1]
        for v, dmd in cls_sub.get(k2, []): lin[v] = lin.get(v, 0.0) - dmd / class_counts[k2]
        if lin: q.add_sq(lin, 0.0, lam["f"])
    return q

# ===== CELL: solver wrapper (OpenJij SQA / SA) =====
def solve(q, method, reads, sweeps, seed):
    if method == "sqa":
        sampler = oj.SQASampler()
        ss = sampler.sample_qubo(q.Q, num_reads=reads, num_sweeps=sweeps, trotter=B["trotter"],
                                 beta=5.0, gamma=3.0, seed=seed)
    else:
        sampler = oj.SASampler()
        ss = sampler.sample_qubo(q.Q, num_reads=reads, num_sweeps=sweeps, seed=seed)
    best = ss.first.sample
    return {int(k): int(v) for k, v in best.items()}

def decode(q, sample, flows_sub):
    """Return {flow id: path index or None}. Multiple selected paths: keep the lowest-delay one."""
    out = {}
    for f in flows_sub:
        chosen = None
        if sample.get(q.idx[("y", f["id"])], 0) == 1:
            for p in range(len(f["paths"])):
                if sample.get(q.idx[("x", f["id"], p)], 0) == 1:
                    chosen = p; break
        out[f["id"]] = chosen
    return out

# ===== CELL: coordinator (priority-ordered repair + greedy fill) =====
def coordinate(assign, flows):
    """Enforce hard capacity: reroute or drop overloaded flows in priority order (EF→AF→BE, then demand),
       then greedily admit unserved flows on any feasible path. Returns final assignment."""
    fmap = {f["id"]: f for f in flows}
    order = sorted(flows, key=lambda f: (-f["w"], -f["demand"]))
    load = {}
    def path_links(f, p): return f["paths"][p]
    def fits(f, p, load):
        return all(load.get(l, 0.0) + f["demand"] <= LINK_CAP + 1e-9 for l in path_links(f, p))
    def add(f, p, load):
        for l in path_links(f, p): load[l] = load.get(l, 0.0) + f["demand"]
    # pass 1: resolve overloads (flows already assigned by pods)
    for f in order:
        p = assign.get(f["id"])
        if p is None: continue
        add(f, p, load)
    final = {f["id"]: assign.get(f["id"]) for f in flows}   # every flow gets an entry (None = rejected)
    for f in order:
        p = final.get(f["id"])
        if p is None: continue
        if any(load.get(l, 0.0) > LINK_CAP + 1e-9 for l in path_links(f, p)):
            for l in path_links(f, p): load[l] -= f["demand"]
            alt = None
            for p2 in range(len(f["paths"])):
                if p2 != p and fits(f, p2, load):
                    alt = p2; break
            if alt is not None:
                add(f, alt, load); final[f["id"]] = alt
            else:
                final[f["id"]] = None
    # pass 2: greedy fill of unserved flows
    for f in order:
        if final.get(f["id"]) is None:
            for p2 in range(len(f["paths"])):
                if fits(f, p2, load):
                    add(f, p2, load); final[f["id"]] = p2; break
    return final

# ===== CELL: baselines (ECMP variants) =====
def ecmp_hash(flows, seed):
    """Hash-based ECMP: uniform random path choice, no capacity check. A flow is lost if it crosses an overloaded link."""
    rng = np.random.default_rng(seed + 7)
    assign = {f["id"]: int(rng.integers(len(f["paths"]))) for f in flows}
    load = {}
    for f in flows:
        for l in f["paths"][assign[f["id"]]]: load[l] = load.get(l, 0.0) + f["demand"]
    served = {}
    for f in flows:
        over = any(load[l] > LINK_CAP + 1e-9 for l in f["paths"][assign[f["id"]]])
        served[f["id"]] = None if over else assign[f["id"]]
    return served

def ecmp_admission(flows, seed):
    """Hash path, but admit in arrival order only if the hash path has residual capacity (capacity-aware ECMP)."""
    rng = np.random.default_rng(seed + 7)
    load = {}; served = {}
    for f in flows:
        p = int(rng.integers(len(f["paths"])))
        if all(load.get(l, 0.0) + f["demand"] <= LINK_CAP + 1e-9 for l in f["paths"][p]):
            for l in f["paths"][p]: load[l] = load.get(l, 0.0) + f["demand"]
            served[f["id"]] = p
        else:
            served[f["id"]] = None
    return served

# ===== CELL: pipelines and metrics =====
def link_load(flows, assign):
    load = np.zeros(len(TOPO["links"]))
    for f in flows:
        p = assign.get(f["id"])
        if p is not None:
            for l in f["paths"][p]: load[l] += f["demand"]
    return load

def loss_on_overload(flows, assign):
    """Raw solver output without repair: flows that cross an overloaded link are counted as lost."""
    load = link_load(flows, assign)
    out = {}
    for f in flows:
        p = assign.get(f["id"])
        if p is None: out[f["id"]] = None; continue
        over = any(load[l] > LINK_CAP + 1e-9 for l in f["paths"][p])
        out[f["id"]] = None if over else p
    return out

def run_mas(flows, seed, Dtot, cc, lam=LAMBDA, method="sqa"):
    """MAS-QA-SDN: 4 pod subproblems (flows grouped by source pod), then Global Coordinator."""
    assign = {}; pod_times = []
    for q in range(4):
        sub = [f for f in flows if f["pod"] == q]
        if not sub: continue
        t0 = time.perf_counter()
        qb = build_qubo(sub, TOPO, np.zeros(len(TOPO["links"])), Dtot, cc, lam)
        smp = solve(qb, method, B["pod_reads"], B["pod_sweeps"], seed * 10 + q)
        assign.update(decode(qb, smp, sub))
        pod_times.append(time.perf_counter() - t0)
    t1 = time.perf_counter()
    final = coordinate(assign, flows)
    coord_t = time.perf_counter() - t1
    return final, dict(pod_parallel_s=max(pod_times), pod_sequential_s=sum(pod_times), coord_s=coord_t)

def run_mono(flows, seed, Dtot, cc, lam=LAMBDA, method="sa"):
    """One monolithic solve. Returns (raw, repaired, extra): raw = solver output with overloaded flows lost;
       repaired = same sample passed through the Global Coordinator. Both use the same sample, so they isolate the repair."""
    t0 = time.perf_counter()
    qb = build_qubo(flows, TOPO, np.zeros(len(TOPO["links"])), Dtot, cc, lam)
    reads, sweeps = (B["sa_reads"], B["sa_sweeps"]) if method == "sa" else (B["sqa_reads"], B["sqa_sweeps"])
    smp = solve(qb, method, reads, sweeps, seed)
    assign = decode(qb, smp, flows)
    raw = loss_on_overload(flows, assign)
    repaired = coordinate(assign, flows)
    return raw, repaired, dict(solve_s=time.perf_counter() - t0)

def metrics(flows, served, Dtot):
    N = len(flows)
    srv = [f for f in flows if served[f["id"]] is not None]
    dem = sum(f["demand"] for f in srv)
    PL = 100.0 * (N - len(srv)) / N                          # PL_flow (%)
    BWL = 100.0 * (1.0 - dem / Dtot)                         # bandwidth-weighted loss (%)
    lat_num = sum(f["w"] * f["pdelay"][served[f["id"]]] for f in srv)
    lat_den = sum(f["w"] for f in srv)
    latency = lat_num / lat_den if lat_den > 0 else float("nan")   # priority-weighted delay (ms)
    # server load: egress demand of served flows per server (16 hosts)
    hosts = [h[3] for h in TOPO["hosts"]]
    load = np.array([sum(f["demand"] for f in srv if f["src"] == h) for h in hosts])
    jfi = load.sum() ** 2 / (len(load) * (load ** 2).sum()) if (load ** 2).sum() > 0 else 0.0
    cov = 100.0 * load.std() / load.mean() if load.mean() > 0 else float("nan")   # population SD
    # hard feasibility check on the served set
    ll = np.zeros(len(TOPO["links"]))
    for f in srv:
        for l in f["paths"][served[f["id"]]]: ll[l] += f["demand"]
    assert ll.max() <= LINK_CAP + 1e-6, "served set violates capacity"
    return dict(PL_flow=PL, BWL=BWL, latency_ms=latency, throughput_mbps=dem, JFI=jfi, CoV=cov)

# ===== CELL: experiment runner =====
def run_all(scenarios=SCENARIOS, seeds=EVAL_SEEDS, lam=LAMBDA, methods=None):
    methods = methods or ["ECMP-hash", "ECMP+adm", "Greedy-only", "SA-mono", "SA-mono+repair",
                          "SQA-mono", "SQA-mono+repair", "MAS-QA"]
    rows = []
    for scen, (N, Dtot) in scenarios.items():
        for seed in seeds:
            flows = gen_traffic(N, Dtot, seed)
            cc = {k: sum(f["demand"] for f in flows if f["cls"] == k) for k in ["EF", "AF", "BE"]}   # class demand D_k
            mono_cache = {}
            for m in methods:
                t0 = time.perf_counter(); extra = {}
                if m == "ECMP-hash":
                    served = ecmp_hash(flows, seed)
                elif m == "ECMP+adm":
                    served = ecmp_admission(flows, seed)
                elif m == "Greedy-only":          # coordinator alone: priority-ordered greedy admission, no QUBO
                    served = coordinate({}, flows)
                elif m.startswith(("SA-mono", "SQA-mono")):
                    meth = "sa" if m.startswith("SA") else "sqa"
                    if meth not in mono_cache:
                        mono_cache[meth] = run_mono(flows, seed, Dtot, cc, lam, method=meth)
                    raw, rep, extra = mono_cache[meth]
                    served = rep if m.endswith("+repair") else raw
                elif m == "MAS-QA":
                    served, extra = run_mas(flows, seed, Dtot, cc, lam)
                else:
                    raise ValueError(m)
                wall = time.perf_counter() - t0
                r = dict(scenario=scen, seed=seed, method=m, wall_s=wall, **metrics(flows, served, Dtot), **extra)
                rows.append(r)
                print(f"{scen} seed={seed} {m:10s} PL={r['PL_flow']:.2f} JFI={r['JFI']:.4f} CoV={r['CoV']:.1f} lat={r['latency_ms']:.2f} t={wall:.1f}s")
    return pd.DataFrame(rows)

LAMBDA_GRID = {
    "baseline (10,5,3,2,1)": dict(A=10, c=10, l=5, t=3, b=2, f=1),
    "equal (3,3,3,3,3)":     dict(A=10, c=3, l=3, t=3, b=3, f=3),
    "latency-focus":         dict(A=10, c=5, l=10, t=3, b=2, f=1),
    "strong-capacity":       dict(A=10, c=20, l=5, t=3, b=2, f=1),
    "balance-focus":         dict(A=10, c=10, l=5, t=3, b=5, f=1),
    "no-fairness":           dict(A=10, c=10, l=5, t=3, b=2, f=0),
}
