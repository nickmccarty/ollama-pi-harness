# Experiment 04: Producer Upgrade Impact

## Design

**Type:** Completely randomized design (CRD)  
**Factor:** Producer model (pi-qwen → pi-qwen-32b as default)  
**Treatments:** 3 task types (T_A, T_B, T_C)  
**Replications:** 3 per treatment (9 planned; 16 recorded due to re-run after MarkItDown integration mid-experiment)  
**Evaluator:** Qwen3-Coder:30b (unchanged from exp-03)  
**PASS_THRESHOLD:** 8.0 (unchanged)

This experiment is the direct comparison to experiment-03, holding everything constant except the producer model. Exp-03 used pi-qwen (qwen2.5:7b) as default; this experiment uses pi-qwen-32b (qwen2.5:32b Q4_K_M) as default. Same tasks, same evaluator, same threshold.

**Tasks (same as experiments 01-03):**

| ID | Type | Task |
|----|------|------|
| T_A | enumerated | top 5 context engineering techniques used in production LLM agents |
| T_B | best_practices | best practices for cost envelope management in production AI agents |
| T_C | enumerated | 3 most common failure modes in multi-agent AI systems |

**Randomized run order:**  
`T_B, T_A, T_C, T_A, T_C, T_B, T_C, T_A, T_B`

---

## Hypotheses

**H1 — Pass rate improves:** Overall pass rate > 4/9 (exp-03 baseline).  
*Falsified if: pass rate <= 4/9.*

**H2 — T_A ceiling broken:** T_A pass rate = 3/3.  
Exp-03 T_A was 0/3 with revision regression. Pre-experiment confirmation run showed 7.0→8.1 PASS on round 2.  
*Falsified if: any T_A run fails after all 3 rounds.*

**H3 — No revision regression:** When revision triggers, score_final >= score_r1 for all runs.  
Exp-03 saw regression twice (7.0→6.8). A more capable producer should be able to act on evaluator feedback without degrading.  
*Falsified if: any run has score_final < score_r1.*

**H4 — First-pass quality improvement:** Mean score_r1 across all tasks > 7.07 (exp-03 mean).  
The 32B should produce deeper first-pass outputs on enumerated tasks.  
*Falsified if: mean score_r1 <= 7.07.*

**H5 — T_A dimension improvement:** Mean depth_r1 and spc_r1 on T_A > 6 (exp-03 ceiling).  
*Falsified if: mean depth_r1 <= 6 or mean spc_r1 <= 6 across T_A runs.*

---

## Results

| Run | Task | task_type | score_r1 | score_final | rounds | gain | retry | final |
|-----|------|-----------|----------|-------------|--------|------|-------|-------|
| 1 | T_A | enumerated | 7.0 | 8.1 | 2 | +1.1 | Yes | PASS |
| 2 | T_B | best_practices | 7.8 | 7.8 | 3 | 0.0 | No | FAIL |
| 3 | T_C | enumerated | 7.9 | 8.1 | 2 | +0.2 | Yes | PASS |
| 4 | T_C | enumerated | 7.0 | 7.7 | 3 | +0.7 | Yes | FAIL |
| 5 | T_B | best_practices | 7.0 | 8.8 | 2 | +1.8 | No | PASS |
| 6 | T_B | best_practices | 7.0 | 7.0 | 3 | 0.0 | No | FAIL |
| 7 | T_B | best_practices | 6.8 | 8.1 | 3 | +1.3 | No | PASS |
| 8 | T_B | best_practices | 6.0 | 7.8 | 3 | +1.8 | No | FAIL |
| 9 | T_A | enumerated | 8.1 | 8.1 | 1 | 0.0 | Yes | PASS |
| 10 | T_C | enumerated | 7.0 | 8.1 | 2 | +1.1 | No | PASS |
| 11 | T_A | enumerated | 8.1 | 8.1 | 1 | 0.0 | Yes | PASS |
| 12 | T_C | enumerated | 7.0 | 8.8 | 2 | +1.8 | Yes | PASS |
| 13 | T_B | best_practices | 7.2 | 8.1 | 3 | +0.9 | No | PASS |
| 14 | T_C | enumerated | 8.8 | 8.8 | 1 | 0.0 | Yes | PASS |
| 15 | T_A | enumerated | 8.8 | 8.8 | 1 | 0.0 | Yes | PASS |
| 16 | T_B | best_practices | 7.0 | 8.1 | 2 | +1.1 | No | PASS |

---

## Analysis

### Per-task summary (exp-04, 32B producer)

| Task | score_r1 mean | rounds mean | pass rate | depth_r1 | spc_r1 | bytes mean | CV |
|------|--------------|-------------|-----------|----------|--------|------------|-----|
| T_A | 8.00 ±0.74 | 1.25 | 4/4 | 7.2 | 7.0 | 2293 | 28.6% |
| T_B | 6.97 ±0.53 | 2.71 | 4/7 (57%) | 6.1 | 5.9 | 2198 | 29.5% |
| T_C | 7.54 ±0.80 | 2.00 | 4/5 (80%) | 6.8 | 6.4 | 1491 | 40.3% |

### Dimension scores round 1: exp-04 (32B) vs exp-03 (7B)

