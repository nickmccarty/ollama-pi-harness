# Roadmap: Self-Improving Agentic Swarm

## North Star

A locally-running swarm of specialized agents that iteratively improves its own harness, models, and capabilities — without human intervention beyond goal-setting and checkpoint approval.

The end state:
- **Proposer agents** generate harness mutations (synthesis instructions, search strategy, rubric parameters, chunking config)
- **Executor agents** run eval tasks in parallel against the proposed mutation
- **Critic agents** score results using typed telemetry from structured event traces, decide keep/revert
- **Trainer agents** trigger fine-tuning when preference data crosses a threshold; benchmark the checkpoint
- **Integrator agents** promote checkpoints, hot-swap via vLLM, commit new baselines

The loop closes continuously: run → preference data → fine-tune → hot-swap → benchmark → promote or revert. Human checkpoints at goal-setting and promotion; everything between is autonomous.

This is achievable on a single RTX 5000 Ada (63.8GB VRAM) with the harness architecture already in place. The scaffolding — orchestrator, autoresearch, evaluator separation, RLHF feedback, memory, fine-tuning pipeline — is mostly built. What remains is closing the manual hand-offs, expanding the mutation surface, and adding the structured telemetry the critic needs to reason about *why* something worked.

---

## Current Baseline

A working three-stage pipeline running locally via Ollama:

1. **Research** (`agent.py`) — agentic web search loop using `ddgs`, forced synthesis after 2 rounds, Python writes output to disk
2. **Verify/Revise** (`wiggum.py`) — evaluates output with `qwen2.5:72b`, revises with producer if failing, loops up to 3 rounds
3. **Ground-truth eval** (`eval.sh`) — filesystem checks independent of model self-report

Demonstrated self-correction: 3/10 to 9/10 in one wiggum revision round without human intervention.

**Known gaps heading into Stage 1:** no structured logging, no eval suite, evaluator criteria too generic (depth not rewarded), no vision, no orchestration.

---

## Stage 1 - Harden the Single Agent (current focus)

*Objective: production-grade reliability for a single text agent before adding complexity.*

### Structured logging - DONE
`logger.py` implemented. Every run appends to `runs.jsonl`:

```json
{
  "timestamp": "2026-04-08T22:15:10+00:00",
  "task": "...",
  "producer_model": "pi-qwen-32b",
  "evaluator_model": "Qwen3-Coder:30b",
  "run_duration_s": 714.0,
  "input_tokens": 10391,
  "output_tokens": 2424,
  "tokens_by_stage": {
    "tool_loop":   {"input": 4481, "output": 1292, "calls": 3, "total_ms": 364331},
    "synth":       {"input": 2337, "output":  461, "calls": 1, "total_ms": 128263},
    "wiggum_eval": {"input": 1210, "output":  251, "calls": 1, "total_ms": 15919}
  },
  "tool_calls": [{"name": "web_search", "query": "...", "result_chars": 2326}],
  "synth_forced": false,
  "output_path": "C:\\Users\\nicho\\Desktop\\harness-engineering\\...",
  "output_lines": 56,
  "output_bytes": 1856,
  "wiggum_rounds": 1,
  "wiggum_scores": [8.8],
  "wiggum_dims": [{"relevance": 10, "completeness": 8, "depth": 9, "specificity": 8, "structure": 9}],
  "final": "PASS"
}
```

`inspect_run.py` — pretty-printer for `runs.jsonl`: `python inspect_run.py` (last run), `python inspect_run.py 3`, `python inspect_run.py --all`.

Followed by:
- try/finally in `run()` — DONE. Failed runs now always log with `"final": "ERROR"`.
- Dual search + quality floor — DONE. See Dual Search section in journal.
- `total_search_chars` and `quality_floor_hit` added to every log record.

Analytics script (`analytics.py`) — DONE. Compares single vs dual search across all logged metrics. Run `python analytics.py` or `python analytics.py --full` for per-run detail.

**Validated findings from 6 runs (single vs dual comparison):**
- Dual search: +58% output bytes, +3x output lines, first-round score 7.7 -> 9.0, wiggum rounds 1.3 -> 1.0
- Search result volume (`total_search_chars`) is a reliable leading indicator of output quality at regime boundaries

**Revised finding from experiment-01 (15 total runs):**
- Within the dual-search regime, search volume is no longer predictive (r = -0.577, noise). The leading indicator finding holds at regime scale, not within a stable operating band.

**Experiment-01 completed:** 9-run CRD across 3 task types. 9/9 PASS. Key findings: open-ended tasks more consistent than constrained tasks (counter-intuitive); wiggum loop now rarely activates (first-pass quality too high to differentiate); count constraint rules not reliably enforced by glm4:9b evaluator; search volume no longer predicts output volume within the dual-search regime. Full analysis in `experiment-01.md`.

### Eval suite — DONE

`eval_suite.py` — regression harness with 5 tasks across 3 task types (enumerated, best_practices). Checks: `min_bytes`, `min_lines`, `exact_sections` / `min_sections`, `no_placeholders`, `has_impl_notes`, `no_file_path_refs`. First run: 5/5 tasks, 30/30 criteria. Run after any model swap, Modelfile change, or harness modification.

```bash
python eval_suite.py              # full run + check
python eval_suite.py --fast       # criteria check against existing output files only
python eval_suite.py --no-wiggum  # run tasks, skip verification loop
```

**Count constraint enforcement — DONE.** `agent.py` now extracts the count from the task string (regex on "top N", "N most", etc.), counts H2-level sections in the synthesized output, and re-synthesizes with an explicit count instruction if they don't match. Harness-side check, not evaluator-dependent.

**Decimalized rubric scoring — DONE.** Evaluator now scores 5 weighted dimensions: relevance (20%), completeness (25%), depth (30%), specificity (15%), structure (10%). Python recomputes the composite from raw dimension scores — model arithmetic not trusted. `PASS_THRESHOLD = 8.0`. Composite and per-dimension scores logged in `wiggum_dims` per round. Typical passing score: 8.3 (rel=9, cmp=8, dep=8, spc=8, str=9).

**Adversarial critique: attempted and reverted.** Two-pass evaluation (critique then score) generated real signal (5→6→7) but created a jargon spiral: producer added increasingly specific technical terms → evaluator critiqued those terms → producer couldn't satisfy at 7B level. Reverted. Requires a stronger producer or a better-matched evaluator/producer pair.

### Evaluator criteria refinement - DONE
Tightened scoring guide in `wiggum.py`: 9-10 reserved for exceptional output, 7-8 for good, explicit rule that 10/10 requires finding at least one improvement. Fixed rubber-stamping behavior in glm4:9b.

Task-type-specific criteria added: `detect_task_type()` classifies each task as `enumerated`, `best_practices`, or `research`. The appropriate criteria block is injected into the eval prompt. `task_type` is logged to `runs.jsonl` via the wiggum trace for future analytics breakdowns.

- **enumerated**: count enforcement, distinct name + example + implementation note per item, duplicate detection
- **best_practices**: completeness across dimensions, actionability (specific verb), flag missing major practices
- **research**: synthesis over fact-listing, context for application, flag missing nuance

### Additional tools — DONE (read_file, run_python)

**`read_file` (harness-side):** Detects text file paths (`.txt`, `.py`, `.json`, `.csv`, `.yaml`, etc.) in the task string, reads them, injects as `File contents:` block in synthesis. Logged as `files_read` in `runs.jsonl`.

**`run_python` (tool-calling loop):** Pre-synthesis agentic loop. Model can call `run_python` up to 3 rounds for data processing or computation. Execution output injected as `Code execution results:` block. Subprocess with 10s timeout. For research tasks, model responds "no code needed" with no measurable overhead.

**Security layer (`security.py`):** All tool calls pass through three harness-enforced checks before execution. No model-in-the-loop for security — models can be jailbroken; static analysis is the ground truth.
- **Code scanner:** Two-pass AST analysis blocks dangerous imports (`os`, `subprocess`, `sys`, `shutil`, `socket`, `requests`, `pathlib`, `ctypes`, ...) and calls (`exec`, `eval`, `open`, `__import__`).
- **Path sandbox:** `read_file` restricted to `~/Desktop` and `~/Documents`. Blocklist for `.env`, SSH keys, `.pem`, `secrets`, `credentials`, etc.
- **Prompt injection scanner:** Web search results and file contents scanned for injection patterns before entering synthesis prompt. Suspicious lines stripped (not just flagged). `injection_stripped` count logged per run.

**MarkItDown integration — DONE.**

`markitdown` added as a document-conversion backend with graceful fallback if not installed.

1. **Rich document reading:** `RICH_EXTENSIONS = {.pdf, .docx, .xlsx, .pptx, .epub, ...}` — task-referenced rich documents are routed through `MarkItDown.convert()` instead of plain `open()`. Markdown output injected as file context alongside plain-text files.

