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

## [2026-04-20] build | Session 17 — MCP security hardening: input validation, concurrency limit, API key auth

Five hardening layers applied to `mcp_server.py`:

1. **`_validate_task()` gate** — called before any subprocess spawn; enforces: (a) task length cap (default 2000 chars, env `MCP_TASK_MAX_CHARS`); (b) UNC path block (`\\` and `//` prefixes); (c) injection scan via `scan_for_injection()` from security.py; (d) output path sandbox via `check_output_path()` — rejects any embedded `.md` path outside `~/Desktop` or `~/Documents`.

2. **Concurrency semaphore** (`threading.Semaphore`) — max 2 simultaneous `run_task`/`run_orchestrated` calls (env `MCP_MAX_CONCURRENCY`). Busy responses return immediately with a retry hint rather than queuing additional model loads.

3. **Optional API key auth** — `MCP_API_KEY` env var; when set, `run_task`/`run_orchestrated` require a matching `api_key` param. No-op when unset (default: no auth). Designed for HTTP transport where the server is reachable over a network.

4. **Imports from security.py** — `check_output_path`, `scan_for_injection` now imported at module level; no new security logic, reuses existing sandboxes already proven in agent.py.

5. **`threading` import added** — `import threading` added alongside other stdlib imports.

**Gap closed:** `mcp_server.py` was a new network-accessible entry point that bypassed all security.py checks applied inside agent.py. Input now validated at the perimeter before any subprocess is spawned.

## [2026-04-20] build | Session 16 — /autoexperiment infrastructure: experiment_panel, runner, analyzer

Three new files close the /autoexperiment loop:

1. **`experiment_panel.py`** — three-persona evaluation panel for experiments-as-artifacts:
   - `ExperimentSpec` dataclass (hypothesis, factor, tasks, replications, mutable_scope, controlled_vars)
   - `run_experiment_panel(spec, traces)` — parallel ThreadPoolExecutor, same pattern as panel.py
   - Three personas with structural model diversity to avoid evaluator conflict of interest:
     - Methodologist (`glm4:9b`) — design validity, falsifiability, confound control
     - Knowledge Auditor (`pi-qwen-32b`) — feedback-to-content alignment, conclusion soundness
     - Loop Optimizer (`Qwen3-Coder:30b`) — actionability, `next_experiment_suggestion`
   - `experiment_panel_decision()` — KEEP / REVISE / REDESIGN from three verdicts
   - `experiment_panel_issues()` — flattened deduplicated issues with persona prefix

2. **`experiment_runner.py`** — generalized CRD executor:
   - Generates randomized run order from spec (seed=42 for reproducibility)
   - Applies treatments via env var overrides (mutable_scope.type=env)
   - Treatment-specific output paths (`eval-ctx-off.md`, `eval-ctx-on.md`) prevent file overwrites
   - Checkpoint at `experiments/<id>/run_log.jsonl`; `--resume` skips completed (task, treatment, rep) tuples
   - Tags each run with `HARNESS_EXPERIMENT_ID` + `HARNESS_TREATMENT_LEVEL` env vars
   - `--dry-run` prints CRD order without executing

3. **`experiment_analyzer.py`** — statistical analysis + report:
   - Loads runs.jsonl filtered by `experiment_id` field
   - Per-(task, treatment) stats: mean/std of score_r1/final, wiggum_rounds, pass_rate, per-dim r1 means
   - Hypothesis evaluation: parses `falsified_if` string, computes treatment delta vs threshold
   - Renders Markdown report to `experiments/<id>/report.md`
   - Calls `run_experiment_panel()` → panel verdicts saved to `experiments/<id>/panel.json`

**`logger.py`**: `RunTrace` now reads `HARNESS_EXPERIMENT_ID` + `HARNESS_TREATMENT_LEVEL` env vars; written as first-class fields in every runs.jsonl record.

**Full /autoexperiment loop (end-to-end):**
```
/autoresearch or /lit-review output (open questions, gap candidates)
  → hand-write ExperimentSpec JSON (or future /experiment-design LLM skill)
    → python experiment_runner.py spec.json           # CRD execution
      → python experiment_analyzer.py experiments/<id>/spec.json  # stats + panel
        → panel.json: KEEP/REVISE/REDESIGN + next_experiment_suggestion
          → use next_experiment_suggestion as input to next ExperimentSpec
```

## [2026-04-20] build | Session 15 — vLLM/Qwen3-14B routing, /contextualize context injection, wiggum issue memory, selective wiki injection

Six changes shipped:

1. **vLLM with Qwen3-14B-AWQ** (`.env`, `inference.py`) — Qwen3.6-35B abandoned (0.6 tok/s unusable). Qwen3-14B-AWQ (`Qwen/Qwen3-14B-AWQ`) fits in VRAM with `--quantization awq_marlin --dtype float16 --max-model-len 16000`. `VLLM_MODEL_MAP` updated to route all logical model names to `pi-qwen3-14b`. `--reasoning-parser qwen3` (not `--enable-reasoning`) is the correct flag for this vLLM build.

2. **`/contextualize` selective wiki injection** (`wiki_sync.py`, `agent.py`) — full `pipeline.md` (14.8K) was being injected wholesale, bloating context to 27K+ chars. Root cause: `introspect: true` in pipeline.md frontmatter. Fix: removed tag, replaced with `get_relevant_wiki_context()` (8K cap) that stitches: body excerpt (first 3K chars of pipeline diagram + arch overview) + `## Implementation Reference` marker block + `## Gap-Targeted Extractions` marker block.

3. **Contextualize synthesis directive** (`agent.py`) — injected before `skill_context` on any `/contextualize` run: forces model to cite exact dimension names/weights, threshold values, function bodies from source rather than summarising generically. Score improved but still capped by model capability.

