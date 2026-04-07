# Harness Engineering: Field Notes

## Motivation

The central question driving this work: can open-source models, running locally via Ollama, approach the utility of frontier models like Claude Code — and if not, how close can harness engineering get us?

The premise, drawn from the harness engineering literature, is that the model is not the 80% factor. The harness is. Swap the underlying model for a competitor and output quality shifts by 10-15%. Change the harness design and you change whether the system works at all.

This is worth testing empirically. If true, it means that a well-engineered harness around a capable open-source model is a practical path toward reliable local agents — with meaningful implications for cost, privacy, and ownership.

---

## Approach

### Tooling

- **Runtime:** Ollama with the Pi harness (`ollama launch pi --model <model>`)
- **Models tested:** qwen2.5:7b, qwen2.5:72b
- **Harness layer:** Pi's built-in tool set (web_search, write, bash), extended with a custom Python wrapper (`agent.py`)

### Method

Start with unmodified defaults. Observe failures. Diagnose root causes. Apply targeted harness interventions. Measure whether behavior improves. Repeat.

The failure surface was the guide — each failure pointed to a specific harness component to build or fix.

---

## Failure Modes Encountered

### 1. Task completion drift
**Symptom:** Model performs web search, produces a verbal summary, stops. The markdown file is never created.

**Diagnosis:** After one tool call returning a large result, the model exits "agent loop" mode and enters "text generation" mode. The write step requires a second tool invocation that the model does not make. The model treats research output as task completion.

**Root cause:** Training distribution bias. "Question → text answer" completions dominate the training data. "Research → write artifact" requires sustained multi-step agentic behavior that smaller models do not maintain through a large context result.

### 2. Placeholder content in written files
**Symptom:** File gets created but contains generic boilerplate — `Pattern One: brief implementation note` — rather than actual researched content.

**Diagnosis:** The model is regenerating content at the write step rather than passing through what it found. The few-shot example in the Modelfile modeled the write call abstractly, which taught placeholder behavior.

**Root cause:** Content fidelity across tool boundaries. The model treats write as a new generation task, not a pass-through of prior output.

### 3. Encoding corruption in Modelfile
**Symptom:** System prompt instructions containing em dashes (`—`) were corrupted to `??"` in the saved Modelfile.

**Impact:** The model was reading garbled instructions. Rules like "always continue to produce the specified output artifact" were being transmitted as noise.

**Fix:** Replace all em dashes with hyphens in Modelfile content.

### 4. Vision + tool calling incompatibility
**Symptom:** `qwen2.5vl:latest does not support tools` error when attempting to use a vision-capable model with Pi.

**Diagnosis:** Vision and tool calling (function/schema-based) are separate capabilities that have not been unified in smaller open-source models. Models supporting both are rare at the 7-13B range.

### 5. Few-shot examples backfired
**Symptom:** Model output `[calls web_search: ...]` and `[web_search returns results]` as literal text instead of invoking the actual tool.

**Diagnosis:** The MESSAGE block in the Modelfile used placeholder syntax to illustrate tool calls. The model learned to mimic that syntax rather than invoke real tools. The example taught the wrong behavior.

**Fix:** Removed MESSAGE blocks entirely. The system prompt rules alone are sufficient — demonstrated patterns should show real content, never abstract placeholders.

### 6. Model loops without synthesizing
**Symptom:** Model called `web_search` 5 times in a row without ever producing final text output. Hit `MAX_TOOL_ROUNDS` with empty content.

**Diagnosis:** After removing the MESSAGE examples, the model lost the pattern for when to stop searching and synthesize. It searched repeatedly without a clear termination signal.

**Fix:** Added `FORCE_SYNTH_AFTER = 2` — after 2 search rounds, inject a user message: "You have gathered enough information. Now output ONLY the markdown document." The forced synthesis prompt reliably breaks the loop.

### 7. Package renamed mid-project
**Symptom:** `RuntimeWarning: This package (duckduckgo_search) has been renamed to ddgs`.

**Fix:** `pip install ddgs`, updated import in `agent.py`.

---

## Interventions Applied

### Modelfile system prompt
Rewrote the system prompt to enforce a planning rule, execution rules, and a completion checklist. Added few-shot MESSAGE examples showing actual content flowing from search results into file writes.

