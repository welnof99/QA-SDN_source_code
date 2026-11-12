# Extension variants for the revised IJIES manuscript (not part of the released code)

These files extend the released code (`code/masqa_lib.py`, `code/exp.py`) for the reviewer
requests on external validity, objective weighting and repair ordering. The released code is
unchanged. Nothing here has been pushed to the GitHub repository.

## What is added

| Variant | Where | Description |
|---|---|---|
| Per-arc capacity `CAP` | `code/masqa_var.py` | Replaces the scalar `LINK_CAP` in `build_qubo`, `coordinate`, `ecmp_admission`, `loss_on_overload`, `metrics`. `set_hetero_core(25.0)` sets agg–core arcs to 25 Mbps; `set_homogeneous()` restores 50 Mbps. |
| Priority-weighted H_bw | `BW_WEIGHTED` flag in `masqa_var.py` | Uses `w_f d_f / Σ_k w_k D_k` instead of `d_f / D_tot`. Default `False` reproduces the released objective. |
| Least-loaded greedy | `least_loaded()` in `masqa_var.py` | Capacity-aware heuristic: flows in priority order; each takes the candidate path with the lowest peak utilisation among paths that fit. |
| Priority-first repair | `coordinate_prio()` in `scripts/job_prio_repair.py` | Visits flows from lowest to highest priority, removes overloaded flows, then refills in priority order. |
| Pass-1 diagnostic | `scripts/job_repair_diag.py` | Counts pass-1 removals and whether the overload is caused only by lower-priority load. |

## Reproduction

Requires the released code, OpenJij 0.12.2, SciPy, NumPy, pandas. Place `code/masqa_var.py` and
`code/exp_var.py` next to the released `masqa_lib.py`/`exp.py` (or change `sys.path` in
`scripts/common_var.py`), then run from the directory that contains the scripts:

    python3 job_var_A.py          # heterogeneous capacity, S2, seeds 42-71
    python3 job_var_B.py          # homogeneous vs heterogeneous x demand vs priority H_bw
    python3 job_var_C.py          # lambda_b = 2, 10, 20 with priority-weighted H_bw
    python3 job_prio_repair.py S1 # priority-first repair vs current coordinator (repeat S2, S3)
    python3 job_repair_diag.py    # pass-1 diagnostic on S2

The scripts use the same tuned settings as the manuscript: SQA beta = 0.5, Gamma = 1.0, P = 16,
10 reads x 5,000 sweeps; SA beta in [0.1, 10], 10 reads x 80,000 sweeps. The `set_sqa` helper in
`common_var.py` sets SQA parameters that the released `solve()` does not expose (see the
reproduction note in the manuscript: the released `solve()` uses beta = 5, Gamma = 3).

Note: `common_var.py` has an absolute `sys.path` entry pointing to the author's scratch directory.
Change it to the local path of `code/` before running.

## Results in `results/`

- `heterogeneous_capacity_S2.csv`: six methods, S2, 30 seeds, agg–core arcs at 25 Mbps.
- `objective_weighting_S2.csv`: SQA monolithic, demand- vs priority-weighted H_bw, both fabrics.
- `priority_weight_lambda_b_S2.csv`: priority-weighted H_bw at lambda_b = 2, 10, 20 (homogeneous).
- `priority_first_repair_S1-S3.csv`: current coordinator vs priority-first repair, monolithic SQA.
- `repair_pass1_diagnostic_S2.csv`: per-seed pass-1 removal counts by class.

## Limitations

- Only the k = 4 Fat-Tree was used. Other topology sizes are not implemented.
- No emulation was run. All metrics are surrogate metrics on the admission model.
- The priority-weighted term changes the QUBO coefficients only. A hard priority constraint was not implemented.

## Script dependencies

- `job_prio_repair.py` and `job_repair_diag.py` import `common.py`, which loads the released
  `masqa_lib` from the released code folder (set `sys.path` in `common.py` to that folder).
- `job_var_A.py`, `job_var_B.py`, `job_var_C.py` import `common_var.py`, which loads the variant
  modules from `code/`.