4. **Wiggum issues as memory facts** (`memory.py`, `agent.py`) — `compress_and_store()` now accepts `wiggum_issues: list[str]`; stored as `[wiggum] <issue>` facts in the ChromaDB observation. `all_wiggum_issues` computed once, passed to both `sync_gaps()` and `_store_memory()`. Future runs see past failure modes as lessons.

5. **Wiggum revision truncation fix** (`wiggum.py`) — root cause: `PARAMETER num_ctx 8192` in pi-qwen-32b Modelfile caps total context, truncating long revisions mid-sentence. Fix: `"num_predict": 8192, "num_ctx": 16384` runtime override on both revision call sites (`loop()` line ~288, `loop_annotate()` line ~716). Qwen3 Modelfile has no hardcoded cap.

6. **Gap pattern expansion + /sync-wiki housekeeping** (`wiki_sync.py`, `agent.py`, `logger.py`) — two new `GAP_EXTRACTIONS` patterns: `make_plan()` (planner.py, task classification + query generation) and `auto_activate()` (agent.py, keyword-to-skill rule table). `sync-wiki` added to `_path_optional` so it no longer requires an explicit `.md` path argument. Logger `→` replaced with `->` for Windows cp1252 console compatibility.

**Self-improving docs loop status:** loop closes correctly end-to-end. Hard ceiling identified: `/contextualize` scores 7.0–7.2 on PASS_THRESHOLD=9.0 regardless of context injection quality. Root cause is model capability — pi-qwen-32b generates code stubs despite instruction, bloating output to 10K+ bytes and overflowing evaluator context. Not a prompt engineering problem.

**GAP_EXTRACTIONS coverage (9 patterns):** planning prompts, eval prompt, synthesis function, novelty scoring, ChromaDB setup, memory compression, research loop, make_plan(), auto_activate().

## [2026-04-20] build | Session 14 — /sync-wiki skill, memory contamination fix, /contextualize fix, dashboard repairs

Seven changes shipped:

1. **`/contextualize` research context fix** (`agent.py`) — context files were injected into `file_context` ("File contents:" label) which models treat as supplementary. Now promoted to `research_context` ("Research findings:") when `_skip_research=True`. Output grew from 661B to 3841B on same task; score lifted 6.2 → 7.1.

2. **Memory contamination fix** (`memory.py`) — `_search()` now soft-penalises observations scoring below 7.0 (half-weight quality component) and deduplicates by title (highest-ranked per unique title kept). Prevents failed runs from re-injecting themselves and anchoring synthesis at their own quality ceiling. Root cause: two copies of "Agent Pipeline Lifecycle (6.2, 7.1)" were crowding out diverse observations.

3. **`memory_context_titles` logging** (`logger.py`, `agent.py`, `memory.py`) — `get_context_with_titles()` returns titles alongside formatted context. `log_memory_hits()` accepts titles list. Console now prints each injected observation title during run. `memory_context_titles` field written to `runs.jsonl`.

4. **Dashboard fixes** (`dashboard.py`) — three bugs resolved: (a) memory card inspector now lists observation titles (was showing only count); (b) synthesis node inspector now shows output content preview (was only on output node); (c) `finishCard()` now fetches `/api/data` and re-populates DAG run list — live runs appear in the DAG explorer immediately on completion instead of requiring a dashboard.py regeneration.

5. **`/sync-wiki` skill** (`wiki_sync.py`, `skills.py`, `agent.py`) — deterministic regex extraction of implementation facts from source code: models by stage, key constants, wiggum dimension weights, memory ranking formula, SYNTH_INSTRUCTION text, Ollama→vLLM model map. Writes idempotent `## Implementation Reference` section to `wiki/pipeline.md` using HTML comment markers. No LLM call. Run as `python agent.py "/sync-wiki"` or `python wiki_sync.py`.

6. **`sync_gaps()` + auto-fire** (`wiki_sync.py`, `agent.py`) — keyword-triggered gap extraction: maps wiggum issue strings to source code sections (7 gap patterns covering planning prompts, eval prompt, synthesis function, novelty scoring, ChromaDB setup, memory compression, research loop). Extracts function bodies and prompt templates into `## Gap-Targeted Extractions` section in wiki/pipeline.md. Auto-fires after any wiggum FAIL on a `/contextualize` run — closes the self-improving docs loop.

7. **vLLM Qwen3.6-35B-A3B-AWQ exploration** — attempted and abandoned. Issues encountered: (a) cpu_offload + Mamba hybrid `may_reinitialize_input_batch` assertion bug (patched via `patch_vllm_cpu_offload.py`); (b) FlashInfer JIT libcuda linker error in WSL2 (fixed via `ln -sf /usr/lib/wsl/lib/libcuda.so.1 ~/miniconda3/envs/vllm/lib64/stubs/libcuda.so`); (c) 0.6 tok/s generation rate with 10GB cpu_offload — unusable for production. Reverted to `pi-qwen-32b` via Ollama. `patch_vllm_cpu_offload.py` and `fix_vllm_patch.py` retained for reference.

**Self-improving docs loop (new):** `/sync-wiki` → `/contextualize` → wiggum FAIL → `sync_gaps(issues)` → wiki enriched → repeat. Each cycle extracts the specific source sections wiggum identified as missing, so future runs have concrete facts rather than architectural summaries.

## [2026-04-21] build | Session 13 — comprehensive agentic data flow schema, run lineage tracking, planner CoT

Seven tracking improvements shipped:

