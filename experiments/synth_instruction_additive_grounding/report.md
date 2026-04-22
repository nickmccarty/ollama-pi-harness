# Experiment Report: synth_instruction_additive_grounding

**Date:** 2026-04-22 03:06 UTC  
**Factor:** `SYNTH_INSTRUCTION variant`  levels: ['baseline', 'additive_grounding']  
**Tasks:** ['T_A', 'T_B', 'T_C']  **Replications:** 3  
**Hypothesis:** A lightweight additive grounding sentence appended per item — requiring one named production system or benchmark with one measured outcome — preserves baseline completeness and depth while retaining the grounded_r1 gain, improving composite score_r1 by >= 0.2 points over baseline.  
**Falsified if:** mean score_r1 delta < 0.2

---

## Hypothesis Verdict

**FALSIFIED**  
Observed: delta=-0.034 (baseline=7.68, additive_grounding=7.64)  
Threshold: < 0.2

---

## Results Table

| Task | Treatment | n | score_r1 (mean±sd) | score_final (mean±sd) | rounds (mean) | PASS rate |
|------|-----------|---|-------------------|----------------------|---------------|-----------|
| T_A | baseline | 3 | 7.80±0.00 | 7.77±0.31 | 3.0 | 0% |
| T_A | additive_grounding | 3 | 7.43±0.40 | 7.43±0.40 | 2.3 | 0% |
| T_B | baseline | 3 | 7.80±0.00 | 7.80±0.00 | 2.0 | 0% |
| T_B | additive_grounding | 3 | 7.80±0.00 | 7.80±0.00 | 2.0 | 0% |
| T_C | baseline | 3 | 7.43±0.64 | 7.17±0.58 | 3.0 | 0% |
| T_C | additive_grounding | 3 | 7.70±0.17 | 7.50±0.00 | 3.0 | 0% |

---

## Per-Dimension Analysis (r1 means)

| Task | Treatment | relevance | completeness | depth | grounded | specificity | structure |
|------|-----------|---|---|---|---|---|---|
| T_A | baseline | 9.0 | 8.0 | 7.0 | 6.0 | 8.0 | 9.0 |
| T_A | additive_grounding | 8.3 | 7.3 | 6.3 | 6.7 | 8.3 | 8.3 |
| T_B | baseline | 9.0 | 8.0 | 7.0 | 6.0 | 8.0 | 9.0 |
| T_B | additive_grounding | 9.0 | 8.0 | 7.0 | 6.0 | 8.0 | 9.0 |
| T_C | baseline | 8.7 | 7.7 | 6.3 | 5.7 | 8.3 | 8.7 |
| T_C | additive_grounding | 8.7 | 7.7 | 6.7 | 7.0 | 8.0 | 9.0 |

---

## Raw Runs

| Run | Task | Treatment | Rep | score_r1 | score_final | rounds | final | bytes | dur(s) |
|-----|------|-----------|-----|----------|-------------|--------|-------|-------|--------|
| 1 | T_B | additive_grounding | 1 | 7.8 | 7.8 | 2 | FAIL | 4632 | 158 |
| 2 | T_B | additive_grounding | 2 | 7.8 | 7.8 | 2 | FAIL | 3655 | 158 |
| 3 | T_B | baseline | 1 | 7.8 | 7.8 | 2 | FAIL | 5347 | 245 |
| 4 | T_A | additive_grounding | 1 | 7.5 | 7.5 | 2 | FAIL | 3001 | 144 |
| 5 | T_B | baseline | 2 | 7.8 | 7.8 | 2 | FAIL | 4725 | 170 |
| 6 | T_C | baseline | 1 | 7.8 | 7.5 | 3 | FAIL | 6659 | 232 |
| 7 | T_C | additive_grounding | 1 | 7.5 | 7.5 | 3 | FAIL | 2201 | 197 |
| 8 | T_C | baseline | 2 | 7.8 | 7.5 | 3 | FAIL | 7369 | 259 |
| 9 | T_A | additive_grounding | 2 | 7.8 | 7.8 | 3 | FAIL | 3721 | 205 |
| 10 | T_C | additive_grounding | 2 | 7.8 | 7.5 | 3 | FAIL | 3095 | 181 |
| 11 | T_A | baseline | 1 | 7.8 | 8.1 | 3 | FAIL | 6901 | 222 |
| 12 | T_A | additive_grounding | 3 | 7.0 | 7.0 | 2 | FAIL | 3856 | 173 |
| 13 | T_A | baseline | 2 | 7.8 | 7.5 | 3 | FAIL | 8873 | 262 |
| 14 | T_B | additive_grounding | 3 | 7.8 | 7.8 | 2 | FAIL | 4647 | 169 |
| 15 | T_C | additive_grounding | 3 | 7.8 | 7.5 | 3 | FAIL | 2257 | 198 |
| 16 | T_C | baseline | 3 | 6.7 | 6.5 | 3 | FAIL | 7417 | 300 |
| 17 | T_A | baseline | 3 | 7.8 | 7.7 | 3 | FAIL | 11295 | 276 |
| 18 | T_B | baseline | 3 | 7.8 | 7.8 | 2 | FAIL | 7289 | 218 |

---

## Experiment Panel Verdicts

### Methodologist — MARGINAL (6/10)
- Limited replication across tasks: The experiment has a total of 15 runs, but these are not evenly distributed across the three tasks (T_A, T_B, T_C). This may lead to an underestimation of variability and potential biases in the results for specific tasks.
- Potential confounding by task complexity: While the controlled variables list specifies certain model parameters, there is no explicit control over the inherent complexity or difficulty of each task. This could affect the outcome and interpretation of the scores.

### Knowledge Auditor — INCONCLUSIVE (6/10)
- Across multiple tasks, there was a lack of meaningful change in output content between rounds despite feedback suggesting specific improvements.
- The final conclusions do not clearly demonstrate new knowledge as the scores and dimensions remained largely consistent across rounds.
- Alternative explanations or potential pitfalls were not sufficiently addressed, leading to an incomplete analysis.

### Loop Optimizer — REVISE (7/10)
- The effect size is not large enough to distinguish signal from noise, as the mean score_r1 delta did not reach the threshold of >=0.2.
- While there are some improvements in certain dimensions (e.g., grounded_r1), these do not consistently translate into a significant improvement across all tasks.

**Next experiment:** To further investigate the effect of additive grounding sentences, we should increase the number of replications for each task (T_A, T_B, T_C) from 3 to at least 5. Additionally, consider varying the level of detail required in the italicized sentence to see if more specific or less specific references impact the outcome differently. This can be achieved by modifying the HARNESS_SYNTH_INSTRUCTION levels with new variations such as 'additive_grounding_detailed' and 'additive_grounding_brief'.

---

## Loop Decision: **REVISE**  
Confidence: 0.5  
Rationale: Mixed verdicts — Methodologist:MARGINAL Auditor:INCONCLUSIVE Optimizer:REVISE

**Next:** To further investigate the effect of additive grounding sentences, we should increase the number of replications for each task (T_A, T_B, T_C) from 3 to at least 5. Additionally, consider varying the level of detail required in the italicized sentence to see if more specific or less specific references impact the outcome differently. This can be achieved by modifying the HARNESS_SYNTH_INSTRUCTION levels with new variations such as 'additive_grounding_detailed' and 'additive_grounding_brief'.