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

def set_topology(topo):
    """Pasang topologi (k = 4 bawaan, atau Fat-Tree k dari extensions/k6_priority_emulation/fattree_k.py).
    Memperbarui L.TOPO (dipakai metrics), jumlah arc, dan partisi arc lokal/bersama."""
    global NL, UP, LOCAL_ARCS, SHARED_ARCS
    L.TOPO = topo
    NL = len(topo["links"])
    UP = np.zeros(NL, dtype=bool)
    for (u, v), lid in topo["links"].items():
        UP[lid] = _is_up(u, v)
    LOCAL_ARCS = set(np.where(UP)[0].tolist())      # arc naik
    SHARED_ARCS = set(np.where(~UP)[0].tolist())    # arc turun

set_topology(L.TOPO)


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
def build_pod_qubo(sub, bg_load, cap_local, price, Dtot, cc, lam, mu, prev=None, kappa=0.0):
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
        # suku proksimal kappa*(z - z_prev)^2 = kappa*z*(1 - 2 z_prev) + konstanta (linear, tanpa kopling baru)
        if kappa and prev is not None and f["id"] in prev:
            pp = prev[f["id"]]
            q.add(y, y, kappa * (1 - 2 * (pp is not None)))
            for p, xv in enumerate(xs):
                q.add(xv, xv, kappa * (1 - 2 * (pp == p)))
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
def price_loop(flows, seed, Dtot, cc, lam, solver="sqa", prm=None, pod_sweeps=None, rho0=10.0, T_max=8,
               tol=0.02, eps_pi=1e-3, mu_mode="analytic", mu_const=20.0, eps_mu=0.1,
               locked_load=None, use_price=True, stage_tag=0,
               kappa=0.0, alpha=1.0, fixed_seed=False, gauss_seidel=False,
               step="decay", rho_mu_mult=None):
    """Koordinasi harga antar-agen pod. Mengembalikan (assign_terbaik, info, trace).
    Keluaran terbaik = putaran dengan jumlah flow diterima terbanyak setelah repair
    (deterministik, dapat dihitung oleh controller); info['last_assign'] = putaran terakhir.
    Stabilisasi (Subbab 6.5.7):
      kappa        : bobot suku proksimal terhadap keputusan putaran sebelumnya (inersia)
      alpha        : rata-rata primal beban, load_avg <- (1-alpha) load_avg + alpha load (1 = tanpa rata-rata)
      fixed_seed   : benih sampler sama di setiap putaran (mengurangi derau antar-putaran)
      gauss_seidel : pod diselesaikan berurutan dan langsung melihat keputusan baru pod sebelumnya
    Langkah harga (Subbab 6.5.10):
      step='decay' : rho_t = rho0 / sqrt(t+1)   (varian awal)
      step='const' : rho_t = rho0               (tanpa peluruhan)
      rho_mu_mult  : bila diisi, rho0 = rho_mu_mult * median(mu_f putaran 0), agar harga sebanding
                     dengan reward admisi yang harus dikalahkan untuk menolak flow"""
    prm = dict(prm or R.TUNED)
    if pod_sweeps:
        prm["pod_sweeps"] = int(pod_sweeps)
    locked = np.zeros(NL) if locked_load is None else locked_load
    cap_eff = np.maximum(C - locked, 0.0)
    pods = sorted({f["pod"] for f in flows})
    price = np.zeros(NL)
    assign = {}
    load_prev = locked.copy()
    load_avg = None
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
        cur = dict(assign)                  # keputusan terkini (diperbarui per pod pada Gauss-Seidel)
        for qd in pods:
            sub = [f for f in flows if f["pod"] == qd]
            if gauss_seidel and cur:
                tot = _load_of(flows, cur) + locked
            else:
                tot = load_prev
            own = _load_of(sub, cur) if cur else np.zeros(NL)
            bg = tot - own                  # beban pod lain + beban terkunci
            t0 = time.perf_counter()
            qb = build_pod_qubo(sub, bg, cap_eff, price if use_price else np.zeros(NL), Dtot, cc, lam, mu,
                                prev=(assign if t > 0 else None), kappa=kappa)
            s = seed * 1000 + stage_tag * 100 + (0 if fixed_seed else t * 10) + qd
            if solver == "sqa":
                smp = R.sample_sqa(qb, prm["pod_reads"], prm["pod_sweeps"], s, prm["sqa_beta"], prm["sqa_gamma"])
                work += len(qb.idx) * R.P * prm["pod_sweeps"] * prm["pod_reads"]
            else:
                smp = R.sample_sa(qb, prm["pod_reads"], prm["pod_sweeps"], s, prm["sa_bmin"], prm["sa_bmax"])
                work += len(qb.idx) * prm["pod_sweeps"] * prm["pod_reads"]
            dec = L.decode(qb, smp, sub)
            new_assign.update(dec)
            if gauss_seidel:
                cur.update(dec)
            pod_times.append(time.perf_counter() - t0)
        t_seq += sum(pod_times); t_par += sum(pod_times) if gauss_seidel else max(pod_times)
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
        trace.append(dict(stage=("ALL" if stage_tag == 0 else CLASSES[stage_tag - 1]), round=t, max_overload_shared=over, pct_changed=changed,
                          raw_admitted=sum(v is not None for v in assign.values()), repaired_admitted=n_adm,
                          price_mean=float(price[list(SHARED_ARCS)].mean()),
                          price_max=float(price[list(SHARED_ARCS)].max())))
        if n_adm > best_n:
            best_n, best = n_adm, dict(assign)
        # pembaruan harga subgradien pada beban rata-rata primal
        load_avg = load.copy() if load_avg is None else (1 - alpha) * load_avg + alpha * load
        if t == 0 and rho_mu_mult is not None and mu:
            rho0 = rho_mu_mult * float(np.median(list(mu.values())))
        rho = rho0 if step == "const" else rho0 / math.sqrt(t + 1)
        new_price = price.copy()
        for l in SHARED_ARCS:
            new_price[l] = max(0.0, price[l] + rho * (load_avg[l] - C) / C)
        dprice = np.linalg.norm(new_price - price) / max(np.linalg.norm(price), 1e-9)
        price = new_price
        load_prev = load
        if not use_price:
            pass
        elif over <= tol or (t > 0 and dprice < eps_pi):
            break
    info = dict(rounds=len(trace), work=work, pods_seq_s=t_seq, pods_par_s=t_par, last_assign=dict(assign), rho0_used=rho0)
    return best, info, trace