1. **`plans.jsonl`** (`schema.py`, `logger.py`) — new JSONL file; `OrchestratorPlan` dataclass written **before** subtask execution (queryable on crash). Fields: `plan_id`, `run_id`, `session_id`, `project_id`, `parent_run_id`, `task`, `plan_type` (agent|orchestrator), `task_type`, `complexity`, `subtasks`, `known_facts`, `knowledge_gaps`, `search_queries`.

2. **`parent_run_id` in `runs.jsonl`** (`logger.py`) — `RunTrace` reads `HARNESS_PARENT_RUN_ID` env var; written as first-class field in every run record. Subtask runs are now linkable to their orchestrator parent.

3. **Orchestrator env propagation** (`orchestrator.py`) — `HARNESS_PROJECT_ID`, `HARNESS_SESSION_ID`, `HARNESS_PARENT_RUN_ID` propagated into each subtask subprocess env. Subtask runs are no longer orphaned: they inherit session + project IDs and carry `parent_run_id`.

4. **Subtask artifact registration** (`orchestrator.py`) — `_cleanup_subtask_files()` now calls `trace.log_artifact(path, "subtask_temp")` on each temp file before deletion. All intermediate outputs are now traceable in `artifacts.jsonl`.

5. **Planner CoT preservation** (`logger.py`, `agent.py`) — `log_planner_cot(response)` extracts thinking text from `make_plan()` response; stored in `planner_cot: []` list in `runs.jsonl`. Parallel to existing `synth_cot`.

6. **`cot` field on `Message`** (`schema.py`, `logger.py`) — `Message` dataclass gains optional `cot` field; `log_message()` accepts `cot=` kwarg for logging thinking text alongside message content in `messages.jsonl`.

7. **`log_plan_record()` on `RunTrace`** (`logger.py`) — agent.py calls this after planning so every single-run also has a `plans.jsonl` record (not just orchestrated runs).

**JSONL file inventory:** `projects.jsonl`, `sessions.jsonl`, `plans.jsonl`, `runs.jsonl`, `artifacts.jsonl`, `messages.jsonl` — six files covering full pipeline lifecycle.

## [2026-04-19] build | Session 12 — Qwen3.6 MoE integration, convergence monitoring, self-knowledge skills, CoT preservation

Eight harness features shipped:

1. **Qwen3.6-35B-A3B-AWQ producer** (`inference.py`, `agent.py`, `Modelfile.qwen3.6`) — MoE model (35B params, 3B activated) served via vLLM 0.19.1 with `awq_marlin` quantization. `think=False` promoted to top-level kwarg for Ollama; `<think>` tag parser added to `_OllamaMessage` for vLLM runs without `--reasoning-parser`. `MODEL` now reads from `HARNESS_PRODUCER_MODEL` env var. `_synth_options()` disables thinking mode for synthesis to prevent token budget starvation.

2. **`/introspect` skill** (`skills.py`, `agent.py`, `context/`) — standalone handler that reads `context/*.md` files + memory store and produces a self-description without web search. Fixes photosynthesis bug where agent searched the web for self-referential tasks.

3. **`/contextualize` skill** (`skills.py`, `agent.py`) — auto-activated on self-referential tasks (regex: "yourself", "what can you", "describe the agent", etc.). Injects context files into synthesis prompt, sets `_skip_research=True`.

4. **Context files** (`context/identity.md`, `context/skills.md`, `context/function.md`) — canonical self-description: model stack, philosophy, skill registry, pipeline flow, env vars. Used by `/introspect` and `/contextualize`.

5. **Supervisor / convergence monitor** (`supervisor.py`) — four signals: wiggum score variance, output size CV, search utilization, content similarity. Threshold warnings + intervention recommendations. CLI: `python supervisor.py --n 20 --json --task-type research`.

6. **ε-greedy novelty gate** (`agent.py`, `NOVELTY_EPSILON=0.15`) — 15% pass-through for sub-threshold search rounds. Prevents search utilization collapse identified by supervisor (first live run: search_utilization WARN at 0.267).

7. **Eval suite OOD expansion** (`eval_suite.py`) — three new task types: T_F (introspect/self-description), T_G (file-based autoresearch_program.md), T_H (off-domain nutrient synergies). Total: 9 tasks (was 6). Criteria: `mentions_skill_names()`, `no_hallucinated_skills()`, `has_h1_heading()`.

8. **CoT preservation + model comparison bench** (`logger.py`, `agent.py`, `bench_model_compare.py`) — `synth_cot: []` field in runs.jsonl stores full thinking text from each synthesis call (not just char count). `bench_model_compare.py` compares test model vs historical baseline: score, pass rate, output KB, duration, thinking chars, CoT length, Δ score.

**env vars added:** `HARNESS_PRODUCER_MODEL`

## [2026-04-15] build | Session 11 — vLLM backend, OCR cascade, prior knowledge pass, wiggum cycling detection

Seven harness features shipped:

1. **Wiggum cycling detection** (`wiggum.py`) — after round 2, identical score+dims triggers early exit and restores best-round content. Applied to both `loop()` and `loop_annotate()`. Saves ~1300s on stuck runs.

2. **OCR preprocessing cascade** (`ocr.py`, `agent.py`) — sparse MarkItDown PDF output triggers: PyMuPDF `get_text("markdown")` (column-aware) → llama-server dedicated OCR (activated by `LLAMA_OCR_BASE_URL`) → llama3.2-vision per-page fallback. `is_sparse()` gate at 300 chars/page.

3. **Closed-book prior knowledge pass** (`planner.py`) — `prior_knowledge_pass()` runs before any search. LLM self-audits: known facts injected into synthesis context as verified block; gaps replace generic topic queries. `Plan` dataclass extended with `known_facts` + `knowledge_gaps`.

