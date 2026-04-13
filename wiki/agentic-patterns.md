---
title: Agentic Patterns — Harness Mapping
updated: 2026-04-11
tags: [architecture, patterns, agent-design]
---

# Agentic Patterns — Harness Mapping

Standard agentic loop patterns mapped to the components in this codebase.

| Pattern | Best for | Main advantage | Main downside |
|---------|----------|---------------|--------------|
| ReAct | Interactive tool use, uncertain environments | Adapts on the fly | Can drift or stop too early |
| Plan-and-Execute | Clear projects with known steps | More predictable | Less flexible if the plan breaks |
| Reflect-and-Refine | Writing, code quality, debugging | Improves outputs iteratively | Can spend extra cycles polishing |
| Manager–Worker | Large tasks with separable subtasks | Scales better than one loop | More orchestration overhead |
| Agent Teams | Feature delivery, test-heavy work | Good separation of responsibilities | More complex to set up |
| Wiggum loop | Mechanical "until tests pass" work | Very persistent | Can overrun or overfit the task |

## Where each pattern lives in this codebase

### ReAct — `gather_research()` saturation loop (`agent.py`)

Each search round observes novelty via `assess_novelty()`, then decides whether to issue another
query or stop. `NOVELTY_THRESHOLD=3` and `SEARCHES_PER_TASK=2` minimum guard against the two
canonical ReAct failure modes: stopping too early and drifting into low-value queries.

### Plan-and-Execute — `planner.py` → `gather_research()` → `synthesize()` → `wiggum`

`plan_query()` generates gap-targeted queries up front; the pipeline executes them in order, then
writes and verifies. Limitation: if the initial plan misses a relevant angle, the pipeline doesn't
adapt mid-run — it just executes the bad plan.

### Reflect-and-Refine — Wiggum loop (`wiggum.py`) and autoresearch loop (`autoresearch.py`)

Two instantiations at different abstraction levels:
- **Wiggum** (object level): evaluator scores output → issues feedback → producer revises → repeat (max 3 rounds). `wiggum_r1` rewards getting it right first pass.
- **Autoresearch** (meta level): propose SYNTH_INSTRUCTION change → eval composite score → keep if delta > 0.1 → loop.

Risk for both: the eval rubric is itself a proxy. The Wiggum loop optimizes against Qwen3-Coder's
scoring, which may not perfectly track real quality. The panel (`WIGGUM_PANEL=1`) partially hedges
this — three disagreeing personas are harder to overfit than a single evaluator.

### Manager–Worker — `autoresearch.py` proposer + eval pipeline

The proposer (kimi-k2.5:cloud) generates candidate instructions; the eval pipeline (worker) scores
them via `eval_suite.py`. Cloud proposer eliminates the 30–60s VRAM load/unload cost that made the
local Qwen3-Coder proposer bottleneck the loop. Kimi also explores orthogonal framing directions
faster — found "applicability constraints" angle in its first experiment, after 20+ experiments
with the local proposer never tried it.

### Agent Teams — `panel.py` (3-persona panel)

Three reviewers with distinct roles: Domain Practitioner, Critical Reviewer, Informed Newcomer.
Each scores the same output independently. Panel runs per Wiggum round and logs to `runs.jsonl` as
`panel_reviews`. Currently underexploited — the structured disagreement between personas is the
right substrate for DPO preference learning but hasn't been used for that yet.

### Wiggum loop — `wiggum.py`

Named for the pattern itself. Works best when the success condition is binary or threshold-based
(score ≥ N, test suite passes). Capped at `WIGGUM_MAX_ROUNDS` to prevent overrun. Eval subprocess
uses `WIGGUM_MAX_ROUNDS=1` to skip extra revision rounds during autoresearch scoring.

## The gap: no reflect step inside synthesis

The `search → compress_knowledge() → synthesize()` chain has no recovery mechanism. If
`compress_knowledge()` lossy-compresses the wrong facts, the synthesis stage proceeds on a degraded
knowledge state with no way to detect or recover. A ReAct loop inside synthesis — check coverage,
identify gaps, re-query — would close this gap and is the natural next architectural layer.
