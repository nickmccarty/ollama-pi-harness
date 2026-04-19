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

**env vars added:** `INFERENCE_BACKEND`, `VLLM_BASE_URL`, `VLLM_MODEL_MAP`, `WIGGUM_EVALUATOR_MODEL`, `WIGGUM_PRODUCER_MODEL`, `LLAMA_OCR_BASE_URL`
