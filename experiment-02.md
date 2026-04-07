# Experiment 02: Harness Upgrade Impact Study

## Objective

Measure the effect of three harness changes made after experiment-01 on the same task set,
using the same CRD design. A direct same-task comparison isolates the harness delta from
task/topic variance.

Changes under test:
1. **Count constraint enforcement** — harness re-synthesizes if item count is wrong
2. **Pass threshold raised to 9** — 8/10 outputs now trigger a wiggum revision round
3. **Task-type-specific evaluator criteria** — `enumerated` / `best_practices` / `research`
   criteria injected per task type

---

## Design

**Type:** One-factor CRD, same structure as experiment-01
**Factor:** Task type (3 levels: T_A, T_B, T_C) — identical prompts to experiment-01
**Replications:** 3 per task
**Total runs:** 9
**Run order:** New randomization (independent draw from [A,A,A,B,B,B,C,C,C])

---

## Tasks

Identical to experiment-01 — enables direct harness-version comparison.

| ID  | Count constraint | Domain              | Output path                                        |
|-----|-----------------|---------------------|----------------------------------------------------|
| T_A | Top 5 (explicit) | Context engineering | harness-engineering/context-engineering.md         |
| T_B | Open-ended       | Cost management     | harness-engineering/cost-management.md             |
| T_C | Top 3 (explicit) | Agent failure modes | harness-engineering/agent-failure-modes.md         |

**Full prompts:** (unchanged from experiment-01)

T_A: "Search for the top 5 context engineering techniques used in production LLM agents and save to ~/Desktop/harness-engineering/context-engineering.md"

T_B: "Search for best practices for cost envelope management in production AI agents and save to ~/Desktop/harness-engineering/cost-management.md"

T_C: "Search for the 3 most common failure modes in multi-agent AI systems and save to ~/Desktop/harness-engineering/agent-failure-modes.md"

---

## Randomized Run Order

New permutation of [A, A, A, B, B, B, C, C, C]:

| Run | Task |
|-----|------|
| 1   | T_B  |
| 2   | T_C  |
| 3   | T_A  |
| 4   | T_B  |
| 5   | T_A  |
| 6   | T_C  |
| 7   | T_A  |
| 8   | T_C  |
| 9   | T_B  |

---

## Response Variables

Same as experiment-01, with one addition:

| Variable             | Description                                      | Direction       |
|----------------------|--------------------------------------------------|-----------------|
| `output_bytes`       | Size of final written file                       | higher = richer |
| `output_lines`       | Line count of final file                         | higher = more structured |
| `first_wiggum_score` | Evaluator score on round 1 (pre-revision)        | higher = better |
| `wiggum_rounds`      | Number of evaluate/revise cycles needed          | lower = better  |
| `final`              | PASS / FAIL / ERROR                              | PASS = success  |
| `total_search_chars` | Merged chars from both searches                  | diagnostic      |
| `count_check_retry`  | Whether re-synthesis was triggered for count     | diagnostic      |
| `task_type`          | Detected task type (enumerated/best_practices/research) | diagnostic |

---

## Controlled Variables

Same as experiment-01:
- Producer model: `pi-qwen` (qwen2.5:7b)
- Evaluator model: `glm4:9b`
- Wiggum max rounds: 3
- Searches per task: 2
- Search quality floor: 1800 chars
- Max search results per query: 5

Changed from experiment-01:
- **Wiggum pass threshold: 9** (was 8)
- **Count constraint enforcement: enabled**
- **Task-type-specific evaluator criteria: enabled**

---

## Hypotheses

**H1 (threshold effect):** At least one run will require `wiggum_rounds > 1` due to the raised
pass threshold. Experiment-01 had all runs pass at 9/10; a stricter criteria set should surface
at least one 8/10 that now triggers revision.

**H2 (count constraint):** Zero runs will produce an output with the wrong item count after
the harness check. Experiment-01 had one silent violation (Run 7, T_C, 7 items for a "top 3" task).

**H3 (pass rate):** All 9 runs will achieve `final = PASS`. Stricter criteria should not
break the pipeline — the wiggum loop exists to recover.

**H4 (task_type routing):** All 9 runs will have the correct `task_type` in the log —
`enumerated` for T_A and T_C, `best_practices` for T_B.

---

## Analysis Plan

1. **Wiggum rounds distribution** — compare to experiment-01. Any runs with `rounds > 1`
   confirm the threshold change is active.

2. **Score distribution** — histogram of `first_wiggum_score`. Experiment-01 was uniformly 9.
   Any 8s confirm the new criteria are stricter.

3. **Count constraint retry rate** — count how many T_A and T_C runs triggered re-synthesis.

4. **Per-task output consistency** — same CV analysis as experiment-01 for `output_bytes`.
   Compare CVs to assess whether harness changes affected stability.

5. **Cross-experiment comparison** — direct comparison of means for `output_bytes`,
   `output_lines`, `first_wiggum_score`, `wiggum_rounds` between experiment-01 and experiment-02
   for each task type.

---

## What Would Falsify Each Hypothesis