4. **vLLM inference backend** (`inference.py`) — `INFERENCE_BACKEND=vllm` routes to vLLM OpenAI-compatible endpoint. `VLLM_MODEL_MAP` replace-semantics (not extend) when env var set. Context-length retry: truncates longest message + halves `max_tokens` up to 2× before raising. `think` flag translation for Qwen3 reasoning mode. Sentence-transformer model cached at module level (no per-call reload).

5. **vLLM embedding** (`inference.py`, `memory.py`) — `embed()` / `get_embedding_function()` public API. vLLM `/v1/embeddings` attempted, falls back to local sentence-transformers (all-MiniLM-L6-v2, 384-dim). `get_embed_collection_suffix()` always returns `""` since both backends produce 384-dim vectors. ChromaDB collection names backend-stable.

6. **Evaluator diversity comparison** (`eval_compare_evaluators.py`) — scores 4 eval output files with two evaluators (default: Qwen3-Coder:30b vs gemma4:26b), prints side-by-side table, flags |Δ| ≥ 1.0 divergences.

7. **vLLM parallelism benchmark** (`bench_vllm_parallel.py`) — times 2/4-subtask orchestrated runs under Ollama vs vLLM. `--ollama-only` / `--vllm-only` flags for split runs. Full model map remapping prevents Ollama fallback when Ollama is stopped. Results appended to `bench_vllm_results.jsonl`.

**Synthesis epilogue fix** (`agent.py`) — `clean_synthesis_output` extended with `---` + meta-commentary pattern (strips "This synthesized guide can be saved to..." trailing text from smaller models).

## [2026-04-21] build | Session 18 — atla/selene-mini evaluator, experiment infrastructure fixes, depth anchoring investigation

Four findings and fixes from the evaluator switch and first controlled experiments:

1. **`atla/selene-mini` evaluator** (`wiggum.py`) — switched from `Qwen3-Coder:30b` to `atla/selene-mini` (Llama-3.1-8B fine-tuned as LLM judge, outperforms GPT-4o on RewardBench, 128K context). `EVALUATOR_MODEL` default updated. `SUMMARIZER_EVAL_THRESHOLD` raised from 5500 → 32000 chars to exploit Selene's context window and preserve depth signal.

2. **Depth rubric calibration** (`wiggum.py`) — replaced generic 3-level anchor with a 7-level prose-grounded ladder (depth=3 through depth=10) to combat score attractor at depth=6 observed across all full-length outputs regardless of content variation.

3. **Experiment infrastructure bug fixes** (`experiment_runner.py`, `logger.py`, `experiment_analyzer.py`):
   - `HARNESS_TASK_ID` now threaded through `_build_env()` → `logger.py` → `runs.jsonl`; analyzer skips pre-tagging runs with `task_id="?"`
   - `extract_run()` fixed: dims read from `wiggum_eval_log[0]['dims']` (not missing `wiggum_dims` field)
   - `_lookup()` helper in `_evaluate_hypothesis()` tries `dim_{metric}_mean` before `{metric}_mean` to match stored key format

4. **Score anchoring diagnosed** — Selene assigns identical dims (9,7,6,8,8) to different-sized T_A outputs. Root cause confirmed: depth=6 is accurate (What/Why/How scaffold produces boilerplate with toy stubs). Qualitative review showed prose_depth outputs ARE more grounded (real systems, real numbers) but Selene cannot distinguish hallucinated specificity (numbers in code stubs) from grounded specificity (real thresholds). `synth_instruction_depth` FALSIFIED at delta=0 — evaluator validity problem, not producer capability.

**Key insight:** the binding constraint on depth scores is the evaluator's inability to distinguish hallucinated scaffold specificity from grounded practitioner specificity. This motivates the `grounded_r1` dimension added in Session 19.

## [2026-04-21] build | Session 19 — grounded_r1 dimension, hallucination detector, hybrid vLLM/Ollama routing, YouTube transcription

Six improvements shipped:

1. **`grounded_r1` eval dimension + hallucination detector** (`wiggum.py`) — new 6th scoring dimension (weight 0.15) measures whether specific claims are traceable to real systems, documented APIs, or published benchmarks. Calibration anchors: grounded=5-6 flags code blocks with invented method names; grounded=3-4 flags mostly hallucinated specifics. Weights redistributed: depth 0.30→0.25, completeness 0.25→0.20, specificity 0.15→0.10. `_count_stub_blocks()` post-score detector: scans code blocks for standalone method calls with 12+ char names on objects not in a known-real namespace (`_KNOWN_OBJECTS`); docks `depth` by 1 per suspicious block (cap 2). Correctly flags `bt.apply_budget_constraints()` / `bt.optimize_resource_usage()` pattern from baseline outputs.

2. **`grounded_r1` registered as response variable** (`experiment_design.py`, `experiment_analyzer.py`) — added to `experiment_design.py` dimension catalog (weight, description). Added to `dim_names` in both the stats computation loop and the per-dimension report table in `experiment_analyzer.py`.

3. **Hybrid vLLM/Ollama routing** (`inference.py`) — separated routing from name translation. `_VLLM_ROUTE: set | None` tracks which models actually go to vLLM. When `VLLM_MODEL_MAP` is set, only its keys route to vLLM; everything else falls to Ollama automatically. When unset (`None`), all calls go to vLLM (pure vLLM mode). `chat()` routing: `_VLLM_ROUTE is None or model in _VLLM_ROUTE`. Enables vLLM for large producer + Ollama for small utilities (glm4:9b summarizer, atla/selene-mini evaluator) on 16GB GPU without VRAM contention. `.env` updated: only `pi-qwen3-14b` and `pi-qwen-32b` (→pi-qwen3-14b) in `VLLM_MODEL_MAP`; glm4:9b, atla/selene-mini fall to Ollama on CPU.