**Result:** Partial improvement. The file-write step became more reliable at 72B. At 7B, the failure persisted.

### Two-turn prompting
Split the single task prompt into two sequential turns:
- Turn 1: "Search for X. Output ONLY markdown — no preamble."
- Turn 2: "Write exactly what you just output to ~/path/file.md"

**Result:** Reliable task completion. The write step is trivial when the content is already in the conversation as visible text — no generation required, no tool-boundary content loss.

### Python harness (`agent.py`)
Engineered a custom agent loop that:
1. Runs Turn 1 as an agentic tool-calling loop (model calls `web_search` until satisfied, then produces markdown text)
2. Performs Turn 2 in Python directly — `open(path, 'w').write(content)` — bypassing the model's file-write weakness entirely
3. Verifies the output via `os.path.exists` rather than trusting model self-report

**Result:** Single-command task completion with ground-truth verification. The file-write failure mode is eliminated, not worked around.

### Wiggum loop (`wiggum.py`)
Added a post-write verification loop that:
1. Normalizes the output file to plain text via markitdown
2. Scores the content against task criteria using a separate evaluator model
3. If the score fails, sends the content + evaluator feedback to the producer for revision
4. Writes the revised content back to disk and re-evaluates
5. Loops up to 3 rounds (rounds 1-2 capture ~75% of reachable improvement)

**Observed result:** Pipeline self-corrected from 3/10 → 9/10 in one revision round without human intervention. First-pass failure was caused by the model outputting placeholder text instead of real content — wiggum caught it and fixed it.

**Key finding:** Evaluator and producer must be different models. Using the same 7B model for both produces circular grading — the evaluator tends to agree with whatever the producer generated. Upgrading the evaluator to `qwen2.5:72b` produced genuinely critical scores.

**Tradeoff observed:** Stronger evaluator (72b) produced more critical but less elaborate output. The 72b evaluator penalized verbosity, which caused the producer to trim code examples and implementation detail in the revision. Evaluator criteria need to explicitly reward depth when depth is desired.

---

## Lessons Learned

**1. The harness gap is real and partially closeable.**
Failure modes encountered here — task completion drift, content fidelity loss, encoding corruption — are all harness failures, not model knowledge failures. The model knew what verification loop patterns were. It just couldn't reliably execute the write step without engineering support.

**2. Prompting has a ceiling; Python doesn't.**
Every system prompt intervention improved behavior marginally. Moving the file write from a model action to a Python action eliminated the failure entirely. The lesson: identify which steps require intelligence and which steps require reliability. Route intelligence to the model; route reliability to code.

**3. Few-shot examples outperform instructions for small models.**
At 7B, declarative rules in the system prompt ("if a task says create a file, the task is not complete until the file exists") had limited effect. Demonstrated examples of the correct behavior had more impact. Small models anchor to patterns more than they follow instructions.

**4. Verification must be external.**
The model consistently reported success before confirming the file existed. Eval based on model self-report is not eval. Ground-truth verification (`os.path.exists`, `ls`, `wc -l`) is the only reliable signal.

**5. Model size matters for multi-step tool use.**
The specific failure — maintaining an agentic loop through a large tool call result — is significantly more reliable at 72B than 7B. Below 32B, multi-step tool-use chains are fragile. No prompt engineering fully compensates.

**6. Cost envelopes are reliability signals, not just financial controls.**
`MAX_TOOL_ROUNDS = 5` in `agent.py` is not primarily about cost. A task that requires more than 5 search iterations is behaving abnormally. The ceiling is a diagnostic.

**7. Few-shot examples can teach the wrong behavior.**
MESSAGE blocks in a Modelfile should never use placeholder syntax (`[calls tool: ...]`). The model learns the form, not the intent. If you use few-shot examples, they must show the exact behavior you want — real content, real tool invocations, real output.

**8. Evaluator criteria shape output quality directly.**
The evaluator prompt is a quality specification. If it doesn't explicitly reward depth, implementation detail, and code examples, a strong evaluator will penalize them as unnecessary verbosity. Specify what good looks like, not just what bad looks like.

