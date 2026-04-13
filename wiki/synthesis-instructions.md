---
title: Synthesis Instructions
updated: 2026-04-09
sources: [autoresearch.tsv, agent.py, runs.jsonl]
tags: [synthesis, autoresearch, prompt-engineering]
---

# Synthesis Instructions

The synthesis instruction is the final directive appended to every synthesis prompt in `agent.py`.
It tells the producer model how to format and structure its output.

Two variants:
- `SYNTH_INSTRUCTION` — used for all task types
- `SYNTH_INSTRUCTION_COUNT` — used when task has a count constraint (e.g. "top 5")

## Constraints (invariants)

- Must tell the model to output ONLY markdown starting with `#`
- Must not mention file paths
- Must be clear and direct
- Modified only by autoresearch — not by hand

## Autoresearch findings (session 1 — 13 experiments)

**Best score: 8.845** (exp 3) — baseline established at 8.285 (exp 1).

Best-performing change (exp 3):
> "Added requirement for production-ready integration examples with full agent loop usage, error handling, and real-world scenarios to address depth and specificity weaknesses."

### What works

- Requiring **full agent loop context** (not just isolated snippets)
- Requiring **error handling** to force concrete implementation depth
- Framing around **real-world scenarios** rather than abstract descriptions

### What doesn't work (discarded, exps 2–13)

| Exp | Score | Change | Why likely failed |
|-----|-------|--------|------------------|
| 2 | 8.250 | Explicit tool versions + integration steps | Over-constrains format |
| 4 | 8.180 | Measurable outcome/config step per section | Too mechanical |
| 5 | 7.935 | Expected cost/perf improvement line | Off-topic for research tasks |
| 6 | 8.320 | Production context + technique application | Too vague |
| 7 | 7.615 | Complete executable code + error handling | Forces code where prose is better |
| 8 | 8.530 | What/Why/How/Outcome sub-structure | Helpful but too rigid |
| 9 | 7.965 | Workflow integration + measurable metric | Redundant with wiggum depth |
| 10 | 7.865 | Working code + core agent components | Over-specifies domain |
| 11 | 8.215 | Real tools only, executable code | Same cluster as prior discards |
| 12 | 7.930 | Tool naming + performance explanation | Same cluster |
| 13 | 7.825 | Production-ready config detail per section | Same cluster |

Score range across session: 7.615–8.845. High variance (±1.2) suggests the instruction
framing matters more than any single addition.

### Proposer behavior

Clustered heavily in "add code examples" space for 10+ consecutive experiments. To escape:
- Steer toward orthogonal dimensions: output structure, comparison/trade-off framing, negative constraints
- The new `gather_proposal_context()` research step (added in session 2) should help break this pattern by grounding proposals in prompt engineering literature

See also: [Experiments](experiments.md) · [Eval Framework](eval-framework.md)

## Autoresearch findings (session 2)

**Best score: 8.420** on T_A + T_B. No per-experiment breakdown retained — session focused on exploring structural variants after session 1 saturated the "add code examples" cluster.

## Autoresearch findings (session 3 — in progress as of 2026-04-11)

**Best score: 8.915** (exp 7, +0.332 delta from session 2 baseline).

Eval tasks switched to **T_D + T_E** (context window management strategies + prompt injection defense).
Proposer switched to **kimi-k2.5:cloud** — first session with no VRAM swap overhead.

### What works (session 3)

- **Applicability constraints framing**: explicitly requiring "when NOT to use" coverage + input/output boundary descriptions. Kimi found this angle immediately — local Qwen3-Coder had never tried it across 20+ experiments.

### What doesn't work (session 3)

| Exp | Delta | Change | Why likely failed |
|-----|-------|--------|------------------|
| 9 | −0.950 | Confidence ratings (High/Med/Low) per library | Hedging reads as shallow, tanks depth score |

### Proposer behavior (session 3)

kimi-k2.5:cloud explores orthogonal directions faster than local Qwen3-Coder. First experiment immediately found a new framing axis (applicability constraints) that hadn't appeared in 20+ prior experiments.

## Autoresearch loop mechanics

See `autoresearch.py`. Key config:
- `DELTA_THRESHOLD = 0.1` — minimum improvement to keep a change
- Eval tasks: T_D + T_E (session 3); T_A + T_B (sessions 1–2)
- Proposer: `kimi-k2.5:cloud` (preferred — no VRAM swap); fallback: Qwen3-Coder:30b at temperature 0.3
