---
title: Roadmap
updated: 2026-04-20
tags: [roadmap, design, architecture]
---

# Roadmap

Ranked by estimated impact vs implementation effort. Items marked **[spec]** have a design doc linked.

---

## Active / next up

### Wiggum rubric: penalise code stubs in prose-format tasks
**Source:** session 15 (2026-04-20)
**Status:** Identified, not implemented

`/contextualize` ceiling of 7.0–7.2 is caused by pi-qwen-32b generating code blocks despite explicit instruction, bloating the document to 10K+ bytes and overflowing the evaluator's context window. The wiggum rubric has no specific penalty for code stubs in tasks where prose is the correct format.

**Proposed fix:** add a `format_compliance` dimension (weight ~0.1) to the wiggum eval prompt for prose-format tasks (task_type=contextualize, introspect). Deduct points when the model generates ```` ``` ```` blocks that aren't explicitly requested. This would lower scores on stub-heavy outputs, surface the violation clearly in wiggum issues, and provide a quality signal for the autoresearch loop.

**Alternative:** switch producer model to Qwen3-14B for `/contextualize` — smaller model with stronger instruction following may comply better.

**Effort:** low for rubric change, medium for per-skill model routing.

---

### Self-improving docs loop (/sync-wiki → /contextualize → sync_gaps)
**Source:** session 14 (2026-04-20)
**Status:** Loop closes correctly; ceiling is model capability, not context coverage

`/sync-wiki` writes ground-truth constants/models/prompts to wiki/pipeline.md. `/contextualize` injects selective wiki context (8K cap via `get_relevant_wiki_context()`). On wiggum FAIL, `sync_gaps(issues)` auto-fires and extracts targeted source sections. Wiggum issues stored as `[wiggum]` facts in ChromaDB so future runs see past failure modes.

**Current gap pattern coverage** (9 patterns): planning prompts, eval prompt, synthesis function, novelty scoring, ChromaDB setup, memory compression, research loop, `make_plan()`, `auto_activate()`.

**Ceiling diagnosis:** `/contextualize` scores 7.0–7.2 regardless of context quality. Model ignores "No code stubs" instruction, generating ```` ``` ```` blocks that bloat output to 10K+ bytes and overflow evaluator context. This is a model behavior problem, not a context gap. Adding more gap patterns will not lift the score.

**Next:** validate loop on a non-self-referential task (e.g. T_A/T_B research) where the ceiling isn't model self-knowledge.

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

## Technical debt / pre-refactor cleanup
**Source:** session 20 (2026-04-21) — directory audit + data model review

Three categories of work that should be resolved before any major refactor. Documented here so the refactor has a complete picture of what exists and why it's shaped this way.

---

### TD-1: Trace pipeline registration gap
**Files:** `logger.py` (`_write_trace`), `schema.py`
**Severity:** medium — traces are invisible to the data model

`_write_trace()` writes Chrome Trace JSON to `traces/` but never calls `log_artifact()`, so traces are not registered in `artifacts.jsonl`. You cannot query "all artifacts for session X" and get traces back — they are filesystem orphans despite `RunTrace` carrying `session_id`, `experiment_id`, `treatment_level`, and `task_id`.

**Current state:** `runs.jsonl`, `artifacts.jsonl`, `messages.jsonl`, `plans.jsonl` are all queryable by `session_id`. Traces are not.

**Fix (two changes to `logger.py`):**

1. **Organize by session** — change `TRACE_DIR` to write into `traces/{session_id}/` so `ls traces/{session_id}/` gives every trace for a session without grepping:
```python
session_dir = os.path.join(TRACE_DIR, self.session_id or "untracked")
os.makedirs(session_dir, exist_ok=True)
path = os.path.join(session_dir, f"{self.run_id}__{label}.json")
```

2. **Register in artifacts.jsonl** — one line after writing the file:
```python
self.log_artifact(path, artifact_type="trace")
```

3. **Meaningful label** — use experiment context when available, fall back to short task slug:
```python
if self.experiment_id and self.task_id and self.treatment_level:
    label = f"{self.experiment_id}__{self.task_id}__{self.treatment_level}"
else:
    raw = re.sub(r"[^\w]+", "_", self._task).strip("_")
    label = raw[:35].rsplit("_", 1)[0] if len(raw) > 35 else raw
```

