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
python autoresearch.py --tasks T_A,T_B   # explicit task subset
python autoresearch.py --delta 0.2       # stricter keep threshold
```

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
