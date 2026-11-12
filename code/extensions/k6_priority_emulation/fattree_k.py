import os
# Generalised Fat-Tree(k) for the topology-validity check. For k=4 it must reproduce masqa_lib exactly.
import sys, time
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
import masqa_lib as L
from masqa_lib import LINK_CAP, PRIO_W, D_MAX

def build_fat_tree_k(k, topo_seed=42):
    h2 = k // 2
    rng = np.random.default_rng(topo_seed)
    links = {}; delay = []
    def add_link(u, v, lo, hi):
        if (u, v) not in links:
            d_ = rng.uniform(lo, hi)
            for a, b in [(u, v), (v, u)]:
                links[(a, b)] = len(delay); delay.append(d_)
        return links[(u, v)]
    hosts = []; E = {}; A = {}; C = [f"c{i}" for i in range(h2 * h2)]
    for p in range(k):
        for j in range(h2):
            E[(p, j)] = f"e{p}{j}"
            for a in range(h2):
                A[(p, a)] = f"a{p}{a}"
            for h in range(h2):
                hosts.append((p, j, h, f"h{p}{j}{h}"))
    for p in range(k):
        for j in range(h2):
            for h in range(h2):
                add_link(f"h{p}{j}{h}", E[(p, j)], 1.0, 3.0)
            for a in range(h2):
                add_link(E[(p, j)], A[(p, a)], 0.5, 1.5)
        for a in range(h2):
            for t in range(h2):
                add_link(A[(p, a)], C[h2 * a + t], 0.1, 0.5)
    return dict(links=links, delay=np.array(delay), hosts=hosts, E=E, A=A, C=C, k=k)

def candidate_paths_k(topo, s, d):
    ps, es, hs, sn = s; pd, ed, hd, dn = d
    E, A, C = topo["E"], topo["A"], topo["C"]; h2 = topo["k"] // 2
    lk = lambda u, v: topo["links"][(u, v)]
    paths = []
    if (ps, es) == (pd, ed):
        paths.append([lk(sn, E[(ps, es)]), lk(E[(pd, ed)], dn)])
    elif ps == pd:
        for a in range(h2):
            paths.append([lk(sn, E[(ps, es)]), lk(E[(ps, es)], A[(ps, a)]), lk(A[(ps, a)], E[(pd, ed)]), lk(E[(pd, ed)], dn)])
    else:
        for a in range(h2):
            for t in range(h2):
                c = C[h2 * a + t]
                paths.append([lk(sn, E[(ps, es)]), lk(E[(ps, es)], A[(ps, a)]), lk(A[(ps, a)], c),
                              lk(c, A[(pd, a)]), lk(A[(pd, a)], E[(pd, ed)]), lk(E[(pd, ed)], dn)])
    out = [(pl, float(sum(topo["delay"][l] for l in pl))) for pl in paths]
    out.sort(key=lambda t: t[1])
    return [p for p, _ in out], [dl for _, dl in out]

def gen_traffic_k(topo, N, D_total, seed):
    rng = np.random.default_rng(seed)
    hosts = topo["hosts"]; flows = []
    raw = 2.0 * (1.0 + rng.pareto(2.0, size=N))
    dem = raw * (D_total / raw.sum())
    n_ef, n_af = int(round(0.1 * N)), int(round(0.3 * N))
    classes = np.array(["EF"] * n_ef + ["AF"] * n_af + ["BE"] * (N - n_ef - n_af))
    rng.shuffle(classes)
    for f in range(N):
        i, j = rng.choice(len(hosts), size=2, replace=False)
        s, d = hosts[i], hosts[j]
        pl, dl = candidate_paths_k(topo, s, d)
        flows.append(dict(id=f, src=s[3], dst=d[3], pod=s[0], demand=float(dem[f]), cls=str(classes[f]),
                          w=PRIO_W[str(classes[f])], paths=pl, pdelay=dl))
    return flows

def run_mas_k(topo, flows, seed, Dtot, cc, lam, method="sqa"):
    """Pod decomposition over k pods, then the unchanged coordinator. Mirrors masqa_lib.run_mas."""
    L.TOPO = topo
    assign = {}; pod_times = []
    for q in range(topo["k"]):
        sub = [f for f in flows if f["pod"] == q]
        if not sub: continue
        t0 = time.perf_counter()
        qb = L.build_qubo(sub, topo, np.zeros(len(topo["links"])), Dtot, cc, lam)
        smp = L.solve(qb, method, L.B["pod_reads"], L.B["pod_sweeps"], seed * 10 + q)
        assign.update(L.decode(qb, smp, sub))
        pod_times.append(time.perf_counter() - t0)
    final = L.coordinate(assign, flows)
    return assign, final, dict(pod_parallel_s=max(pod_times), pod_sequential_s=sum(pod_times))