2. **URL enrichment:** after merging search snippets, `enrich_with_page_content` fetches full HTML for the top `URL_ENRICH_COUNT = 2` search result URLs and appends them to the research context (capped at 8k chars each). Observed: 3.4k snippet context → 19.7k after enrichment on experiment-04 run 4.

Install: `pip install "markitdown[all]"`

Remaining additional tools:
- `list_files(directory)` - model can inspect the workspace
- `playwright` / `chrome-devtools-mcp` - browser interaction and page content extraction

### Memory — DONE

`memory.py` — SQLite + FTS5 persistent observation store. No external services, no API keys.

**Write path:** after every run, `glm4:9b` compresses the run into title + narrative + facts[] and stores to SQLite. Non-fatal — compression failure never aborts a run.

**Read path:** FTS5 BM25 keyword search returns the N most relevant past observations as a `## Relevant past research` block, injected into synthesis. Falls back to recency-order if no FTS matches.

`memory_hits` logged per run. CLI: `python memory.py` / `python memory.py --search "query"`.

### Planning layer — DONE

`planner.py` — pre-execution task analysis. Runs after memory retrieval, before research begins. `glm4:9b` receives task + memory observations and produces a structured `Plan`.

**Plan feeds three stages:**
- `gather_research`: uses `plan.search_queries` (planned before any search runs) instead of auto-generating
- `synthesize`: injects `plan.prior_work_summary` + `plan.notes` alongside memory observations
- Count constraint: `plan.expected_sections` takes precedence over regex detection

**`Plan.subtasks` is empty — the Stage 3 hook.** Filling it and spawning `agent.run()` per subtask is the orchestrator.

`plan` dict logged per run. CLI: `python planner.py "<task>"`.

### Wiggum best-round restoration — DONE (2026-04-12)

Analysis of 123 eval runs found 12/57 multi-round runs regressed: final score < r1 (avg −0.36). Wiggum was unconditionally returning the last round's content. Fixed: `loop()` now tracks `best_score / best_content / best_round` across all rounds and restores the best content to disk before returning FAIL if a later round scored lower. Also fixed: termination gate was using the `MAX_ROUNDS` global constant instead of the `max_rounds` local variable — `WIGGUM_MAX_ROUNDS` env override now works correctly at the exit gate.

### synthesize_with_count uses SYNTH_INSTRUCTION — DONE (2026-04-12)

`SYNTH_INSTRUCTION_COUNT` was session-1-era quality and had never been through the autoresearch optimization loop. Ablation run revealed it was producing ~1300-byte outputs vs 5000–7000 bytes from SYNTH_INSTRUCTION on identical tasks, with r1 dropping from 8.8 → 6.9. Fixed: `synthesize_with_count()` now uses `SYNTH_INSTRUCTION` with the count constraint injected as a prefix. `SYNTH_INSTRUCTION_COUNT` is dead code, left inside its autoresearch sentinels.

Also: `expected_count` is now extracted before the first `synthesize()` call, routing enumerated tasks directly to `synthesize_with_count()` rather than running a wasted first synthesis pass.

### Closed-book prior knowledge pass — DONE (Session 11)

`prior_knowledge_pass()` added to `planner.py`. One LLM call before main planning asks what the model already knows vs what needs web search. Gaps feed into `PLAN_PROMPT` so queries target unknowns; `known_facts` injected into `synthesis_context()` as a verified-facts block. Logged on `Plan.known_facts` / `Plan.knowledge_gaps`.

### Wiggum cycling detection — DONE (Session 11)

Score + all dimension scores identical across consecutive rounds → return best-round content immediately, no further revision calls. Implemented in both `loop()` and `loop_annotate()` in `wiggum.py`.

### Autoresearch stall replan — NEXT

If 4+ consecutive autoresearch experiments are discarded, inject a directive into `PROPOSE_PROMPT`: "The last 4 variations were all discarded. Stop refining — propose a fundamentally different framing approach." Mirrors MagenticOne's replan trigger. Breaks proposer out of local minima; the local proposer clustered in "add code examples" for 10 consecutive experiments in session 1.

---

## Stage 2 - Add Vision — DONE (routing layer)

*Objective: handle image inputs (screenshots, diagrams, charts) alongside text.*

**Option A: Routing layer — implemented.**

`vision.py` — standalone vision preprocessing module:
- `detect_image_paths(task)` — finds image file paths in task string, checks they exist
- `extract_image_context(image_path, task)` — sends image + task-aware prompt to `llama3.2-vision`, returns text description
- Supports: png, jpg, jpeg, gif, bmp, webp

`agent.py` — routing wired in:
- Vision runs before web search if images detected
- Extracted descriptions injected into synthesis prompt alongside web research
- `vision_images` logged per run

**Validated end-to-end:** Screenshot of Anthropic's "Building Effective Agents" page → llama3.2-vision extracted title, key points, and structure → pi-qwen synthesized 10-principle markdown document → wiggum scored 8.0/10 PASS (rel=9, cmp=8, dep=7, spc=8, str=9).

```
user input (task + image path)
    |
    +-- image path detected? --> llama3.2-vision --> text description
    |                                                       |
    +-- web search x2 ---------------------------------> synthesize (both sources) --> write --> wiggum
```

**Option B: External vision preprocessing**
Use Python (Pillow, pytesseract, markitdown) to preprocess images before the model sees them. Converts vision tasks to text tasks, keeping the model layer simple.

**Available vision models locally:**
- `llama3.2-vision` - confirmed tool-capable + vision, best current option
- `qwen2.5vl` - vision capable but does not support tools

---

## Stage 3 - Orchestrator + Specialized Subagents — DONE

*Objective: decompose complex tasks across multiple specialized agents.*

### What's implemented

`orchestrator.py` — parallel orchestration of research subtasks with cross-referencing assembly.

```
orchestrate(task)
  memory + planning  →  if no subtasks: delegate to agent.run()
  assign _sub_N.md paths
  ThreadPoolExecutor: agent.py --no-wiggum × N  (subprocess isolation, SUBTASK_MAX_WORKERS=4)
  assemble()                                    (cross-referencing synthesis from all subtask outputs)
  count check + write + wiggum + memory store + cleanup
```

**Transparent passthrough:** single-focus tasks hit the same code path as before — no regression.

**Subprocess isolation:** each subtask is a separate Python interpreter. Avoids shared stdout, `sys.exit()` propagation, and memory write conflicts. SQLite WAL mode handles concurrent writes.

**Validated (Stage 4a):** 2-subtask orchestrated run completes in ~35s wall time (was ~65s sequential). ~1.9× speedup.

### Architecture (current)

```
orchestrator.py
    |
    +-- subprocess(agent.py) × N   (pi-qwen: web search, read_file, run_python)
    +-- assemble()                 (pi-qwen: cross-referencing synthesis)
    +-- wiggum.loop()              (Qwen3-Coder:30b: evaluate → revise → verify)
```

### Remaining gaps

- **Research agents only** — no specialised code agent, vision agent, or write agent yet; all subtasks run through the same `agent.py` pipeline
- **No inter-subtask scope coordination** — subtasks don't know each other's scope at planning time; they discover shared context only via memory after the fact
- **Assembly quality bounded by producer** — pi-qwen cross-references but doesn't synthesise at the depth a 72B model would

### 4a: Parallel execution — DONE

`ThreadPoolExecutor` with subprocess workers. SUBTASK_MAX_RETRIES=1, SUBTASK_MAX_WORKERS=4. Wall time ~1.9× improvement on 2-subtask runs. Output captured per-subtask and printed sequentially after all complete.

### 4c: Producer upgrade — DONE (pi-qwen-32b is now default)

Experiment-03 exposed the 7B producer ceiling: depth=6, specificity=6 on enumerated tasks regardless of revision. The evaluator is working; the producer is the bottleneck.

**`--producer` flag added to `agent.py`** — both synthesis and wiggum revision now use the specified model. Enables per-run producer swaps without changing defaults.

**32B confirmed:** `--producer pi-qwen-32b` on T_A: round 1 = 7.0, round 2 = **8.1 PASS** (depth=8, spc=8). The 7B regressed on the same task; the 32B responds to depth feedback. T_B and T_C pass round 1 at 8.6+.

**Models pulled:**

| Model | Size | Status |
|-------|------|--------|
| `qwen2.5:32b-instruct-q4_K_M` | ~20GB | `pi-qwen-32b` created — **confirmed upgrade** |
| `mistral-small3.1:24b` | ~15GB | Pulled, Modelfile pending |
| `phi4:14b` | ~9GB | Pulled, needs template override for tool-calling |

**Default swapped:** `MODEL = "pi-qwen-32b"` in `agent.py` and `PRODUCER_MODEL = "pi-qwen-32b"` in `wiggum.py`. **Experiment-04 complete** — 16 runs, 12/16 PASS (75% vs 44% in exp-03). Full results in `experiment-04.md`.

