# Experiment 04: Producer Upgrade Impact

## Design

**Type:** Completely randomized design (CRD)  
**Factor:** Producer model (pi-qwen → pi-qwen-32b as default)  
**Treatments:** 3 task types (T_A, T_B, T_C)  
**Replications:** 3 per treatment  
**Total runs:** 9  
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

*(populated after run_exp04.py completes)*

| Run | Task | task_type | score_r1 | score_final | rounds | gain | final |
|-----|------|-----------|----------|-------------|--------|------|-------|
| 1 | T_B | | | | | | |
| 2 | T_A | | | | | | |
| 3 | T_C | | | | | | |
| 4 | T_A | | | | | | |
| 5 | T_C | | | | | | |
| 6 | T_B | | | | | | |
| 7 | T_C | | | | | | |
| 8 | T_A | | | | | | |
| 9 | T_B | | | | | | |

---

## Analysis

*(populated after analyze_exp04.py completes)*
