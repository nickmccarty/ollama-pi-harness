# autoresearch — harness self-improvement

This is the program file for autonomous improvement of the synthesis instruction in `agent.py`.

## What this is

`autoresearch.py` runs an indefinite loop that proposes modifications to `SYNTH_INSTRUCTION` in
`agent.py`, tests them against a fixed eval metric, and keeps improvements. The goal is to find
the synthesis instruction text that maximises mean first-pass wiggum score across the eval tasks.

## The fixed metric

```
composite = 0.7 * mean_wiggum_r1 + 0.3 * criteria_rate * 10
```

- `mean_wiggum_r1`: mean first-pass evaluator score (0–10) across eval tasks
- `criteria_rate`: fraction of content criteria (bytes, sections, impl notes) that passed
- Evaluated on `T_A` (top 5 enumerated) and `T_B` (best practices open-ended) by default

The metric is computed from `runs.jsonl` after each eval run. The evaluator (`Qwen3-Coder:30b`)
and the eval task definitions in `eval_suite.py` are **immutable**.

## The mutable scope

Only `SYNTH_INSTRUCTION` and `SYNTH_INSTRUCTION_COUNT` in `agent.py` — the strings between the
`AUTORESEARCH:SYNTH_INSTRUCTION:*` sentinels. Everything else is off-limits.

Both constants must:
- Tell the model to output ONLY markdown starting with `#`
- Not reference file paths
- Stay under ~300 characters combined

## The keep rule

An experiment is **kept** if `new_score - baseline_score > 0.1`. Kept means:
- `git commit` stays
- Baseline updates to the new score

An experiment is **discarded** if delta ≤ 0.1:
- `git reset HEAD~1 --soft` + `git checkout -- agent.py`
- Baseline unchanged

## Running

```bash
conda activate ollama-pi
python autoresearch.py                   # default: T_A + T_B, delta=0.1
python autoresearch.py --tasks T_D,T_E   # Session 3 tasks (context window + prompt injection)
python autoresearch.py --tasks T_A,T_B   # Session 1/2 tasks (context engineering + cost mgmt)
python autoresearch.py --delta 0.2       # stricter keep threshold
```

**Proposer model:** `kimi-k2.5:cloud` (set via `PROPOSER_MODEL` env var). Cloud proposer runs without VRAM swap, eliminating the 30–60s load/unload cost between producer and evaluator. Preferred for all new sessions.

`autoresearch.tsv` is untracked by git. Do not commit it.

## What good looks like

The current bottleneck is **depth** (weight 0.30) and **specificity** (weight 0.15). The evaluator
consistently penalises outputs where each item is described in one or two sentences without a code
snippet, named tool, or step-by-step procedure.

High-scoring synthesis instructions tend to:
- Explicitly require code blocks or step-by-step procedures for each item
- Name the structure within each item (e.g. "what it is / why it matters / how to apply it")
- Ask for specific tool names, library versions, or command-line examples where applicable
- Forbid filler phrases ("it is important to", "one should consider")
- **Frame applicability constraints** — "when NOT to use" + input/output boundaries (Session 3 exp 7, +0.332, biggest jump to date)

### What kills scores

- Confidence ratings (High/Med/Low) per technique or library — hedging reads as shallow and directly tanks the depth dimension (Session 3 exp 9, −0.950)
- Practitioner persona ("deploying tomorrow") — forces specific versions but adds prologue noise, net negative (Session 3 exp 10, −0.595)
- Failure-mode enumeration per strategy — too prescriptive, penalises well-structured non-failure-mode content (Session 3 exp 6, −0.233)

### Unexplored angles for Session 4

The current instruction (8.915 baseline) already has: What/Why/How structure, 150-word min, code fences, error handling, tool versions, edge case notes, trade-offs, "when NOT to use", input boundaries.

Candidate next steps (roughly ranked by expected gain):
1. **Cross-strategy synthesis** — require an explicit comparison table or trade-off matrix across all strategies (targets completeness + depth simultaneously)
2. **Quantified claims** — require at least one benchmark, latency, or throughput number per strategy (targets specificity)
3. **Anti-pattern section** — dedicate a subsection per strategy to "common mistakes and how to detect them" without requiring confidence ratings
4. **Output contract** — add an explicit "no filler, no hedge, no qualifiers" ban list beyond the current forbid clause

Note: "when NOT to use" and input boundaries (exp 7) were the biggest single jump (+0.332). The next gains will likely come from the structure of cross-strategy content, not per-strategy depth (which is already well-specified).

## Session history

| Session | Tasks | Best score | Best exp | Winning change |
|---------|-------|-----------|----------|----------------|
| 1 | T_A, T_B | 8.315 | 1 | Numbered steps + inline code |
| 2 | T_A, T_B | 8.420 | 2 | Edge case implementation notes |
| 3 | T_D, T_E | 8.915 | 7 | "when NOT to use" + input boundaries |
| 4 | T_D, T_E | — | — | TBD |

## Dimensions and weights (for reference)

| Dimension | Weight | What drives it |
|-----------|--------|---------------|
| relevance | 0.20 | Task addressed correctly |
| completeness | 0.25 | All required items present |
| depth | 0.30 | Concrete examples / implementation steps per item |
| specificity | 0.15 | Named tools, commands, numbers — not vague claims |
| structure | 0.10 | Clear organisation and readability |

## NEVER STOP

Once running, `autoresearch.py` loops indefinitely. Do not pause to ask whether to continue.
The human may be sleeping. If an experiment fails to parse or eval crashes, log it and continue.