**9. Separate evaluator from producer — always.**
Same-model evaluation is circular. The evaluator should be a different model, ideally larger or specialized differently. In this setup: `qwen2.5:72b` as evaluator, `pi-qwen` (7b) as producer.

**10. Evaluators follow rules selectively, not reliably.**
Structured rules in evaluator prompts ("if count is wrong, cap score at 5") are not reliably applied when the rest of the output looks strong. glm4:9b passed a "top 3" output containing 7 items at 9/10. The lesson: don't use the evaluator to enforce structural constraints — use Python. Extract the count from the task string, count items in the output, and fail fast before wiggum runs. Reserve the evaluator for judgements that require reading comprehension.

**11. Open-ended tasks produce more consistent output than constrained tasks.**
Counter to intuition: in experiment-01, the unconstrained task (T_B, cost management) had the lowest output variance (CV=13.2%), while the most constrained task (T_C, top 3) had the highest (CV=44.2%). A count constraint gives the evaluator a checkable criterion, but it also gives the model two ways to fail: under-deliver or over-deliver. An open-ended task converges to whatever depth the research supports, which is more stable.

**12. Success in the verification loop can hide a ceiling effect.**
When every run scores 9/10 on the first pass and wiggum never revises, the pipeline looks excellent — but the metric has become uninformative. A uniformly high first-pass score means either quality is genuinely high, or the evaluator is too lenient, or the pass threshold is too low. Distinguish these by raising the threshold or using a stricter evaluator before concluding the harness has no room to improve.

**13. Correlation between search volume and output quality only holds at regime boundaries.**
Within the dual-search regime (all runs 2900-3600 chars), search volume had no predictive power for output quality (r = -0.577, noise). The prior positive correlation was a regime effect: single-search runs were qualitatively different from dual-search runs, not just smaller. Leading indicators lose their predictive value once the floor they were measuring has been consistently cleared.

---

## Dual Search + Quality Floor

Restructured `research()` to always run two searches before synthesizing:
1. First query extracted from the task string
2. Second query generated by the producer model as a complementary angle
3. Results merged and deduplicated by URL
4. Total chars checked against `SEARCH_QUALITY_FLOOR = 1800` — if below, a fallback search runs

**Observed impact across 5 runs (same task):**

| Run | search chars | output bytes | wiggum rounds |
|---|---|---|---|
| 1 (single search) | 2326 | 1264 | 2 |
| 2 (single search) | 1414 | 683 | 1 |
| 3 (single search) | 1984 | 1499 | 1 |
| 4 (dual search) | 3198 | 2014 | 1 |
| 5 (dual search) | 3424 | 1485 | 1 |

Dual search consistently produces 3000+ chars of research context. Output depth and byte count stabilized. No more 683-byte shallow runs.

**Bug found:** First query was extracted too literally from the task string, including trailing "and" — e.g. `"the top 3 verification loop patterns used in production agent harnesses and"`. Fixed with a regex strip of trailing punctuation and conjunctions.

**Minor producer artifact:** Synthesis output sometimes ended with `"This document is saved to ~/path/..."` — the producer treating the task's save instruction as content. Fixed in the synthesis prompt: added explicit instruction not to reference file paths.

---

## Experiment 01: Pipeline Generalization Study

Ran a Montgomery-style completely randomized design (CRD): 3 task types × 3 replications = 9 runs in randomized order. Tasks: context engineering (T_A, top 5), cost management (T_B, open-ended), agent failure modes (T_C, top 3). Full design and analysis in `experiment-01.md`.

**Key findings:**

- **Pass rate: 9/9 PASS.** H3 confirmed. The wiggum + dual-search harness generalizes across topic domains and count constraints without failure.

- **Open-ended task was most consistent.** T_B (no count constraint) CV = 13.2% — the most stable. T_A (top 5) CV = 39.7%. T_C (top 3) CV = 44.2% — most variable. H1 partially falsified: the harness does not produce consistent quality across all task types at CV < 20%.

- **Wiggum rounds degenerate.** All 9 runs: score_r1 = 9, wiggum_rounds = 1. Zero variance in the revision metric — H2 indeterminate. The dual-search harness now produces first-pass quality so consistently that the revision loop rarely activates. This is a success, but it means wiggum_rounds is no longer a useful differentiator unless the pass threshold is raised.

