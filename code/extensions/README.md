# Extensions: k=6 topology, hard priority penalty, emulation, and variants

These scripts extend the release code in `code/` (masqa_lib.py, exp.py). The release code is unchanged.

## Layout
- `k6_priority_emulation/`
  - `fattree_k.py`: Fat-Tree(k) topology, candidate paths and traffic generator. For k=4 it reproduces `masqa_lib` exactly (checked by `check_k4.py`).
  - `run_k.py`: k-generic runner for ECMP, greedy, MAS-QA (pod decomposition plus coordinator), monolithic SQA and SA. Usage: `python3 run_k.py <k> <N> <D_total> <seed_from> <seed_to> <methods> <out.csv>`. Methods: `ECMP-hash,ECMP+adm,Greedy-only,MAS-QA,MAS-decomp-only,SQA-mono,SA-mono`.
  - `prio.py`: hard-priority penalty. For each pair (higher-class flow g, lower-class flow f) whose candidate paths share an arc, it adds `lam_p * y_f * (1 - y_g)` to the QUBO. It is a large soft penalty, not an exact constraint.
  - `run_prio.py`: priority grid on k=4 S2. Usage: `python3 run_prio.py <lam_p> <seed_from> <seed_to> <out.csv>`.
  - `emu2.py`, `emu2_run.py`, `emu2_probe.py`: Mininet emulation with kernel forwarding. Every switch is a Mininet node with IP forwarding. Each flow has its own source and destination alias, and its path is a set of static /32 routes. Flows are driven with iperf3 UDP at scaled demand. Requires Linux, root, and the packages `mininet`, `iperf3`, `ethtool`, `iproute2`. The OpenFlow/Open vSwitch approach was tried and abandoned because of datapath artefacts; it is not included.
- `variants/`: heterogeneous-capacity, weighted-objective and priority-first repair variants (see `variants/README.md`).
- `results_k6_priority_emulation/`: CSV outputs used in the k=6, priority and emulation sections of the manuscript.

## Settings used for the reported results
- SQA in the extension scripts uses beta = 0.5, gamma = 1.0, P = 16 (the tuned setting of the manuscript). The release `solve()` uses beta = 5, gamma = 3 (the initial setting). Both are reported in the manuscript.
- SA uses the tuned schedule beta in [0.1, 10], 10 reads of 80,000 sweeps (matched sweep budget with SQA: 10 reads x 5,000 sweeps x 16 Trotter slices).
- Pod solves: 10 reads x 500 sweeps (pod_reads, pod_sweeps in masqa_lib.BUDGETS["paper"]).
- k=6 scenario: N = 338 flows, D_tot = 4313.5 Mbps (S2 intensity scaled by 54/16 hosts), seeds 42-71.
- Normalised bandwidth weight in the energy check: lambda_b = 2N = 200 for S2 (N = 100 flows).

## Reproduction (sandbox versions: Python 3.13, NumPy 2.5.3, SciPy 1.18.1, OpenJij 0.12.2)
```
cd code/extensions/k6_priority_emulation
python3 check_k4.py                                      # k=4 equivalence check
python3 run_k.py 6 338 4313.5 42 72 ECMP-hash,ECMP+adm,Greedy-only,MAS-QA,MAS-decomp-only,SQA-mono k6_main.csv
python3 run_k.py 6 338 4313.5 42 72 SA-mono k6_sa.csv    # about 6.5 min per seed
python3 run_prio.py 100 42 72 prio_lp100.csv
sudo python3 emu2_run.py 42 72 emu2_k4_S2.csv           # needs root and Mininet
```

## Known limitations
- Emulation: 30 seeds, demands and capacities scaled by 0.1, iperf3 UDP only, no propagation delay (netem unavailable in the sandbox). Loss is measured per flow; latency is not measured.
- The priority penalty did not reduce EF loss in any tested setting (see manuscript, "Hard priority constraint").
- Timings are from a two-core sandbox and are not controller benchmarks.
