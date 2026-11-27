"""
BAB VI - MAS-QA berbasis harga (MAS-QA-pi).

Modul ini memakai ulang komponen rilis artikel (masqa_lib: topologi, trafik, decode, coordinate;
revision2/r2lib: sampler tuned dan hitung kerja) tanpa mengubahnya, lalu menambah:

  1. Pembagian arc: arc lokal (naik: host->edge, edge->agg, agg->core) hanya dipakai flow dari
     pod sumbernya, sehingga kapasitasnya ditegakkan di QUBO pod dengan slack biner. Arc bersama
     (turun: core->agg, agg->edge, edge->host) ditegakkan koordinator melalui harga pi_l.
  2. Reward admisi analitis per flow mu_f (Subbab 6.2), dihitung dari beban putaran sebelumnya.
  3. Loop harga subgradien (Subbab 6.3, varian A):
        pi_l <- max(0, pi_l + rho_t * (load_l - c_l) / c),  rho_t = rho0 / sqrt(t + 1)
  4. Pentahapan prioritas EF -> AF -> BE (Subbab 6.4, MAS-QA-pi-Lex).

Semua keluaran akhir tetap melewati coordinate() yang sama dengan artikel, sehingga kelayakan
terjamin dan perbedaan hasil berasal dari koordinasi, bukan dari repair.
"""
import os, sys, math, time, itertools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "revision2"))
import masqa_lib as L          # noqa: E402
import r2lib as R              # noqa: E402

C = L.LINK_CAP
NL = len(L.TOPO["links"])
SLACK_BITS = L.SLACK_BITS
CLASSES = ["EF", "AF", "BE"]


# ---------------------------------------------------------------- pembagian arc
def _is_up(u, v):
    return (u[0] == "h" and v[0] == "e") or (u[0] == "e" and v[0] == "a") or (u[0] == "a" and v[0] == "c")

UP = np.zeros(NL, dtype=bool)
for (u, v), lid in L.TOPO["links"].items():
    UP[lid] = _is_up(u, v)
LOCAL_ARCS = set(np.where(UP)[0].tolist())      # 48 arc naik
SHARED_ARCS = set(np.where(~UP)[0].tolist())    # 48 arc turun


def check_arc_partition(flows):
    """Verifikasi: setiap arc lokal hanya dilalui flow dari satu pod sumber."""
    owner = {}
    for f in flows:
        for pl in f["paths"]:
            for l in pl:
                if l in LOCAL_ARCS:
                    owner.setdefault(l, set()).add(f["pod"])
    bad = {l: s for l, s in owner.items() if len(s) > 1}
    assert not bad, f"arc lokal dipakai >1 pod: {bad}"
    return True


# ---------------------------------------------------------------- reward admisi analitis (6.2)
def mu_analytic(f, u, cc, lam, eps=0.1, variant="load"):
    """mu_f = (1+eps) * min_p mu_f^min(p).  u: utilisasi arc (array NL) dari beban yang diketahui.
    variant='load'  : u_l dari beban putaran sebelumnya (batas berbasis beban).
    variant='worst' : u_l = 1, u_bar = 0 (batas kasus terburuk)."""
    a = f["demand"] / C
    ubar = float(np.mean(u))
    dk = f["demand"] / max(cc[f["cls"]], 1e-9)
    fair_max = 2.0 * (2.0 * dk + dk * dk)
    best = math.inf
    for p, pl in enumerate(f["paths"]):
        h = len(pl)
        if variant == "worst":
            dbal = 2.0 * a * h + h * a * a * (1.0 - h / NL)
        else:
            dbal = 2.0 * a * sum(u[l] - ubar for l in pl) + h * a * a * (1.0 - h / NL)
        eps_cap = h / (4.0 * (2 ** SLACK_BITS - 1) ** 2)
        cost = (lam["l"] * dbal + lam["t"] * f["w"] * f["pdelay"][p] / L.D_MAX
                + lam["f"] * fair_max + lam["c"] * eps_cap - lam["b"] * f["demand"] / sum(cc.values()))
        best = min(best, cost)
    return (1.0 + eps) * max(best, 0.0)


