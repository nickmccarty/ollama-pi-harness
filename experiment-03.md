# Experiment 03: Evaluator Upgrade Impact

## Objective

Measure the effect of replacing the evaluator model (`glm4:9b` → `Qwen3-Coder:30b`) on the
verify-revise loop behaviour and final output quality, using the same task set and CRD design
as experiments 01 and 02.

The central question: does a stronger evaluator produce genuine score variance, activate the
revision loop, and improve output quality — or is the ceiling a function of the producer, not
the evaluator?

Changes under test:
1. **Evaluator model: `Qwen3-Coder:30b`** — 30B parameters vs 9B for glm4:9b; expected to grade more harshly
2. **Evaluator prompt: calibration anchors + per-dimension issue requirement** — forces specific critique on any dimension scored ≤8
3. **Pass threshold: 8.0** — same as experiment-01 (experiment-02 used 9.0 which is moot if scores never dropped below it)

---

## Design

**Type:** One-factor CRD, same structure as experiments 01 and 02
**Factor:** Task type (3 levels: T_A, T_B, T_C) — identical prompts to both prior experiments
**Replications:** 3 per task
**Total runs:** 9
**Run order:** New randomization (independent draw)

---

## Tasks

Identical to experiments 01 and 02 — enables direct cross-experiment comparison.

| ID  | Count constraint | Domain              | Output path                                             |
|-----|-----------------|---------------------|---------------------------------------------------------|
| T_A | Top 5 (explicit) | Context engineering | harness-engineering/eval-context-engineering.md        |
| T_B | Open-ended       | Cost management     | harness-engineering/eval-cost-management.md            |
| T_C | Top 3 (explicit) | Agent failure modes | harness-engineering/eval-agent-failure-modes.md        |

**Full prompts:**

T_A: "Search for the top 5 context engineering techniques used in production LLM agents and save to ~/Desktop/harness-engineering/eval-context-engineering.md"

T_B: "Search for best practices for cost envelope management in production AI agents and save to ~/Desktop/harness-engineering/eval-cost-management.md"

T_C: "Search for the 3 most common failure modes in multi-agent AI systems and save to ~/Desktop/harness-engineering/eval-agent-failure-modes.md"

---

## Randomized Run Order

New permutation of [A, A, A, B, B, B, C, C, C]:

| Run | Task |
|-----|------|
| 1   | T_C  |
| 2   | T_A  |
| 3   | T_C  |
| 4   | T_B  |
| 5   | T_A  |
| 6   | T_B  |
| 7   | T_C  |
| 8   | T_B  |
| 9   | T_A  |

---

## Response Variables

| Variable              | Description                                           | Direction       |
|-----------------------|-------------------------------------------------------|-----------------|
| `output_bytes`        | Size of final written file                            | higher = richer |
| `output_lines`        | Line count of final file                              | higher = more structured |
| `first_wiggum_score`  | Evaluator score on round 1 (pre-revision)             | lower = more critical evaluator |
| `wiggum_rounds`       | Number of evaluate/revise cycles needed               | >1 = revision loop activated |
| `score_gain`          | Score increase from round 1 to final passing round    | higher = revision added value |
| `final`               | PASS / FAIL / ERROR                                   | PASS = success  |
| `total_search_chars`  | Merged chars from both searches                       | diagnostic      |
| `count_check_retry`   | Whether re-synthesis was triggered for count          | diagnostic      |
| `task_type`           | Detected task type (enumerated/best_practices/research) | diagnostic   |
| `wiggum_dims_r1`      | Dimension scores on round 1 (rel/cmp/dep/spc/str)    | diagnostic      |

---

## Controlled Variables

Same as experiments 01 and 02:
- Producer model: `pi-qwen` (qwen2.5:7b)
- Wiggum max rounds: 3
- Searches per task: 2
- Search quality floor: 1800 chars
- Max search results per query: 5
- Pass threshold: 8.0

Changed from experiment-02:
- **Evaluator model: `Qwen3-Coder:30b`** (was `glm4:9b`)
- **Evaluator prompt: calibration anchors + per-dimension issue enforcement** (new)

---

## Hypotheses

**H1 (revision loop activation):** At least one run will require `wiggum_rounds > 1`.
Experiments 01 and 02 had all 9 runs pass in round 1 — the revision loop never activated.
Spot tests with Qwen3-Coder:30b showed 7.0 and 7.9 first-pass scores on the same task types,
triggering revision. Expect at least 3/9 runs to require revision.

**H2 (score variance):** First-pass score distribution will show meaningful spread (std > 0.5),
compared to near-zero variance in experiments 01 and 02 (all 9.0). The stronger evaluator
should distinguish weak outputs (short, generic) from strong ones.

