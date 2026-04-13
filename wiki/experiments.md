---
title: Experiments
updated: 2026-04-10
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

## Autoresearch session 2 — results (T_D + T_E, final)

Eval tasks switched from T_A+T_B to T_D+T_E after T_A structural failure (producer
knowledge gap on LangChain APIs) and T_B extreme latency (4000s+ from model
attempting file writes via run_python).

Infrastructure fixes applied before session 2:
- `WIGGUM_MAX_ROUNDS=1` in eval subprocess — eliminated revision rounds 2+3 (~600s savings/exp)
- `OLLAMA_KEEP_ALIVE=-1` baked into ollama.chat shim — prevents model unload between stages
- ChromaDB semantic memory replacing FTS5 keyword retrieval in memory.py

Session 2 baseline (T_D=8.1, T_E=8.1 → avg 8.1):

| Exp | Instruction change | Score | Status |
|-----|-------------------|-------|--------|
| 1 | Added numbered steps + inline code blocks in How sections | 8.315 | KEEP |
| 2 | Added concrete implementation notes for edge cases (chunk overlap, anomaly detection) | 8.420 | KEEP |
| 3 | Added practical examples/implementation details for all sections | 8.315 | DISCARD (-0.105) |

Session 2 final: **8.420** (exp 2, +0.320 above baseline). 3 experiments total.

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

## Autoresearch session 3 — setup (T_D + T_E)

Infrastructure changes applied before session 3:

- `num_predict=8192` added to all `synthesize()` calls — fixes T_E output truncation (Section 5 was cut off mid-sentence, capping score at ~8.1 regardless of instruction quality)
- Proposer anti-stuck improvements in `autoresearch.py`:
  - `{already_present}` section: regex-detects 9 instruction features already in the active prompt; listed explicitly so proposer doesn't re-propose them
  - `{discarded_list}` section: lists descriptions of all previously-discarded experiments; proposer instructed to avoid retreading discarded ground
  - Removed "Common effective changes" list from PROPOSE_PROMPT — was anchoring proposer to a narrow cluster
  - Added "Unexplored angles" list — broadens search space
- Skills system (`skills.py`) added — `/annotate`, `/cite`, `/kg`, `/deep`, `/panel`
- `chunker.py` added — large-doc context extraction with provenance metadata
- Perfetto tracing in `logger.py` — per-stage waterfall available via `traces/`
- Panel parallelism in `panel.py` — 3 personas run via ThreadPoolExecutor

Session 3 baseline: T_D=8.420 (best from session 2). T_E truncation fix (`num_predict=8192`) may shift baseline.

**Session 3 partial results (in progress):**

| Exp | Change | Score | Status |
|-----|--------|-------|--------|
| 6 | Failure modes + detection/mitigation per strategy | 8.350 | DISCARD −0.233 |
| **7** | **"When NOT to use" + input boundaries** | **8.915** | **KEEP +0.332** |
| 8 | Measurable success criteria / validation tests | 8.915 | DISCARD +0.000 |
| 9 | Confidence ratings (High/Med/Low) per library | 7.965 | DISCARD −0.950 |
| 10+ | ongoing… | — | — |

New best: **8.915** (exp 7) — largest single-experiment jump across all sessions (+0.332). Kimi found the "applicability constraint" framing (when NOT to use, input boundaries) in its first session; the local proposer had not explored this direction in 9 previous experiments.

Strong negative signal: confidence/hedging annotations (exp 9, −0.950) are explicitly harmful — evaluator reads uncertainty markers as lack of authority and penalises depth. Added to `already_present` blocklist.

**Infrastructure changes applied mid-session 3:**

- `WIGGUM_PANEL=1` now propagated through autoresearch eval subprocess — panel scoring was silently skipped in all prior autoresearch runs; now all 3 personas contribute to the rubric score
- `RESEARCH_CACHE=1` added to eval subprocess env — full `gather_research()` output cached in SQLite (`research_cache` table, 24 h TTL); experiment 1 cold-populates per task, experiments 2-N skip the entire search + compress loop (~400-600s savings per task per experiment)
- DDGS result cache already active (`search_cache` table) — redundant with research cache for autoresearch, but covers interactive runs

Start session 3 (resume):
```bash
python autoresearch.py --tasks T_D,T_E --proposer kimi-k2.5:cloud
```

## Code fixes applied 2026-04-12

Based on deep analysis of 123 eval runs in `runs.jsonl`:

**Fix 1 — Wiggum best-round restoration (`wiggum.py`)**
12/57 multi-round runs regressed: final score < r1. Wiggum was returning the last round's content regardless of score trajectory. Fixed: track `best_score/best_content/best_round` across all rounds; restore best content to disk before returning FAIL if a later round scored lower. Also fixed termination gate from `MAX_ROUNDS` constant to `max_rounds` variable — env override `WIGGUM_MAX_ROUNDS` now works correctly at the exit gate.

**Fix 2 — Enumerated task synthesis path (`agent.py`)**
`expected_count` now extracted before first `synthesize()` call. Enumerated tasks route directly to `synthesize_with_count()` — no wasted first synthesis + count retry. Safety-net retry path retained for cases where count compliance still fails.

**Fix 3 — SYNTH_INSTRUCTION_COUNT eliminated (`agent.py`)**
Ablation run (Priority 5) revealed `synthesize_with_count()` was using `SYNTH_INSTRUCTION_COUNT`, which had not been through autoresearch optimization (session-1-era quality). Scores dropped from 8.8 → 6.9 r1 for T_D. Fixed: `synthesize_with_count()` now uses `SYNTH_INSTRUCTION` (session-3-optimized) with the count constraint injected as prefix. `SYNTH_INSTRUCTION_COUNT` is now dead code inside its autoresearch sentinels.

## Ablation — saturation loop vs single search (2026-04-12, Priority 5)

**Design:** same task (T_D — top 3 context window management strategies), different search depths. `NOVELTY_THRESHOLD=0` forces all rounds to run.

First run confounded by Fix 3 above — both runs used the inferior SYNTH_INSTRUCTION_COUNT, depressing scores. Rerun in progress after fix.

**Preliminary finding (pre-fix):** 1-round and 5-round both scored r1=6.9 with identical dimension profiles — extra search rounds did not lift synthesis quality. Requires clean rerun to confirm.

**Implication if confirmed:** the saturation loop's value may be in redundancy/robustness rather than synthesis quality lift. The closed-book prior knowledge pass (see roadmap) would be a more targeted improvement.
