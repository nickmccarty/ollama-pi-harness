# Experiment Report: prior_knowledge_pass_depth_impact

**Date:** 2026-04-21 14:39 UTC  
**Factor:** `Prior Knowledge Pass`  levels: ['off', 'on']  
**Tasks:** ['T_A', 'T_B', 'T_C']  **Replications:** 3  
**Hypothesis:** Enabling prior knowledge pass improves mean depth_r1 by >= 0.2 points.  
**Falsified if:** mean depth_r1 delta < 0.2

---

## Hypothesis Verdict

**FALSIFIED**  
Observed: delta=+0.111 (off=5.78, on=5.89)  
Threshold: < 0.2

---

## Results Table

| Task | Treatment | n | score_r1 (mean±sd) | score_final (mean±sd) | rounds (mean) | PASS rate |
|------|-----------|---|-------------------|----------------------|---------------|-----------|
| T_A | off | 3 | 7.30±0.00 | 7.30±0.00 | 2.0 | 0% |
| T_A | on | 3 | 7.30±0.00 | 7.30±0.00 | 2.0 | 0% |
| T_B | off | 3 | 7.30±0.00 | 7.30±0.00 | 2.0 | 0% |
| T_B | on | 3 | 7.43±0.12 | 7.43±0.12 | 2.3 | 0% |
| T_C | off | 3 | 6.77±0.46 | 7.37±0.12 | 2.7 | 0% |
| T_C | on | 3 | 6.80±0.87 | 7.30±0.00 | 2.3 | 0% |

---

## Per-Dimension Analysis (r1 means)

| Task | Treatment | relevance | completeness | depth | specificity | structure |
|------|-----------|---|---|---|---|---|
| T_A | off | 9.0 | 7.0 | 6.0 | 8.0 | 8.0 |
| T_A | on | 9.0 | 7.0 | 6.0 | 8.0 | 8.0 |
| T_B | off | 9.0 | 7.0 | 6.0 | 8.0 | 8.0 |
| T_B | on | 9.0 | 7.0 | 6.0 | 8.0 | 8.7 |
| T_C | off | 7.7 | 6.3 | 5.3 | 8.0 | 8.7 |
| T_C | on | 8.3 | 6.7 | 5.7 | 6.7 | 8.0 |

---

## Raw Runs

| Run | Task | Treatment | Rep | score_r1 | score_final | rounds | final | bytes | dur(s) |
|-----|------|-----------|-----|----------|-------------|--------|-------|-------|--------|
| 1 | T_B | on | 1 | 7.3 | 7.3 | 2 | FAIL | 8406 | 261 |
| 2 | T_B | on | 2 | 7.5 | 7.5 | 2 | FAIL | 11686 | 275 |
| 3 | T_B | off | 1 | 7.3 | 7.3 | 2 | FAIL | 8790 | 246 |
| 4 | T_A | on | 1 | 7.3 | 7.3 | 2 | FAIL | 12364 | 255 |
| 5 | T_B | off | 2 | 7.3 | 7.3 | 2 | FAIL | 8463 | 229 |
| 6 | T_C | off | 1 | 6.5 | 7.3 | 3 | FAIL | 1971 | 204 |
| 7 | T_C | on | 1 | 7.3 | 7.3 | 2 | FAIL | 6977 | 200 |
| 8 | T_C | off | 2 | 7.3 | 7.3 | 2 | FAIL | 1739 | 129 |
| 9 | T_A | on | 2 | 7.3 | 7.3 | 2 | FAIL | 9857 | 260 |
| 10 | T_C | on | 2 | 5.8 | 7.3 | 3 | FAIL | 1000 | 234 |
| 11 | T_A | off | 1 | 7.3 | 7.3 | 2 | FAIL | 10455 | 262 |
| 12 | T_A | on | 3 | 7.3 | 7.3 | 2 | FAIL | 9039 | 220 |
| 13 | T_A | off | 2 | 7.3 | 7.3 | 2 | FAIL | 9970 | 236 |
| 14 | T_B | on | 3 | 7.5 | 7.5 | 3 | FAIL | 9034 | 352 |
| 15 | T_C | on | 3 | 7.3 | 7.3 | 2 | FAIL | 6459 | 192 |
| 16 | T_C | off | 3 | 6.5 | 7.5 | 3 | FAIL | 2058 | 218 |
| 17 | T_A | off | 3 | 7.3 | 7.3 | 2 | FAIL | 9250 | 244 |
| 18 | T_B | off | 3 | 7.3 | 7.3 | 2 | FAIL | 6630 | 212 |