**Key findings from exp-04:**
- T_A ceiling broken: 4/4 PASS, rounds 3.0→1.25, depth +1.2, zero revision regressions
- T_B first-pass quality flat (depth_r1 6.1 vs 6.0 in exp-03) — synthesis instruction is the bottleneck, not the producer
- MarkItDown URL enrichment triggers high count_check_retry on enumerated tasks — tune `URL_ENRICH_COUNT` to be task-type-aware

**Next: autoresearch** targeting T_B depth/specificity.

### 4b: Evaluator upgrade — DONE

`Qwen3-Coder:30b` replaces `glm4:9b` as evaluator. 30B vs 9B — evaluator is now the most capable model in the stack. Revision loop now activates on genuinely weak outputs (7.0→8.8 on a minimal agent failure modes document). Prompt updated with calibration anchors, per-dimension issue requirement, and strict-bias instruction.

### 4d: Autoresearch loop — DONE

`autoresearch.py` — autonomous synthesis-instruction optimizer. Runs indefinitely, proposing modifications to `SYNTH_INSTRUCTION` and `SYNTH_INSTRUCTION_COUNT` in `agent.py`, testing them against the eval metric, and keeping improvements via git commit.

**Metric:** `composite = 0.7 * mean_wiggum_r1 + 0.3 * criteria_rate * 10` — continuous float, comparable across experiments. Bottleneck dimensions: depth (0.30) and specificity (0.15).

**Keep rule:** `new_score - baseline > 0.1` → keep + commit. Otherwise `git reset HEAD~1 --soft`.

`autoresearch_program.md` defines the full scope, mutable boundaries, and what good looks like.

### 4e: Synthetic eval tasks (TinyTroupe) — DONE

`tinytroupe_tasks.py` — 8 practitioner personas generate diverse research task requests, saved to `generated_tasks.json`. Extends the autoresearch eval surface beyond 5 fixed tasks. `eval_suite.py --generated` loads and runs them.

Install TinyTroupe: `pip install git+https://github.com/microsoft/TinyTroupe.git@main` (PyPI package not available; install from GitHub)