# ---------------------------------------------------------------- QUBO agen pod
def build_pod_qubo(sub, bg_load, cap_local, price, Dtot, cc, lam, mu):
    """QUBO satu agen pod.
    bg_load  : beban arc dari pod lain / tahap terkunci (array NL), dipakai di suku balance.
    cap_local: kapasitas efektif arc lokal (array NL) = c - beban terkunci.
    price    : harga pi_l (array NL), hanya bernilai pada arc bersama.
    mu       : dict flow id -> reward admisi."""
    q = L.QUBO()
    link_terms = {l: {} for l in range(NL)}
    for f in sub:
        y = q.var(("y", f["id"]))
        xs = []
        for p, pl in enumerate(f["paths"]):
            xv = q.var(("x", f["id"], p)); xs.append(xv)
            price_term = 0.0
            for l in pl:
                link_terms[l][xv] = f["demand"]
                if l in SHARED_ARCS:
                    price_term += price[l]
            q.add(xv, xv, lam["t"] * f["w"] * f["pdelay"][p] / L.D_MAX + price_term * f["demand"] / C)
        lin = {xv: 1.0 for xv in xs}; lin[y] = -1.0
        q.add_sq(lin, 0.0, lam["A"])
        q.add(y, y, -lam["b"] * f["demand"] / Dtot - mu.get(f["id"], 0.0))
    # kapasitas dengan slack: hanya arc lokal
    delta = C / (2 ** SLACK_BITS - 1)
    for l in LOCAL_ARCS:
        if not link_terms[l]:
            continue
        lin = {v: a / C for v, a in link_terms[l].items()}
        for k in range(SLACK_BITS):
            lin[q.var(("s", l, k))] = delta * (2 ** k) / C
        q.add_sq(lin, -cap_local[l] / C, lam["c"])
    # balance pada seluruh arc, beban pod lain sebagai konstanta
    total_lin, total_c0 = {}, 0.0
    for l in range(NL):
        lin = {v: a / C for v, a in link_terms[l].items()}
        c0 = bg_load[l] / C
        if lin or c0:
            q.add_sq(lin, c0, lam["l"])
        for v, a in lin.items():
            total_lin[v] = total_lin.get(v, 0.0) + a
        total_c0 += c0
    if total_lin:
        q.add_sq(total_lin, total_c0, -lam["l"] / NL)
    # fairness (dimatikan pada tahap Lex lewat lam["f"] = 0)
    if lam["f"]:
        cls_sub = {}
        for f in sub:
            cls_sub.setdefault(f["cls"], []).append((q.var(("y", f["id"])), f["demand"]))
        for k1, k2 in itertools.combinations(CLASSES, 2):
            lin = {}
            for v, d in cls_sub.get(k1, []): lin[v] = lin.get(v, 0.0) + d / cc[k1]
            for v, d in cls_sub.get(k2, []): lin[v] = lin.get(v, 0.0) - d / cc[k2]
            if lin:
                q.add_sq(lin, 0.0, lam["f"])
    return q


def _load_of(flows, assign):
    load = np.zeros(NL)
    for f in flows:
        p = assign.get(f["id"])
        if p is not None:
            for l in f["paths"][p]:
                load[l] += f["demand"]
    return load