4. **Model map cleanup** (`inference.py`, `.env`) — built-in `_MODEL_MAP` now merges with env overrides (not replaced). Added `pi-qwen3-32b` self-mapping for future Qwen3-32B serve. Fixed `Qwen3-Coder:30b` mapping (was `QwQ-32B`, now correct HF ID). Corrected comment: `pi-qwen3-14b` is `Qwen/Qwen2.5-14B-Instruct-AWQ` (not Qwen3). `experiment_panel.py` Loop Optimizer default changed from `Qwen3-Coder:30b` → `pi-qwen-32b` to prevent panel hanging when Qwen3-Coder:30b is unloaded from Ollama.

5. **`synth_instruction_grounded` experiment** — re-ran SYNTH_INSTRUCTION factor with `grounded_r1` as primary response variable. Result: delta=+1.223 (baseline=6.33, prose_depth=7.56), FALSIFIED at threshold 1.5. Confirms prose_depth instruction produces measurably more grounded outputs but does not yet clear the 1.5-point bar. The hallucination detector correctly docked depth scores on baseline outputs with fabricated stub blocks.

6. **YouTube transcription** (`youtube_transcribe.py`, `agent.py`) — `fetch_url_content()` now routes YouTube URLs (`youtube.com/watch`, `youtu.be/`, `youtube.com/shorts/`) through `transcribe_youtube()` instead of MarkItDown (which silently fails). Downloads audio via yt-dlp with `--extractor-args youtube:player_client=android` (avoids JS runtime dependency), transcribes with `openai-whisper`. Configurable via `WHISPER_MODEL` (default: `base`) and `WHISPER_DEVICE` (default: `cpu`, avoids vLLM VRAM contention).

**env vars added:** `WHISPER_MODEL`, `WHISPER_DEVICE`
**files added:** `youtube_transcribe.py`

**env vars added:** `INFERENCE_BACKEND`, `VLLM_BASE_URL`, `VLLM_MODEL_MAP`, `WIGGUM_EVALUATOR_MODEL`, `WIGGUM_PRODUCER_MODEL`, `LLAMA_OCR_BASE_URL`


## [2026-04-23] build | Session 26 — eval loop order, explore/exploit modes, subagent demos, HTML renderer, memory injection gate

**Autoresearch loop restructured — generate → verify → revise (Ralph pattern):**
- Old order: evaluate (old feedback) → revise → verify. Proposer never saw signal from the eval it triggered — always one loop stale.
- New order: propose → apply → eval → capture fresh feedback immediately → feed to next proposal.
- On discard: tight inner loop — no research re-gather, fresh signal used directly.
- On keep: research context refreshed before next proposal (outer loop).
- `--mode explore|exploit|auto` added. `auto` (default): exploit by default, switches to explore after `PLATEAU_DISCARDS=3` consecutive discards with `|delta| < 0.05`. Explore re-gathers web research context; exploit skips it. `consecutive_discards` counter resets on keep or after auto-explore fires.

**`subagent_demo.py` / `subagent_demo_v2.py` — sequential and parallel subagent demos:**
- `subagent_demo.py`: submits 6 research tasks ("State of Agentic AI in 2026") to server queue; polls until idle; prints file summary.
- `subagent_demo_v2.py`: 5 grounded self-analysis tasks (read actual files: `autoresearch.tsv`, `runs.jsonl`, `skills.py`, `agent.py`, `wiki/`) — harder to hallucinate, signal is verifiable.
- `--parallel` mode: fires all tasks simultaneously via MCP HTTP server (`ThreadPoolExecutor`); `--workers N` sets concurrency. `--sequential` (default) uses Flask queue.
- MCP semaphore changed from `blocking=False` (immediate rejection) to `blocking=True` (queues at server) so parallel submissions don't get refused.

**`render_html.py` — deterministic markdown → HTML renderer:**
- LLMs produce markdown; HTML with a specific design system is a rendering problem, not a generation problem.
- Converts any directory of `.md` files: `index.html` (landing page, card grid, click-to-expand) + individual `<slug>.html` per report.
- Fixed design system: `#0d1117` bg, `#58a6ff` accent, card grid, JS expand-on-click previews, no external deps.
- `render_dir(out_dir, title, subtitle)` callable from scripts; CLI: `python render_html.py <dir> --title "..."`.
- Requires `markdown` + `jinja2`; falls back to basic converter if missing.
- `subagent_demo_v2.py` calls `render_dir()` as final step after all tasks complete — landing page is guaranteed to match design system regardless of what the agents produced.

**agent.py fixes:**
- `extract_path()` rewritten: prefers "save to `<path>`" phrasing over first path found — previously grabbed read-paths from task description, overwriting source wiki files. Falls back to last `.md`/`.html` path in task.
- `detect_text_files()` extended: now matches relative paths (`autoresearch.tsv`, `wiki/log.md`, `runs.jsonl`) in addition to absolute paths. Resolves against harness directory; deduplicates.
- Research gate: when local files were read (`text_files` non-empty), sets `_skip_research=True` — agent synthesises from file content instead of web-searching for data already on disk.
- `_is_technical_task()`: data-analysis phrasing ("analyze", "extract", "trace how", "read autoresearch", "which dimensions", etc.) now routes to `SYNTH_INSTRUCTION_PROSE` — prevents Python tutorials being generated instead of actual analysis.

