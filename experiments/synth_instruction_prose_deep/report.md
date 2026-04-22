# Experiment Report: synth_instruction_prose_deep

**Date:** 2026-04-22 01:20 UTC  
**Factor:** `SYNTH_INSTRUCTION variant`  levels: ['baseline', 'prose_grounded_deep']  
**Tasks:** ['T_A', 'T_B', 'T_C']  **Replications:** 3  
**Hypothesis:** A prose instruction that explicitly demands 4-paragraph implementation depth recovers depth_r1 to baseline levels while preserving the grounded_r1 gain from prose_depth, improving composite score_r1 by >= 0.2 points over baseline.  
**Falsified if:** mean score_r1 delta < 0.2

---

## Hypothesis Verdict

**FALSIFIED**  
Observed: delta=-0.034 (baseline=7.77, prose_grounded_deep=7.73)  
Threshold: < 0.2

---

## Results Table

| Task | Treatment | n | score_r1 (mean±sd) | score_final (mean±sd) | rounds (mean) | PASS rate |
|------|-----------|---|-------------------|----------------------|---------------|-----------|
| T_A | baseline | 3 | 7.70±0.17 | 7.50±0.00 | 3.0 | 0% |
| T_A | prose_grounded_deep | 3 | 7.60±0.17 | 7.60±0.17 | 3.0 | 0% |
| T_B | baseline | 3 | 7.80±0.00 | 7.80±0.00 | 2.0 | 0% |
| T_B | prose_grounded_deep | 3 | 8.00±0.35 | 8.00±0.35 | 2.3 | 0% |
| T_C | baseline | 3 | 7.80±0.00 | 7.33±0.42 | 2.7 | 0% |
| T_C | prose_grounded_deep | 3 | 7.60±0.17 | 7.60±0.17 | 2.3 | 0% |

---

## Per-Dimension Analysis (r1 means)

| Task | Treatment | relevance | completeness | depth | grounded | specificity | structure |
|------|-----------|---|---|---|---|---|---|
| T_A | baseline | 9.0 | 8.0 | 6.7 | 6.0 | 8.0 | 9.0 |
| T_A | prose_grounded_deep | 8.3 | 7.3 | 6.3 | 8.0 | 8.0 | 8.3 |
| T_B | baseline | 9.0 | 8.0 | 7.0 | 6.0 | 8.0 | 9.0 |
| T_B | prose_grounded_deep | 9.0 | 7.7 | 6.7 | 8.0 | 8.7 | 9.0 |
| T_C | baseline | 9.0 | 8.0 | 7.0 | 6.0 | 8.0 | 9.0 |
| T_C | prose_grounded_deep | 8.3 | 7.3 | 6.3 | 8.0 | 8.0 | 8.3 |

---

## Raw Runs

| Run | Task | Treatment | Rep | score_r1 | score_final | rounds | final | bytes | dur(s) |
|-----|------|-----------|-----|----------|-------------|--------|-------|-------|--------|
| 1 | T_B | prose_grounded_deep | 1 | 7.6 | 7.6 | 2 | FAIL | 3500 | 234 |
| 2 | T_B | prose_grounded_deep | 2 | 8.2 | 8.2 | 3 | FAIL | 3587 | 263 |
| 3 | T_B | baseline | 1 | 7.8 | 7.8 | 2 | FAIL | 5388 | 222 |
| 4 | T_A | prose_grounded_deep | 1 | 7.8 | 7.8 | 3 | FAIL | 12335 | 334 |
| 5 | T_B | baseline | 2 | 7.8 | 7.8 | 2 | FAIL | 6735 | 232 |
| 6 | T_C | baseline | 1 | 7.8 | 7.2 | 3 | FAIL | 5515 | 263 |
| 7 | T_C | prose_grounded_deep | 1 | 7.5 | 7.5 | 2 | FAIL | 9542 | 214 |
| 8 | T_C | baseline | 2 | 7.8 | 7.8 | 2 | FAIL | 5599 | 245 |
| 9 | T_A | prose_grounded_deep | 2 | 7.5 | 7.5 | 3 | FAIL | 10749 | 360 |
| 10 | T_C | prose_grounded_deep | 2 | 7.8 | 7.8 | 3 | FAIL | 7455 | 321 |
| 11 | T_A | baseline | 1 | 7.5 | 7.5 | 3 | FAIL | 7688 | 238 |
| 12 | T_A | prose_grounded_deep | 3 | 7.5 | 7.5 | 3 | FAIL | 15947 | 380 |
| 13 | T_A | baseline | 2 | 7.8 | 7.5 | 3 | FAIL | 9912 | 288 |
| 14 | T_B | prose_grounded_deep | 3 | 8.2 | 8.2 | 2 | FAIL | 3519 | 159 |
| 15 | T_C | prose_grounded_deep | 3 | 7.5 | 7.5 | 2 | FAIL | 7801 | 202 |
| 16 | T_C | baseline | 3 | 7.8 | 7.0 | 3 | FAIL | 6115 | 241 |
| 17 | T_A | baseline | 3 | 7.8 | 7.5 | 3 | FAIL | 8910 | 252 |
| 18 | T_B | baseline | 3 | 7.8 | 7.8 | 2 | FAIL | 4293 | 185 |