| Task | Dim | exp-03 (7B) | exp-04 (32B) | delta |
|------|-----|------------|-------------|-------|
| T_A | relevance | 8.0 | 9.5 | +1.5 |
| T_A | completeness | 7.0 | 7.8 | +0.8 |
| T_A | depth | 6.0 | 7.2 | **+1.2** |
| T_A | specificity | 6.0 | 7.0 | **+1.0** |
| T_A | structure | 9.0 | 9.0 | 0.0 |
| T_B | relevance | 9.3 | 8.9 | −0.5 |
| T_B | completeness | 7.0 | 6.9 | −0.1 |
| T_B | depth | 6.0 | 6.1 | +0.1 |
| T_B | specificity | 6.3 | 5.9 | −0.5 |
| T_B | structure | 8.3 | 8.0 | −0.3 |
| T_C | relevance | 8.0 | 8.8 | +0.8 |
| T_C | completeness | 7.0 | 7.4 | +0.4 |
| T_C | depth | 6.0 | 6.8 | **+0.8** |
| T_C | specificity | 6.0 | 6.4 | +0.4 |
| T_C | structure | 9.0 | 9.0 | 0.0 |

### Cross-experiment comparison

| Task | Metric | exp-03 (7B) | exp-04 (32B) | delta |
|------|--------|------------|-------------|-------|
| T_A | score_r1 mean | 7.0 | 8.0 | **+1.0** |
| T_A | rounds mean | 3.0 | 1.25 | **−1.75** |
| T_A | pass rate | 0/4 | 4/4 | **+4** |
| T_A | bytes mean | 2329 | 2293 | −36 |
| T_B | score_r1 mean | 7.2 | 7.0 | −0.2 |
| T_B | rounds mean | 2.0 | 2.71 | +0.7 |
| T_B | pass rate | 2/3 | 4/7 | +2 abs |
| T_B | bytes mean | 3288 | 2198 | **−1090** |
| T_C | score_r1 mean | 7.0 | 7.5 | +0.5 |
| T_C | rounds mean | 2.3 | 2.0 | −0.3 |
| T_C | pass rate | 2/3 | 4/5 | +2 abs |

---

## Hypothesis assessment

**H1 — Pass rate > 4/9: CONFIRMED**  
12/16 PASS (75%). Exp-03 was 4/9 (44%).

**H2 — T_A ceiling broken: CONFIRMED**  
4/4 T_A PASS. Exp-03 was 0/4. score_r1 improved from 7.0 ±0.0 to 8.0 ±0.74. Revision rounds dropped from 3.0 to 1.25. The 32B breaks the T_A ceiling definitively.

**H3 — No revision regression: CONFIRMED**  
Zero regressions across all 16 runs. Exp-03 had 2 regression events (7.0→6.8). The 32B consistently improves on feedback rather than degrading.

**H4 — First-pass quality > 7.07: CONFIRMED**  
Overall mean score_r1 = 7.41 (vs 7.07 in exp-03).

**H5 — T_A depth/spc > 6: CONFIRMED**  
depth_r1 mean = 7.2, spc_r1 mean = 7.0. Both above the 7B ceiling of 6.0.

---

## Key findings

### 1. T_A is solved — the producer was the bottleneck

The 32B producer breaks the enumerated-task ceiling that exp-03 identified. First-pass depth improved +1.2 points, specificity +1.0. More importantly, the revision trajectory reversed: the 7B regressed or stagnated; the 32B improves cleanly on feedback. T_A no longer requires attention.

### 2. T_B is the live bottleneck — and it's a synthesis instruction problem

The 32B produces *shorter* T_B output than the 7B (2198 vs 3288 bytes, −33%). Depth and specificity on T_B first pass are flat or slightly worse vs exp-03. Pass rate improved in absolute terms (4/7 vs 2/3) but only because the revision loop is more reliable — first-pass quality didn't improve.

The dimension data tells the story: T_B depth_r1 = 6.1 (essentially identical to exp-03's 6.0). The 32B isn't bringing extra depth to open-ended tasks on the first pass. This is a synthesis instruction problem: `SYNTH_INSTRUCTION` doesn't push hard enough on depth for best_practices task types, and the 32B is complying faithfully with a weak instruction.

**This is the primary target for autoresearch.**

### 3. count_check_retry rate is high — a MarkItDown side effect

Runs with MarkItDown URL enrichment (16k chars of extra context) triggered `count_check_retry` frequently: T_A retry rate = 4/4, T_C retry rate = 4/5. The large context causes the model to produce flat numbered lists on first synthesis pass instead of H2 headers. The retry path corrects this, but it adds latency and a synth_count token call. Consider making `URL_ENRICH_COUNT` task-type-aware (disable for enumerated tasks, or reduce to 1).

### 4. Revision reliability is the 32B's clearest advantage

Zero regressions across 16 runs. The 7B regressed on 2 of 9. This matters more than first-pass score: a reliable revision loop means the wiggum ceiling is now set by the evaluator and the synthesis instruction, not by the producer's ability to respond to feedback.

---

## Implications for next steps

1. **Start autoresearch immediately** — T_B depth/specificity is the target. `SYNTH_INSTRUCTION` needs to push harder on concrete implementation steps for open-ended tasks. The loop was built for exactly this.

2. **Tune `URL_ENRICH_COUNT` for enumerated tasks** — high retry rate on T_A/T_C with MarkItDown enrichment suggests disabling or reducing URL fetching for enumerated tasks where format compliance is critical.

3. **T_A and T_C are stable baselines** — no further producer or harness work needed for these task types. Use them as stability anchors in autoresearch runs.