# ---------------------------------------------------------------- loop harga (6.3)
def price_loop(flows, seed, Dtot, cc, lam, solver="sqa", prm=None, rho0=10.0, T_max=8,
               tol=0.02, eps_pi=1e-3, mu_mode="analytic", mu_const=20.0, eps_mu=0.1,
               locked_load=None, use_price=True, stage_tag=0):
    """Koordinasi harga antar-agen pod. Mengembalikan (assign_terbaik, info, trace).
    Keluaran terbaik = putaran dengan jumlah flow diterima terbanyak setelah repair
    (deterministik, dapat dihitung oleh controller)."""
    prm = prm or R.TUNED
    locked = np.zeros(NL) if locked_load is None else locked_load
    cap_eff = np.maximum(C - locked, 0.0)
    pods = sorted({f["pod"] for f in flows})
    price = np.zeros(NL)
    assign = {}
    load_prev = locked.copy()
    best, best_n, trace, work = None, -1, [], 0.0
    t_seq = t_par = 0.0
    prev_x = None
    for t in range(T_max):
        u = load_prev / C
        if mu_mode == "analytic":
            mu = {f["id"]: mu_analytic(f, u, cc, lam, eps_mu) for f in flows}
        elif mu_mode == "const":
            mu = {f["id"]: mu_const for f in flows}
        else:
            mu = {}
        new_assign, pod_times = {}, []
        for qd in pods:
            sub = [f for f in flows if f["pod"] == qd]
            own = _load_of(sub, assign) if assign else np.zeros(NL)
            bg = load_prev - own            # beban pod lain + beban terkunci
            t0 = time.perf_counter()
            qb = build_pod_qubo(sub, bg, cap_eff, price if use_price else np.zeros(NL), Dtot, cc, lam, mu)
            s = seed * 1000 + stage_tag * 100 + t * 10 + qd
            if solver == "sqa":
                smp = R.sample_sqa(qb, prm["pod_reads"], prm["pod_sweeps"], s, prm["sqa_beta"], prm["sqa_gamma"])
                work += len(qb.idx) * R.P * prm["pod_sweeps"] * prm["pod_reads"]
            else:
                smp = R.sample_sa(qb, prm["pod_reads"], prm["pod_sweeps"], s, prm["sa_bmin"], prm["sa_bmax"])
                work += len(qb.idx) * prm["pod_sweeps"] * prm["pod_reads"]
            new_assign.update(L.decode(qb, smp, sub))
            pod_times.append(time.perf_counter() - t0)
        t_seq += sum(pod_times); t_par += max(pod_times)
        assign = new_assign
        load = _load_of(flows, assign) + locked
        # ukuran konvergensi
        over = max(0.0, float(max((load[l] - C) / C for l in SHARED_ARCS)))
        x_now = {k: v for k, v in assign.items()}
        changed = (100.0 * sum(x_now.get(k) != prev_x.get(k) for k in x_now) / len(x_now)) if prev_x else float("nan")
        prev_x = x_now
        # repair untuk memilih putaran terbaik (tidak dipakai untuk memperbarui harga)
        rep = repair(flows, assign, locked)
        n_adm = sum(v is not None for v in rep.values())
        trace.append(dict(round=t, max_overload_shared=over, pct_changed=changed,
                          raw_admitted=sum(v is not None for v in assign.values()), repaired_admitted=n_adm,
                          price_mean=float(price[list(SHARED_ARCS)].mean()),
                          price_max=float(price[list(SHARED_ARCS)].max())))
        if n_adm > best_n:
            best_n, best = n_adm, dict(assign)
        # pembaruan harga subgradien
        rho = rho0 / math.sqrt(t + 1)
        new_price = price.copy()
        for l in SHARED_ARCS:
            new_price[l] = max(0.0, price[l] + rho * (load[l] - C) / C)
        dprice = np.linalg.norm(new_price - price) / max(np.linalg.norm(price), 1e-9)
        price = new_price
        load_prev = load
        if not use_price:
            pass
        elif over <= tol or (t > 0 and dprice < eps_pi):
            break
    info = dict(rounds=len(trace), work=work, pods_seq_s=t_seq, pods_par_s=t_par)
    return best, info, trace


def repair(flows, assign, locked=None):
    """coordinate() rilis, dengan beban terkunci (tahap Lex) diperhitungkan sebagai flow semu."""
    if locked is None or not locked.any():
        return L.coordinate(assign, flows)
    ghosts = []
    for l in np.where(locked > 0)[0]:
        ghosts.append(dict(id=-1 - int(l), demand=float(locked[l]), w=99, cls="LOCK",
                           paths=[[int(l)]], pdelay=[0.0], pod=-1))
    a = dict(assign); a.update({g["id"]: 0 for g in ghosts})
    out = L.coordinate(a, ghosts + flows)
    return {f["id"]: out[f["id"]] for f in flows}


# ---------------------------------------------------------------- metode lengkap
def run_mas_price(flows, seed, Dtot, cc, lam=None, **kw):
    lam = dict(lam or R.LAM)
    t0 = time.perf_counter()
    best, info, trace = price_loop(flows, seed, Dtot, cc, lam, **kw)
    t1 = time.perf_counter()
    final = L.coordinate(best, flows)
    info.update(coord_s=time.perf_counter() - t1, total_s=time.perf_counter() - t0)
    return final, info, trace


def run_mas_price_lex(flows, seed, Dtot, cc, lam=None, **kw):
    """Pentahapan EF -> AF -> BE. Admisi tiap tahap dikunci (setelah repair tahap) sebelum tahap berikut."""
    lam = dict(lam or R.LAM); lam["f"] = 0.0
    t0 = time.perf_counter()
    locked = np.zeros(NL); assign_all = {}; infos, traces = [], []
    for si, k in enumerate(CLASSES):
        fk = [f for f in flows if f["cls"] == k]
        if not fk:
            continue
        best, info, trace = price_loop(fk, seed, Dtot, cc, lam, locked_load=locked, stage_tag=si + 1, **kw)
        rep = repair(fk, best, locked)
        assign_all.update(rep)
        locked = locked + _load_of(fk, rep)
        infos.append(info); traces += [dict(stage=k, **r) for r in trace]
    final = L.coordinate(assign_all, flows)
    info = dict(rounds=sum(i["rounds"] for i in infos), work=sum(i["work"] for i in infos),
                pods_seq_s=sum(i["pods_seq_s"] for i in infos), pods_par_s=sum(i["pods_par_s"] for i in infos),
                total_s=time.perf_counter() - t0)
    return final, info, traces
