import os
import sys, json, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
import numpy as np, pandas as pd, openjij as oj
import masqa_lib as L
import exp as E
ORIG_SOLVE = L.solve
def set_sqa(beta, gamma):
    def s(q, method, reads, sweeps, seed):
        if method == "sqa":
            ss = oj.SQASampler().sample_qubo(q.Q, num_reads=reads, num_sweeps=sweeps, trotter=L.B["trotter"], beta=beta, gamma=gamma, seed=seed)
            return {int(k): int(v) for k, v in ss.first.sample.items()}
        return ORIG_SOLVE(q, method, reads, sweeps, seed)
    L.solve = s
def set_budget(**kw):
    L.B.update(kw)
def set_sa_tuned(bmin=0.1, bmax=10.0):
    def s(q, method, reads, sweeps, seed):
        if method == "sqa":
            return ORIG_SOLVE(q, method, reads, sweeps, seed)
        ss = oj.SASampler().sample_qubo(q.Q, num_reads=reads, num_sweeps=sweeps, beta_min=bmin, beta_max=bmax, seed=seed)
        return {int(k): int(v) for k, v in ss.first.sample.items()}
    L.solve = s