- H1 falsified: all 9 runs pass in round 1 again — threshold change had no effect on score distribution.
- H2 falsified: any run has wrong item count in the final output (harness check failed or was bypassed).
- H3 falsified: any run reaches `final = FAIL`.
- H4 falsified: any run has `task_type` misclassified in the log.

---

## Results

| Run | Task | task_type      | search_chars | output_bytes | output_lines | score_r1 | wiggum_rounds | count_retry | final |
|-----|------|----------------|-------------|--------------|--------------|----------|---------------|-------------|-------|
| 1   | T_B  | best_practices | 3083        | 4001         | 60           | 9        | 1             | False       | PASS  |
| 2   | T_C  | enumerated     | 6258        | 1630         | 19           | 9        | 1             | False       | PASS  |
| 3   | T_A  | enumerated     | 2960        | 1310         | 20           | 9        | 1             | False       | PASS  |
| 4   | T_B  | best_practices | 4172        | 3032         | 30           | 9        | 1             | False       | PASS  |
| 5   | T_A  | enumerated     | 3126        | 2075         | 18           | 9        | 1             | False       | PASS  |
| 6   | T_C  | enumerated     | 3631        | 870          | 10           | 9        | 1             | False       | PASS  |
| 7   | T_A  | enumerated     | 4170        | 1650         | 23           | 9        | 1             | False       | PASS  |
| 8   | T_C  | enumerated     | 2988        | 1668         | 19           | 9        | 1             | False       | PASS  |
| 9   | T_B  | best_practices | 3290        | 3076         | 34           | 9        | 1             | False       | PASS  |

### Per-task descriptive statistics

| Task | bytes mean | bytes std | CV    | lines mean | score mean | rounds mean |
|------|-----------|-----------|-------|------------|------------|-------------|
| T_A  | 1678      | 383       | 22.8% | 20.3       | 9.0        | 1.0         |
| T_B  | 3370      | 547       | 16.2% | 41.3       | 9.0        | 1.0         |
| T_C  | 1389      | 450       | 32.4% | 16.0       | 9.0        | 1.0         |

---

## Findings

### H1 (threshold effect) — falsified

All 9 runs scored 9/10 on round 1 and passed immediately. The raised threshold from 8 to 9 had zero effect on `wiggum_rounds`. The evaluator (glm4:9b) is calibrated at 9/10 for any well-structured, relevant output regardless of task type. Changing the threshold does not change the score — the score must change first. The ceiling effect is an evaluator calibration problem, not a threshold problem.

**Implication:** Either the evaluator model needs to be replaced with one that grades more harshly, or the scoring criteria need to penalize specific flaws more aggressively. Raising thresholds alone is a no-op if the evaluator never assigns scores below the new threshold.

### H2 (count constraint) — confirmed, but not tested under pressure

Zero count_check_retry events across all 9 runs. The count constraint enforcement was never triggered because the model got the count right on every first synthesis. This is positive — count violations are gone — but the fix was never exercised. The experiment-01 violation (7 items for a "top 3" task) did not recur, which may reflect stochastic variation, not the harness change.

The enforcement is present and correct, but its effectiveness under adversarial conditions (ambiguous task wording, more complex topics) is untested.

### H3 (pass rate) — confirmed

9/9 PASS. H3 confirmed unconditionally.

### H4 (task_type routing) — confirmed

9/9 correct routing: T_A and T_C → `enumerated`, T_B → `best_practices`. The regex patterns cover all three task prompts without collision. H4 confirmed.

### Cross-experiment output size comparison

| Task | exp-01 bytes mean | exp-02 bytes mean | delta  | exp-01 CV | exp-02 CV |
|------|------------------|------------------|--------|-----------|-----------|
| T_A  | 2322             | 1678             | -644   | 39.7%     | 22.8%     |
| T_B  | 2905             | 3370             | +465   | 13.2%     | 16.2%     |
| T_C  | 1754             | 1389             | -365   | 44.2%     | 32.4%     |

T_A and T_C both shrank in mean byte count (-644 and -365) but also became more consistent (CV dropped from 39.7% → 22.8% and 44.2% → 32.4%). The experiment-01 outlier (Run 4, T_A: 3332 bytes, 68 lines) drove that experiment's high variance and high mean; experiment-02 T_A runs are more uniform.

T_B grew slightly (+465 bytes) and remained the most consistent task type across both experiments. Open-ended tasks continue to produce the most stable output.

The CV improvements for T_A and T_C are the clearest measurable effect of the combined harness changes. Whether this is attributable to the count constraint check, the task-type-specific criteria, or regression to the mean cannot be determined from 3 reps. A blocked design with replications across both harness versions would be needed to isolate the effect.

### Persistent finding: evaluator calibration ceiling

Both experiments returned uniformly 9/10 first-pass scores. The wiggum loop, designed to surface and fix quality gaps, has no signal to act on. The revision capability exists but is dormant. The root cause is glm4:9b's scoring distribution — it concentrates at 9/10 for anything structurally complete and topically correct.

**Two paths forward:**
1. **Swap evaluator** — use a model with sharper discrimination (qwen2.5:72b is known to be harsher but slow; an intermediate model like qwen2.5:32b, if available, may balance both)
2. **Add adversarial eval** — explicitly ask the evaluator to find one concrete failure before scoring, forcing active critique rather than passive acceptance
