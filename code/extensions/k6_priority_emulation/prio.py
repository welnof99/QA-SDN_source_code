import os
# Hard priority constraint in the QUBO.
# For every pair (g higher class, f lower class) whose candidate path sets share a physical arc, add
#   lam_p * y_f * (1 - y_g)
# which is 0 when g is admitted or f is rejected, and lam_p when f is admitted while g is rejected.
# Pairs with disjoint path sets cannot displace each other, so they get no term.
# With lam_p large, the minimum admits every higher-class flow that can be admitted before any lower-class flow.
import sys; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
import itertools
import masqa_lib as L
RANK = {"EF": 0, "AF": 1, "BE": 2}

def overlap(f, g, topo_links=None):
    arcs_f = {l for p in f["paths"] for l in p}
    arcs_g = {l for p in g["paths"] for l in p}
    return len(arcs_f & arcs_g) > 0

def add_priority_penalty(qb, flows, lam_p):
    if lam_p == 0: return 0
    n = 0
    for g, f in itertools.permutations(flows, 2):
        if RANK[g["cls"]] < RANK[f["cls"]] and overlap(f, g):
            yg = qb.idx[("y", g["id"])]; yf = qb.idx[("y", f["id"])]
            qb.add(yf, yf, lam_p)            # + lam_p * y_f
            qb.add(yf, yg, -lam_p)           # - lam_p * y_f * y_g
            n += 1
    return n

def build_qubo_prio(flows, topo, bg, Dtot, cc, lam, lam_p):
    qb = L.build_qubo(flows, topo, bg, Dtot, cc, lam)
    n = add_priority_penalty(qb, flows, lam_p)
    qb.n_prio_pairs = n
    return qb