- **Count constraint not enforced by evaluator.** Run 7 (T_C) produced 7 failure modes despite the "top 3" instruction. glm4:9b scored it 9/10 and passed it, ignoring the explicit count rule in the scoring prompt. Structured rules in evaluator prompts are not reliably followed when the surrounding content reads as high quality.

- **Search chars vs output bytes: correlation inverted at steady state.** Prior study (single vs dual regime comparison) showed r ≈ +0.9. This experiment (all dual-search, narrow chars range 2952-3577) shows r = -0.577. The prior finding holds at regime scale but search volume is not a predictor once the floor is comfortably cleared. Within a tight band, output length is driven by model + task, not search volume.

**Anomaly requiring investigation:** T_A (top 5) byte variance was dominated by Run 4, which produced 3332 bytes and 68 lines — the richest output in the entire experiment. Run 4 used essentially the same task string and search volume as Runs 2 and 9. The difference is stochastic: same model, different synthesis draw. Implication: at temperature=0.1, the producer still has meaningful output variance between replications. This is expected but worth quantifying — it suggests 3 reps is insufficient to estimate true task-type means.

---

## Analytics

Added `analytics.py` — reads `runs.jsonl` and prints a summary comparing single-search vs dual-search runs.

**Results after 6 runs (3 single, 3 dual):**

```
                        single      dual
avg output bytes        1148.7    1816.7
avg output lines          10.7      31.0
avg 1st wiggum score       7.7       9.0
avg wiggum rounds          1.3       1.0
```

Dual search produced 58% more output bytes, 3x more lines, first-round wiggum score up from 7.7 to 9.0, and revision rounds dropped from 1.3 to 1.0. Every metric improved. The data confirmed the hypothesis that search result volume is a leading indicator of output quality.

`avg search chars` shows `n/a` for single-search runs because `total_search_chars` was not yet a log field at that time. Early records are missing it — not worth backfilling, just a gap in the historical data.

---

## Logging

Added `logger.py` — a `RunTrace` class that collects data throughout a run and appends one JSON record to `runs.jsonl` on completion.

Each record captures:
- Timestamp, task, producer and evaluator model
- Every tool call: name, query, result size in chars
- Whether forced synthesis was triggered
- Output path, line count, byte size
- Wiggum round count, per-round scores, final status

**Bug found and fixed:** `trace.finish()` was called twice on the no-wiggum path (once in the else branch, once unconditionally after). Fixed by moving `finish()` inside each branch.

**Observed:** first run in a session does not always log if the process exits before `finish()` is reached — any unhandled exception between write and finish will drop the record. A future improvement is to wrap `run()` in a try/finally so the trace is always written.

---

## Current State

A working local agent pipeline with orchestration:

**Entry points:**
- `orchestrator.py` — compound tasks: decomposes → runs subtasks → assembles final doc
- `agent.py` — single-focus tasks: memory → plan → search → vision → read_file → run_python → synthesize → write

**Shared services:**
- `wiggum.py` — evaluate (5-dimension decimalized rubric), revise, verify
- `memory.py` / `memory.db` — SQLite + FTS5 persistent observation store; glm4:9b compression
- `planner.py` — pre-execution task analysis; search queries, synthesis notes, subtask decomposition
- `security.py` — code scanner, path sandbox, prompt injection scanner
- `logger.py` / `runs.jsonl` — structured per-run traces

**Tooling:**
- `eval_suite.py` — regression harness: 5 tasks × 6 criteria
- `vision.py` — llama3.2-vision routing
- `analytics.py` — cross-run analysis and experiment comparison

**Model roster:**
- Producer: `pi-qwen` (qwen2.5:7b) — fast, tool-capable
- Evaluator: `glm4:9b` — different architecture (Zhipu AI), fast, genuinely critical with tightened prompt criteria
- Vision (future): `llama3.2-vision` — only locally available model confirmed to support both vision and tool calling
- Code tasks (future): `Qwen3-Coder:30b` — purpose-built for code generation and review
- Heavy evaluation (on-demand): `qwen2.5:72b` — slowest but most critical; use for high-stakes tasks

