# Experiment Report: synth_instruction_grounded

**Date:** 2026-04-21 23:43 UTC  
**Factor:** `SYNTH_INSTRUCTION variant`  levels: ['baseline', 'prose_depth']  
**Tasks:** ['T_A', 'T_B', 'T_C']  **Replications:** 3  
**Hypothesis:** Replacing the code-template SYNTH_INSTRUCTION with a prose-depth instruction improves mean grounded_r1 by >= 1.5 points.  
**Falsified if:** mean grounded_r1 delta < 1.5

---

## Hypothesis Verdict

**FALSIFIED**  
Observed: delta=+1.223 (baseline=6.33, prose_depth=7.56)  
Threshold: < 1.5

---

## Results Table

| Task | Treatment | n | score_r1 (mean±sd) | score_final (mean±sd) | rounds (mean) | PASS rate |
|------|-----------|---|-------------------|----------------------|---------------|-----------|
| T_A | baseline | 6 | 7.77±0.08 | 7.60±0.00 | 2.8 | 0% |
| T_A | prose_depth | 6 | 7.63±0.08 | 7.60±0.00 | 2.2 | 0% |
| T_B | baseline | 6 | 7.77±0.08 | 7.70±0.11 | 2.3 | 0% |
| T_B | prose_depth | 6 | 7.67±0.10 | 7.70±0.11 | 2.2 | 0% |
| T_C | baseline | 6 | 7.67±0.15 | 7.60±0.00 | 2.8 | 0% |
| T_C | prose_depth | 6 | 7.63±0.08 | 7.60±0.00 | 2.2 | 0% |

---

## Per-Dimension Analysis (r1 means)

| Task | Treatment | relevance | completeness | depth | grounded | specificity | structure |
|------|-----------|---|---|---|---|---|---|
| T_A | baseline | 9.0 | 7.8 | 6.8 | 6.3 | 8.0 | 9.0 |
| T_A | prose_depth | 9.0 | 7.2 | 6.2 | 7.7 | 8.0 | 9.0 |
| T_B | baseline | 9.0 | 7.8 | 6.8 | 6.3 | 8.0 | 9.0 |
| T_B | prose_depth | 9.0 | 7.3 | 6.3 | 7.3 | 8.0 | 9.0 |
| T_C | baseline | 9.0 | 7.8 | 6.5 | 6.3 | 8.0 | 9.0 |
| T_C | prose_depth | 9.0 | 7.2 | 6.2 | 7.7 | 8.0 | 9.0 |

---

## Raw Runs

| Run | Task | Treatment | Rep | score_r1 | score_final | rounds | final | bytes | dur(s) |
|-----|------|-----------|-----|----------|-------------|--------|-------|-------|--------|
| 1 | T_B | prose_depth | 1 | 7.6 | 7.6 | 2 | FAIL | 6060 | 195 |
| 2 | T_B | prose_depth | 2 | 7.6 | 7.6 | 2 | FAIL | 5864 | 173 |
| 3 | T_B | baseline | 1 | 7.8 | 7.6 | 3 | FAIL | 5006 | 245 |
| 4 | T_A | prose_depth | 1 | 7.6 | 7.6 | 2 | FAIL | 9514 | 197 |
| 5 | T_B | baseline | 2 | 7.8 | 7.8 | 2 | FAIL | 4519 | 171 |
| 6 | T_C | baseline | 1 | 7.8 | 7.6 | 3 | FAIL | 6392 | 257 |
| 7 | T_C | prose_depth | 1 | 7.6 | 7.6 | 2 | FAIL | 7993 | 195 |
| 8 | T_C | baseline | 2 | 7.6 | 7.6 | 2 | FAIL | 5543 | 222 |
| 9 | T_A | prose_depth | 2 | 7.6 | 7.6 | 2 | FAIL | 9715 | 230 |
| 10 | T_C | prose_depth | 2 | 7.8 | 7.6 | 3 | FAIL | 8129 | 282 |
| 11 | T_A | baseline | 1 | 7.8 | 7.6 | 3 | FAIL | 12319 | 260 |
| 12 | T_A | prose_depth | 3 | 7.6 | 7.6 | 2 | FAIL | 8357 | 219 |
| 13 | T_A | baseline | 2 | 7.8 | 7.6 | 3 | FAIL | 11529 | 275 |
| 14 | T_B | prose_depth | 3 | 7.8 | 7.8 | 2 | FAIL | 4333 | 168 |
| 15 | T_C | prose_depth | 3 | 7.6 | 7.6 | 2 | FAIL | 6754 | 213 |
| 16 | T_C | baseline | 3 | 7.8 | 7.6 | 3 | FAIL | 6235 | 350 |
| 17 | T_A | baseline | 3 | 7.8 | 7.6 | 3 | FAIL | 8399 | 267 |
| 18 | T_B | baseline | 3 | 7.8 | 7.8 | 2 | FAIL | 4680 | 183 |
| 19 | T_B | prose_depth | 4 | 7.6 | 7.6 | 2 | FAIL | 7063 | 260 |
| 20 | T_B | prose_depth | 5 | 7.8 | 7.8 | 2 | FAIL | 4373 | 179 |
| 21 | T_B | baseline | 4 | 7.6 | 7.6 | 2 | FAIL | 4272 | 172 |
| 22 | T_A | prose_depth | 4 | 7.6 | 7.6 | 2 | FAIL | 8448 | 196 |
| 23 | T_B | baseline | 5 | 7.8 | 7.8 | 2 | FAIL | 4328 | 174 |
| 24 | T_C | baseline | 4 | 7.5 | 7.6 | 3 | FAIL | 6015 | 235 |
| 25 | T_C | prose_depth | 4 | 7.6 | 7.6 | 2 | FAIL | 7919 | 233 |
| 26 | T_C | baseline | 5 | 7.5 | 7.6 | 3 | FAIL | 6179 | 260 |
| 27 | T_A | prose_depth | 5 | 7.8 | 7.6 | 3 | FAIL | 9806 | 259 |
| 28 | T_C | prose_depth | 5 | 7.6 | 7.6 | 2 | FAIL | 8949 | 210 |
| 29 | T_A | baseline | 4 | 7.6 | 7.6 | 2 | FAIL | 8882 | 217 |
| 30 | T_A | prose_depth | 6 | 7.6 | 7.6 | 2 | FAIL | 10424 | 244 |
| 31 | T_A | baseline | 5 | 7.8 | 7.6 | 3 | FAIL | 8290 | 228 |
| 32 | T_B | prose_depth | 6 | 7.6 | 7.8 | 3 | FAIL | 2810 | 212 |
| 33 | T_C | prose_depth | 6 | 7.6 | 7.6 | 2 | FAIL | 5922 | 260 |
| 34 | T_C | baseline | 6 | 7.8 | 7.6 | 3 | FAIL | 6606 | 255 |
| 35 | T_A | baseline | 6 | 7.8 | 7.6 | 3 | FAIL | 9099 | 245 |
| 36 | T_B | baseline | 6 | 7.8 | 7.6 | 3 | FAIL | 5598 | 262 |