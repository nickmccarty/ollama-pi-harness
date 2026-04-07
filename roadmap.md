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
  "timestamp": "2026-04-07T18:13:15+00:00",
  "task": "...",
  "producer_model": "pi-qwen",
  "evaluator_model": "glm4:9b",
  "tool_calls": [{"name": "web_search", "query": "...", "result_chars": 2326}],
  "synth_forced": false,
  "output_path": "C:\\Users\\nicho\\Desktop\\harness-engineering\\...",
  "output_lines": 13,
  "output_bytes": 1264,
  "wiggum_rounds": 2,
  "wiggum_scores": [5, 9],
  "final": "PASS"
}
```

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

## Stage 3 - Orchestrator + Specialized Subagents — DONE (sequential, research agents)

*Objective: decompose complex tasks across multiple specialized agents.*

### What's implemented

`orchestrator.py` — sequential orchestration of research subtasks with cross-referencing assembly.

```
orchestrate(task)
  memory + planning  →  if no subtasks: delegate to agent.run()
  assign _sub_N.md paths
  agent.run(subtask) × N   (full pipeline, no per-subtask wiggum)
  assemble()               (cross-referencing synthesis from all subtask outputs)
  write + wiggum + memory store + cleanup
```

**Transparent passthrough:** single-focus tasks hit the same code path as before — no regression.

**Shared memory works automatically:** subtask 2 sees subtask 1's memory observations because they execute sequentially through `agent.run()`, which writes to `memory.db` after every run.

**Validated:** compound task (failure modes + context engineering) → 2 subtasks → 57-line cross-referencing guide. 3 memory observations stored (2 subtasks + orchestrated run).

### Architecture (current)

```
orchestrator.py
    |
    +-- agent.run() × N    (pi-qwen: web search, read_file, run_python)
    +-- assemble()         (pi-qwen: cross-referencing synthesis)
    +-- wiggum.loop()      (glm4:9b: single verification pass on final output)
```

### Remaining gaps

- **Sequential only** — parallel subtask execution (threading) would reduce wall time by ~N×
- **Research agents only** — no specialised code agent, vision agent, or write agent yet; all subtasks run through the same `agent.run()` pipeline
- **No inter-subtask scope coordination** — subtasks don't know each other's scope at planning time; they discover shared context only via memory after the fact
- **Assembly quality bounded by producer** — pi-qwen cross-references but doesn't synthesise at the depth a 72B model would

### Shared harness layer (in place)
- Shared memory (`memory.db` — all agents read/write across the session)
- Shared observability (`runs.jsonl` — each subtask logs its own full trace)
- Shared security (`security.py` — applied per subtask run)
- Shared workspace (filesystem — subtasks can read each other's outputs via `read_file`)

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