**Result:** `traces/20260421T...-session123/20260421T...-abc123__synth_prose_deep__T_A__baseline.json`

**Note on existing 227 traces:** leave them as-is. The `run_id` prefix is intact for joins; retroactive renaming risks breaking any artifact registry pointers. Future runs will be clean.

**Effort:** low (~15 lines in `logger.py`).

---

### TD-2: Directory cleanup — Phase 1 (no code changes)
**Files:** root directory (130+ items)
**Severity:** low — cosmetic, but slows navigation and obscures the actual module surface area

Zero-risk moves that require no import changes:

**Delete outright:**
- `tinytroupe.20260409_*.log`, `tinytroupe.20260415_*.log` (3 stale log files)
- `_email_out.txt`, `_panel_test.md` (scratch outputs)
- `eval_compare_out.txt` (ad-hoc output)
- `harness-engineering/` nested directory (contains only `vllm_test_output.md` — move that to `scratch/` or delete)
- Deduplicate `email-drafts/` vs `email_drafts/` — confirm which is current, delete other

**Move to `data/`:**
- `3dgs-paper-markdown.csv` (12MB), `geo-week-talks.csv` (1MB)
- `arxiv_agentic_papers.csv/md`, `arxiv_agentic_papers_annotated.csv`
- `arxiv_agentic_harness_engineering_papers.md`, `arxiv_agentic_harness_engineering_papers_annotated.csv`
- `arxiv_functional_nutrition.csv`, `arxiv_prompt_injection.csv` (untracked)
- `annotated-abstracts.csv`, `autoresearch.tsv`
- `finetune_dataset.jsonl` (660KB), `finetune_dataset_v2.jsonl` (4MB), `finetune_metrics.jsonl`

**Move to `modelfiles/`:**
- `Modelfile`, `Modelfile.32b`, `Modelfile.qwen3.6`, `Modelfile.v2`

**Move to `archive/` or delete:**
- `experiment-01.md` through `experiment-04.md` (pre-framework manual notes)
- `ablation-1round.md`, `ablation-5round.md`
- `2308.04079-annotated.md`, `2602.16928-annotated.md`
- `orchestrator-test.md`, `orchestrator-test-2.md` (untracked), `introspection-test.md`, `lifecycle_test.md`
- `bench-parallel-2.md`, `bench_vllm_results.jsonl` (untracked bench outputs)
- `eval-qwen36-test.md`, `top-5-nutrient-synergies.md`, `guide.md` (untracked)
- `context-engineering.md`, `cost-management.md`, `verification-patterns.md`, `agent-failure-modes.md` (superseded by wiki/)
- `autoresearch_program.md`, `annotate-test.md`, `pipeline-lifecycle.md`

**Move to `experiments/` (treatment sample snapshots):**
- `eval-agent-failure-modes.md` + `-baseline`, `-off`, `-on`, `-prose_depth`, `-prose_grounded_deep`, `-qwen35` variants
- `eval-context-engineering.md` + all variants
- `eval-cost-management.md` + all variants
- `eval-context-window.md`, `eval-prompt-injection.md`
- These are per-treatment wiggum output samples; consider `experiments/{name}/samples/`

**Effort:** low — file moves only, no code changes, no import impact.

---

### TD-3: Directory cleanup — Phase 2 (script graveyard)
**Files:** various root-level one-off scripts
**Severity:** low — these are never imported, just clutter the module surface

Scripts with no local importers (verified by import audit) that should move to `scripts/`:
- `analyze_exp01.py` through `analyze_exp04.py` — replaced by `experiment_analyzer.py`
- `run_exp03.py`, `run_exp04.py` — replaced by `experiment_runner.py`
- `backfill_metrics.py`, `mine_knowledge.py`, `index_papers.py`
- `build_dpo_dataset.py`, `build_finetune_from_annotations.py`, `hf_export.py`
- `finetune_annotate.py`, `run_annotations.py`
- `bench_vllm_parallel.py`, `bench_model_compare.py`
- `fix_vllm_patch.py`, `patch_vllm_cpu_offload.py`
- `eval_compare_evaluators.py`, `inspect_run.py`