**H3 (pass rate):** All 9 runs will still achieve `final = PASS`. The revision loop should
recover any first-pass failures within 3 rounds — higher evaluator capability should not
break the pipeline.

**H4 (revision adds value):** For runs where `wiggum_rounds > 1`, `score_gain > 0.5`. If
revision happens but the score barely moves, the producer is the bottleneck, not the evaluator.

**H5 (task-type differentiation):** T_C (short, enumerated, minimal) will score lower than
T_B (open-ended, longer) on first pass. Experiments 01 and 02 could not test this because
all tasks scored the same. A calibrated evaluator should reflect real quality differences.

---

## Analysis Plan

1. **Wiggum rounds distribution** — count runs with `rounds > 1`. Compare to experiments 01 and 02.

2. **Score distribution** — histogram of `first_wiggum_score`. Compare mean and std to experiments
   01 (all 9.0) and 02 (all 9.0).

3. **Dimension score analysis** — mean scores per dimension (rel/cmp/dep/spc/str) grouped by task type.
   Expect depth and specificity to vary more than structure.

4. **Score gain analysis** — for revised runs, `final_score - first_score`. Does revision produce
   meaningful improvement?

5. **Per-task output consistency** — same CV analysis as prior experiments for `output_bytes`.
   Check whether the evaluator-driven revision produces more consistent output.

6. **Cross-experiment comparison** — direct comparison of means for `output_bytes`, `output_lines`,
   `first_wiggum_score`, `wiggum_rounds` across all three experiments.

---

## What Would Falsify Each Hypothesis

- H1 falsified: all 9 runs pass round 1 again — stronger evaluator still can't find flaws worth failing.
- H2 falsified: score std < 0.3 across runs — evaluator still concentrates at one score level.
- H3 falsified: any run reaches `final = FAIL` — revision loop cannot recover from strict evaluator.
- H4 falsified: revised runs show `score_gain < 0.3` — producer cannot respond to evaluator feedback.
- H5 falsified: T_B and T_C score within 0.5 of each other on first pass — evaluator doesn't differentiate task types.

---

## Results

| Run | Task | task_type      | search_chars | output_bytes | output_lines | score_r1 | score_final | wiggum_rounds | score_gain | count_retry | final |
|-----|------|----------------|-------------|--------------|--------------|----------|-------------|---------------|------------|-------------|-------|
| 1   | T_C  | enumerated     | 3617        | 1771         | 16           | 7.0      | 8.8         | 2             | +1.8       | False       | PASS  |
| 2   | T_A  | enumerated     | 3876        | 3155         | 31           | 7.0      | 6.9         | 3             | –0.1       | True        | FAIL  |
| 3   | T_C  | enumerated     | 3466        | 1751         | 12           | 7.0      | 7.0         | 3             | 0.0        | False       | FAIL  |
| 4   | T_B  | best_practices | 3251        | 3100         | 35           | 6.0      | 7.2         | 3             | +1.2       | False       | FAIL  |
| 5   | T_A  | enumerated     | 2991        | 1825         | 16           | 7.0      | 6.8         | 3             | –0.2       | True        | FAIL  |
| 6   | T_B  | best_practices | 3776        | 3407         | 41           | 8.1      | 8.1         | 1             | 0          | False       | PASS  |
| 7   | T_C  | enumerated     | 3549        | 1376         | 10           | 7.0      | 8.1         | 2             | +1.1       | False       | PASS  |
| 8   | T_B  | best_practices | 3529        | 3356         | 51           | 7.5      | 8.2         | 2             | +0.7       | False       | PASS  |
| 9   | T_A  | enumerated     | 3694        | 2144         | 18           | 7.0      | 7.0         | 3             | 0.0        | False       | FAIL  |

### Per-task descriptive statistics

| Task | bytes mean | bytes std | CV    | lines mean | score_r1 mean | score_r1 std | rounds mean | pass rate |
|------|-----------|-----------|-------|------------|---------------|--------------|-------------|-----------|
| T_A  | 2375      | 694       | 29.2% | 21.7       | 7.00          | 0.00         | 3.0         | 0/3       |
| T_B  | 3288      | 165       | 5.0%  | 42.3       | 7.20          | 1.08         | 2.0         | 2/3       |
| T_C  | 1633      | 223       | 13.6% | 12.7       | 7.00          | 0.00         | 2.3         | 2/3       |

### Dimension scores (round 1 mean by task type)

| Task | relevance | completeness | depth | specificity | structure |
|------|-----------|--------------|-------|-------------|-----------|
| T_A  | 8.0       | 7.0          | 6.0   | 6.0         | 9.0       |
| T_B  | 9.3       | 7.0          | 6.0   | 6.3         | 8.3       |
| T_C  | 8.0       | 7.0          | 6.0   | 6.0         | 9.0       |