**Evaluator model history:**
- `qwen2.5:72b` — too slow (47GB, bottlenecks the loop)
- `glm4:9b` with loose criteria — too lenient (10/10 with no issues, rubber-stamping)
- `glm4:9b` with tightened criteria — working correctly (5/10 first pass, 9/10 after revision)

Remaining limitations:
- Eval suite partial — experiment-01 covers 3 task types but not a regression harness
- Text only — vision pipeline not yet wired in
- Single agent — no orchestration layer
- Analytics `avg search chars` missing for pre-dual-search runs (schema gap)
- Count constraint enforcement gap: **fixed** — harness-side check in `agent.py` re-synthesizes if item count is wrong
- Wiggum ceiling effect: **partially fixed** — pass threshold raised to 9, enforced in Python; 8/10 runs now trigger revision
- Task-type-specific evaluation: **done** — `detect_task_type()` routes to enumerated / best_practices / research criteria; `task_type` logged per run
- Adversarial two-pass evaluation: **attempted and reverted** — forced critique before scoring destabilized the 7B producer (jargon spiral, 5→6→6 ceiling). Not viable with mismatched evaluator/producer capability.
- Decimalized rubric scoring: **done** — evaluator now scores 5 dimensions (relevance 20%, completeness 25%, depth 30%, specificity 15%, structure 10%); composite computed in Python; `wiggum_dims` logged per round. PASS_THRESHOLD = 8.0.

## Stage 2: Vision Routing Layer

Implemented Option A from the roadmap — a routing layer that detects image paths in the task string and preprocesses them through `llama3.2-vision` before the text model runs.

**`vision.py`:**
- `detect_image_paths(task)` — regex search for image extensions, verifies files exist
- `extract_image_context(image_path, task)` — base64-encodes image, sends task-aware extraction prompt to `llama3.2-vision`, returns text description
- Standalone usage: `python vision.py image.png "task description"`

**`agent.py` integration:**
- Vision runs first if images detected — before web search
- Extracted descriptions injected as `vision_context` into `synthesize()` and `synthesize_with_count()`
- `vision_images` field added to run log

**Validated end-to-end test:**
- Input: screenshot of Anthropic's "Building Effective Agents" page
- llama3.2-vision extracted: title, subtitle, key points, visual structure (3487 chars)
- pi-qwen synthesized a 10-principle document grounded in both the image and web search
- wiggum: 8.0/10 PASS on first round (rel=9, cmp=8, dep=7, spc=8, str=9)

**Key finding:** vision context and web research are complementary — the image gave specific Anthropic framing while web search added implementation examples (Google ADK, prompt chaining patterns) not visible in the screenshot. The combined synthesis was richer than either source alone.

## Experiment 02: Harness Upgrade Impact Study

Reran the same 3 × 3 CRD from experiment-01 with the updated harness (count constraint enforcement, PASS_THRESHOLD=9, task-type-specific criteria). Full design and analysis in `experiment-02.md`.

**Key findings:**

- **H1 falsified.** All 9 runs scored 9/10 on round 1 again. Raising the pass threshold from 8 to 9 had zero effect because glm4:9b never scores below 9 for well-structured output. Threshold changes are a no-op if the evaluator's score distribution doesn't change. The ceiling effect is an evaluator calibration problem.

- **H2 confirmed (not stressed).** Zero count_check_retry events — the model got the count right on every first synthesis. The enforcement was never triggered, so its effectiveness under pressure (ambiguous prompts, complex topics) is untested.

- **H3 confirmed.** 9/9 PASS.

- **H4 confirmed.** 9/9 correct task_type routing: T_A/T_C → enumerated, T_B → best_practices.

- **CV improved for constrained tasks.** T_A CV dropped 39.7% → 22.8%; T_C CV dropped 44.2% → 32.4%. Output became more consistent across replications, though causation is unclear with 3 reps.

- **Persistent problem: glm4:9b evaluator is calibrated at 9/10.** It assigns 9/10 to anything structurally complete and topically correct. The wiggum revision loop is dormant. Two paths: swap evaluator model, or add an adversarial critique step that forces the evaluator to find flaws before scoring.

---

## Eval Suite

Built `eval_suite.py` — a regression harness that runs a fixed set of representative tasks and checks content criteria beyond file existence.

