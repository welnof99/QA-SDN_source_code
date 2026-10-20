# Data dictionary

All files are UTF-8 CSV. One row is one run: one instance (scenario, scale N, or small-instance setting), one seed, and one method. Data are released under CC BY 4.0; code is released under MIT (see `LICENSE`).

## Metric definitions (from `code/masqa_lib.py`, function `metrics`)

| Column | Definition | Unit |
|---|---|---|
| `PL_flow` | Share of flows not admitted (rejected or dropped by repair) | % |
| `BWL` | Bandwidth-weighted loss: 100 · (1 − served demand / total demand D_tot) | % |
| `latency_ms` | Priority-weighted mean propagation delay of served flows, weights w = 3 (EF), 2 (AF), 1 (BE) | ms |
| `latency_p95_ms` | 95th-percentile propagation delay of served flows | ms |
| `throughput_mbps` | Total demand of served flows | Mbps |
| `JFI` | Jain's fairness index over the 16 host egress loads (dimensionless, 0–1) | – |
| `CoV` | Population standard deviation of host egress loads divided by their mean | % |
| `PL_EF`, `PL_AF`, `PL_BE` | Flow loss within each traffic class | % |

Each solution is checked for link-capacity feasibility before metrics are computed (the function asserts this).

## Timing and work columns (recorded, not validated)

`pod_parallel_s`, `pod_sequential_s`, `coord_s`, `solve_s`, `time_s` are wall-clock times on the machine used. They are **not validated** and make no claim in the article; Section 4.7 uses the annealing-work measures instead. `pod_vars`, `pod_work`, `mono_vars` and `matched_sweeps` are problem sizes and spin-update counts.

## Files

### Main protocol (Sections 4.1–4.4)

| File | Rows | Scenarios and seeds | Methods |
|---|---|---|---|
| `matched_all.csv` | 630 | S1, S2, S3; 30 seeds each (42–71) | `ECMP+adm`, `Greedy-only`, `SA-mono-m+repair`, `SQA-mono-v2+repair`, `MAS+SA-m`, `MAS-QA-v2`, `ITER-SQA-v2-R3` |
| `eval_sa_mono_tuned.csv` | 90 | S1, S2, S3; 30 seeds each (42–71) | `SA-mono-mt+repair` (tuned schedule, β ∈ [0.1, 10]) |

`matched_all.csv` holds the matched-compute runs. `eval_sa_mono_tuned.csv` holds the tuned-SA comparator on the same seeds and is analysed together with it.

### Earlier protocol (Section 4.2 equal-work control)

| File | Rows | Scenarios | Methods |
|---|---|---|---|
| `main_S1_S2.csv` | 780 | S1, S2; 30 seeds | `ECMP+adm`, `ECMP-hash`, `Greedy-only`, `MAS+SA`, `MAS-QA`, `MAS-QA-tuned`, `MAS-decomp-only`, `SA-mono raw`, `SA-mono+repair`, `SQA-mono raw`, `SQA-mono+repair`, `SQA-mono-matched raw`, `SQA-mono-matched+repair` |
| `main_S3.csv` | 390 | S3; 30 seeds | Same 13 methods as `main_S1_S2.csv` |

These files come from the earlier SQA setting (β = 5, Γ = 3). "raw" means the solver output before repair. The equal-work control rows are `SQA-mono-matched*`.

### Scale study (Section 4.5, Figure 10)

| File | Rows | Content |
|---|---|---|
| `scale_full.csv` | 495 | N ∈ {50, 100, 200, 300} flows at constant per-flow demand 12.8 Mbps. Methods: `ECMP+adm`, `Greedy-only`, `SA-mono-mt+repair`, `SQA-mono-v2+repair`, `MAS-QA-v2`. Column `N` replaces `scenario`. Seeds: 25 per size for N = 50, 100, 200 and 24 for N = 300. |

### Exact small-instance reference (Sections 3.9 and 4.6, Figure 11)

| File | Rows | Content |
|---|---|---|
| `small_v2_all.csv` | 560 | N ∈ {8, 12}, load ratio r ∈ {0.8, 1.6}, seeds 42–61 (20 per setting). Total demand D_tot = r · 12.8 · N Mbps. Methods: `OPT-count` and `OPT-bw` (MILP optimum, HiGHS via SciPy), `ECMP+adm`, `Greedy-only`, `MAS-QA`, `SA-mono-mt+repair`, `SQA-mono-v2+repair`. Columns: `N`, `ratio`, `seed`, `method`, `PL_flow`, `BWL`. |

### Solver tuning and validation (Section 3.5, Figure 3)

| File | Rows | Content |
|---|---|---|
| `val2_sqa_mono.csv` | 60 | SQA grid on validation seeds 105–114: `beta`, `gamma`, `PL_flow`. |
| `tune_sa_mono_matched.csv` | 20 | SA schedule candidates on validation seeds 100–104: `beta_min`, `beta_max`, `PL_flow`. |
| `diagB_validation.csv` | 50 | SA validation grid on seeds 100–104 (β ∈ {1, 5, 10}, γ ∈ {1, 3, 6}): `seed`, `beta`, `gamma`, `PL_flow`, `BWL`, `JFI`, `method`. |
| `diagB_validation_low.csv` | 50 | Same layout, lower grid (β ∈ {0.25, 0.5, 1}, γ ∈ {0.5, 1, 2}). |

The `gamma` column is stored as recorded from the validation grid. The article's SA results use the schedule parameters given in Section 3.5.

### Iterated pod solves (Section 4.2, Figure 6)

| File | Rows | Content |
|---|---|---|
| `diagA_jacobi.csv` | 20 | 10 seeds × 2 solvers (`sa`, `sqa`): `seed`, `method`, `mode`, `PL_final`, and `change`, a list with the fraction of decision variables that changed in each of the re-solve rounds. |

## Reproducibility notes

- `code/exp.py` still contains an earlier optimum step that writes `optimum_small.csv`. That file used the superseded demand rule and is **not** used by the article. Use `code/small_instances.py` to regenerate `small_v2_all.csv`.
- Tuning seeds (100–114) are disjoint from evaluation seeds (42–71 and the scale and small-instance seeds).
