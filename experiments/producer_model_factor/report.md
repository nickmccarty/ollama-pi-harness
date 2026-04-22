# Experiment Report: producer_model_factor

**Date:** 2026-04-22 16:18 UTC  
**Factor:** `producer_model`  levels: ['qwen25_14b', 'qwen3_14b']  
**Tasks:** ['T_A', 'T_B', 'T_C']  **Replications:** 3  
**Hypothesis:** Qwen3-14B-AWQ (newer generation, same VRAM budget) improves mean score_r1 by >= 0.3 points over Qwen2.5-14B-Instruct-AWQ on T_A/T_B/T_C with no SYNTH_INSTRUCTION applied.  
**Falsified if:** mean score_r1 delta < 0.3

---

## Hypothesis Verdict

**FALSIFIED**  
Observed: delta=-0.344 (qwen25_14b=7.80, qwen3_14b=7.46)  
Threshold: < 0.3

---

## Results Table

| Task | Treatment | n | score_r1 (mean±sd) | score_final (mean±sd) | rounds (mean) | PASS rate |
|------|-----------|---|-------------------|----------------------|---------------|-----------|
| T_A | qwen25_14b | 3 | 7.80±0.00 | 7.43±0.40 | 3.0 | 0% |
| T_A | qwen3_14b | 3 | 7.63±0.29 | 7.70±0.17 | 3.0 | 0% |
| T_B | qwen25_14b | 3 | 7.80±0.00 | 7.80±0.00 | 2.3 | 0% |
| T_B | qwen3_14b | 3 | 7.67±0.15 | 7.97±0.40 | 3.0 | 0% |
| T_C | qwen25_14b | 3 | 7.80±0.00 | 7.53±0.46 | 2.7 | 0% |
| T_C | qwen3_14b | 3 | 7.07±0.12 | 7.17±0.29 | 2.3 | 0% |

---

## Per-Dimension Analysis (r1 means)

| Task | Treatment | relevance | completeness | depth | grounded | specificity | structure |
|------|-----------|---|---|---|---|---|---|
| T_A | qwen25_14b | 9.0 | 8.0 | 7.0 | 6.0 | 8.0 | 9.0 |
| T_A | qwen3_14b | 8.0 | 8.3 | 6.3 | 7.0 | 8.0 | 9.0 |
| T_B | qwen25_14b | 9.0 | 8.0 | 7.0 | 6.0 | 8.0 | 9.0 |
| T_B | qwen3_14b | 9.0 | 8.0 | 6.0 | 7.0 | 8.0 | 9.0 |
| T_C | qwen25_14b | 9.0 | 8.0 | 7.0 | 6.0 | 8.0 | 9.0 |
| T_C | qwen3_14b | 8.0 | 7.0 | 5.7 | 6.3 | 8.7 | 8.0 |

---

## Raw Runs

| Run | Task | Treatment | Rep | score_r1 | score_final | rounds | final | bytes | dur(s) |
|-----|------|-----------|-----|----------|-------------|--------|-------|-------|--------|
| 1 | T_B | qwen3_14b | 1 | 7.7 | 8.2 | 3 | FAIL | 15230 | 451 |
| 2 | T_B | qwen3_14b | 2 | 7.5 | 8.2 | 3 | FAIL | 11496 | 280 |
| 3 | T_A | qwen3_14b | 1 | 7.8 | 7.8 | 3 | FAIL | 12673 | 256 |
| 4 | T_C | qwen3_14b | 1 | 7.2 | 7.5 | 3 | FAIL | 2813 | 316 |
| 5 | T_A | qwen3_14b | 2 | 7.8 | 7.8 | 3 | FAIL | 11396 | 259 |
| 6 | T_C | qwen3_14b | 2 | 7.0 | 7.0 | 2 | FAIL | 8768 | 241 |
| 7 | T_A | qwen3_14b | 3 | 7.3 | 7.5 | 3 | FAIL | 12050 | 232 |
| 8 | T_B | qwen3_14b | 3 | 7.8 | 7.5 | 3 | FAIL | 6744 | 269 |
| 9 | T_C | qwen3_14b | 3 | 7.0 | 7.0 | 2 | FAIL | 6318 | 218 |
| 10 | T_C | qwen25_14b | 1 | 7.8 | 7.0 | 3 | FAIL | 7334 | 268 |
| 11 | T_A | qwen25_14b | 1 | 7.8 | 7.0 | 3 | FAIL | 9152 | 260 |
| 12 | T_A | qwen25_14b | 2 | 7.8 | 7.5 | 3 | FAIL | 7933 | 204 |
| 13 | T_C | qwen25_14b | 2 | 7.8 | 7.8 | 2 | FAIL | 6322 | 189 |
| 14 | T_A | qwen25_14b | 3 | 7.8 | 7.8 | 3 | FAIL | 7961 | 232 |
| 15 | T_B | qwen25_14b | 1 | 7.8 | 7.8 | 3 | FAIL | 4256 | 214 |
| 16 | T_B | qwen25_14b | 2 | 7.8 | 7.8 | 2 | FAIL | 7182 | 298 |
| 17 | T_B | qwen25_14b | 3 | 7.8 | 7.8 | 2 | FAIL | 4838 | 183 |
| 18 | T_C | qwen25_14b | 3 | 7.8 | 7.8 | 3 | FAIL | 10315 | 300 |

---

## Experiment Panel Verdicts

### Methodologist — MARGINAL (7/10)
- replications are insufficient for strong statistical inference

### Knowledge Auditor — INCONCLUSIVE (6/10)
- Feedback was not consistently acted upon across all tasks and rounds, leading to limited improvement in depth and specificity.
- The final conclusions do not clearly demonstrate new knowledge; many outputs remained largely unchanged despite feedback suggesting specific improvements.

### Loop Optimizer — REVISE (6/10)
- The mean score_r1 delta is not large enough to distinguish a clear signal from noise, as the hypothesis required an improvement of >=0.3 points but was not met.
- There's no clear indication that Qwen3-14B-AWQ significantly outperforms Qwen2.5-14B-Instruct-AWQ across all tasks.

**Next experiment:** {'factor': 'producer_model', 'levels': ['qwen25_14b', 'qwen3_14b'], 'tasks': ['T_A', 'T_B', 'T_C'], 'change': 'Increase the number of replications to 6 for each level to get a more robust estimate of the effect size and confirm whether Qwen3-14B-AWQ provides a significant improvement over Qwen2.5-14B-Instruct-AWQ.'}

---

## Loop Decision: **REVISE**  
Confidence: 0.5  
Rationale: Mixed verdicts — Methodologist:MARGINAL Auditor:INCONCLUSIVE Optimizer:REVISE

**Next:** {'factor': 'producer_model', 'levels': ['qwen25_14b', 'qwen3_14b'], 'tasks': ['T_A', 'T_B', 'T_C'], 'change': 'Increase the number of replications to 6 for each level to get a more robust estimate of the effect size and confirm whether Qwen3-14B-AWQ provides a significant improvement over Qwen2.5-14B-Instruct-AWQ.'}