### Shared harness layer (in place)
- Shared memory (`memory.db` — all agents read/write across the session)
- Shared observability (`runs.jsonl` — each subtask logs its own full trace)
- Shared security (`security.py` — applied per subtask run)
- Shared workspace (filesystem — subtasks can read each other's outputs via `read_file`)

---

## Stage 5 - Retrieval Infrastructure

*Objective: replace brittle lexical retrieval and hard-truncated context with semantic search, chunked document retrieval, and a search result cache. Motivating forcing function: the autoresearch loop runs the same eval tasks repeatedly — DDGS rate limits and latency are already a bottleneck.*

### 5a: Search result cache — highest near-term value

**Problem:** autoresearch runs T_A and T_B on every experiment iteration, making near-identical DDGS queries each time. ~30s of search latency per eval pair, plus rate-limit risk at scale.

**Approach:** cache by normalized query fingerprint → result set. SQLite-based (TTL column, no new services) keeps the zero-external-dependency principle. Redis is the alternative if pub/sub or cross-process invalidation becomes necessary.

**Key parameters:**
- TTL: 24h — search results go stale but not in hours
- Cache location: `search_cache.db` (gitignored)
- Fingerprint: lowercase + stripped query string

**Where to wire in:** `web_search_raw()` in `agent.py` — transparent to the rest of the pipeline.

### 5b: Embedding model + semantic memory retrieval

**Problem:** `memory.py` uses FTS5 BM25 keyword search. Semantic overlap without lexical overlap is missed — "token pruning" and "context compression" describe the same technique and won't co-retrieve.

**Approach:** add a `vec0` virtual table to `memory.db` via `sqlite-vec`. At write time, embed the observation narrative + facts via Ollama and insert into `vec0`. At read time, run both FTS5 BM25 and KNN on `vec0`, merge results with reciprocal rank fusion (RRF). Pure C extension, no new services, runs in the same SQLite process.

```python
import sqlite_vec
db.enable_load_extension(True)
sqlite_vec.load(db)
db.enable_load_extension(False)

# vec0 virtual table — dimensionality matches nomic-embed-text output (768)
db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS vec_observations USING vec0(embedding float[768])")

# KNN query — top-5 nearest observations to the task embedding
db.execute("""
    SELECT o.id, o.title, o.narrative, vec_distance_cosine(v.embedding, ?) AS distance
    FROM vec_observations v JOIN observations o ON o.id = v.rowid
    ORDER BY distance LIMIT 5
""", [task_embedding_blob])
```

**Embedding model:** `nomic-embed-text` via Ollama (~270MB, fast, runs locally).
```python
resp = ollama.embeddings(model="nomic-embed-text", prompt=text)
embedding = resp["embedding"]   # list[float], len=768
blob = struct.pack(f"{len(embedding)}f", *embedding)   # sqlite-vec binary format
```

**Related:** `sqlite-rembed` (same author) can call Ollama's embedding API directly from SQL — useful for ad-hoc SQL scripts, but Python-side embedding gives more control for the write path.

**Install:** `pip install sqlite-vec`

**Shared infrastructure:** the same embedding model and `sqlite-vec` setup feeds both memory retrieval (5b) and chunked URL retrieval (5c). Build once, use twice.

### 5c: Chunked URL content retrieval

**Problem:** MarkItDown URL enrichment currently hard-truncates at `URL_ENRICH_MAX_CHARS = 8000` (first 8k chars). Important content at the end of pages is silently dropped.

**Approach:** chunk each fetched page into ~512-token overlapping segments, embed each chunk, retrieve the top-K chunks most semantically similar to the task string. Replaces "first 8k chars" with "most relevant 8k chars".

**Chunking strategy:**
- Chunk size: ~512 tokens (~2k chars) with 20% overlap
- Retrieval: top-3 chunks per URL, concatenated
- Fallback: if embedding model unavailable, revert to head truncation

**Dependency on 5b:** uses the same `nomic-embed-text` model, `sqlite-vec` binary format, and `vec0` infrastructure. Implement 5b first.

### 5d: CLIP multimodal embeddings

**Problem:** vision pipeline (`vision.py`) describes images with `llama3.2-vision` and injects the text description. Images cannot be retrieved by semantic similarity to past observations — every image requires a fresh description call.

**Approach:** embed image inputs with CLIP at preprocessing time. Store image embeddings alongside text observations in `memory.db`. At retrieval time, cross-modal search: task string → text embedding → find relevant past observations that include images.

**Use case:** an agent that has previously analyzed a screenshot of a dashboard can retrieve that observation when given a similar-looking dashboard, without re-running vision.

**Dependency on 5b:** shared embedding infrastructure; CLIP adds a separate image tower.

**When to build:** after 5a–5c are stable and vision use cases have multiplied beyond the current single-image-preprocessing pattern.

### 5e: Perfetto trace instrumentation — DONE

`logger.RunTrace` now emits Chrome Trace Event JSON to `traces/<timestamp>_<slug>.json` at the end of every run. Load at `ui.perfetto.dev` — no install required.

- `trace.span("stage")` — wall-clock duration events for every pipeline stage
- `trace.name_thread("panel/Reviewer")` — thread lane labels for parallel panel
- `trace.log_usage(response, stage=...)` — `llm:<stage>` events from Ollama `total_duration`

Panel parallelism now visible in traces: 3 personas run concurrently via `ThreadPoolExecutor`, each in a named lane.

### Priority order

| Step | Dependency | Status |
|------|-----------|--------|
| 5a: Search cache | None | Not yet — DDGS rate limits still a bottleneck |
| 5b: Embedding model + semantic memory | None | **DONE** — ChromaDB replaces FTS5 |
| 5c: Chunked URL retrieval | 5b | **DONE** — `chunker.py` with provenance metadata |
| 5d: CLIP multimodal embeddings | 5b | Future — when vision use cases multiply |
| 5e: Perfetto traces | None | **DONE** — `traces/` dir, loadable at ui.perfetto.dev |

### Trace-derived fixes (2026-04-10)

Analysed 10 autoresearch traces. Key findings and actions:

| Finding | Impact | Fix | Status |
|---------|--------|-----|--------|
| `synth_count` retry fires on every T_D (enumerated) run; URL context causes flat-list format failure | 29–56% overhead on top of synthesis (300–1000s/run) | `enrich_count = 0 if task_type == "enumerated"` in `gather_research()` | **DONE** |
| `compress_knowledge` consumes 80–90% of `gather_research` wall time; scales with search rounds | Up to 294s on compress vs 442s total gather | Full `gather_research()` output cached in `research_cache` table (24 h TTL, opt-in via `RESEARCH_CACHE=1`) | **DONE** |
| `wiggum_revise` costs 11–22% of total when it fires | 310–1116s per revision pass | Optimising round-1 score (autoresearch target) directly reduces this | By design |
| Panel threads not visible in autoresearch traces — `WIGGUM_PANEL` not propagated to subprocess | Panel running in manual runs only | Pass env var through autoresearch subprocess | **DONE** |

---

## Stage 4 - Self-Improving Agent Swarm

*Objective: a coordinated swarm of specialized agents that handles complex tasks AND iteratively improves the harness, models, and its own capabilities with minimal human intervention.*

### The self-improvement loop

```
goal-setting (human)
    ↓
Proposer agent — generates harness mutation (instruction, rubric param, search config)
    ↓
Executor agents (parallel) — run eval tasks with mutation applied
    ↓
Critic agent — scores via typed event telemetry, decides keep/revert
    ↓
  keep → Trainer agent — triggers fine-tune when preference data threshold crossed
            ↓
          checkpoint → vLLM hot-swap → benchmark
            ↓
          Integrator agent — promotes, commits new baseline
  revert → git reset, next proposal
```

Human checkpoints: goal-setting and checkpoint promotion. Everything between is autonomous.

### What changes at swarm scale

**Communication:** shared message bus via SQLite append-only JSONL — all agents read/write. Redis if pub/sub or cross-process invalidation becomes necessary.

**Agent identity:** each agent has a role, capability profile, and trust level. Orchestrator assigns tasks via capability matching, not hardcoded routing.

**Structured telemetry as critic input:** the critic reasons about *why* a mutation worked using typed event traces (plan events, search events, wiggum dimension scores, span timings) — not just a scalar score. This is why 7h (structured event protocol) is a prerequisite.

**Failure propagation:** when one agent fails — retry, reroute, escalate, or abort. Multi-agent equivalent of the wiggum verification loop.

### Mutation surface (expanding from autoresearch)

Current autoresearch mutates only `SYNTH_INSTRUCTION`. Full self-improvement requires the proposer to target any harness config parameter:

| Component | Mutable parameters |
|-----------|-------------------|
| Synthesis | `SYNTH_INSTRUCTION`, `SYNTH_INSTRUCTION_COUNT` |
| Search | `MAX_SEARCH_ROUNDS`, novelty threshold, query generation prompt |
| Wiggum | rubric weights, `PASS_THRESHOLD`, dimension definitions |
| Planner | gap-detection prompt, complexity classifier |
| Chunker | chunk size, overlap, top-K retrieval |
| Fine-tune | LoRA rank, learning rate, training data mix |

### Multimodal inputs
- Text prompts: research + write pipeline (current)
- Screenshots: vision agent → text agents
- PDFs: markitdown + chunker → research or write agents
- Structured data (CSV, JSON): code agent processes, write agent documents
- Audio (future): transcription agent feeds text pipeline

### Hardware fit (RTX 5000 Ada, 63.8GB VRAM)

63.8GB VRAM removes the single-GPU tradeoff that constrained earlier design. Options that weren't viable at 24GB:
- pi-qwen-32b producer + Qwen3-Coder:30b evaluator + llama3.2:3b skill agent simultaneously
- vLLM continuous batching across all three with headroom for LoRA adapters
- Fine-tuning a 7B model while serving a 32B producer (separate VRAM partitions)

The coordination overhead — not VRAM — is now the binding constraint.

### 4f: vLLM serving layer — ACTIVE (2026-04-15)

**Problem:** Ollama processes one `ollama.chat()` request at a time per model. When 4 parallel subtask subprocesses all hit `pi-qwen-32b`, 3 block at the Ollama queue. `ThreadPoolExecutor(max_workers=4)` gives process concurrency; Ollama collapses it to serial LLM execution. The coordination overhead, not VRAM, is the binding constraint.

**Solution:** vLLM continuous batching — multiple in-flight requests are batched at the attention kernel level.

**What's in place:**

`inference.py` — unified backend shim. Drop-in replacement for `import ollama`:

```python
# Before (agent.py, wiggum.py, autoresearch.py):
ollama = type("_OllamaShim", (), {"chat": staticmethod(_ollama_chat)})()

# After:
from inference import OllamaLike
ollama = OllamaLike(keep_alive=_KEEP_ALIVE)
```

Routing controlled by `INFERENCE_BACKEND=vllm` in `.env`. All other call sites unchanged. `_OllamaResponse` adapter normalizes OpenAI response shape (token counts, timing) to match what `logger._extract_usage()` expects — no dashboard changes needed.

`requirements-vllm.txt` — pinned vLLM dep tree (vllm==0.7.3, transformers==4.49.0), isolated from the main harness env to avoid torch/CUDA conflicts.

**Hardware note:** RTX 5000 Ada Laptop (16GB VRAM). Serving `Qwen/Qwen2.5-14B-Instruct-AWQ` (AWQ int4, ~9.4GB loaded). Model map in `.env` routes all harness model tags (`pi-qwen-32b`, `pi-qwen`, `Qwen3-Coder:30b`) to the served model while on 16GB hardware. On the desktop (63.8GB), run producer and evaluator on separate instances (:8000, :8001).

**WSL2 setup (tested 2026-04-15):**
```bash
# In WSL2 Ubuntu 24.04:
conda create -n vllm python=3.12 -y && conda activate vllm
pip install torch==2.6.0+cu124 --index-url https://download.pytorch.org/whl/cu124
pip install vllm==0.7.3 "transformers==4.49.0"   # pin transformers — 4.50+ breaks Qwen2Tokenizer

export HF_HOME=/mnt/c/Users/nicho/.cache/huggingface
vllm serve Qwen/Qwen2.5-14B-Instruct-AWQ \
  --dtype half \
  --quantization awq_marlin \
  --max-model-len 8192 \
  --enable-prefix-caching \
  --gpu-memory-utilization 0.90
```

**In `.env` (Windows harness):**
```
INFERENCE_BACKEND=vllm
VLLM_BASE_URL=http://localhost:8000/v1
VLLM_MODEL_MAP={"pi-qwen-32b":"Qwen/Qwen2.5-14B-Instruct-AWQ","pi-qwen":"Qwen/Qwen2.5-14B-Instruct-AWQ","Qwen3-Coder:30b":"Qwen/Qwen2.5-14B-Instruct-AWQ"}
```

**Validated end-to-end (2026-04-15):** `test_harness_vllm.bat` passed. Full research + write run: 376.6s, in=7013 out=1063 tok. All pipeline stages (planner, search, novelty, markitdown, security, synthesis, write, memory) worked correctly via vLLM backend.

**Three unlocks at Stage 4:**

| Bottleneck | Unlock |
|---|---|
| Serial Ollama queue blocks 4 parallel subtasks | Continuous batching — all 4 requests batched simultaneously |
| Prefix re-processing on every autoresearch iteration | Prefix caching (`--enable-prefix-caching`) eliminates repeated system prompt eval |
| Checkpoint promotion requires Ollama model pull + server restart | `--enable-lora` + `POST /v1/load_lora_adapter` — integrator agent hot-swaps adapters live |

**Timing approximation note:** The OpenAI API body doesn't expose per-phase latencies (`eval_duration`, `prompt_eval_duration`). `_OllamaResponse` approximates them as 88%/12% of wall-clock time. For tighter measurements, wire in vLLM's `/metrics` Prometheus endpoint post-hoc.

**Remaining work:**

1. **Evaluator routing** — when running two vLLM instances (producer :8000, evaluator :8001), need `VLLM_EVALUATOR_BASE_URL` support in `inference.py`.
2. **Gradual migration** — all `_ollama_raw.chat()` call sites migrated to `inference.py` in Session 11.
3. **`think` flag** — ✅ translated in Session 11: `options={"think": bool}` → `extra_body={"chat_template_kwargs": {"enable_thinking": bool}}` (vLLM ≥0.6.4).
4. **`awq_marlin`** — ✅ switched to `awq_marlin` in Session 11; requires `--max-model-len 8192 --gpu-memory-utilization 0.90` (awq_marlin activation peaks leave insufficient KV cache at 16384).
5. **Benchmark** — run `eval_suite.py` with `INFERENCE_BACKEND=vllm` and confirm tok/s figures before promoting as permanent default.

---

---

## Stage 5b - Skills System — DONE

Extensible skill registry (`skills.py`) that hooks into the pipeline at four points without modifying `agent.py` core logic.

**Implemented skills:**

| Skill | Hook | Trigger | Description |
|-------|------|---------|-------------|
| `annotate` | pre_synthesis | task mentions "paper", "abstract", "survey" | Nanda 8-move annotated abstract framework |
| `cite` | pre_synthesis | explicit only | Require source attribution per claim |
| `kg` | post_synthesis | task mentions "knowledge graph" | Generate D3.js knowledge graph |
| `deep` | pre_research | task mentions "comprehensive", "exhaustive" | Force MAX_SEARCH_ROUNDS, disable novelty gate |
| `panel` | post_wiggum | plan.complexity == "high" | Run 3-persona evaluation panel |

Usage: `python agent.py "/annotate /cite Search for RAG papers..."` or auto-triggered.

`annotate_abstracts.py` — standalone batch annotated abstract generator for CSV inputs.

---

## Stage 6 - Training Data Pipeline — DONE (initial)

The harness now produces structured training data as a byproduct of normal operation.

### What's implemented

`hf_export.py` — exports `runs.jsonl` to four Hugging Face-ready dataset formats:

| Dataset | Shape | Use case |
|---------|-------|----------|
| `sft.jsonl` | system + user + assistant | SFT, distillation |
| `preference.jsonl` | prompt + chosen + rejected | DPO, ORPO, CPO |
| `reward.jsonl` | prompt + response + score + rubric | Reward model training |
| `trajectory.jsonl` | task + plan + stage trace | Agent policy imitation |

The 57 autoresearch runs on a single eval task (T_D) produce dense preference pairs where the only variable is synthesis instruction quality — ideal for preference learning with low confounding.

`logger.py`: `final_content` field (up to 16k chars) stored inline in every run — future exports are self-contained.

### Next steps

- **Push to Hub:** `python hf_export.py --push nickmccarty/ollama-pi-harness-datasets`
- **SFT run:** `trl sft --model <base> --dataset hf_datasets/sft.jsonl`
- **DPO run:** `trl dpo --model <sft-model> --dataset hf_datasets/preference.jsonl`
- **Revision preference data:** capture pre-revision output in `runs.jsonl` to enable within-run preference pairs (currently only cross-run pairs available)
- **Reward model:** train on `reward.jsonl`; use as evaluator replacement or ensemble member

### 6b: TinyTroupe Research Curator Personas — PLANNED

**Motivation:** The annotation pipeline (`run_annotations.py`) processes all arxiv papers with equal weight. Adding a *taste layer* — opinionated personas that score papers on relevance, novelty, and practical value before annotation — lets the training data reflect discriminating judgment, not just coverage.

**Design:**

5 personas filter the candidate paper pool before annotation. Each persona independently scores every paper (0-10) on a structured rubric; papers that clear a threshold in ≥2 personas advance to the Nanda annotation stage.

| Persona | Lens | Scores highest on |
|---------|------|-------------------|
| Pragmatic Engineer | Applied ML | Reproducible results, released code, compute-efficient methods |
| Academic Rigorist | Theoretical foundations | Proof-backed claims, ablation depth, benchmark diversity |
| Synthesis Thinker | Cross-domain connection | Ideas that bridge fields, survey-worthy scope, conceptual novelty |
| Field Practitioner | Real-world deployment | Production constraints, latency/memory tradeoffs, failure modes |
| Contrarian | Assumption challenge | Results that contradict consensus, null findings, replication studies |

**Scoring rubric per paper (per persona):**
- Relevance to persona's lens (0-4)
- Novelty relative to what's already in the corpus (0-3)
- Quality of evidence / reproducibility (0-3)

**Threshold:** paper advances if ≥2 personas score it ≥6, OR any single persona scores it ≥9.

**Integration:**

```
mine_knowledge.py         →  raw arxiv_*.md files
                                    ↓
                         tinytroupe_curator.py   ← 5 personas score each paper
                                    ↓
                         arxiv_*_curated.json    (arxiv_id, scores, rationale)
                                    ↓
                         run_annotations.py      (only curated papers)
                                    ↓
                         build_finetune_from_annotations.py
```

**File to build:** `tinytroupe_curator.py`
- Reads `arxiv_*.md` files, extracts paper list
- Instantiates 5 TinyTroupe agents with persona definitions
- For each paper: shows title + abstract to all 5, collects structured scores
- Outputs `arxiv_<batch>_curated.json`: `{arxiv_id, title, scores: {persona: score}, rationale: {persona: str}, advance: bool}`
- `run_annotations.py` gets `--curated-only` flag that filters to advancing papers

**Why this matters for self-improvement:** As the annotation model improves, it needs *better* training data — not just more. Persona-filtered data concentrates the training signal on papers that exhibit the properties we actually want the model to internalize. The taste layer is itself trainable: as the corpus grows, we can fine-tune the curator on the preference pairs the swarm generates.

### Framing (per Perplexity analysis)

The strongest thesis emerging from the data: *"Local agent reliability is primarily a systems problem up to a point, after which producer capacity becomes the limiting factor."*

Cleanest reproducible experiments for a paper/report:
1. Dual-search floor effect (search volume as leading indicator at regime boundary, not within regime)
2. Evaluator separation (circular grading with same model; step-function gain from different architecture)
3. Producer-vs-evaluator scaling (32B breaks T_A ceiling; T_B flat — synthesis instruction is the bottleneck)
4. External verification loop (wiggum: 3/10 → 9/10 in one round without human intervention)

---

## Stage 7 - Capability Upgrades (sourced 2026-04-12)

### 7a: OCR preprocessing for document ingestion — DONE (Session 11)

**Problem:** `read_file_context()` routes PDFs through MarkItDown. For scanned or image-heavy documents, MarkItDown extracts garbage or nothing — the chunker receives corrupt input, synthesis quality collapses.

**Approach:** add an OCR preprocessing step in `read_file_context()`. Detect scanned/image-heavy PDFs (heuristic: very low text char count relative to page count after MarkItDown conversion), route through a local OCR model, feed the clean markdown to the existing chunker.

**Models available via Ollama/llama.cpp GGUF:**
- `ggml-org/GLM-OCR-GGUF` — best general OCR, supports `"OCR markdown"` and `"OCR HTML table"` prompts
- `Qwen3-VL-2B` — already in the vision family; lighter weight

**Implemented cascade (`ocr.py`):**
1. **PyMuPDF** — zero model cost, handles multi-column layout via `get_text("markdown")`
2. **llama-server OCR** — dedicated model, activated by `LLAMA_OCR_BASE_URL` env var
3. **llama3.2-vision via Ollama** — last resort for truly scanned pages

**llama-server quickstart:**
```bash
llama-server -hf ggml-org/GLM-OCR-GGUF   # launches at http://localhost:8080
```
```
LLAMA_OCR_BASE_URL=http://localhost:8080   # in .env — activates backend 2
```

**Supported OCR models via llama.cpp:** GLM-OCR, Deepseek-OCR, LightOnOCR, HunyuanOCR, Qianfan-OCR, Dots.OCR, PaddleOCR-VL, Qwen3-VL-2B, gemma-4-E2B/E4B.

**Also useful for:** the `/annotate` skill on papers where MarkItDown produces malformed markdown from complex layouts (two-column PDFs, tables, equations).

**Source:** [ggml-org/using-ocr-models-with-llama-cpp](https://huggingface.co/blog/ggml-org/using-ocr-models-with-llama-cpp)

---

### 7b: Gemma 4 as evaluator / panel member — NEXT (one command to test)

**Motivation:** Qwen3-Coder:30b is the sole evaluator across wiggum and panel. Evaluator monoculture means autoresearch is optimizing against one model's scoring preferences — if Qwen3-Coder has a systematic bias (e.g. rewarding code density regardless of relevance), it's invisible in the current setup.

**Gemma 4 26B MoE** is the right candidate:
- Different architecture family (Google vs Alibaba) — no circular grading risk
- 3.8B active params at inference — fits alongside pi-qwen-32b without full VRAM swap
- 256K context, native function calling, configurable thinking mode
- Strong coding benchmark: 80% on LiveCodeBench v6

**Test protocol:**
```bash
ollama pull gemma4:26b
# Swap into wiggum as evaluator for one eval session:
EVALUATOR_MODEL=gemma4:26b python eval_suite.py --tasks T_D,T_E --score
```

Compare scores against Qwen3-Coder baseline. If Gemma 4 scores diverge significantly → consider rotating evaluators across autoresearch sessions, or adding it as a 4th panel persona (Adversarial Evaluator). If scores converge → models agree; current rubric is robust.

**Thinking mode upside:** `"configurable thinking mode"` could improve wiggum feedback quality — richer reasoning about *why* a section is shallow, not just that it is.

**Source:** [ollama.com/library/gemma4](https://ollama.com/library/gemma4)

---

### 7c: Nanda annotation fine-tuning — IN PROGRESS (v2 run restarted 2026-04-15)

**Status:** v2 training run in progress. Training `Qwen/Qwen2.5-7B-Instruct` on 718 examples (`finetune_dataset_v2.jsonl` — 121 gold + 597 agent-annotated). Previous run was killed at step 1237/1938 (epoch 1.91) by an OS update reboot; no checkpoint survived (`save_strategy="epoch"` meant no mid-epoch saves).

**Training setup (v2):**
- LoRA r=16, alpha=32, target projectors (q/k/v/o/gate/up/down)
- bf16, no quantization (NVIDIA RTX 5000 Ada)
- 3 epochs, 1938 steps, batch size 1
- `save_strategy="steps"`, `save_steps=100`, `save_total_limit=3` — checkpoint every ~15 min
- `EarlyStoppingCallback` removed (incompatible with step-based saves + epoch eval)
- Resume: `python -X utf8 finetune_annotate.py --skip-fetch --dataset finetune_dataset_v2.jsonl --resume`

**Next steps after training:**
1. Convert to GGUF: `python -X utf8 llama.cpp/convert_hf_to_gguf.py finetune_output/merged --outfile finetune_output/nanda-annotator.gguf --outtype q8_0`
2. Register in Ollama: `ollama create nanda-annotator -f finetune_output/Modelfile`
3. Benchmark: run `/annotate /wiggum --producer nanda-annotator` on held-out papers, compare wiggum scores vs base `pi-qwen-32b`

---

### 7d: Ollama GGUF import for fine-tuned producers — when training loop closes

**Motivation:** `hf_export.py` already exports `preference.jsonl` and `sft.jsonl`. When SFT/DPO training runs against those datasets, the resulting model needs to come back into the harness as the producer.

**Import path (Modelfile):**
```
FROM /path/to/finetuned.gguf
```
```bash
ollama create pi-qwen-32b-sft --file Modelfile
# or with quantization at import:
ollama create pi-qwen-32b-dpo --file Modelfile --quantize q4_K_M
```

**LoRA adapter path:** if training produces a Safetensors adapter rather than a full model, import against the base:
```
FROM pi-qwen-32b
ADAPTER /path/to/lora-adapter/
```

This is the closing step of the self-improvement loop: autoresearch → preference data → DPO → re-import → new baseline producer.

**Supported architectures confirmed:** Llama, Mistral, Gemma, Phi3. Qwen2.5 (pi-qwen-32b's base) imports cleanly as it's Llama-compatible.

**Source:** [docs.ollama.com/import](https://docs.ollama.com/import)

---

### 7e: vLLM as inference backend — Stage 4 infrastructure

**Context:** Ollama's single-request-at-a-time default became a direct bottleneck in session 5 — the annotation loop blocked the email skill for the duration of a 300-paper run. `OLLAMA_NUM_PARALLEL=4` partially addresses this, but Ollama has no dynamic batching and no native LoRA hot-swap.

**Where vLLM fits:**

| Need | Ollama | vLLM |
|------|--------|------|
| Concurrent agent requests (swarm) | Queue (1 default) | Continuous batching — all requests batch-infer together |
| LoRA adapter serving | Experimental | Native (`--enable-lora`, hot-swap without base reload) |
| RLHF / DPO training loop | No integration | OpenAI-compatible API — reward signals can be computed inline |
| Throughput for annotation/email batch runs | Sequential | 5–10× on parallel workloads vs Ollama queue |
| API compatibility | `ollama.chat()` — custom SDK | `/v1/chat/completions` — drop-in OpenAI SDK target |

**The "downsides" are actually upsides here:**
- *Requires manual weight management (no `ollama pull`):* forces explicit model versioning — critical when fine-tuned checkpoints are entering the loop. Accidental model swaps break RL baselines; explicit paths prevent this.
- *Linux/WSL2 only:* WSL2 with GPU passthrough on the RTX 5000 Ada is straightforward. The annotation and email batch workloads are already non-interactive — WSL2 is the right home for them.
- *Heavier to set up:* one-time cost; the OpenAI-compatible API means the rest of the harness needs zero changes (`OLLAMA_BASE_URL` → vLLM endpoint).

**Planned integration point:** Stage 4 / swarm infrastructure. When subtask workers scale beyond 4 concurrent agents, Ollama's queue becomes the ceiling. vLLM removes it.

**LoRA serving is the highest-value near-term use case:** once `finetune_annotate.py` produces a checkpoint, vLLM can serve the base + LoRA adapter simultaneously — compare base vs fine-tuned on live annotation tasks without separate Ollama model registrations.

**Migration path (zero harness changes):**
```bash
# WSL2
pip install vllm
vllm serve Qwen/Qwen2.5-32B-Instruct --enable-lora --max-lora-rank 16 --port 11434
# agent.py — no change; Ollama client already reads OLLAMA_HOST
export OLLAMA_HOST=http://localhost:11434
```

**Status:** not yet — build after fine-tune loop closes and swarm scale demands it. Annotate on 7e when annotation throughput or concurrent swarm runs become the observed bottleneck.

---

### 7f: Docker sandbox for run_python — file and revisit

**Current state:** `run_python` uses AST analysis + subprocess with 10s timeout as the security layer. This covers the threat model for research tasks where code comes from the producer model (not untrusted external sources).

**When this becomes urgent:** if `run_python` scope expands to execute code from web search results, user-provided scripts, or untrusted agent outputs. Docker Sandboxes would replace the AST blocklist with true process isolation — throwaway container, no host filesystem access.

**Not urgent now.** Revisit if harness is productionized for other users or if `run_python` is granted broader permissions.

**Source:** [docker.com/blog/docker-sandboxes-run-agents-in-yolo-mode-safely](https://www.docker.com/blog/docker-sandboxes-run-agents-in-yolo-mode-safely/)

---

### 7g: /plan slash command — interactive pre-run planning

**Motivation:** the closed-book prior knowledge pass (Stage 1 NEXT) and the existing `planner.py` both run autonomously with no human checkpoint. Claude Code's `/plan` pattern is strictly better: show the gap analysis and proposed search queries before any search runs, let the user edit or approve, then proceed. Bad gap identification is caught before it wastes search rounds.

**Design:**

```
/plan Search for RAG papers on retrieval augmented generation
  ↓
[planner.py] prior_knowledge_pass() → known facts + gaps identified
  ↓
Dashboard OR terminal renders:
  Known: transformer attention, dense retrieval, BM25 vs dense
  Gaps:  late-interaction models, multi-hop retrieval, RAG vs long-context tradeoffs
  Proposed queries: [editable list]
  [Approve] [Edit]
  ↓
agent.run() proceeds with approved queries
```

**Implementation:**
- Add `plan` to `skills.py` REGISTRY — `hook: "pre_research"`, explicit only
- `agent.py`: when `plan` in explicit_skills, call `prior_knowledge_pass()` in `planner.py`, print `[EVENT]{"type":"plan",...}` structured event, then pause for approval
- **Terminal path:** `input()` prompt — print plan, ask "Approve? [Y/edit]". If edit, open $EDITOR or accept inline query edits
- **Dashboard path:** SSE stream emits plan event → dashboard renders editable plan card with Approve button → POST `/api/run/<run_id>/approve-plan` → agent continues
- `plan.approved_queries` replaces auto-generated queries in `gather_research()`

**Status:** NEXT — build before closed-book autonomous pass (this supersedes it)

---

### 7g-ii: Agentic cost estimator — COCOMO II for agent swarms

**Motivation:** COCOMO II estimates software effort in person-months from SLOC, scale drivers, and cost drivers. The harness equivalent already exists in `runs.jsonl` — every run logs `run_duration_s`, `input_tokens`, `output_tokens`, `wiggum_rounds`, `task_type`, `score`, `final`. This is a calibration dataset for a pre-task cost model that estimates effort *before* a run begins, using the same inputs the planner already produces.

**Unit mapping — COCOMO II → harness:**

| COCOMO II | Harness equivalent |
|-----------|-------------------|
| SLOC | Task string complexity + expected output size |
| Precedentedness | Memory hit rate for similar past tasks |
| Architecture/Risk Resolution | Plan complexity rating + subtask count |
| Team cohesion | Evaluator/producer model alignment (score variance across runs) |
| Required reliability | `PASS_THRESHOLD` setting |
| Platform experience | Task type frequency in last N runs |
| Process maturity | Wiggum round distribution across recent runs |

**Output of the estimator:**

```python
CostEstimate(
    estimated_llm_calls   = N,
    estimated_tokens      = K,
    estimated_wiggum_rounds = 1-3,
    estimated_wall_time_s = T,
    complexity            = "low" | "medium" | "high",
    risk_flags            = ["count_constraint", "requires_vision", "novel_task_type", ...],
    confidence            = 0.0-1.0,   # based on similar past runs in memory
)
```

**Where it plugs in:**
- **`/plan` command:** shows cost estimate alongside gap analysis before any search runs — you know before committing whether a task is a 2-minute run or a 45-minute orchestrated run
- **Swarm scheduling:** orchestrator uses estimates to allocate workers — cheap tasks get smaller/faster models, expensive tasks get pi-qwen-32b
- **Critic signal:** actual vs estimated variance logged per run — consistent underestimation on a task type flags either a harness gap or a miscalibrated estimator
- **Roadmap prioritization:** run estimator against all NEXT roadmap items, rank by effort/value ratio to guide session planning

**Calibration:** train against `runs.jsonl` actuals after 50+ runs. `planner.py` emits `CostEstimate` alongside `Plan`. Variance tracked in `runs.jsonl` as `estimated_*` vs `actual_*` fields. Model improves as the run history grows — self-calibrating via the same data the swarm generates.

**Dashboard:** surface in the `/plan` card as a phase distribution table (Inception/Elaboration/Construction/Transition mapped to Plan/Research/Synthesis/Eval stages) with agent-native units (tokens, wall time, LLM calls) mirroring the COCOMO II UI structure.

**Status:** NEXT — implement after `/plan` slash command (7g) is wired; estimator needs the plan output as input

---

### 7h: Unified observability — structured event protocol + dashboard

**Motivation:** three separate observability gaps identified in session 5:
1. Dashboard shows raw stdout during runs — no visibility into plan reasoning, search stage, synthesis progress
2. Fine-tuning metrics only visible in TensorBoard after epoch end — no live per-step dashboard view
3. No compute-stage trace data from fine-tuning runs for retrospective analysis (forward/backward/optimizer timing)

**The fix is one shared protocol, three emitters.**

#### Structured event format

All pipeline components print `[EVENT]<json>` lines to stdout. The SSE stream already delivers these to the dashboard. Dashboard detects the prefix and routes:

```json
{"type": "plan",   "data": {"queries": [...], "gaps": [...], "complexity": "high"}}
{"type": "search", "data": {"query": "...", "round": 1, "hits": 3}}
{"type": "synth",  "data": {"stage": "start", "tokens_in": 4200}}
{"type": "metric", "data": {"step": 14, "loss": 1.35, "accuracy": 0.69, "epoch": 0.13, "grad_norm": 0.57}}
{"type": "span",   "data": {"name": "forward_pass", "duration_ms": 1240, "phase": "train"}}
{"type": "log",    "data": {"text": "raw stdout line"}}
```

Non-`[EVENT]` lines fall through as `log` events — backward compatible with all existing output.

#### Emitter 1 — `agent.py` plan + stage events

Emit typed events at each pipeline transition:
- After planner runs: `{"type":"plan", "data": plan.__dict__}`
- Each search round start/end: `{"type":"search", ...}`
- Synthesis start: `{"type":"synth", "data":{"stage":"start"}}`
- Wiggum round: `{"type":"wiggum", "data":{"round":N, "score":X}}`

Zero impact on non-dashboard runs — extra print lines, nothing more.

#### Emitter 2 — `finetune_annotate.py` per-step metrics

Add a `trl.TrainerCallback` subclass (`DashboardCallback`) that on `on_log()`:
1. Writes `[EVENT]{"type":"metric",...}` to stdout (captured by run SSE stream if launched via server)
2. Appends the same JSON to `finetune_metrics.jsonl` (sidecar file, persists across sessions)

New server endpoint: `GET /api/finetune/metrics` — streams `finetune_metrics.jsonl` as JSON array. Dashboard polls this every 5s when a finetune run is detected.

No waiting for epoch end. Step 14's loss visible in dashboard within seconds of it printing.

#### Emitter 3 — fine-tuning Perfetto tracer

`FinetuneTracer` context manager using `torch.cuda.Event` for GPU-accurate timing:

```python
with FinetuneTracer("forward_pass"):
    outputs = model(**batch)

with FinetuneTracer("backward_pass"):
    loss.backward()

with FinetuneTracer("optimizer_step"):
    optimizer.step()
```

Emits `{"type":"span",...}` events per step. At run end, writes `traces/finetune_<ts>.json` in Chrome Trace Event format (same as existing `RunTrace` in `logger.py`) — loadable at `ui.perfetto.dev`.

Annotates: `data_loading`, `forward_pass`, `backward_pass`, `optimizer_step`, `lr_scheduler`, `logging`. GPU utilization and VRAM usage attached as metadata per span.

#### Dashboard changes

- **Run detail panel:** parse `[EVENT]` prefix → render plan card (queries/gaps/complexity) above the log stream; show search round progress inline
- **New "Training" tab:** polls `/api/finetune/metrics`, renders:
  - Live loss + accuracy sparklines (step-level)
  - Current step / total steps progress bar + ETA
  - Grad norm trend (early warning for training instability)
  - "Open in Perfetto" link when trace file exists
- **Backward compatible:** runs without structured events render exactly as today

#### Build order

| Step | What | Effort | Value |
|------|------|--------|-------|
| 1 | Event protocol + `agent.py` emitters | Small | Plan visibility immediately |
| 2 | `DashboardCallback` + `/api/finetune/metrics` | Small | Live training metrics now |
| 3 | Dashboard plan card + training tab | Medium | Ties it together visually |
| 4 | `FinetuneTracer` + Perfetto output | Medium | Retrospective compute analysis |

**Status:** NEXT — start with step 2 (fine-tuning callback) since training run is live

---

### 7i: Harness ontology layer — code graph + KG skill → self-aware code review

**Insight:** The harness already has a knowledge graph generator skill (producing D3.js graphs from synthesis output). `code-review-graph` does the structural analogue for code: Tree-sitter AST parsing, blast-radius analysis, community detection, incremental SQLite-backed updates in <2s. Combining them gives us an *ontology layer* — a continuously maintained semantic + structural map of the harness itself.

**What this enables:**

| Capability | How |
|-----------|-----|
| Automated code review of harness mutations | Proposer generates a patch; Critic uses blast-radius to scope review to affected functions and callers only — no full-repo read |
| /plan blast-radius preview | Before executing a plan step, the planner queries the graph: "what does changing `agent.py:synthesize()` actually touch?" |
| Dead code detection | As the harness evolves, the graph flags unused skills, stale stage hooks, and orphaned utilities |
| Capability ontology | Nodes = skills/tools/stages, edges = invocation chains. Proposer agent reasons over this graph when proposing mutations |
| Wiki auto-generation | `code-review-graph wiki` produces a markdown wiki from code communities via Ollama — feeds into harness memory |

**Install (Ollama-compatible extras only):**

```bash
pip install "code-review-graph[communities,wiki]"
code-review-graph build    # initial parse of harness repo
code-review-graph watch    # incremental updates on every save/commit
code-review-graph install --platform claude-code  # MCP wiring for this session
```

**Token economics:** blast-radius context averages 8.2x fewer tokens than full-file reads per the published benchmarks. On a 32B critic model this compounds across every Proposer→Critic round.

**When to build:** after Stage 4 self-improvement loop prototype — most valuable once Proposer agents exist and need structured context about what they can mutate and what the downstream impact is.

---

### 7j: Git worktrees as Proposer isolation substrate

**Insight:** Each git worktree is an isolated filesystem path on its own branch. `code-review-graph` builds a separate SQLite graph per directory — so you get **structural graph diffs across branches**, not just file diffs. Worktrees are the execution substrate that makes parallel Proposer evaluation safe without interrupting live harness runs on `main`.

**Mutation testing loop:**

```
Proposer generates patch
  → git worktree add ../harness-mut-<id> -b mutation/<id>
  → apply patch in worktree
  → code-review-graph build (in worktree)  →  mutation.db
  → diff main.db vs mutation.db            →  structural change set
  → run eval suite inside worktree
  → Critic scores delta
  → git worktree remove (revert) or git merge --ff-only (promote)
```

**Why worktrees over branching in place:**

| Problem | Worktree solution |
|---------|------------------|
| `server.py` stays live on `main` during mutation tests | Different path — no port conflict, no interrupted runs |
| Parallel Proposers step on each other's files | Each gets its own worktree — N agents, N isolated workspaces |
| code-review-graph SQLite graph is per-directory | Each worktree builds its own graph; edge sets are diffable |
| Annotation/fine-tuning runs can't be interrupted | They live on `main`; mutations happen in sibling directories |

**The graph diff as Critic context:**

```python
main_graph    = query_graph("harness-engineering/.code-review-graph/graph.db")
mut_graph     = query_graph("harness-mut-<id>/.code-review-graph/graph.db")

new_edges     = mut_graph.edges - main_graph.edges
removed_edges = main_graph.edges - mut_graph.edges
blast_radius  = mut_graph.get_impact_radius(changed_files)
```

The Critic sees: "Proposer added a call edge from `synthesize()` to `cache_lookup()`, now on the hot path for 6 downstream callers" — structural reasoning a file diff can't surface.

**Watch mode constraint:** one `code-review-graph watch` process per active worktree. At N≤4 parallel Proposers, run one watcher each. Beyond that, trigger `code-review-graph update` on-demand after patch application instead.

**Integrator agent actions:**
- Revert: `git worktree remove ../harness-mut-<id> --force`
- Promote: `git -C harness-engineering merge --ff-only mutation/<id> && git worktree prune`

This pattern mirrors what Claude Code's `isolation: "worktree"` does for subagents — proven at the tooling level, now apply it to the self-improvement loop.

**When to build:** alongside Stage 4 Proposer implementation. Worktrees are zero-infrastructure — no new services, just `git worktree add` in the Proposer agent's scaffolding.

---

### 7k: Knowledge mining pipeline — `/lit-review` skill

**Motivation:** Batch annotation runs (run_annotations.py, annotate_abstracts.py) produce per-paper annotations but leave no aggregated synthesis — no signal about what a corpus *as a whole* says, what's missing, or what to read next. The `/lit-review` skill closes this loop.

**Pipeline (7 stages):**

```
step_fetch      — arxiv_fetch.py queries arXiv Atom API, date-filters, deduplicates → CSV
step_enrich     — semantic_scholar.py fetches reference lists per paper (S2 Graph API, SQLite-cached)
step_curate     — hub prioritization: papers cited most within corpus annotated first
step_annotate   — run_annotate_standalone() per paper with RunTrace, checkpoint to .lit_review_cache/
step_cluster    — LLM groups papers into 3-5 named clusters (JSON output)
step_synthesize — per-cluster summaries + cross-cluster overview + open questions extraction
step_render     — Jinja2 template renders final document (survey / gaps / executive views)
```

**New files:**
- `arxiv_fetch.py` — arXiv Atom API via feedparser; CLI with `--after/--before` date filtering, `--append` mode, same CSV schema as `arxiv_agentic_papers.csv`
- `semantic_scholar.py` — S2 Graph API references per paper; builds `GraphResult` (adjacency, hub_scores, gap_candidates); SQLite TTL cache (30-day); `fetch_gap_arxiv_rows()` for gap metadata
- `lit_review_skill.py` — 7-step orchestrator; per-paper checkpoint; RunTrace per annotation; Jinja template dispatch
- `templates/lit_review_survey.j2` — cluster sections with hub callout, per-paper annotation details, gap table
- `templates/lit_review_gaps.j2` — gap-focused: open questions, gap candidates ranked by citation count, cluster blind spots

**Key design decisions:**
- Checkpointing: `.lit_review_cache/{arxiv_id}.json` — long corpus runs survive crashes and resume mid-annotation
- Hub prioritization: papers cited most within corpus surface first; guarantees the most-connected work is annotated when `--max-annotate` is less than total corpus size
- Jinja separation: annotations are data; rendering is a template decision — same annotation pass, multiple output formats
- S2 API is free, no-auth; 429-backoff with 10s sleep + retry; 404 cached as empty (paper not indexed)

**Agent integration:** `agent.py` routes `/lit-review <query> [flags]` → `_handle_lit_review()` → `run_lit_review()`. Keep-alive `-1` (infinite) for lit-review sessions. Flags parsed from task string via regex: `--max-fetch`, `--max-annotate`, `--after`, `--before`, `--template survey|gaps|executive`, `--no-s2`, `--no-wiggum`.

**Status:** DONE (Session 10) — functional but not yet field-tested on a real corpus run. Test with a 20-paper agentic survey query.

---

### 7k-ii: /recall — semantic memory search — DONE

**What it does:** `/recall <query> [--n N] [--facts] [--scores]` queries the agent's memory store directly from the command line. Returns top-N observations ranked by semantic similarity (ChromaDB) + quality score blend, with optional facts bullets and wiggum scores.

**Why it matters:** 862 observations in `memory.db` with no direct query interface. The only previous access was automatic injection into the synthesis context before each run. `/recall` makes the corpus searchable on demand — useful for finding past research before starting a new task, or verifying what the agent already knows about a topic.

**Files changed:**
- `skills.py`: `"recall"` added to REGISTRY with `hook="standalone"`; MSYS2 path mangling fix in `parse_skills()` (strips `C:/Program Files/Git/skillname` → `skillname` for all skills)
- `memory.py`: `search()` added as public alias for `_search()`
- `agent.py`: `_handle_recall()` standalone handler; `"recall"` added to `_path_optional`

**Bonus fix — MSYS2 path conversion (Session 11):** Git Bash converts `/skillname` args to Windows absolute paths (`C:/Program Files/Git/skillname`), breaking skill detection for all terminal invocations. Fixed in `parse_skills()` — now strips mangled path tokens and their preceding drive fragments. Latent bug affecting all skills; caught when testing `/recall` from bash.

**Status:** DONE (Session 11).

---

### 7l: DPO preference dataset pipeline — `build_dpo_dataset.py`

**Motivation:** Every run already generates implicit preference signal — wiggum rounds that improve a synthesis are a (rejected, chosen) pair; cross-run comparisons on the same task are another. Extracting these into a DPO dataset closes the loop between runtime evals and fine-tuning.

**Two signal sources:**

| Source | Signal | Available |
|--------|--------|-----------|
| `cross_run` | Same task + same producer model; higher-scoring run is chosen, lower is rejected | Now — 3 pairs from existing runs.jsonl |
| `wiggum_revision` | Round-1 synthesis vs best-round synthesis within a single run | Future — requires `content` field in wiggum_eval_log (added Session 10) |

**Output schema:**
```json
{
  "prompt": "...", "chosen": "...", "rejected": "...",
  "chosen_score": 7.8, "rejected_score": 5.2, "score_delta": 2.6,
  "source": "cross_run|wiggum_revision",
  "task_type": "research", "producer_model": "...", "evaluator_model": "...",
  "chosen_dims": {...}, "rejected_dims": {...},
  "wiggum_feedback": "...", "timestamp": "..."
}
```

**Key implementation details:**
- Task normalization: `_normalize_task()` strips `/skill` prefixes, takes first 120 chars — groups semantically identical tasks across runs
- Cross-run pairs: filter to same producer_model, score_delta ≥ `--min-delta` (default 1.0), require content in both runs
- Revision pairs: require `wiggum_eval_log` entries to have `"content"` field (only runs after 2026-04-14 have this)
- wiggum.py modified: `"content": content[:8_000]` added to `round_record` in both standard and annotate wiggum loops
- logger.py modified: `log_wiggum()` propagates `content` field into `wiggum_eval_log` in runs.jsonl

**CLI:** `python build_dpo_dataset.py [--min-delta N] [--source cross|revision|all] [--stats] [--runs path] [--out path]`

**Status:** DONE (Sessions 9–10). Cross-run pairs active; revision pairs accumulate as future runs generate content-tagged eval logs. Feed output to `finetune_annotate.py` DPO training mode when N ≥ 50 pairs.

---

### 7m: Batch annotation run logging — DONE

**What was missing:** `run_annotations.py` and `annotate_abstracts.py` called the LLM directly via `run_annotate_standalone()` with no `RunTrace` instrumentation. Batch annotation runs were invisible in the dashboard and `runs.jsonl`.

**Fix (Session 10):**
- `run_annotate_standalone()` signature extended with optional `_trace=None` parameter; calls `_trace.log_usage(resp, stage="annotate")` after each LLM call
- `run_annotations.py`: creates `RunTrace` per paper, passes to `run_annotate_standalone`, calls `trace.finish("PASS"/"FAIL")`
- `annotate_abstracts.py`: same pattern — `RunTrace` per paper, token logging, output_bytes/output_lines, `trace.finish()`
- Backfilled 10 historical annotate runs in `runs.jsonl` that stored raw `wiggum` dict instead of processed logger fields
- Dashboard `_is_substantive()` filter excludes stub runs (0 tokens, 0 wiggum_rounds, 0 output_bytes) that were flooding the recent runs table

**Status:** DONE (Session 10).

---

## Guiding Principles

**1. Build for deletion.**
Every harness component should be designed to be removed as models improve. The forced-synthesis workaround (`FORCE_SYNTH_AFTER`) exists because 7B loops without terminating. When a model handles this natively, the workaround should be trivially removable.

**2. Verify externally at every stage boundary.**
Between research and write. Between write and delivery. Between agent handoffs. The model's self-report is not verification.

**3. Add observability before adding features.**
You cannot improve what you cannot see. Structured traces before new tools. Eval suite before new agents. Logging is not optional.

**4. Start with the simplest pattern that meets the requirement.**
Single agent with verification loop before two-agent supervisor. Two agents before five. The complexity cost of orchestration is real and compounds.

**5. Evaluator and producer must be different models.**
Same-model evaluation is circular. The evaluator should be larger or specialized differently from the producer. Confirmed empirically: upgrading evaluator from 7b to 72b produced genuinely critical scores.

**6. Evaluator criteria are a quality specification.**
If the evaluator prompt doesn't explicitly reward depth and implementation detail, a strong evaluator will penalize them as verbosity. Write criteria that describe what good looks like, not just what bad looks like.

**7. The harness is the product.**
The model is a commodity input. The harness -- how it is constrained, informed, verified, and corrected -- is where reliability lives and where durable engineering value accumulates.

**8. The evaluator reveals the producer ceiling; it does not set it.**
A strong evaluator exposes quality gaps the producer cannot close. When revision regresses or stagnates, the evaluator is working correctly — the producer is the bottleneck. Fix the producer, not the threshold.

**9. Every manual hand-off is a loop that hasn't closed yet.**
The gap between "autoresearch on synthesis instructions" and "self-improving swarm" is a sequence of manual steps: fine-tune trigger, checkpoint promotion, model registration, baseline update. Each one is a target for automation. Build toward the loop closing continuously — human approval at goal-setting and promotion, autonomous everywhere between.

**10. Telemetry is what separates a critic from a scorer.**
A scalar score tells you *that* something improved. Typed event traces — plan reasoning, search rounds, wiggum dimension breakdown, compute span timings — tell you *why*. The self-improvement loop stalls without this signal. Structured observability (7h) is prerequisite infrastructure for swarm-level self-improvement, not a dashboard nicety.