---

## Experiment Panel Verdicts

### Methodologist — MARGINAL (7/10)
- Limited replication adequacy: While the experiment specifies 3 replications per task, the run summary shows a high degree of variability in scores across runs. This may not be enough to reliably distinguish signal from noise.

### Knowledge Auditor — INCONCLUSIVE (6/10)
- Across multiple tasks, there was a lack of meaningful change in output content between rounds despite feedback requesting specific improvements.
- In some cases, the final conclusions did not fully follow from the observed score data and feedback provided.
- Alternative explanations were not sufficiently addressed; the analysis sometimes jumped to favored conclusions without robust justification.

### Loop Optimizer — REVISE (7/10)
- The effect size for score_r1 improvement is not consistently above the threshold of 0.2, with some replications showing no significant gain.
- Variability in grounded_r1 and depth_r1 suggests that further refinement or additional replications are needed to confirm stability.

**Next experiment:** Factor=SYNTH_INSTRUCTION variant, levels=['baseline', 'prose_grounded_deep'], tasks=['T_A', 'T_B', 'T_C'], change=harness_synthesis.py::update_instruction('HARNESS_SYNTH_INSTRUCTION', {'levels': {'baseline': '', 'prose_grounded_deep': 'Output ONLY the markdown starting with #. For each item write exactly 4 prose paragraphs — no bullet scaffolding, no code blocks. Paragraph 1: state the mechanism precisely — what it does, why it works at a technical level, and the key invariant that makes it reliable. Paragraph 2: give a concrete implementation scenario with the real configuration values a practitioner would set (specific token limits, timeout values, chunk sizes, retry counts, memory thresholds, latency budgets) and explain what the system does at each boundary condition. Paragraph 3: name the two most common failure modes, the exact symptom each produces in production (the log message pattern, metric that spikes, or user-visible behavior), and the specific remediation step. Paragraph 4: state the decision rule for choosing this approach over its nearest alternative — what property of the workload tips the decision — and name at least one production system or published benchmark that uses this approach with a specific measured outcome (throughput, latency, cost, error rate). Every number and system name must be one a practitioner could verify against public documentation or their own infrastructure. Do not invent API method names or library calls that do not exist. Write entirely in English.'}})

---

## Loop Decision: **REVISE**  
Confidence: 0.5  
Rationale: Mixed verdicts — Methodologist:MARGINAL Auditor:INCONCLUSIVE Optimizer:REVISE

**Next:** Factor=SYNTH_INSTRUCTION variant, levels=['baseline', 'prose_grounded_deep'], tasks=['T_A', 'T_B', 'T_C'], change=harness_synthesis.py::update_instruction('HARNESS_SYNTH_INSTRUCTION', {'levels': {'baseline': '', 'prose_grounded_deep': 'Output ONLY the markdown starting with #. For each item write exactly 4 prose paragraphs — no bullet scaffolding, no code blocks. Paragraph 1: state the mechanism precisely — what it does, why it works at a technical level, and the key invariant that makes it reliable. Paragraph 2: give a concrete implementation scenario with the real configuration values a practitioner would set (specific token limits, timeout values, chunk sizes, retry counts, memory thresholds, latency budgets) and explain what the system does at each boundary condition. Paragraph 3: name the two most common failure modes, the exact symptom each produces in production (the log message pattern, metric that spikes, or user-visible behavior), and the specific remediation step. Paragraph 4: state the decision rule for choosing this approach over its nearest alternative — what property of the workload tips the decision — and name at least one production system or published benchmark that uses this approach with a specific measured outcome (throughput, latency, cost, error rate). Every number and system name must be one a practitioner could verify against public documentation or their own infrastructure. Do not invent API method names or library calls that do not exist. Write entirely in English.'}})