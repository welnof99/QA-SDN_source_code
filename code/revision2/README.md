# Second-round revision scripts

Scripts that produced the second-round results in `data/revision2/`. Run them from this folder
(`python3 e1_resume2.py`, etc.). Each script writes to `../../data/revision2/` and is resumable per seed
where marked. They import the release library `code/masqa_lib.py` through `r2lib.py`.

| Script | Purpose | Output (in `data/revision2/`) |
|---|---|---|
| `d_enum.py` | Exhaustive check of a 3-flow, 2-arc QUBO (19 variables, 2^19 states) | `d_enum.json` |
| `e4_calib_valid.py` | Admission-bonus calibration, mu in {0,5,10,20,40,80}, validation seeds 100–104, S2 | `e4a_mu_validation.csv` |
| `e1_equalwork.py` | Equal-work control with tuned settings, S1 (first run, all seeds 42–71) | `e1_equalwork_tuned.csv` (S1 rows) |
| `e1_resume2.py` | Same control for S2 and S3, resumable per seed | `e1_equalwork_tuned_S23.csv` |
| `e4b_resume.py` | Evaluation of mu* = 20 on seeds 42–71, S1–S3 (resumable) | `e4b_mu20_eval.csv` |
| `e23_resume.py` | End-to-end timing and quality-versus-time on S2, seeds 42–71 (resumable); run alone | `e23_timing_curves.csv`, `e23_summary.csv` |

`e1_equalwork_tuned_ALL.csv` is the S1 rows of `e1_equalwork_tuned.csv` plus the S2/S3 rows of `e1_equalwork_tuned_S23.csv`.
`revision_comparisons.csv` holds the paired statistics used in the manuscript. The baseline (mu = 0) SA values come from
`data/eval_sa_mono_tuned.csv`; two seeds were rerun and reproduced exactly.

Notes
- The "MAS-QA-tuned" label in older files denotes the weight-grid variant, not the tuned solver with baseline weights used here.
- Timing was measured alone on a two-core sandbox (Python 3.13.18). Pod time includes QUBO construction of each pod.
- Packages: see `../../requirements-lock.txt`.
