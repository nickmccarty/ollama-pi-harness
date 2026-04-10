# Roadmap: Toward Multimodal Agent Swarms

## Current Baseline

A working three-stage pipeline running locally via Ollama:

1. **Research** (`agent.py`) - agentic web search loop using `ddgs`, forced synthesis after 2 rounds, Python writes output to disk
2. **Verify/Revise** (`wiggum.py`) - evaluates output with `qwen2.5:72b`, revises with producer if failing, loops up to 3 rounds
3. **Ground-truth eval** (`eval.sh`) - filesystem checks independent of model self-report

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
| `compress_knowledge` consumes 80–90% of `gather_research` wall time; scales with search rounds | Up to 294s on compress vs 442s total gather | Skip compress on borderline-novelty rounds; cache state across autoresearch exps | Future |
| `wiggum_revise` costs 11–22% of total when it fires | 310–1116s per revision pass | Optimising round-1 score (autoresearch target) directly reduces this | By design |
| Panel threads not visible in autoresearch traces — `WIGGUM_PANEL` not propagated to subprocess | Panel running in manual runs only | Pass env var through autoresearch subprocess | Future |

---

## Stage 4 - Multimodal Agent Swarm

*Objective: a coordinated swarm of agents handling complex, long-horizon tasks across text, images, code, and structured data.*

### What changes at swarm scale

**Communication:** agents need a shared message bus or state store. Options: SQLite, Redis, or a simple append-only JSONL log that all agents read and write.

**Agent identity:** each agent has a role, a capability profile, and a trust level. The orchestrator assigns tasks based on capability matching, not hardcoded routing.

**Emergent decomposition:** the orchestrator uses an LLM to decompose tasks dynamically. The decomposition itself becomes a harness component to verify and correct.

**Failure propagation:** when one agent fails, the swarm needs a policy: retry, reroute, escalate, or abort. This is the multi-agent equivalent of a verification loop.

### Multimodal inputs
- Text prompts: research + write pipeline (current capability)
- Screenshots: vision agent extracts content, text agents act on it
- PDFs: markitdown extracts text, routes to research or write agents
- Structured data (CSV, JSON): code agent processes, write agent documents
- Audio (future): transcription agent feeds text pipeline

### The hardware question
A swarm of 7B models running in parallel is feasible on a single GPU with 24GB VRAM. Four simultaneous 7B agents use approximately the same memory as one 32B agent, with potentially higher throughput on parallelizable tasks. The coordination overhead is the cost.

With a 32B producer the single-agent pipeline consumes the full 24GB budget — parallelism is no longer free. The architectural choice becomes: one high-quality agent or multiple lower-quality agents in parallel. Experiment-03 suggests the 7B producer is the quality bottleneck, not the harness, which shifts the calculus toward the single high-quality agent path.

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

### Framing (per Perplexity analysis)

The strongest thesis emerging from the data: *"Local agent reliability is primarily a systems problem up to a point, after which producer capacity becomes the limiting factor."*

Cleanest reproducible experiments for a paper/report:
1. Dual-search floor effect (search volume as leading indicator at regime boundary, not within regime)
2. Evaluator separation (circular grading with same model; step-function gain from different architecture)
3. Producer-vs-evaluator scaling (32B breaks T_A ceiling; T_B flat — synthesis instruction is the bottleneck)
4. External verification loop (wiggum: 3/10 → 9/10 in one round without human intervention)

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