**Criteria implemented (factory functions):**
- `min_bytes(n)` / `min_lines(n)` — basic size checks
- `exact_sections(n)` — counts H2 content sections (excluding structural headers like Introduction, Conclusion); checks for exact match. Used for constrained tasks (top-N).
- `min_sections(n)` — counts all H2 sections; checks for minimum. Used for open-ended tasks.
- `no_placeholders()` — flags `[placeholder]`, `TODO`, `brief implementation note`, etc. Note: `"..."` removed from the blocklist after a false positive on truncated citation titles in search output.
- `has_impl_notes()` — requires at least one code block, "example:", or "implementation note" marker.
- `no_file_path_refs()` — blocks producer artifact leakage ("This document is saved to ~/...").

**Suite (5 tasks):**
| ID | Type | Task | Criteria |
|----|------|------|----------|
| T_A | enumerated | top 5 context engineering techniques | exact_sections(5) |
| T_B | best_practices | cost envelope management | min_sections(3) |
| T_C | enumerated | top 3 agent failure modes | exact_sections(3) |
| T_D | enumerated | top 3 context window management strategies | exact_sections(3) |
| T_E | best_practices | prompt injection defense | min_sections(3) |

**Usage:**
```bash
python eval_suite.py              # run all tasks then check criteria
python eval_suite.py --fast       # check existing output files only (no re-runs)
python eval_suite.py --no-wiggum  # run tasks but skip wiggum loop
```

**First run result:** 5/5 tasks, 30/30 criteria. T_E FAIL in wiggum (7.6/10 after 3 rounds on specificity) — that's a wiggum calibration issue, not a content criteria issue.

---

## Additional Tools: read_file and run_python

Expanded agent capability with two new tools.

### read_file (harness-side context injection)

Detects non-image text file paths (`.txt`, `.py`, `.json`, `.csv`, `.yaml`, `.toml`, `.xml`, `.html`) in the task string, reads them, and injects their content as a `File contents:` block in the synthesis prompt. Excludes the output `.md` file. Logged as `files_read` in `runs.jsonl`.

Usage: any task string that references a readable file — e.g., `"Analyze ~/Desktop/data.csv and summarize to ~/Desktop/summary.md"`.

### run_python (tool-calling loop)

Pre-synthesis agentic loop that gives the model access to a `run_python` tool for data processing or computation tasks. Up to 3 rounds. Model responds with "no code needed" for research tasks (no overhead). Execution output injected as `Code execution results:` block into synthesis.

`execute_python()` runs code in a subprocess with a 10-second timeout. Stdout + stderr captured, truncated at 4000 chars. Logged via the existing `tool_calls` array in `runs.jsonl`.

---

## Security Layer

Built `security.py` with three harness-enforced layers. Key design principle: **no model-in-the-loop for security decisions** — models can be jailbroken; the scanner is the ground truth.

### Threat model

The primary attack surface is **prompt injection via web search results**: a malicious web page embeds instructions that survive into the synthesis prompt, then cause the model to call `run_python` with harmful code. Secondary threats: `read_file` path traversal to credentials, model hallucinating dangerous code.

### Layer 1: Static code scanner (`check_python_code`)

Two-pass AST analysis:
1. Raw regex — catches obfuscated patterns (`getattr(os, 'system')(...)`, `open(`, `__builtins__`)
2. AST walk — catches `import os`, `from pathlib import Path`, `exec()`, `eval()`, `__import__()`

Blocked imports: `os`, `sys`, `subprocess`, `shutil`, `socket`, `requests`, `urllib`, `httpx`, `pathlib`, `tempfile`, `glob`, `pty`, `ctypes`, `winreg`, and others. Safe imports pass: `math`, `json`, `statistics`, `itertools`, `csv` (useless without `open()`), etc.

Applied in `execute_python()` before the subprocess is ever launched.

### Layer 2: Path sandbox (`check_file_path`)

Applied before `read_file` opens any file.
- **Allowlist:** `~/Desktop`, `~/Documents` — paths outside these are blocked.
- **Blocklist:** `.env`, `id_rsa`, `.pem`, `.key`, `secrets`, `credentials`, `api_key`, `.ssh/`, `known_hosts`, `.netrc`.