**wiggum.py fixes:**
- `format="json"` added to both `ollama.chat` eval calls — constrains token-level output to valid JSON.
- `<think>...</think>` stripping added to parse path.
- `_extract_eval_from_prose()`: regex fallback that extracts dimension scores from markdown prose (`**Relevance**: 8/10`) when model ignores `format=json`. Logs `prose fallback succeeded` when it fires. Prevents `score=0.0` parse failures from tanking the wiggum loop.

**server.py fix:**
- `import re` added to module-level imports (was missing; `/api/voice` "Note:" prefix check failed with `NameError`).

**memory.py — prompt injection gate on write paths:**
- `_scan_obs(title, narrative, facts)`: runs `scan_for_injection()` from `security.py` on compressed observation content before any SQLite/ChromaDB write.
- Applied to both `compress_and_store()` and `store_direct()`.
- Motivation: web-fetched or synthesised content riding into future sessions as trusted memory context via a poisoned page. Reuses existing injection patterns — no new logic.

## [2026-04-23] build | Session 27 — llama-server parallel backend, MCP log panel, dashboard timezone fix

**llama-server parallel inference (qwen3-8b, 8 slots):**
- Ollama serializes all requests; llama.cpp `--parallel N --cont-batching` genuinely interleaves N inference streams on one GPU via continuous batching.
- RTX 5000 Ada (16GB): qwen3-8b Q4_K_M (~4.4GB weights) leaves ~10GB for KV cache → 8 parallel slots at 8192 ctx each.
- Theoretical: 5 subagent tasks in ~240s wall-clock vs ~20min sequential through Ollama (5x speedup).
- GGUF extracted from Ollama blob: `~/.ollama/models/blobs/sha256-2bada8a...` → `models/qwen3-8b.gguf`.
- llama-server found pre-built at `llama.cpp/build/bin/llama-server.exe` (CUDA-enabled).
- WSL port conflict: port 8080 intercepted by `wslrelay.exe`; moved to 8082.
- `.env` updated: `HARNESS_ENDPOINTS={"qwen3-8b": {"url": "http://localhost:8082/v1", ...}}` + `HARNESS_PRODUCER_MODEL=qwen3-8b`. `inference.py`'s existing `HARNESS_ENDPOINTS` routing handles the rest.
- `subagent_demo_v2.py`: default workers bumped from 3 → 8.

**MCP log panel (dashboard):**
- `mcp_server.py`: `_run_subprocess` replaced `subprocess.run` with `Popen` + line-by-line streaming; status lines (`[agent]`, `[research]`, etc.) written to `mcp_tasks.jsonl` via `_log_event()`. `PYTHONUNBUFFERED=1` + `PYTHONIOENCODING=utf-8` + `encoding="utf-8"` on Popen fix real-time delivery and Unicode characters.
- `server.py`: `/api/mcp/log` endpoint tails `mcp_tasks.jsonl` with optional `?since=` filter.
- `dashboard.py`: "MCP parallel tasks" panel polls `/api/mcp/log` every 5s; renders start/line/done/fail events live. Panel height 520px.
- Fixed: edits initially went to `dashboard.html` (static file); Flask serves from `dashboard.py` via `db.render()`.

**Dashboard timezone fix:**
- Token-by-date chart bucketed timestamps as UTC dates; at PDT (UTC-7) runs after 5PM appeared under next day.
- Fix: `datetime.fromisoformat(ts).astimezone().strftime("%Y-%m-%d")` converts UTC → local before date bucketing.

**MCP server fixes:**
- `mcp_server.py --http`: FastMCP ignores `FASTMCP_PORT` env var at `run()` time; switched to `uvicorn.run(mcp.streamable_http_app(), host=..., port=...)`.
- `subagent_demo_v2.py`: full MCP session handshake (initialize → Mcp-Session-Id → initialized → tools/call); SSE response parsing (`event: message\r\ndata: {...}`); `Accept: application/json, text/event-stream` header.

**files modified:** `mcp_server.py`, `server.py`, `dashboard.py`, `subagent_demo_v2.py`, `.env` (gitignored)

## [2026-04-22] build | Session 25 — bug fixes, qwen3_think_mode findings, playwright rewrite

**qwen3_think_mode experiment — CONFIRMED (delta=+0.330):**
75 runs (15 ERROR excluded), think_off=7.40 vs think_on=7.73. Delta exceeds 0.3 threshold.
Panel verdict: REVISE (confidence=0.5) — recommends 30 reps per treatment for stronger inference.
Practical decision: treat think_on as the default; delta is consistent across T_A/T_B/T_C.
Moving on — no further replications planned unless a new experiment revisits this variable.

**Fixes shipped:**
- `playwright_skill.py` rewritten: ARIA accessibility-tree snapshots (`page.aria_snapshot()`) replace DOM link scraping. Actions now use semantic locators (`get_by_role`, `get_by_text`, `get_by_placeholder`). New action set: `fill` (role+name) + `press` (Enter) replaces old `search`; `click` matches visible text not href. More robust to dynamic pages.
- `planner.py`: `prior_knowledge_pass()` now receives `memory_context` so the model sees existing high-quality answers and returns `gaps=[]` instead of re-searching answered tasks. `PRIOR_KNOWLEDGE_PROMPT` updated accordingly.
- `agent.py`: auto-detect playwright intent from navigation verbs ("go to / navigate to / visit / open" + domain) — routes to `/playwright` without requiring explicit prefix. `_is_technical_task()` classifier + `SYNTH_INSTRUCTION_PROSE` fallback prevents Python code blocks being hallucinated into non-technical output (recipes, general knowledge, etc.).
- `server.py`: `/orientation` skips agent subprocess on restart if `harness_orientation_raw.md` is fresher than 30 min; loads from disk instead. `_orientation_age()` helper; `force=True` param to bypass.
- `memory.py`: `_parse_compression()` strips markdown fences before regex — fixes `\`\`\`json` being stored as observation title.

