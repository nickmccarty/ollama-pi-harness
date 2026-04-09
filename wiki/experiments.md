---
title: Experiments
updated: 2026-04-09
sources: [experiment-01.md, experiment-02.md, experiment-03.md, experiment-04.md]
tags: [experiments, results, producer, eval]
---

# Experiments

## Summary table

| Exp | Key change | T_A depth | T_B depth | Finding |
|-----|-----------|-----------|-----------|---------|
| 01 | Baseline (7B producer, no wiggum) | ~2.5 | ~2.5 | Ceiling at 7B; wiggum absent |
| 02 | Added wiggum eval loop (up to 3 rounds) | +0.3 | +0.4 | Wiggum revision lifts scores; T_B bottleneck identified |
| 03 | Wiggum + criteria enforcement | stable | +0.2 | criteria_rate improves; depth still limited by 7B |
| 04 | Upgraded producer to 32B (pi-qwen-32b) | **+1.2** | flat | **32B breaks T_A ceiling; T_B bottleneck is synthesis instruction, not model** |

## Experiment 04 — key findings

- **H1 confirmed**: 32B producer improves depth on T_A (enumerated tasks) — 4/4 PASS
- **H2 confirmed**: T_B (open research) flat at first pass — synthesis instruction is the bottleneck
- **H3 confirmed**: Zero revision regressions with wiggum loop
- **H4 confirmed**: MarkItDown URL enrichment active; high `count_check_retry` on enumerated tasks (4/4 T_A, 4/5 T_C) — enriched context inflates prose, format fails
- **H5 confirmed**: 32B does not regress T_B scores

## Implications

- T_A ceiling broken — further gains need better synthesis instructions, not a bigger model
- T_B synthesis instruction is the primary lever → autoresearch targets this
- URL enrichment should be task-type-aware: disable or reduce to 1 for enumerated tasks to reduce count_check_retry

See also: [Eval Framework](eval-framework.md) · [Synthesis Instructions](synthesis-instructions.md) · [Architecture](architecture.md)

## Autoresearch session 1 — results

Loop fixed after two bugs:
1. `sys.executable` resolved to wrong conda env → fixed with `PYTHON = sys.executable` at module load
2. `→` (U+2192) in print statements → `UnicodeEncodeError` in cp1252 subprocess → fixed with `PYTHONIOENCODING=utf-8` + `encoding="utf-8"` in subprocess call

Session 1 results (13 experiments):
- Baseline: 8.285 (exp 1)
- **Best: 8.845 (exp 3)** — "production-ready integration examples with full agent loop usage, error handling, and real-world scenarios"
- Score range: 7.615–8.845
- Proposer stuck in "add code examples" cluster for exps 4–13; no further improvements found
- Session terminated; exp 3 instructions restored as canonical

See [Synthesis Instructions](synthesis-instructions.md) for full discard table.