### Layer 3: Prompt injection scanner (`scan_for_injection` / `strip_injection_candidates`)

Applied to web search results before synthesis, and to file contents before injection. Suspicious lines are **stripped** (not just flagged) — the model never sees them. Patterns detected: "ignore all previous instructions", "you are now a...", "new instructions:", `<system>` tags, "execute the following code:", "write this to ~/...", "delete all...".

Stripping count logged as `injection_stripped` in `runs.jsonl`.

### What it doesn't protect against

- Subtle injections that don't match the regex patterns
- `math.factorial(10**9)` or similar compute bombs — handled by the 10s timeout
- The output file path — `write_output` writes wherever `extract_path` points (no sandbox on writes yet)

---

## Memory Layer

Built `memory.py` — a persistent observation store inspired by claude-mem's architecture but running fully locally via Ollama. No external services, no API keys, no daemon process.

**Architecture decision:** claude-mem uses the Claude Agent SDK (Anthropic API) for compression and ChromaDB for semantic retrieval. This pipeline is fully local Ollama, so Path B was chosen: SQLite + FTS5 for storage/retrieval, `glm4:9b` for compression. SQLite's FTS5 is built into Python's stdlib — zero new dependencies.

**Storage:** `memory.db` (SQLite). `observations` table with FTS5 virtual table for keyword search. Trigger-based index sync. Fields: title, narrative, facts (JSON array), task_type, output_path, final_score, final.

**Write path — `compress_and_store()`:**
After every run completes, the run summary (task, search queries, output excerpt, wiggum scores) is sent to `glm4:9b` for compression into a structured observation: title (≤80 chars), narrative (2-3 sentences), facts (3-5 specific strings). Stored to SQLite. Non-fatal — a compression failure never aborts a run.

**Read path — `get_context()`:**
FTS5 BM25 search across task/title/narrative/facts. Returns the N most relevant past observations as a formatted `## Relevant past research` block. Falls back to recency-ordered results if no FTS matches. Called before synthesis; result injected as `memory_context` into `synthesize()`.

**Lifecycle in `agent.py`:**
1. `memory.get_context(task)` → `memory_context` (before planning)
2. `memory_context` injected into synthesis as 5th context block
3. After run: `_store_memory()` → compress → SQLite

**`memory_hits`** logged per run in `runs.jsonl`. CLI: `python memory.py` (list observations) or `python memory.py --search "query"`.

**Validated:** First run stores observation, second run retrieves it. `memory_hits: 1` confirmed in log.

---

## Planning Layer

Built `planner.py` — pre-execution task analysis that uses memory context to produce a structured plan before any research begins. This is the first step toward Stage 3 orchestration.

**Why memory makes planning viable:** without memory, a planner is just prompt decomposition with no grounding. With memory, the planner knows what was researched before, what quality scores those runs achieved, and what dimensions were weak. It can plan to build on prior work rather than repeat it.

**`make_plan(task, memory_context)` → `Plan`:**

`glm4:9b` receives the task and all relevant memory observations and produces a structured JSON plan:
```python
@dataclass
class Plan:
    task_type: str            # enumerated / best_practices / research
    complexity: str           # low / medium / high
    expected_sections: int | None
    search_queries: list[str] # 2 planned queries
    prior_work_summary: str   # distilled from memory hits
    notes: str                # one actionable note for the producer
    subtasks: list[str]       # empty for now — Stage 3 hook
```

Parsing is robust: strips markdown fences, extracts the JSON block, falls back to a default `Plan()` on any failure. Never raises.

**Three stages the plan feeds:**

1. **`gather_research`** — uses `plan.search_queries` directly instead of auto-generating. Queries are planned before any search runs, using task semantics + memory knowledge of what prior searches found. Both queries printed with `(planned)` marker.

2. **`synthesize`** — `plan.synthesis_context()` appends `**Prior work:**` and `**Planner note:**` to the memory block. Example from second run: *"Incorporate specific tool names and version numbers"* — a direct response to the specificity weakness recorded in the prior observation's facts.

3. **Count constraint** — `plan.expected_sections or extract_count_constraint(task)`. The planner understands count from semantics, not just regex — better coverage for phrasing like "five strategies" that the regex would miss.