## [2026-04-22] build | Session 24 — /playwright skill, LLM-guided browser navigation

Three components shipped:

1. **`playwright_skill.py`** (new file) — LLM-guided browser navigation engine. `navigate_and_extract(start_url, goal, model, max_steps=10, headed=True)` drives a Playwright Chromium instance via a decision loop: each step takes a page snapshot (title, URL, up to 60 visible links with JS, search selector, 2 KB text excerpt), calls `_decide()` which asks the oracle LLM for a JSON action (`search` / `click` / `goto` / `extract` / `fail`), executes the action, repeats. `_clean_full_text()` pulls up to 16 KB on extract. `parse_playwright_task()` extracts URL + goal from natural-language strings like "go to flavortotaste.com, find the fruit-flavored water recipe". `PLAYWRIGHT_HEADLESS=1` env var enables headless mode. Custom Chrome user-agent and 1280×900 viewport set to avoid bot blocks.

2. **`agent.py` — `_handle_playwright()` standalone handler** — calls `navigate_and_extract()`, synthesizes a summary from extracted content using the active model, stores result to memory and (if path given) writes the `.md` output file. `"playwright"` added to `_STANDALONE` dispatch dict and `_path_optional` set (no path required).

3. **`skills.py`** — `"playwright"` skill entry added with `hook: "standalone"`, `auto: None`. Example invocation: `/playwright go to flavortotaste.com, find the fruit-flavored water recipe and summarize it`.

**Integration with voice:** microphone input like "go to flavortotaste.com, find the fruit-flavored water recipe" → voice bridge classifies as task → confirmation card → approve → `/playwright` dispatched as live DAG run, browser opens, navigates intelligently, synthesizes and saves result.

**files added:** `playwright_skill.py`
**files modified:** `agent.py`, `skills.py`

## [2026-04-22] build | Session 23 — voice-to-agent bridge, active-model fallback, search activity analysis

Three features shipped:

1. **Voice-to-agent bridge** (`server.py`, `dashboard.py`) — `/api/voice` now returns structured JSON instead of a plain markdown answer. LLM classifies intent as `"task"` or `"answer"`, corrects ASR errors (brand names: "lang chained"→LangChain, "clock post"→blog post, etc.), generates a complete agent task string with suggested output path. Dashboard shows a confirmation card with editable task textarea + "Run task" / "Cancel" buttons. Approve → `POST /api/run` → appears as a live DAG run. Answer-type responses still render as markdown with copy button.

2. **Active-model fallback at agent startup** (`agent.py`) — `MODEL` and `COMPRESS_MODEL` are now resolved against the live vLLM `/v1/models` list at import time. If the configured model isn't served (e.g. `pi-qwen25-14b` not loaded), silently falls back to whatever model is actually running. Prevents 404s mid-run without requiring env var changes. Same pattern applied in `server.py`'s `/api/voice` endpoint and `orientation_skill.py`'s `_compress()`.

3. **`search_analysis.py`** — chronological analysis of agentic search activity from `runs.jsonl`. Seven sections: volume over time (weekly), topic evolution (sliding term-frequency windows), search efficiency (Pearson r of queries/score), query specificity drift (word count proxy), per-model search behaviour, top repeated queries, zero-yield query audit. No external dependencies beyond stdlib + statistics. CLI: `python search_analysis.py --windows 5 --out search_report.md`. Key findings from first run (534 runs, 1345 searches, 2.43M chars): r(n_queries, score_r1)=-0.465; query word count grew 8.2→13.8 words over 3 weeks; "cost envelope management" and "context engineering" dominate all time windows (eval suite tasks hardcoded); zero zero-yield queries.

**Validated end-to-end:** voice query "Lang Chained latest clock post" → LLM corrected to "LangChain latest blog post" → confirmation card → approved → agent dispatched → `langchain-latest-blog-post.md` written → wiggum PASS 7.0/10. grounded_r1=5 flags hallucinated code stubs (known `synth_instruction` trade-off).

**files added:** `search_analysis.py`, `search_report.md`

## [2026-04-22] build | Session 21-22 — HARNESS_ENDPOINTS multi-backend routing, /orientation skill, voice input, YouTube rewrite, Claude usage stats

Eleven features and fixes shipped:

1. **`HARNESS_ENDPOINTS` per-model routing** (`inference.py`) — highest-priority routing layer (above `INFERENCE_BACKEND`/`VLLM_MODEL_MAP`). JSON dict: `{"tag": {"url": "...", "model_id": "...", "backend": "vllm"|"llamacpp"|"openai"}}`. Enables vLLM on port 8000 + llama-server GGUFs on port 8001 simultaneously. `backend="llamacpp"` sends `chat_template_kwargs` (recent llama.cpp honors it via Jinja2 renderer); `backend="openai"` skips Qwen-specific headers. `top_k`, `top_p`, `presence_penalty` now forwarded from `options` to OAI kwargs. `get_active_vllm_model(base_url=)` accepts optional URL param. `list_endpoints()` introspection helper added.

2. **llama-server GGUF path unlocked** — `Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf` (MoE: 35B total, 3B activated; 262K native context; ~22GB Q4_K_XL) is the primary target. Serve: `llama-server.exe -m <path> --port 8001 -ngl 99 -c 65536 --alias qwen3.6-35b`. Wire: `HARNESS_ENDPOINTS={"qwen3.6": {"url": "http://localhost:8001/v1", "model_id": "qwen3.6-35b", "backend": "llamacpp"}}`.