def repair(flows, assign, locked=None):
    """Aturan coordinate() rilis (urutan prioritas, pass 1 reroute/drop, pass 2 greedy fill),
    dengan beban terkunci tahap sebelumnya sebagai beban awal yang TIDAK dapat dibuang.
    Tanpa beban terkunci, hasilnya identik dengan L.coordinate()."""
    if locked is None or not locked.any():
        return L.coordinate(assign, flows)
    order = sorted(flows, key=lambda f: (-f["w"], -f["demand"]))
    load = {int(l): float(locked[l]) for l in np.where(locked > 0)[0]}
    fits = lambda f, p: all(load.get(l, 0.0) + f["demand"] <= C + 1e-9 for l in f["paths"][p])
    def add(f, p, s=1.0):
        for l in f["paths"][p]:
            load[l] = load.get(l, 0.0) + s * f["demand"]
    final = {f["id"]: assign.get(f["id"]) for f in flows}
    for f in order:
        if final[f["id"]] is not None:
            add(f, final[f["id"]])
    for f in order:
        p = final[f["id"]]
        if p is None:
            continue
        if any(load.get(l, 0.0) > C + 1e-9 for l in f["paths"][p]):
            add(f, p, -1.0)
            alt = next((p2 for p2 in range(len(f["paths"])) if p2 != p and fits(f, p2)), None)
            final[f["id"]] = alt
            if alt is not None:
                add(f, alt)
    for f in order:
        if final[f["id"]] is None:
            p2 = next((p2 for p2 in range(len(f["paths"])) if fits(f, p2)), None)
            if p2 is not None:
                add(f, p2); final[f["id"]] = p2
    return final


# ---------------------------------------------------------------- metode lengkap
def run_mas_price(flows, seed, Dtot, cc, lam=None, **kw):
    lam = dict(lam or R.LAM)
    t0 = time.perf_counter()
    best, info, trace = price_loop(flows, seed, Dtot, cc, lam, **kw)
    t1 = time.perf_counter()
    final = L.coordinate(best, flows)
    info["last_final"] = L.coordinate(info.pop("last_assign"), flows)
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
        info.pop("last_assign", None)
        rep = repair(fk, best, locked)
        assign_all.update(rep)
        locked = locked + _load_of(fk, rep)
        infos.append(info); traces += trace
    final = L.coordinate(assign_all, flows)
    info = dict(rounds=sum(i["rounds"] for i in infos), work=sum(i["work"] for i in infos),
                pods_seq_s=sum(i["pods_seq_s"] for i in infos), pods_par_s=sum(i["pods_par_s"] for i in infos),
                total_s=time.perf_counter() - t0)
    return final, info, traces


def run_v2_restarts(flows, seed, Dtot, cc, K, lam=None, mu=0.0, prm=None):
    """Kontrol: MAS-QA-v2 (tanpa koordinasi) dengan K restart independen, ambil yang menerima flow
    terbanyak setelah repair. Memisahkan efek koordinasi dari efek 'terbaik dari beberapa sampel'."""
    lam = dict(lam or R.LAM); prm = prm or R.TUNED
    best, best_n, work, t_seq = None, -1, 0.0, 0.0
    for k in range(K):
        fin, inf = run_v2_k(flows, seed + 100000 * k, Dtot, cc, lam, mu, prm)
        n = sum(v is not None for v in fin.values())
        work += inf["work"]; t_seq += inf["pods_seq_s"]
        if n > best_n:
            best_n, best = n, fin
    return best, dict(rounds=K, work=work, pods_seq_s=t_seq)


def run_v2_k(flows, seed, Dtot, cc, lam=None, mu=0.0, prm=None):
    """MAS-QA-v2 (dekomposisi pod sumber, b_l = 0, tanpa koordinasi) untuk sembarang jumlah pod.
    Identik dengan r2lib.pod_solve pada k = 4."""
    lam = dict(lam or R.LAM); prm = prm or R.TUNED
    assign, work, t_seq, t_max = {}, 0.0, 0.0, 0.0
    for qd in sorted({f["pod"] for f in flows}):
        sub = [f for f in flows if f["pod"] == qd]
        t0 = time.perf_counter()
        qb = R.add_bonus(L.build_qubo(sub, L.TOPO, np.zeros(NL), Dtot, cc, lam), sub, mu)
        smp = R.sample_sqa(qb, prm["pod_reads"], prm["pod_sweeps"], seed * 10 + qd, prm["sqa_beta"], prm["sqa_gamma"])
        work += len(qb.idx) * R.P * prm["pod_sweeps"] * prm["pod_reads"]
        assign.update(L.decode(qb, smp, sub))
        dt = time.perf_counter() - t0; t_seq += dt; t_max = max(t_max, dt)
    return L.coordinate(assign, flows), dict(rounds=1, work=work, pods_seq_s=t_seq, pods_par_s=t_max)