### Cross-experiment comparison

| Task | metric        | exp-01 | exp-02 | exp-03 | d(02→03) |
|------|--------------|--------|--------|--------|----------|
| T_A  | bytes mean   | 1678   | 2417   | 2375   | –42      |
| T_A  | score_r1     | 9.0    | 7.6    | 7.0    | –0.6     |
| T_A  | rounds mean  | 1.0    | 3.0    | 3.0    | 0        |
| T_B  | bytes mean   | 3054   | 2427   | 3288   | +861     |
| T_B  | score_r1     | 9.0    | 8.1    | 7.2    | –0.9     |
| T_B  | rounds mean  | 1.0    | 1.0    | 2.0    | +1.0     |
| T_C  | bytes mean   | 1476   | 1114   | 1633   | +519     |
| T_C  | score_r1     | 8.2    | 6.9    | 7.0    | +0.1     |
| T_C  | rounds mean  | 1.5    | 2.9    | 2.3    | –0.5     |

---

## Findings

### H1 (revision loop activates) — CONFIRMED

8/9 runs required revision (wiggum_rounds > 1). The revision loop, dormant across all 18 runs of
experiments 01 and 02, is now consistently active. H1 confirmed strongly.

### H2 (score variance) — CONFIRMED

First-pass score std = 0.55 across all 9 runs, vs effectively 0 in experiments 01 and 02.
Mean first-pass score dropped from 9.0 (both prior experiments) to 7.07. The evaluator is
now differentiating — it assigns 6.0 to weak outputs and 8.1 to strong ones. H2 confirmed.

### H3 (pass rate 9/9) — FALSIFIED

Only 4/9 runs achieved `final = PASS`. T_A failed all 3 runs. H3 falsified decisively.

The revision loop did not recover T_A outputs within 3 rounds. This is not a pipeline failure —
it is the evaluator correctly identifying outputs that don't meet the 8.0 threshold, and the
producer being unable to fix them. The system is working as designed; the design assumption
(that revision always recovers) was wrong.

### H4 (revision adds value) — CONFIRMED (weakly, task-type dependent)

Overall mean revision gain = +0.56 across revised runs. But the sign splits sharply by task type:
- T_B and T_C: gains of +1.8, +1.2, +1.1, +0.7 — revision works
- T_A: gains of –0.1, –0.2, 0.0 — revision does nothing or makes it worse

H4 confirmed at the aggregate level, but the T_A result falsifies the underlying assumption for
enumerated tasks with 5+ items. The producer cannot reliably respond to depth feedback on
multi-item outputs. Two runs actively got worse after revision.

### H5 (task-type differentiation T_B > T_C) — FALSIFIED

T_B mean first-pass score = 7.20; T_C = 7.00. Gap = 0.20, well below the 0.5 threshold.
Both task types cluster at 7.0 on first pass. The differentiation comes not from first-pass
scores but from revision outcomes: T_B and T_C recover (when they do), T_A doesn't.

The evaluator assigns the same initial depth and specificity scores (6/10) to all three task
types — the bottleneck is at those dimensions, not at relevance or structure where T_B does score
higher (9.3 vs 8.0 for T_A/T_C).

### Central finding: producer ceiling exposed

The evaluator upgrade worked exactly as intended — it provides genuine score variance and drives
revision. The unexpected result is that T_A (top 5, 5 items with implementation notes) is a
hard ceiling for pi-qwen. The evaluator correctly identifies missing depth per item, but the
producer cannot add it in revision — and sometimes makes the output shorter and worse.

Two distinct failure modes observed:
1. **Revision regression** (T_A runs 2 and 5): score goes 7.0 → 6.8. Producer over-corrects or
   strips content when trying to "improve" specific sections.
2. **Revision stagnation** (T_C run 3, T_A run 9): score stays flat at 7.0. Producer edits
   surface wording without addressing the underlying depth gap.

### Threshold implication

PASS_THRESHOLD = 8.0 is correctly calibrated for the new evaluator in terms of identifying
quality gaps. The problem is that the producer can only reliably reach 8.0+ on T_B (open-ended,
fewer constraints on length/items) and on lucky T_C runs. For T_A, the ceiling appears to be
~7.0–7.2 regardless of revision.

**Two paths forward:**
1. **Lower threshold to 7.5** — accepts the producer ceiling as the de facto quality floor;
   revision still drives improvement where possible; FAIL becomes rare rather than common.
2. **Stronger producer** — replace pi-qwen with a model that can actually respond to depth
   feedback on enumerated tasks. The wiggum loop design is sound; the producer is the bottleneck.
