# Experiment Report: synth_instruction_depth

**Date:** 2026-04-21 16:29 UTC  
**Factor:** `SYNTH_INSTRUCTION variant`  levels: ['baseline', 'prose_depth']  
**Tasks:** ['T_A', 'T_B', 'T_C']  **Replications:** 3  
**Hypothesis:** Replacing the code-template SYNTH_INSTRUCTION with a prose-depth instruction improves mean depth_r1 by >= 1.0 point.  
**Falsified if:** mean depth_r1 delta < 1.0

---

## Hypothesis Verdict

**FALSIFIED**  
Observed: delta=+0.000 (baseline=6.00, prose_depth=6.00)  
Threshold: < 1.0

---

## Results Table

| Task | Treatment | n | score_r1 (mean±sd) | score_final (mean±sd) | rounds (mean) | PASS rate |
|------|-----------|---|-------------------|----------------------|---------------|-----------|
| T_A | baseline | 3 | 7.50±0.00 | 7.50±0.00 | 2.0 | 0% |
| T_A | prose_depth | 3 | 7.50±0.00 | 7.70±0.35 | 2.7 | 0% |
| T_B | baseline | 3 | 7.50±0.00 | 7.50±0.00 | 2.0 | 0% |
| T_B | prose_depth | 3 | 7.37±0.12 | 7.50±0.00 | 2.7 | 0% |
| T_C | baseline | 3 | 7.50±0.00 | 7.50±0.00 | 2.0 | 0% |
| T_C | prose_depth | 3 | 7.43±0.12 | 7.43±0.12 | 2.3 | 0% |

---

## Per-Dimension Analysis (r1 means)

| Task | Treatment | relevance | completeness | depth | specificity | structure |
|------|-----------|---|---|---|---|---|
| T_A | baseline | 9.0 | 7.0 | 6.0 | 8.0 | 9.0 |
| T_A | prose_depth | 9.0 | 7.0 | 6.0 | 8.0 | 9.0 |
| T_B | baseline | 9.0 | 7.0 | 6.0 | 8.0 | 9.0 |
| T_B | prose_depth | 9.0 | 7.0 | 6.0 | 8.0 | 8.3 |
| T_C | baseline | 9.0 | 7.0 | 6.0 | 8.0 | 9.0 |
| T_C | prose_depth | 9.0 | 7.0 | 6.0 | 8.0 | 8.7 |

---

## Raw Runs

| Run | Task | Treatment | Rep | score_r1 | score_final | rounds | final | bytes | dur(s) |
|-----|------|-----------|-----|----------|-------------|--------|-------|-------|--------|
| 1 | T_B | prose_depth | 1 | 7.5 | 7.5 | 2 | FAIL | 3006 | 126 |
| 2 | T_B | prose_depth | 2 | 7.3 | 7.5 | 3 | FAIL | 6444 | 262 |
| 3 | T_B | baseline | 1 | 7.5 | 7.5 | 2 | FAIL | 6879 | 194 |
| 4 | T_A | prose_depth | 1 | 7.5 | 8.1 | 3 | FAIL | 5481 | 205 |
| 5 | T_B | baseline | 2 | 7.5 | 7.5 | 2 | FAIL | 10006 | 257 |
| 6 | T_C | baseline | 1 | 7.5 | 7.5 | 2 | FAIL | 2729 | 222 |
| 7 | T_C | prose_depth | 1 | 7.5 | 7.5 | 2 | FAIL | 4568 | 146 |
| 8 | T_C | baseline | 2 | 7.5 | 7.5 | 2 | FAIL | 6104 | 164 |
| 9 | T_A | prose_depth | 2 | 7.5 | 7.5 | 2 | FAIL | 5631 | 139 |
| 10 | T_C | prose_depth | 2 | 7.3 | 7.3 | 3 | FAIL | 8540 | 302 |
| 11 | T_A | baseline | 1 | 7.5 | 7.5 | 2 | FAIL | 10089 | 224 |
| 12 | T_A | prose_depth | 3 | 7.5 | 7.5 | 3 | FAIL | 5700 | 188 |
| 13 | T_A | baseline | 2 | 7.5 | 7.5 | 2 | FAIL | 9941 | 211 |
| 14 | T_B | prose_depth | 3 | 7.3 | 7.5 | 3 | FAIL | 2565 | 168 |
| 15 | T_C | prose_depth | 3 | 7.5 | 7.5 | 2 | FAIL | 5846 | 184 |
| 16 | T_C | baseline | 3 | 7.5 | 7.5 | 2 | FAIL | 7562 | 212 |
| 17 | T_A | baseline | 3 | 7.5 | 7.5 | 2 | FAIL | 8883 | 204 |
| 18 | T_B | baseline | 3 | 7.5 | 7.5 | 2 | FAIL | 6127 | 188 |

---

## Experiment Panel Verdicts

### Methodologist — MARGINAL (7/10)
- The hypothesis is falsifiable with a specified measurable threshold of >= 1.0 point improvement in mean depth_r1.
- Confounds are controlled as only one variable, the SYNTH_INSTRUCTION variant, is changed at a time.
- Replication adequacy is questionable due to the high number of failures across tasks and rounds, suggesting that more replications may be needed to distinguish signal from noise.
- Run order randomization is not explicitly mentioned in the provided information.

### Knowledge Auditor — INCONCLUSIVE (6/10)
- The feedback was often not acted upon meaningfully between rounds, as evidenced by identical scores and content excerpts across multiple rounds.
- There is a lack of clear information gain or new knowledge produced from the revisions. The output seems to be iterative but does not show significant changes in depth or specificity beyond what was already known.

### Loop Optimizer — REDESIGN (3/10)
- No significant effect size observed for depth_r1 delta; all tasks show consistent failure with no improvement over baseline
- The prose-depth instruction does not appear to be effectively guiding the model to increase depth, suggesting the instruction format may be flawed or misaligned with the task
- The response variables (depth_r1, score_r1) show minimal variation across conditions and tasks, indicating lack of signal

**Next experiment:** factor=SYNTH_INSTRUCTION variant, levels=[baseline, prose_depth, prose_depth_with_examples], tasks=[T_A, T_B, T_C], change=update HARNESS_SYNTH_INSTRUCTION env var in harness.py to include example-based instruction format that explicitly shows how to apply the mechanism with concrete numbers and failure modes

---

## Loop Decision: **REDESIGN**  
Confidence: 0.7  
Rationale: Loop Optimizer: REDESIGN — findings insufficient to advance

**Next:** factor=SYNTH_INSTRUCTION variant, levels=[baseline, prose_depth, prose_depth_with_examples], tasks=[T_A, T_B, T_C], change=update HARNESS_SYNTH_INSTRUCTION env var in harness.py to include example-based instruction format that explicitly shows how to apply the mechanism with concrete numbers and failure modes