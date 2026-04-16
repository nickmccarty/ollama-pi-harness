---
title: Roadmap
updated: 2026-04-15
tags: [roadmap, design, architecture]
---

# Roadmap

Ranked by estimated impact vs implementation effort. Items marked **[spec]** have a design doc linked.

---

## Active / next up

### Stall-triggered replan in autoresearch
**Source:** MagenticOne architecture review (2026-04-12)
**Status:** Idea, not designed

MagenticOne replans after N consecutive stalls. Autoresearch equivalent: if 4+ consecutive experiments are discarded, inject a directive into the PROPOSE_PROMPT:

> "The last 4 variations were all discarded. Stop refining the existing instruction — propose a fundamentally different framing approach that hasn't been tried."

**Expected benefit:** breaks proposer out of local minima faster. The local Qwen3-Coder proposer clustered in "add code examples" space for 10 experiments. Kimi found an orthogonal angle immediately but that was model quality, not loop design.

**Effort:** low — add stall counter to autoresearch.py loop; modify PROPOSE_PROMPT conditionally.

---

### Closed-book prior knowledge pass
**Source:** MagenticOne architecture review (2026-04-12)
**Status:** Implemented (2026-04-15)

Before `gather_research()`, add a `prior_knowledge_pass()` that asks the producer:

> "What do you already know about: {task}? List: (1) facts you're confident about, (2) specific gaps you'd need to look up to answer authoritatively."

The gap list replaces generic topic queries in `plan_query()`. This addresses two known problems:
- Searches for well-known topics retrieve content the model already knows, inflating novelty scores with no synthesis gain
- Current gap queries are generated from the task string alone; prior knowledge pass grounds them in actual model knowledge

**Integration points:**
- `planner.py` — `make_plan()` gets a new optional `prior_knowledge` field (list of known facts + list of gaps)
- `gather_research()` — `plan_query()` uses gaps as seeding queries; novelty scoring calibrated against gaps rather than blank slate
- `synthesize()` — known facts injected as a "verified facts" block in the synthesis prompt

**Expected benefit:** more targeted searches, fewer wasted rounds, cleaner synthesis context. Should reduce count_check_retry on enumerated tasks where the model already knows the correct structure.

**Effort:** medium — one new LLM call in planner.py, minor changes to gather_research() and synthesize() prompt assembly.


---

## Pending (lower priority)

### Novelty threshold tuning
**Source:** runs.jsonl analysis (2026-04-12)

Novelty scores are effectively binary {2, 3} — only 1 score of 4 in 123 runs. The NOVELTY_THRESHOLD=3 gate means we stop if score=2. But later search rounds (round 4: mean 2.83) are approaching the threshold and still finding useful content. Options:
- Lower NOVELTY_THRESHOLD to 2 (stop only on score<2) — allows more searches before gating
- Raise MAX_SEARCH_ROUNDS to 7
- Use per-round adaptive threshold (stricter in early rounds, looser in later)

Pending clean ablation results (Priority 5) to determine if more search rounds actually help.

### SYNTH_INSTRUCTION_COUNT retirement
**Source:** ablation analysis (2026-04-12)

`SYNTH_INSTRUCTION_COUNT` is now dead code — `synthesize_with_count()` uses `SYNTH_INSTRUCTION`. The autoresearch sentinels for `SYNTH_INSTRUCTION_COUNT` remain in `agent.py` but serve no purpose. Clean up once session 3 is complete and the fix is confirmed stable.

### Panel DPO preference learning
**Source:** architecture review (ongoing)

`panel.py` produces structured per-persona scores and issues per wiggum round. This is the right substrate for DPO preference learning — (task, winning_output, losing_output) pairs from panel disagreements. Currently unconnected to any training loop.

**Prerequisite:** enough panel-scored runs to form a preference dataset (target: ~200 pairs across T_A–T_E).

---

## Completed

| Item | Completed | Notes |
|------|-----------|-------|
| Marginal-value search saturation loop | 2026-04-09 | [spec](marginal-value-search.md) |
| ChromaDB semantic memory | 2026-04-09 | [spec](chromadb-memory-migration.md) |
| Multi-persona panel (panel.py) | 2026-04-09 | WIGGUM_PANEL=1 |
| Research cache (SQLite, 24h TTL) | 2026-04-10 | RESEARCH_CACHE=1 |
| Knowledge graph (kg_gen.py) | 2026-04-10 | /kg skill |
| Wiggum best-round restoration | 2026-04-12 | wiggum.py fix |
| synthesize_with_count uses SYNTH_INSTRUCTION | 2026-04-12 | agent.py fix |
| Cloud proposer (kimi-k2.5:cloud) | 2026-04-10 | eliminates VRAM swap |
| Wiggum cycling detection | 2026-04-15 | identical score+dims → early exit, restores best round |
| OCR preprocessing cascade | 2026-04-15 | ocr.py: PyMuPDF → llama-server → llama3.2-vision |
| Closed-book prior knowledge pass | 2026-04-15 | planner.py: gaps seed queries, known facts in synthesis context |
| vLLM inference backend (inference.py) | 2026-04-15 | INFERENCE_BACKEND=vllm; context-length retry with truncation |
| Evaluator diversity comparison script | 2026-04-15 | eval_compare_evaluators.py |
| vLLM parallelism benchmark | 2026-04-15 | bench_vllm_parallel.py; --ollama-only / --vllm-only flags |
| Synthesis epilogue stripping | 2026-04-15 | clean_synthesis_output: --- + meta-commentary pattern |