**Execution order in `run()`:**
```
memory.get_context()  →  make_plan()  →  gather_research(planned_queries)
    →  run_tool_loop()  →  synthesize(full_memory_context)  →  write  →  wiggum  →  compress_and_store()
```

**`plan` dict** logged per run in `runs.jsonl`. CLI: `python planner.py "<task>"`.

**Observed behaviour (second run):**
- `memory_hits: 1`, `prior_work_summary` correctly populated from first run's stored facts
- Planner generated a distinct second query (`top context window techniques in AI research` vs first run's `top context window management strategies...`)
- `notes` field specifically targeted the weak dimension from prior run

**Known limitation:** `glm4:9b` sometimes misses the `expected_sections` count from "top N" phrasing. The regex fallback in `extract_count_constraint()` handles this reliably.

---

## Stage 3: Orchestrator

Built `orchestrator.py` — a coordination layer that decomposes compound tasks into subtasks, executes each through the existing agent pipeline, and assembles a unified final document.

### Design

The orchestrator is a transparent passthrough for simple tasks: if the planner returns no subtasks, `orchestrate()` delegates directly to `agent.run()`. No new code path, no regression risk for existing tasks.

For compound tasks (two or more distinct research domains):
```
orchestrate(task)
  memory.get_context()  →  make_plan()           # subtasks populated for compound tasks
  _assign_paths()                                 # each subtask gets a _sub_N.md path
  agent.run(subtask, use_wiggum=False) × N        # full pipeline per subtask, no per-subtask verify
  assemble(task, subtask_outputs)                 # cross-referencing synthesis
  write final output
  wiggum on final output                          # single verification pass on assembled doc
  compress_and_store()  →  cleanup _sub_*.md
```

### Planner changes

Two additions required to make subtask generation work:

1. **Prompt rule updated** — `subtasks` now populated for tasks containing synthesis keywords ("and", "both", "synthesize", "unified", "combine") across multiple distinct domains. Constrained to research directives only; synthesis/assembly steps explicitly excluded.

2. **Filter in `_parse_plan`** — `glm4:9b` persistently adds a synthesis subtask ("Synthesize findings into...") even when told not to. A regex filter strips any subtask containing synthesis/assembly verbs before they reach the orchestrator.

### Assembly

`assemble()` is a distinct synthesis step, not concatenation. Prompt explicitly asks the model to cross-reference across source documents, identify patterns that appear in multiple sources, and note tensions or conflicts. The structure should emerge from the material, not from the source document order.

### Shared memory across subtasks

Subtasks execute sequentially through `agent.run()`, each of which writes to `memory.db`. The second subtask in a run therefore has `memory_hits: 1` from the first — it enters synthesis already knowing what the first subtask found. This happened automatically in the first validated run without any special wiring.

### Validated end-to-end run

Task: *"Research agent failure modes and context engineering techniques, then synthesize both into a unified LLM reliability guide"*

- Plan: `research / high / 2 subtasks`
- Subtask 1: top 3 failure modes → `_sub_1.md` (950 chars, 10 lines)
- Subtask 2: context engineering techniques → `_sub_2.md` (3251 chars, 41 lines); `memory_hits: 1` from subtask 1
- Assembly: 57-line cross-referencing guide mapping context engineering mitigations to specific failure modes
- Memory: 3 observations stored (subtask 1, subtask 2, orchestrated run)
- `_sub_1.md` and `_sub_2.md` cleaned up automatically

### What's logged

`orchestrated: true`, `subtask_count: N`, `plan` dict — all in `runs.jsonl`. Each subtask also logs its own full trace independently.

### Known gaps

- **Sequential only** — subtasks run one after another. Parallel execution (threading) would cut wall time for N subtasks by ~N×, at the cost of shared-memory write ordering.
- **No inter-subtask coordination** — subtasks don't know about each other's scope at planning time; they discover shared context only via memory. A richer subtask spec (including what other subtasks are doing) would reduce overlap.
- **Assembly quality bounded by producer** — the final synthesis is only as good as pi-qwen's ability to cross-reference. A stronger assembly model (qwen2.5:72b) would produce richer synthesis, at latency cost.