These are all importless (confirmed: no other root-level module imports them). Move is safe.

**Effort:** low — file moves only.

---

### TD-4: Package refactor — Phase 3 (import path updates required)
**Files:** multiple — requires coordinated changes
**Severity:** medium — do this after Phase 1/2, not before

**Import audit summary (session 20):**
- `inference.py` — 16 dependents (imported by almost everything; must stay importable from root or become a proper package)
- `schema.py` — 2 dependents (`logger`, `server`)
- `wiggum.py` — 2 dependents (`agent`, `orchestrator`)
- `experiment_panel.py` — 3 dependents (`experiment_analyzer`, `experiment_design`, `experiment_runner`); also invoked as subprocess by panel
- All `*_skill.py` files and `panel.py` — import only `inference`; relatively isolated

**Proposed groupings:**
- `skills/` — `email_skill.py`, `github_skill.py`, `lit_review_skill.py`, `review_skill.py`, `skills.py`, `panel.py`, `tinytroupe_tasks.py`
- `server/` — `server.py`, `mcp_server.py`, `mcp_dispatch.py`, `dashboard.py`

**Prerequisite:** convert root to a proper Python package (`__init__.py`) or add a `sys.path` shim in moved files so `import inference` still resolves. The subprocess invocation of `experiment_runner.py` in `experiment_panel.py` must also be updated if runner moves.

**Effort:** medium — coordinated import path updates across ~20 files; test all entry points after move.

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
| Qwen3-14B-AWQ via vLLM | 2026-04-20 | `Qwen/Qwen3-14B-AWQ`, awq_marlin, `--reasoning-parser qwen3`; fits in VRAM without cpu_offload |
| /contextualize selective wiki injection | 2026-04-20 | get_relevant_wiki_context() (8K cap): body excerpt + impl ref + gap extractions |
| Contextualize synthesis directive | 2026-04-20 | forces citation of exact values/function names from source context |
| Wiggum issues stored as memory facts | 2026-04-20 | [wiggum] prefix facts in ChromaDB; future runs see past failure modes |
| Wiggum revision num_ctx override | 2026-04-20 | num_predict=8192, num_ctx=16384 at call site; overrides Modelfile cap |
| GAP_EXTRACTIONS: make_plan() + auto_activate() | 2026-04-20 | 9 total patterns; closes planner classification + skill routing gaps |
| /sync-wiki path-optional | 2026-04-20 | added to _path_optional; no .md arg required |
| Logger ASCII arrow fix | 2026-04-20 | → replaced with -> for Windows cp1252 console compatibility |
| experiment_panel.py | 2026-04-20 | 3-persona panel (Methodologist/KnowledgeAuditor/LoopOptimizer); KEEP/REVISE/REDESIGN |
| experiment_runner.py | 2026-04-20 | CRD runner; env var treatments; checkpoint; treatment-specific output paths |
| experiment_analyzer.py | 2026-04-20 | stats + hypothesis eval + Markdown report + panel integration |
| runs.jsonl: experiment_id + treatment_level fields | 2026-04-20 | logger.py reads HARNESS_EXPERIMENT_ID/TREATMENT_LEVEL env vars |
| MCP server security hardening | 2026-04-20 | _validate_task(): length cap, UNC block, injection scan, output path sandbox; semaphore; API key |
| atla/selene-mini evaluator | 2026-04-21 | wiggum.py: EVALUATOR_MODEL default; SUMMARIZER_EVAL_THRESHOLD 5500→32000 |
| grounded_r1 eval dimension | 2026-04-21 | wiggum.py: 6th dim (weight 0.15); depth 0.30→0.25; registered in experiment_design.py + analyzer |
| Hallucination detector | 2026-04-21 | wiggum.py: _count_stub_blocks() docks depth for fabricated API stubs (cap -2) |
| Hybrid vLLM/Ollama routing | 2026-04-21 | inference.py: _VLLM_ROUTE set; VLLM_MODEL_MAP keys → vLLM, rest → Ollama on CPU |
| YouTube transcription | 2026-04-21 | youtube_transcribe.py: yt-dlp (android client) + openai-whisper; hooked into fetch_url_content() |
