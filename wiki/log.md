# Wiki Log

Append-only record of wiki operations. Each entry: `## [YYYY-MM-DD] <operation> | <subject>`

Grep recent: `grep "^## \[" wiki/log.md | tail -10`

---

## [2026-04-09] ingest | wiki scaffold created
Initial wiki directory, index, and seed pages created from experiments 01–04 and project context.

## [2026-04-09] ingest | autoresearch session 1 — 13 experiments, best 8.845 (exp 3)

## [2026-04-09] ingest | marginal-value-search spec added

## [2026-04-09] ingest | chromadb-memory-migration spec added

## [2026-04-09] update | session 2 progress + ChromaDB migration + kg_gen added

## [2026-04-12] analysis | runs.jsonl deep-dive — 123 eval runs
Key findings: specificity (6.65) is weakest dimension, weaker than depth (6.97). 12/57 multi-round wiggum runs regressed (final score < r1). count_check_retry fires on 25% of enumerated runs, −0.39 score penalty. 5-round search produces higher r1 (8.12) than 2-round (7.85). Novelty scores compressed to {2,3} — scale effectively binary.

## [2026-04-12] fix | wiggum best-round restoration + SYNTH_INSTRUCTION_COUNT elimination
Three code changes: (1) wiggum.py now tracks best-scoring round and restores it before returning FAIL — recovers 12 historical regressions. (2) Fixed wiggum termination check from MAX_ROUNDS constant to max_rounds variable (env override now works correctly). (3) synthesize_with_count() switched from SYNTH_INSTRUCTION_COUNT to SYNTH_INSTRUCTION — eliminates stale unoptimized instruction for enumerated tasks.

## [2026-04-12] analysis | ablation — 1-round vs 5-round saturation loop (Priority 5)
First run confounded: ablation revealed SYNTH_INSTRUCTION_COUNT was session-1-era quality (6.9 r1 vs 8.8 historical T_D baseline). Root cause fixed (see above). Rerun in progress. Preliminary: both 1-round and 5-round scored identically at r1, suggesting extra search rounds may not lift synthesis quality.

## [2026-04-12] review | MagenticOne architecture (v0.4.4)
Reviewed Microsoft MagenticOne vs harness architecture. Key borrow identified: closed-book prior knowledge pass before gather_research() — ask producer what it already knows and what gaps exist before any web search. This front-loads knowledge audit, makes gap queries more targeted, and addresses the synthesis gap (no reflect step between search and synthesis). Roadmap item added.

## [2026-04-12] ingest | wiki additions — agentic-patterns.md, roadmap.md created; synthesis-instructions.md + autoresearch_program.md updated with sessions 2+3 findings
