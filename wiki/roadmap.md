---
title: Roadmap
updated: 2026-04-20
tags: [roadmap, design, architecture]
---

# Roadmap

Ranked by estimated impact vs implementation effort. Items marked **[spec]** have a design doc linked.

---

## Active / next up

### Self-improving docs loop (/sync-wiki → /contextualize → sync_gaps)
**Source:** session 14 (2026-04-20)
**Status:** Implemented — loop closes but gap-to-extraction coverage is partial

`/sync-wiki` writes ground-truth constants/models/prompts to wiki/pipeline.md. `/contextualize` injects the wiki as research context. On wiggum FAIL, `sync_gaps(issues)` auto-fires and extracts source code sections targeted at the specific gaps identified. Next run has concrete facts.

**Current gap pattern coverage** (7 patterns in `wiki_sync.py::GAP_EXTRACTIONS`): planning prompts, eval prompt, synthesis function, novelty scoring, ChromaDB setup, memory compression, research loop. Each maps issue keyword substrings to a `(file, kind, name)` extraction spec.

**Next:** run the loop end-to-end until `/contextualize` passes wiggum. Add gap patterns for any remaining issues that still lack coverage. Target: /contextualize pipeline-lifecycle task reaches 9.0+.

**Effort:** low — add gap patterns as needed; each is 5 lines.

---

### Qwen3-14B AWQ via vLLM (deferred)
**Source:** session 14 (2026-04-20)
**Status:** Not yet attempted — Qwen3.6-35B abandoned in favour of stability

Qwen3.6-35B-A3B-AWQ achieved only 0.6 tok/s with 10GB cpu_offload on RTX 5000 Ada — unusable. Qwen3-14B AWQ (~8GB) fits in VRAM without cpu_offload and should achieve 10–15 tok/s. No `--cpu-offload-gb`, no `--kv-cache-dtype fp8` needed.

**Launch template:**
```bash
python -m vllm.entrypoints.openai.api_server \
  --model <qwen3-14b-awq-repo> \
  --quantization awq_marlin \
  --dtype float16 \
  --max-model-len 16000 \
  --reasoning-parser qwen3 \
  --gpu-memory-utilization 0.90 \
  --enforce-eager \
  --served-model-name pi-qwen3
```

**Effort:** low — find HF repo, update `.env` with `INFERENCE_BACKEND=vllm` + model map.

---

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

---

### Automated financial analyst skill family
**Source:** architecture discussion (2026-04-16)
**Status:** Designed, not implemented

Build a `/finance` skill family that integrates with the existing autoresearch → wiggum → panel stack for domain-specific financial analysis.

**Files to create:**
- `finance_skill.py` — standalone `/finance` pipeline modeled on `lit_review_skill.py`: ingest (yfinance/EDGAR/FRED) → compute (ratios, DCF via `run_python` tool loop) → research (`gather_research()`) → synthesize → evaluate → render
- `finance_panel.py` — 3 domain personas: Fundamental Analyst (valuation accuracy), Risk Manager (scenario coverage), Compliance Reviewer (source attribution)
- `templates/equity-report.md.j2`, `sector-comparison.md.j2`, `risk-assessment.md.j2`

**REGISTRY entries in `skills.py`:**
- `finance-context` (hook: `pre_synthesis`) — auto-triggered on financial tasks; injects prompt requiring data-backed claims with dates and sources
- `finance-eval` (hook: `post_wiggum`) — auto-triggers finance panel after wiggum

**Autoresearch integration:** add `T_FIN_A` / `T_FIN_B` to `eval_suite.py`; run `autoresearch.py --tasks T_FIN_A,T_FIN_B` to optimize financial synthesis instruction.

**Usage:**
```bash
python orchestrator.py "/finance AAPL MSFT --period 1y save to analysis.md"
python orchestrator.py "/cite /deep /finance NVDA DCF valuation save to nvda_dcf.md"
```

**New dependency:** `yfinance`, `pandas` (ingest/compute stage). Everything else reuses existing harness components.

**Effort:** high — new standalone skill pipeline, panel personas, Jinja2 templates, rubric tuning, eval tasks.

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
| Qwen3.6-35B-A3B-AWQ producer | 2026-04-19 | vLLM 0.19.1 + awq_marlin; think=False synthesis; <think> tag parser |
| /introspect + /contextualize skills | 2026-04-19 | context/*.md files; fixes self-referential task hallucination |
| Supervisor / convergence monitor | 2026-04-19 | supervisor.py: 4 signals, thresholds, intervention recommendations |
| ε-greedy novelty gate | 2026-04-19 | NOVELTY_EPSILON=0.15; prevents search utilization collapse |
| Eval suite OOD expansion (T_F/T_G/T_H) | 2026-04-19 | 9 tasks total; introspect, file-based, off-domain |
| CoT preservation + model comparison bench | 2026-04-19 | synth_cot in runs.jsonl; bench_model_compare.py |
| /contextualize research context fix | 2026-04-20 | context files promoted to research_context slot; 661B → 3841B output |
| Memory contamination fix | 2026-04-20 | quality floor (< 7.0 half-weighted) + title dedup in _search() |
| memory_context_titles logging | 2026-04-20 | titles logged to runs.jsonl; printed to console; dashboard memory card |
| Dashboard: memory card titles + synthesis preview + live DAG refresh | 2026-04-20 | finishCard() fetches /api/data; synthesis node shows content preview |
| /sync-wiki skill (wiki_sync.py) | 2026-04-20 | deterministic fact extraction from source; idempotent marker-based wiki injection |
| sync_gaps() auto-fire on contextualize FAIL | 2026-04-20 | 7 gap patterns; extracts prompts/functions targeted at wiggum issues |