3. **`/orientation` skill** (`orientation_skill.py` NEW, `agent.py`, `skills.py`) — standalone handler gathering situational awareness: directory tree (mtime + size), .env config (secrets redacted), recent runs summary, active experiments with run counts, git log, GPU state (nvidia-smi), wiki self-knowledge. Compresses via LLM if >14K chars. Raw doc written to `<tmp>/harness_orientation_raw.md` for server cache pickup. `final_content` and `output_bytes` written to RunTrace so synthesis output appears in dashboard inspector.

4. **Orientation refresh as live DAG run** (`server.py`) — `_refresh_orientation()` now calls `_launch("/orientation")` instead of `build_orientation()` directly. Orientation cache refresh appears as a real agent subprocess in the dashboard run list with full streaming stdout. Server reads `_ORIENTATION_RAW` after subprocess completes to populate `_orientation_doc`.

5. **Voice input** (`dashboard.py`, `server.py`) — mic FAB → MediaRecorder (webm) → POST `/api/voice` → imageio_ffmpeg conversion → whisper transcription → LLM with orientation context → markdown response with copy button. Orientation doc used as system grounding context. Active vLLM model queried as fallback when configured model returns 404.

6. **YouTube transcription rewrite** (`youtube_transcribe.py`) — yt-dlp removed entirely (Chrome cookie WSL2 lock issue). New strategy: youtube-transcript-api (auto-captions, no download) → pytubefix + whisper fallback. Direct media URLs (mp4/mp3/wav/webm etc.) via ffmpeg + whisper. `_get_ffmpeg()` resolves binary: system PATH → imageio_ffmpeg portable fallback. `WHISPER_DEVICE=cuda` default (set in `.env`).

7. **Claude Code usage stats** (`dashboard.py`) — reads `~/.claude/stats-cache.json`. Three charts: daily activity (requests/day), daily tokens (input+output stacked), input vs output by model (stacked bar). Filtered to Claude models only.

8. **Model naming fix** — `pi-qwen3-14b` renamed to `pi-qwen25-14b` throughout `inference.py`, `.env`, `experiments/producer_model_factor/spec.json` (it's Qwen2.5-14B-Instruct-AWQ, not Qwen3).

9. **`experiment_runner.py` fixes** — `_load_checkpoint` now only marks `ok=True` runs as completed (was incorrectly skipping failed runs, blocking re-runs). `--treatment <level>` flag added for single-treatment execution (avoids 404s when vLLM serves only one model at a time).

10. **`autoresearch.py` pdfminer fix** — stderr redirected to devnull during `_md.convert(url)` to suppress hundreds of color warning lines from pdfminer when processing arxiv PDFs.

11. **`qwen3_think_mode` experiment spec** (`experiments/qwen3_think_mode/spec.json` NEW) — factor: `HARNESS_PRODUCER_THINK` (think_off vs think_on); model: `qwen3-14b`; tests whether chain-of-thought reasoning improves wiggum score_r1 delta >= 0.5.

**env vars added:** `HARNESS_ENDPOINTS`
**files added:** `orientation_skill.py`, `experiments/qwen3_think_mode/spec.json`
**model serve commands:** see `.env.example` for `--max-model-len` values (pi-qwen25-14b: 23000, qwen3-14b: 28000)

## [2026-04-21] build | Session 20 — synth_instruction_prose_deep experiment, wiggum mid-run fixes, refactor audit

Three areas of work:

1. **`synth_instruction_prose_deep` experiment running** (`experiments/synth_instruction_prose_deep/`): tests whether a 4-paragraph prose instruction (mechanism → boundary conditions w/ real config values → failure modes w/ log patterns → decision rule + case study) recovers depth_r1 to baseline levels while preserving the grounded_r1 gain from prose_depth. Primary metric: `score_r1` composite delta >= 0.2. Secondary: grounded_r1 >= 7.0, depth_r1 >= 6.5. First-ever PASS observed on run 1 (T_A prose_grounded_deep). Experiment still in progress at session end.

2. **Wiggum mid-run fixes** (`wiggum.py`) — three bugs caught and patched while experiment was running (changes apply to future subprocess invocations without restart):
   - **Style reminder in REVISE_PROMPT**: `_revise_style_reminder()` injects `HARNESS_SYNTH_INSTRUCTION` into the revision prompt so grounded constraints are maintained across revision rounds. Root cause: grounded dropped 8→6→8 during revision because REVISE_PROMPT had no reference to original output constraints.
   - **Language consistency rule** in `EVAL_PROMPT` universal rules: caps `structure` at 3 if non-English characters appear in the output. Root cause: Qwen2.5-14B code-switched to Chinese in a JPMorgan paragraph; Selene gave a PASS despite mixed-language output.
   - **Restore message display fix**: `cmp = ">" if best_score > score else "="` — previously always showed `>` even when scores were equal, making cycling logs misleading.

3. **Refactor audit + technical debt roadmap** (`wiki/roadmap.md`) — full directory survey and import dependency audit:
   - Root directory has 130+ items; catalogued into 4 cleanup phases (TD-1 through TD-4 in roadmap)
   - Import audit: `inference.py` has 16 dependents; `*_skill.py` files and `panel.py` import only `inference` and are safe to move to `skills/`; `experiment_runner.py` is also invoked as a subprocess (impacts move planning)
   - Trace pipeline gap identified: `_write_trace()` never calls `log_artifact()`, making traces invisible to the session data model. Proposed fix: session-scoped subdirectories + artifact registration + experiment-context label
   - All findings documented as TD-1 through TD-4 in roadmap under new "Technical debt / pre-refactor cleanup" section

**files modified:** `wiggum.py`, `wiki/roadmap.md`, `wiki/log.md`
