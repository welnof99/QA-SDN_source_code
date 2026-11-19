"""D: exhaustive check of the QUBO on a small instance (3 flows, 2 arcs).
Enumerates EVERY binary state of the QUBO (all y, x and slack bits), reports the exact state count, and checks
that the minimum-energy state is the best feasible admission. For each (x, y) the slack bits are minimised
exhaustively, so E*(x,y) = min over slack states; the global minimum over (x,y) is compared with a brute-force
search over feasible (x,y) using the same energy terms."""
import os
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "revision2")
import itertools, json
import numpy as np
import r2lib as R
L = R.L
flows = [
    dict(id=0, cls="EF", demand=20.0, paths=[[0]], pdelay=[2.0], w=3, pod=0),
    dict(id=1, cls="AF", demand=15.0, paths=[[0], [1]], pdelay=[2.0, 3.0], w=2, pod=0),
    dict(id=2, cls="BE", demand=10.0, paths=[[1]], pdelay=[3.0], w=1, pod=0),
]
Dtot = sum(f["demand"] for f in flows)
cc = R.cc_of(flows)
qb = L.build_qubo(flows, L.TOPO, np.zeros(len(L.TOPO["links"])), Dtot, cc, R.LAM)
n = len(qb.idx)
names = {v: k for k, v in qb.idx.items()}
Qu = np.zeros((n, n))
for (i, j), v in qb.Q.items():
    Qu[i, j] += v
states = ((np.arange(2 ** n)[:, None] >> np.arange(n)[None, :]) & 1).astype(np.float64)
E = np.sum((states @ Qu) * states, axis=1)
gmin = int(np.argmin(E))
print("variables:", n, " states enumerated:", 2 ** n)
print("global minimum energy:", round(E[gmin], 6))
# feasibility-aware reading: for each (x, y) choose the best slack state
xy_idx = [i for i, k in names.items() if k[0] in ("x", "y")]
s_idx = [i for i, k in names.items() if k[0] == "s"]
best = {}
for i in range(2 ** n):
    key = tuple(int(states[i, j]) for j in xy_idx)
    if key not in best or E[i] < best[key][0]:
        best[key] = (E[i], i)
ordered = sorted(best.items(), key=lambda kv: kv[1][0])
bk, (be, bi) = ordered[0]
print("best (x,y) after slack minimisation:", {names[j]: bk[t] for t, j in enumerate(xy_idx)}, round(be, 6))
# brute force over feasible assignments: one path per admitted flow, capacity satisfied with some slack state
def feasible_admissions():
    out = []
    for choice in itertools.product(*[[None] + list(range(len(f["paths"]))) for f in flows]):
        load = np.zeros(len(L.TOPO["links"]))
        ok = True
        for f, p in zip(flows, choice):
            if p is None: continue
            for l in f["paths"][p]: load[l] += f["demand"]
        if np.any(load > L.LINK_CAP + 1e-9): ok = False
        if ok: out.append(choice)
    return out
feas = feasible_admissions()
print("feasible admission/path choices:", len(feas))
def e_of(choice):
    key = []
    for name in [names[j] for j in xy_idx]:
        pass
    vec = {}
    for f, p in zip(flows, choice):
        vec[("y", f["id"])] = 0 if p is None else 1
        for pp in range(len(f["paths"])):
            vec[("x", f["id"], pp)] = 1 if (p == pp) else 0
    kvec = tuple(vec[names[j]] for j in xy_idx)
    return best[kvec][0] if kvec in best else None
scores = [(e_of(c), c) for c in feas]
scores = [s for s in scores if s[0] is not None]
scores.sort(key=lambda s: s[0])
print("lowest-energy feasible choice:", scores[0][1], round(scores[0][0], 6))
print("global minimum (x,y) equals lowest feasible:", abs(be - scores[0][0]) < 1e-9)
json.dump(dict(variables=n, states=2 ** n, slack_bits_total=len(s_idx), global_min=float(E[gmin]),
               best_xy_energy=float(be), lowest_feasible_energy=float(scores[0][0]),
               feasible_choices=len(feas)),
          open(os.path.join(OUT_DIR, "d_enum.json"), "w"), indent=2)
