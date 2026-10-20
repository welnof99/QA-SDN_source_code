import re, nbformat as nbf
src = open('masqa_all.py').read()
parts = re.split(r'^# ===== CELL: (.*?) =====\n', src, flags=re.M)
chunks = [(parts[i], parts[i+1]) for i in range(1, len(parts), 2)]
md = {
 "config": "## 1. Configuration\nBudget presets, scenarios (Table 3), seeds and corrected penalty weights. Set `MASQA_BUDGET=smoke` (Colab: `os.environ` before running, or edit `BUDGET`) for a quick check. The `paper` preset follows the manuscript where it states values; the remaining values (pod reads, monolithic SQA reads) are assumptions and are listed here.",
 "Fat-Tree k=4 topology and candidate paths": "## 2. Topology\nFat-Tree k=4: 16 hosts, 20 switches, 48 physical links = 96 directed arcs. Each arc has 50 Mbps capacity (full duplex). Delays are sampled once per physical link (topology seed 42) and shared by both directions.",
 "traffic generation": "## 3. Traffic\nPareto(a = 2, x_min = 2 Mbps) demands, scaled to each scenario's total D_total. DiffServ classes are 10 / 30 / 60 % (EF / AF / BE).",
 "QUBO builder (corrected formulation; see manuscript Section 3.2)": "## 4. Corrected QUBO\nH = λA·H_A + λc·H_cap + λl·H_bal + λt·H_lat + λb·H_bw + λf·H_fair, with λ = (10, 10, 5, 3, 2, 1).\n- **H_A** one path per admitted flow.\n- **H_cap** hard capacity, in utilization units, through binary slack bits.\n- **H_bal** = |E|·Var(u), written as Σu² − (1/|E|)(Σu)², which is quadratic.\n- **H_lat** priority-weighted normalized delay.\n- **H_bw** unserved bandwidth (d/D_tot)(1 − y).\n- **H_fair** parity of served-bandwidth share across classes, ρ_k = Σ d·y / D_k. This replaces an earlier count-based surrogate that was zero when nothing was served and therefore rewarded rejecting every flow.\n\nThe energy offset (constant terms) is not stored, so reported energies are relative.",
 "solver wrapper (OpenJij SQA / SA)": "## 5. Solvers\nOpenJij SQA (Trotter = 16) for the pods and the SQA monolithic baseline; OpenJij SA for the SA monolithic baseline. The annealing schedule is OpenJij's default, which anneals the transverse field from `gamma`. This only approximates the manuscript's geometric schedule (Γ0 = 3.0 → Γf = 0.001). `beta` and `gamma` are fixed at 5.0 and 3.0 and have not been tuned.",
 "coordinator (priority-ordered repair + greedy fill)": "## 6. Global Coordinator\nResolves overloads in priority order (EF → AF → BE, then demand). A flow is rerouted to the next feasible path or dropped. Unserved flows are then admitted greedily wherever a feasible path exists.",
 "baselines (ECMP variants)": "## 7. Baselines\n- **ECMP-hash**: uniform random path, no admission check. A flow is lost if it crosses an overloaded arc. This is a strict all-or-nothing reading of the manuscript's ECMP.\n- **ECMP+adm**: random path, admitted in arrival order if it fits.\n- **Greedy-only**: the coordinator alone, with no QUBO. This isolates the contribution of the optimizer.\n- **SA-mono / SQA-mono**: one monolithic solve. The `raw` variant counts flows on overloaded arcs as lost. The `+repair` variant passes the same sample through the coordinator, which isolates the effect of repair.\n\n**Not implemented here:** MADDPG, GNN+RL, PPO, ACO and GA. The manuscript reports them, so they must be added before Tables 5–7 can be reproduced.",
 "pipelines and metrics": "## 8. Pipelines and metrics\n- **PL_flow**: percent of flows not served.\n- **BWL**: percent of demand not served.\n- **Latency**: priority-weighted mean delay of served flows (ms).\n- **Throughput**: served demand (Mbps).\n- **JFI / CoV**: over the 16 server egress loads. CoV uses the population SD.\n\nThe pod stage is timed per pod, so both the parallel (max) and the sequential (sum) wall-clock are reported.",
 "experiment runner": "## 9. Main experiment (evaluation seeds 42–51)\nRuns every scenario and method and writes `masqa_per_run_results.csv`. Expect about 20–30 minutes on Colab with the `paper` preset.",
 "statistics (paired over seeds; Bonferroni over MAS-QA comparisons)": "## 10. Paired statistics\nPaired t-test and exact Wilcoxon per comparison. The Bonferroni multiplier is the number of MAS-QA comparisons. Significance is p_Bon ≤ 0.05.",
 "validation-seed tuning of λ (S2 only). Choose weights here, NOT on evaluation seeds.": "## 11. Weight tuning on validation seeds (100–104)\nChoose weights here, not on the evaluation seeds in Section 9. The grid reproduces the six configurations of the manuscript's Table 9.",
 "verification (exact check of the formulation on a tiny instance)": "## 12. Formulation check\nExhaustive enumeration on a 3-flow, 2-link instance (8,192 states) confirms the minimum energy of the QUBO form. It checks the energy function only; it does not validate the Fat-Tree experiments.",
 "consistency checks on the output": "## 13. Consistency check\nWith JFI and CoV computed from the same load vector, JFI = 1/(1 + CoV²) holds exactly. The manuscript's S1 and S3 values did not satisfy this identity.",
 "diagnostics (flows that cannot fit on any path are infeasible regardless of method)": "## 14. Diagnostics\nA flow larger than one arc's capacity can never be admitted, so this share is a lower bound on PL_flow for every method.",
 "plots": "## 15. Plot",
 "export": "## 16. Export",
}
cells = [nbf.v4.new_markdown_cell(
"""# MAS-QA-SDN: reference notebook for the corrected formulation

This notebook implements the corrected formulation from `paper_IJIES_revisi_v2.docx`:
- **QUBO:** five objective terms and a one-hot consistency constraint. Hard capacity is enforced with binary slack bits.
- **Decomposition:** four pod subproblems solved with OpenJij SQA, then a Global Coordinator.
- **Baselines:** ECMP-hash, ECMP+admission, Greedy-only, and SA and SQA monolithic, each with and without repair.
- **Statistics:** paired tests over seeds, Bonferroni correction, and validation-seed tuning of λ.

**Status.** The results are new runs of the corrected model. They are not the manuscript's numbers, which came from the previous formulation and must be replaced. The model also differs from the manuscript in two places: capacity is per directed arc, and H_fair is defined on served-bandwidth share.

**Not included.** MADDPG, GNN+RL, PPO, ACO and GA (Section 7).

**Findings to check at the paper budget.** Repaired monolithic solvers and Greedy-only are close to MAS-QA in the smoke test. If that holds, most of the gain comes from the coordinator rather than from the QUBO solver, which is the point raised by Reviewer 2.

**How to run.** Runtime → Run all. The first cell installs OpenJij. The `paper` preset takes about 20–30 minutes."""),
 nbf.v4.new_code_cell("# Colab setup: install dependencies (run once per session)\n!pip install -q openjij scipy pandas matplotlib")]
for name, body in chunks:
    if name in md: cells.append(nbf.v4.new_markdown_cell(md[name]))
    cells.append(nbf.v4.new_code_cell(body.strip("\n")))
nb = nbf.v4.new_notebook(); nb.cells = cells
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nb.metadata["colab"] = {"provenance": []}
nbf.validate(nb)
nbf.write(nb, 'MASQA_SDN_corrected.ipynb')
print("cells:", len(cells))
