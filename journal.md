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

- ~~Sequential only~~ — **fixed in Stage 4a** (parallel subprocess execution).
- **No inter-subtask coordination** — subtasks don't know about each other's scope at planning time; they discover shared context only via memory. A richer subtask spec (including what other subtasks are doing) would reduce overlap.
- **Assembly quality bounded by producer** — the final synthesis is only as good as pi-qwen's ability to cross-reference. A stronger assembly model (qwen2.5:72b) would produce richer synthesis, at latency cost.

---

## Stage 4a: Parallel Subtask Execution

### Problem
Sequential subtask execution imposed a wall time proportional to N subtasks × average subtask duration. On a 3-subtask orchestrated run, that was ~90s total.

### Implementation
Subtasks now execute in parallel via `ThreadPoolExecutor` — each thread spawns a subprocess (`agent.py --no-wiggum`). Subprocess isolation avoids shared-state problems (stdout interleaving, `sys.exit()` propagating):

- `_run_one_subtask(sub)` — subprocess runner with retry policy (`SUBTASK_MAX_RETRIES = 1`). Captures all output in memory; writes nothing to stdout until the future completes.
- `_run_subtasks_parallel(subtask_defs)` — collects futures via `as_completed`, prints each subtask's output sequentially after all complete. Reports wall time vs sequential estimate.
- `SUBTASK_MAX_WORKERS = 4` — caps concurrency to avoid Ollama queue saturation.

### SQLite concurrent writes
Multiple subprocess agents write to `memory.db` simultaneously. Fix: `PRAGMA journal_mode=WAL` in `MemoryStore._init_db()` allows one writer + multiple readers concurrently without locking errors.

### Results
Wall time: ~35s for 2-subtask run (was ~65s sequential). Sequential estimate: ~65s. ~1.9× speedup with 2 workers.

---

## Stage 4b: Evaluator Replacement

### Problem
`glm4:9b` as evaluator produced a ceiling of ~8.3/10 regardless of output quality. The wiggum revision loop was effectively dormant — peer-tier model evaluating peer-tier output, rubber-stamping everything above PASS_THRESHOLD.

Root cause: the evaluator needs to be *more capable* than the producer to identify genuine deficiencies. Peer evaluation is circular.

### Fix
**Model:** `Qwen3-Coder:30b` — 30B parameters vs 9B for glm4:9b, 3× the reasoning capacity. Available locally (18GB).

**Prompt changes:**
1. Calibration anchors added — concrete score-to-behaviour mappings prevent vague "good enough" middle scores.
2. Per-dimension issue rule — every dimension scored 8 or below must have at least one named issue.
3. Strict bias instruction — "when in doubt, score lower rather than higher."

### Observed behaviour after change

| Output | Old score (glm4:9b) | New score (Qwen3-Coder:30b) | Rounds |
|---|---|---|---|
| eval-context-engineering.md | ~8.3 pass | 8.1 pass | 1 (issues named) |
| eval-agent-failure-modes.md | ~8.3 pass | **7.0 fail → 8.8 pass** | 2 |
| eval-cost-management.md | ~8.3 pass | **7.9 fail → 8.1 pass** | 2 |

The revision loop now activates on genuinely weak outputs. Issues are specific and named rather than generic praise.

### Design note
The three-model architecture is now: `pi-qwen` (producer, 7B), `glm4:9b` (planner/compressor, 9B), `Qwen3-Coder:30b` (evaluator, 30B). The evaluator is the most capable model in the stack — which is the correct hierarchy for the verify-then-revise loop to have teeth.

---

## Experiment 03: Evaluator Upgrade Impact

### Design
9-run CRD, same 3 tasks as experiments 01/02. First experiment with `Qwen3-Coder:30b` as evaluator. PASS_THRESHOLD = 8.0.

### Key results

| Task | score_r1 mean | rounds mean | pass rate | revision gains |
|---|---|---|---|---|
| T_A (top 5) | 7.00 ±0.00 | 3.0 | 0/3 | –0.1, –0.2, 0.0 |
| T_B (best practices) | 7.20 ±1.08 | 2.0 | 2/3 | +1.2, +0.7 |
| T_C (top 3) | 7.00 ±0.00 | 2.3 | 2/3 | +1.8, 0.0, +1.1 |

Overall: 4/9 PASS. Revision loop active in 8/9 runs. First-pass score std = 0.55 (vs ~0 in both prior experiments).

### What worked

The evaluator is doing its job. Score variance is real, issues are specific, revision triggers on anything below 8.0. H1 (revision activates) and H2 (score variance) both confirmed.

### What failed

T_A is a 0/3 failure rate. Revision makes it *worse* on two of three runs (7.0→6.8 twice). The producer cannot respond to depth feedback on 5-item enumerated outputs — it over-corrects or strips content instead of deepening it.

### Two distinct revision failure modes

1. **Regression**: score 7.0 → 6.8. Producer rewrites sections and makes them shorter/worse while trying to address specific critique. The evaluator's feedback may be too precise for a 7B model to apply.
2. **Stagnation**: score stays at 7.0 across all 3 rounds. Producer edits surface wording without touching the underlying depth gap the evaluator identified.

### Implication: producer ceiling exposed

The wiggum loop design is correct. The evaluator is now calibrated. The bottleneck is the producer. Pi-qwen (7B) can produce output the new evaluator scores ≥8.0 on open-ended tasks (T_B) and short enumerated tasks (T_C) when depth per item is achievable. For T_A (5 items, each requiring a concrete implementation note), the ceiling is ~7.0 regardless of revision.

**Decision:** replace the producer. Lowering the threshold accepts the ceiling permanently; swapping the producer tests whether the ceiling is real or model-specific.

---

## Producer Upgrade Research

### Problem statement from experiment-03

T_A failure signature: depth=6, specificity=6 on every run. Composite = 6.95. To reach 8.0 requires depth=8, specificity=8, completeness=8 simultaneously — 2 points above what pi-qwen reliably produces.

The gap is content generation quality, not prompt engineering. The model writes to ~7-line depth per item; a passing output requires concrete implementation steps specific enough that the evaluator cannot call them generic.

### Model selection criteria

1. Available in Ollama with a named tag
2. Native JSON tool-calling support (Ollama format)
3. Different family from Qwen3-Coder:30b (evaluator) — no circular evaluation
4. Fits in ~24GB VRAM at Q4_K_M
5. 4.5× parameter count vs current 7B minimum

### Candidates researched and pulled

| Model | Size | Tool-calling | Family | Verdict |
|-------|------|-------------|--------|---------|
| `qwen2.5:32b-instruct-q4_K_M` | ~20GB | Native | Qwen2.5 (same as current) | **Test first** — one Modelfile line change, zero compatibility risk |
| `mistral-small3.1:24b` | ~15GB | Native | Mistral | Different family; 15GB leaves headroom; backup if 32B too slow |
| `phi4:14b` | ~9GB | Needs template override | Microsoft | Best instruction-following per GB; tool-calling requires community Modelfile workaround |

**Hard passes:** llama3.3:70b (~42GB, blows VRAM budget), gemma3:27b (tool-calling officially broken, GitHub issue #9941).

### `--producer` flag added to agent.py

Both synthesis and wiggum revision previously hardcoded to `MODEL = "pi-qwen"`. Now `run()` accepts `producer_model` parameter threaded through to:
- `run_tool_loop()` — pre-synthesis code execution
- `generate_second_query()` — complementary search query generation
- `synthesize()` — initial document generation
- `synthesize_with_count()` — count-constrained re-synthesis
- `wiggum_loop()` — revision model during evaluate → revise → verify

CLI: `python agent.py --producer pi-qwen-32b "task..."` — overrides producer for the full run including revision. Default behaviour unchanged.

### Initial test result (pi-qwen-32b, T_A)

First run with `--producer pi-qwen-32b` flag hit a wiring bug: `--producer` was not implemented, flag prepended to task string, pi-qwen (7B) ran the whole task. Bug fixed before real test.

The pre-fix run showed an interesting artifact: round 2 score was 7.7 (depth=8) — the first time depth=8 appeared on T_A in any experiment. This was stochastic improvement from the 7B, not the 32B. But it confirms the threshold is reachable on T_A; the 32B should hit it more consistently.

### 32B producer confirmed — T_A ceiling broken

Post-fix test with `--producer pi-qwen-32b` on T_A (top 5 context engineering techniques):

- Round 1: **7.0** (depth=7, spc=7) — identical first-pass to 7B baseline
- Round 2: **8.1 PASS** (depth=8, spc=8) — revision produced a concrete implementation note per item

This is a clean result: the 32B responds to depth feedback where the 7B couldn't. The first-pass score is the same (both models produce shallow first drafts), but the revision trajectory is different. The 7B regressed or stagnated; the 32B improved.

T_B and T_C also tested — both PASS on round 1 at 8.6+ (open-ended tasks benefit more from 32B on first pass).

**Decision:** pi-qwen-32b is the confirmed upgrade path. Next: make it the default producer.

---

## Token Tracking

Added per-run token and timing instrumentation to `runs.jsonl`.

### Motivation

Previously, runs.jsonl captured what happened (tools called, scores, final status) but not the cost (tokens consumed, time spent). Token data is needed to understand model cost envelopes, identify expensive stages, and compare producers fairly on token-per-quality ratios.

### Implementation

**`logger.py` — `_extract_usage()` and `log_usage()`:**

Ollama's `ChatResponse` is a Pydantic object with fields: `prompt_eval_count` (input tokens), `eval_count` (output tokens), and duration fields in nanoseconds (`total_duration`, `eval_duration`, `prompt_eval_duration`). `_extract_usage()` extracts all five values safely (returns zeros for missing fields). `log_usage(response, stage)` accumulates into:
- `input_tokens` / `output_tokens` — run-level totals
- `tokens_by_stage` — `{stage: {input, output, calls, total_ms}}`

Called immediately after every `ollama.chat()` call with a stage name.

**Stages tracked:**
- `tool_loop` — pre-synthesis code execution rounds
- `synth` — initial document synthesis
- `synth_count` — count-constrained re-synthesis (when triggered)
- `wiggum_eval` — evaluator scoring call
- `wiggum_revise` — producer revision call (each round)
- `search_query` — second query generation
- `planner` — task plan generation
- `memory` — memory compression

**`wiggum.py` — local trace pattern:**

`loop()` creates a lightweight local `RunTrace` for accumulation, passes `_trace=_local_trace` to `evaluate()` and `revise()`. On return, `_attach_token_stats()` copies the wiggum-specific token data into the wiggum trace dict. `logger.py`'s `log_wiggum()` then merges it into the main run record — no double counting.

**`run_duration_s`:**

`RunTrace.__init__` calls `time.monotonic()`. `finish()` computes the difference and stores it as `run_duration_s`. Also prints: `[log] {dur}s  in={tok_in} out={tok_out} tok  → runs.jsonl`.

### First confirmed output (run 75)

```json
{
  "input_tokens": 10391,
  "output_tokens": 2424,
  "run_duration_s": 714.0,
  "tokens_by_stage": {
    "tool_loop": {"input": 4481, "output": 1292, "calls": 3, "total_ms": 364331},
    "synth":     {"input": 2337, "output":  461, "calls": 1, "total_ms": 128263},
    "synth_count":{"input":2363, "output":  420, "calls": 1, "total_ms": 112990},
    "wiggum_eval":{"input": 1210, "output":  251, "calls": 1, "total_ms": 15919}
  },
  "wiggum_rounds": 1,
  "wiggum_scores": [8.8]
}
```

`tool_loop` dominates input tokens (3 calls to pi-qwen-32b for code execution decisions on a research task where run_python was blocked each time). `wiggum_eval` is cheap — 1.2s for a Qwen3-Coder 30B scoring call.

### `inspect_run.py`

Added a utility for interactive inspection:
```bash
python inspect_run.py          # last run (full detail)
python inspect_run.py 3        # last 3 runs
python inspect_run.py --all    # summary table of all runs
```

Prints: timestamp, models, final status, duration, token totals, per-stage breakdown, wiggum rounds/scores/dims, output path/size.

### `extract_path()` fix

Also fixed a latent bug: the regex in `extract_path()` required a path prefix (`~/`, drive letter, `/`) — bare filenames like `output.md` would fail with "no .md output path found". Added a fallback branch to match bare filenames. Backwards-compatible — prefixed paths still match first.

---

## CoT / Evaluator Reasoning Capture

The Qwen3-Coder:30b evaluator does not support `think=True` (the code-variant model returns HTTP 400 on that flag). However, the evaluator's `feedback` field — the prose explanation of why a score was assigned — is the functional equivalent of chain-of-thought for scoring decisions.

The `wiggum_eval_log` field was added to every run record in `runs.jsonl`:

```json
"wiggum_eval_log": [
  {
    "round": 1,
    "score": 7.0,
    "dims": {"relevance": 8, "completeness": 7, "depth": 6, "specificity": 6, "structure": 9},
    "issues": ["Section 2 lacks concrete implementation steps", "..."],
    "feedback": "The output covers all required items but each is described in one to two sentences without a code snippet or step-by-step procedure..."
  }
]
```

The `thinking` key is also extracted and stored if the model ever returns it (non-empty `response.message.thinking`) — forward-compatible for when a thinking-capable evaluator is used.

---

## Autoresearch Loop

Built `autoresearch.py` — an autonomous synthesis-instruction optimizer in the style of Karpathy's self-improvement loop.

### What it does

Runs indefinitely. Each iteration:
1. Reads the current `SYNTH_INSTRUCTION` and `SYNTH_INSTRUCTION_COUNT` from `agent.py` (between `AUTORESEARCH:*:BEGIN/END` sentinel markers)
2. Asks Qwen3-Coder:30b to propose a modification, given current instructions + experiment history + the last failed run's evaluator feedback
3. Writes the proposal to `agent.py` and commits it
4. Runs `eval_suite.py --score --tasks T_A,T_B` to get the composite score
5. If `new_score - baseline > 0.1`: keeps the commit, updates the baseline
6. Otherwise: `git reset HEAD~1 --soft && git checkout -- agent.py`, baseline unchanged
7. Logs to `autoresearch.tsv` (untracked) and loops

### Metric

```
composite = 0.7 * mean_wiggum_r1 + 0.3 * criteria_rate * 10
```

Continuous float — comparable across experiments. Bottleneck dimensions: **depth** (weight 0.30) and **specificity** (weight 0.15). The evaluator consistently penalises outputs where each item is described in 1-2 sentences without a code snippet, named tool, or step-by-step procedure.

### Mutable scope

Only `SYNTH_INSTRUCTION` and `SYNTH_INSTRUCTION_COUNT` in `agent.py` — the strings between the sentinel markers. Everything else is off-limits. Both constants must stay under ~300 characters combined.

### Usage

```bash
python autoresearch.py                    # default: T_A + T_B, delta=0.1
python autoresearch.py --tasks T_A,T_B   # explicit task subset
python autoresearch.py --delta 0.2       # stricter keep threshold
```

`autoresearch.tsv` is untracked by git. Full specification in `autoresearch_program.md`.

---

## TinyTroupe Synthetic Task Generation

Built `tinytroupe_tasks.py` — generates diverse eval tasks from 8 practitioner persona archetypes (DevOps, Data Scientist, Backend Engineer, Product Manager, Security Engineer, ML Infrastructure Engineer, Startup Founder, Tech Lead).

Each persona is prompted to request a research task from an AI agent. The response is parsed, a filename is inferred, and criteria are auto-generated (exact_sections(N) for "top N" tasks, min_sections(3) for open-ended). Output saved to `generated_tasks.json`.

Uses TinyTroupe persona simulation if `tinytroupe` is installed; falls back to raw `ollama.chat` with persona descriptions if not.

`eval_suite.py` updated with:
- `load_generated_suite(path)` — loads `generated_tasks.json` and converts serialisable `criteria_specs` to callable criterion functions
- `--generated [path]` CLI flag — appends generated tasks to any run mode
- `score_suite(..., extra_tasks=)` — generated tasks count toward the composite metric for autoresearch

```bash
python tinytroupe_tasks.py                    # generate from all 8 personas
python eval_suite.py --generated              # run eval suite + generated tasks
python eval_suite.py --score --generated      # include generated tasks in autoresearch score
```

---

## MarkItDown Integration

Added `markitdown` as a document-conversion backend throughout the research pipeline.

### 1. Rich document reading

`detect_text_files` now also matches `RICH_EXTENSIONS = {.pdf, .docx, .doc, .xlsx, .xls, .pptx, .ppt, .epub, .htm}`. When a task references one of these files, `read_file_context` routes it through `MarkItDown.convert()` instead of plain `open()`. The resulting markdown is injected into the synthesis prompt the same way plain-text file context is. All converted content still passes through the injection scanner before synthesis.

```python
result = _md_converter.convert(path)   # returns MarkItDownResult
content = result.text_content          # markdown string
```

### 2. URL enrichment

After merging search results, `enrich_with_page_content` fetches full page content for the top `URL_ENRICH_COUNT = 2` search result URLs via `MarkItDown.convert(url)`. Each is capped at `URL_ENRICH_MAX_CHARS = 8000` characters and appended as a `## Full page content` block before synthesis.

**Observed impact (run 4/9, experiment-04):**
- Search snippet context: 3,368 chars
- After URL enrichment: +16,312 chars (2 pages fetched, 1 failed on Wikipedia robots block)
- Nearly 6× more synthesis context

**Side effect observed:** the larger context (19k chars) occasionally causes the model to produce a flat numbered list on first synthesis pass instead of H2 headers, triggering `count_check_retry`. This is caught and corrected by the existing retry path — not a functional regression.

### 3. Graceful fallback

`try/except ImportError` at startup. If `markitdown` is not installed, both paths are silently skipped and the agent runs exactly as before.

```bash
pip install "markitdown[all]"
```

---

## Experiment 04: Producer Upgrade Impact

### Design

9-run CRD (16 recorded due to MarkItDown integration mid-experiment), same 3 tasks as experiments 01-03. First experiment with `pi-qwen-32b` (qwen2.5:32b Q4_K_M) as the default producer. Evaluator and threshold unchanged (Qwen3-Coder:30b, 8.0).

### Key results

| Task | score_r1 mean | rounds mean | pass rate | depth_r1 | spc_r1 |
|------|--------------|-------------|-----------|----------|--------|
| T_A | 8.00 ±0.74 | 1.25 | 4/4 | 7.2 | 7.0 |
| T_B | 6.97 ±0.53 | 2.71 | 4/7 (57%) | 6.1 | 5.9 |
| T_C | 7.54 ±0.80 | 2.00 | 4/5 (80%) | 6.8 | 6.4 |

Overall: 12/16 PASS (75%). Exp-03 was 4/9 (44%). Zero revision regressions (exp-03 had 2).

### H1–H5 assessment

- **H1 (pass rate > 4/9): CONFIRMED** — 12/16
- **H2 (T_A ceiling broken): CONFIRMED** — 4/4 PASS, rounds 3.0→1.25
- **H3 (no regression): CONFIRMED** — 0 regressions vs 2 in exp-03
- **H4 (score_r1 > 7.07): CONFIRMED** — 7.41
- **H5 (T_A depth/spc > 6): CONFIRMED** — depth=7.2, spc=7.0

### What worked

**T_A is solved.** The 32B producer breaks the enumerated-task ceiling. First-pass depth +1.2, specificity +1.0 vs exp-03. The revision trajectory reversed: the 7B regressed or stagnated on T_A; the 32B improves cleanly on feedback every time.

**Revision reliability.** Zero regressions across 16 runs is the clearest signal: the 32B can act on evaluator feedback without degrading. This means the wiggum ceiling is now set by the synthesis instruction and evaluator, not by the producer's revision capability.

### What failed / what's next

**T_B first-pass quality is flat.** depth_r1 = 6.1 (exp-03: 6.0). The 32B produces *shorter* T_B output than the 7B (2198 vs 3288 bytes, −33%). Longer revision loop required (mean 2.71 rounds). Two T_B runs failed outright after 3 rounds.

The dimension data is decisive: T_B depth is unchanged despite a 4.5× parameter increase. This is not a producer problem — it's a **synthesis instruction problem**. `SYNTH_INSTRUCTION` doesn't push hard enough on depth for open-ended tasks, and the 32B complies faithfully with a weak instruction. This is the autoresearch target.

**count_check_retry rate is high on MarkItDown-enriched runs.** T_A retry rate 4/4, T_C 4/5 on runs with URL enrichment. The 16k-char context causes the model to produce flat lists instead of H2 sections on first synthesis pass. The retry path fixes it but adds latency. Consider making `URL_ENRICH_COUNT` task-type-aware — disable for enumerated tasks where format compliance is critical.

### Decision

Start autoresearch immediately. T_B depth/specificity is the target. T_A and T_C are stable baselines.

---

## Throughput Optimisations + Perfetto Tracing

Several pipeline changes made to reduce wall-time per run:

- **Panel parallelism:** `panel.py` now runs the 3 evaluator personas concurrently via `ThreadPoolExecutor`. Each thread calls `trace.name_thread()` so Perfetto traces show true parallelism.
- **Tool loop skip:** `run_python` tool loop is skipped entirely for `task_type in ("research", "best_practices")` — saves ~30s on every eval task run.
- **COMPRESS_MODEL env var:** `compress_knowledge()` and `plan_query()` can use a lighter model (e.g. `glm4:9b`) independent of the producer. Eliminates the VRAM swap cost when using a heavy producer.
- **Novelty-gated URL enrichment:** `enrich_with_page_content()` skips URLs where >60% of snippet words already appear in the knowledge state. Prevents redundant full-page fetches.
- **num_predict=8192:** added to all `synthesize()` calls. Fixed a latent truncation bug on T_E — Section 5 was being cut off mid-sentence on every run, capping wiggum scores at ~8.1 regardless of instruction quality. The bug had been active all of session 2.

**Perfetto / Chrome Trace Event instrumentation added to `logger.py`:**

`RunTrace` now emits `traceEvents` in Chrome Trace Event JSON format to `traces/<timestamp>_<slug>.json` at the end of every run. Load at `ui.perfetto.dev` for a per-stage waterfall and panel thread parallelism view. Key span types:
- `trace.span("stage")` — wall-clock duration event
- `trace.name_thread("panel/Reviewer")` — lane labels per thread
- `trace.log_usage(response, stage=...)` — emits `llm:<stage>` event from Ollama's `total_duration`

---

## Skills System

Added a skill registry and invocation layer (`skills.py`) that extends the pipeline at four hook points without modifying `agent.py` internals:

| Hook | Fires | Skills |
|------|-------|--------|
| `pre_research` | before gather_research | `deep` — forces MAX_SEARCH_ROUNDS, disables novelty gate |
| `pre_synthesis` | injected into synthesis prompt | `annotate`, `cite` |
| `post_synthesis` | after output written | `kg` — D3.js knowledge graph |
| `post_wiggum` | after verification loop | `panel` — 3-persona evaluation |

Skills activate via `/skillname` prefix on the task string, or automatically via predicate functions (e.g. `panel` auto-triggers on `plan.complexity == "high"`; `annotate` auto-triggers when task mentions "paper", "abstract", "survey").

`annotate_abstracts.py` added as a standalone batch tool: given a CSV of papers with `markdown_content` column, generates Nanda 8-move annotated abstracts via Ollama. Handles structured section extraction and /no_think suffix for Qwen3 models.

---

## Chunker + Provenance Metadata

`chunker.py` added for large document context extraction. Called by `read_file_context()` for any file > 12,000 chars.

**Strategy selection:**
- ≥3 markdown headings → section extraction (Abstract, Conclusion, Introduction, Results, etc.) assembled in priority order within char budget
- Otherwise → overlapping character windows embedded with `all-MiniLM-L6-v2` via ephemeral ChromaDB; top-K by cosine similarity re-sorted to reading order

**`Chunk` dataclass** carries full provenance metadata: `source` (filename), `url`, `page` (estimated from `page_size` hint), `paragraph` (`\n\n` count before chunk start), `char_offset`, `section`. Tags are embedded inline in the assembled output so the model can cite specific passages:

```
=== Introduction [source:paper.pdf | p.3 | ¶12 | §Introduction | @4,200] ===
```

---

## Autoresearch Session 3: Kimi as Cloud Proposer

Session 2 best: **8.420** (2 experiments). Session 2 was bottlenecked by two factors: the proposer (Qwen3-Coder:30b) had to be loaded/unloaded from VRAM on each propose step, and T_E scores were capped at ~8.1 due to a latent truncation bug (`num_predict` not set in `synthesize()`).

**Infrastructure changes before session 3:**
- `num_predict=8192` in all `synthesize()` calls — fixes T_E truncation
- Proposer now configurable: `python autoresearch.py --proposer kimi-k2.5:cloud`
- Anti-stuck improvements to `PROPOSE_PROMPT`: explicit `{already_present}` and `{discarded_list}` sections; removed anchoring "Common effective changes" list; added "Unexplored angles" list

**Session 3 results (in progress, eval tasks T_D + T_E):**

| Exp | Change | Score | Status |
|-----|--------|-------|--------|
| 6 | Failure modes + detection/mitigation per strategy | 8.350 | DISCARD −0.233 |
| **7** | **"When NOT to use" + input boundaries framing** | **8.915** | **KEEP +0.332** |
| 8 | Measurable success criteria / validation tests | 8.915 | DISCARD +0.000 |
| 9 | Confidence ratings (High/Med/Low) per library | 7.965 | DISCARD −0.950 |
| 10+ | ongoing… | — | — |

**New best: 8.915** (exp 7 — largest single jump in any session). Kimi found an angle the local proposer never tried: framing each section around applicability constraints ("when NOT to use") rather than adding more implementation density.

**Key negative signal:** exp 9 (confidence ratings) produced a −0.950 regression — the largest single drop in any session. Hedging annotations actively hurt depth scores. The evaluator reads uncertainty markers as lack of authority. Added to `already_present` blocklist.

**Observation on cloud proposer:** Kimi explores structurally different angles from Qwen3-Coder:30b. Sessions 1–2 converged on "add more code / implementation detail" variations. Session 3 immediately tried constraint framing, boundary conditions, and persona specification — approaches closer to rhetorical structure than content density.

---

## HuggingFace Dataset Export

`hf_export.py` added: reads `runs.jsonl` and writes four Hugging Face-ready dataset files to `hf_datasets/`.

| Dataset | Rows (182 runs) | Format | Use |
|---------|-----------------|--------|-----|
| `sft.jsonl` | 62 | chat messages (system/user/assistant) | SFT, distillation |
| `preference.jsonl` | 158 | prompt + chosen + rejected | DPO, ORPO, CPO |
| `reward.jsonl` | 113 | prompt + response + score + rubric | reward model training |
| `trajectory.jsonl` | 182 | task + plan + stage trace | agent policy imitation |

Preference pairs are generated by grouping runs on the same task text, ranking by wiggum score, and pairing top-third vs bottom-third with a minimum score delta (default 0.5). The 57 autoresearch runs on the T_D task alone yield dense preference signal where the only variable between chosen and rejected is synthesis instruction quality.

`logger.py` updated: `final_content` field (up to 16k chars) stored inline in every run record. Future exports are self-contained regardless of whether output files are still on disk.

**Training pipeline (TRL):**
```bash
trl sft --model <base> --dataset hf_datasets/sft.jsonl
trl dpo --model <sft-model> --dataset hf_datasets/preference.jsonl
python hf_export.py --push nickmccarty/ollama-pi-harness-datasets
```

---

## Dashboard

`dashboard.py` generates a self-contained `dashboard.html` (no server) with Chart.js charts:
- Score trend over time, tokens by date (stacked input/output), tokens by stage (donut), wiggum dimension radar, pass/fail/error donut, run duration trend, activity by hour
- **Cost analysis section:** cloud equivalent cost at 6 provider tiers (GPT-4o, GPT-4o mini, Claude Sonnet/Haiku, Gemini 1.5 Pro/Flash) vs local electricity estimate; cumulative cost-over-time chart; tokens by model role (producer/evaluator/planner)
- Recent runs table with inline score bars and pass/fail badges

```bash
python dashboard.py --open
```

---

## Trace Analysis: URL Enrichment Disabled for Enumerated Tasks

Perfetto trace analysis across 10 autoresearch runs revealed four actionable findings:

**1. `synth_count` retry (T_D only) — 29–56% overhead on top of synthesis**
Every T_D (enumerated) run triggered the count check retry. T_E (best_practices) never did. The full-page URL context causes the model to produce flat prose lists rather than H2 sections on the first synthesis pass; the harness catches this and re-synthesises. The last traced T_D run spent *more time on the retry than the original synthesis* (1052s vs 842s). Fix applied: `enrich_count = 0 if task_type == "enumerated"`. Saves 300–1000s per T_D eval run.

**2. `compress_knowledge` consumes ~80–90% of `gather_research` wall time**
compress_knowledge is as expensive as the search itself — scales with search rounds (up to 4 calls per run at 5 rounds). Largest outlier: 294s on compress vs 442s total gather. Future fix: skip compress on borderline-novelty rounds, or cache compressed state between autoresearch experiments on the same task.

**3. `wiggum_revise` costs 11–22% of total when it fires**
4/10 runs triggered revision, adding 310–1116s. Confirms that optimising for first-round score (the autoresearch metric) directly optimises runtime — each +0.5 point on round-1 score avoids a full revision pass.

**4. Panel threads not visible — `WIGGUM_PANEL` not set in autoresearch subprocess**
All 10 traces show only a `main` thread. The parallel panel is not running during autoresearch eval runs. The env var isn't being passed through the subprocess call.

---

## Search Cache (SQLite TTL)

Autoresearch runs the same search queries repeatedly across experiments — proposer converges on similar instructions, so the underlying research questions are nearly identical. Without a cache, every experiment pays full DDGS latency + `compress_knowledge` cost for queries already answered.

**Design:** SQLite, SHA-256 keyed on normalised query, 24 h TTL, lazy expiration eviction on every `put()`. Schema lives in `search_cache.db` (gitignored). `cached_search()` is the only public interface agent.py needs to call.

```
web_search_raw(query)
  -> cached_search(query, _ddgs, max_results=n)
       -> HIT:  return from DB          (< 1 ms)
       -> MISS: call DDGS, store, return (~300-600 ms per result set)
```

**Integration:** `web_search_raw()` in agent.py now wraps `cached_search` with a local `_ddgs` lambda. The cache import is lazy (inside the function) so the rest of agent.py has no hard dependency.

**Expected savings in autoresearch:** Within a session, the first experiment cold-populates the cache for a given task. Subsequent experiments on the same task (same proposer queries) are served from cache. This cuts DDGS + compress_knowledge time — the two stages that dominate `gather_research` wall time.

**Cache management:**
```bash
python search_cache.py            # stats
python search_cache.py --expired  # evict expired rows
python search_cache.py --clear    # wipe all
```

---

## Research Context Cache (gather_research full-output cache)

The search result cache (above) eliminated DDGS latency but not `compress_knowledge` — the LLM compression calls that account for 80-90% of `gather_research` wall time. In autoresearch, the task definitions never change between experiments (same T_D/T_E), so the entire research phase produces identical output across a session. The right cache level is the full `gather_research()` return value.

**Design:** Second table (`research_cache`) in the same `search_cache.db`. Key: `SHA-256(normalised_task + "|" + task_type)`. Value: complete merged context string + `search_rounds` + `novelty_scores` (trace metadata). 24 h TTL, same lazy eviction.

```
gather_research(task, ...)
  RESEARCH_CACHE=1 set?
    -> get_research(task, task_type)
         HIT:  restore trace metadata, return context  (< 1 ms)
         MISS: run full search+compress loop, put_research(), return
```

**Opt-in via env var:** `RESEARCH_CACHE=1` is only set by autoresearch's eval subprocess. Interactive `python agent.py` runs always get fresh search results. `force_deep` skips the cache even in autoresearch (ensures deep-search tasks aren't served stale).

**Autoresearch session profile after both caches:**

| Experiment | gather_research | synthesize + wiggum |
|------------|----------------|---------------------|
| 1 (cold)   | full cost (~400-600s) | full cost |
| 2-N        | ~1 ms (cache hit) | full cost |

The optimizer now runs at the speed of synthesis + wiggum alone. On a 2-task session (T_D + T_E), exp 1 pays ~800-1200s for research; exps 2-N skip it entirely. A 10-experiment session that previously cost ~100-200 min of research overhead now costs ~10-20 min for the cold run only.

**Also fixed in this session:** `WIGGUM_PANEL=1` now propagated through autoresearch eval subprocess — panel scoring was silently skipped in all prior autoresearch runs.

---

## External Source Review (2026-04-12)

Evaluated four sources for project relevance. Findings added to roadmap Stage 7.

**OCR models with llama.cpp (ggml-org):** `GLM-OCR-GGUF` and `Qwen3-VL-2B` run via `llama-server` and expose a standard `/v1/chat/completions` endpoint. Prompts: `"OCR markdown"`, `"OCR HTML table"`. Direct fix for the MarkItDown-on-scanned-PDF failure mode in `read_file_context()`. Low effort: detect low text yield from MarkItDown, route through OCR, feed clean markdown to chunker unchanged.

**Gemma 4 (Ollama):** 26B MoE variant has 3.8B active params at inference, 256K context, native function calling, configurable thinking mode, different architecture family from Qwen3-Coder. Candidate evaluator for diversity-testing the wiggum rubric. One command to test: `ollama pull gemma4:26b` + swap into `eval_suite.py` for one session and compare scores against Qwen3-Coder baseline.

**Ollama import:** GGUF and Safetensors (full model + LoRA adapter) both supported. `--quantize q4_K_M` at import time. This is the re-import leg of the self-improvement loop once DPO/SFT training closes against `hf_datasets/preference.jsonl`. Qwen2.5 imports cleanly (Llama-compatible).

**Docker Sandboxes:** containerized execution for agent code. Not urgent — current AST blocklist covers the research-task threat model. Revisit if `run_python` is expanded to execute untrusted external code or harness is productionized for other users.

---

## runs.jsonl Analysis + Pipeline Fixes (2026-04-12)

Deep analysis of 123 eval runs in `runs.jsonl` revealed several actionable findings and led to three code fixes.

### Findings

**Dimension bottleneck (confirmed with precision):** specificity (mean r1 = 6.65) is actually weaker than depth (6.97), despite depth receiving 2× the composite weight. The synthesis instruction has been targeting depth language; specificity has more headroom and is undertargeted.

**Wiggum revision regressions:** 12 of 57 multi-round runs scored lower on the final round than round 1 (avg −0.36). All regressions on T_A (context engineering techniques). The evaluator demands code depth; the producer overcorrects and loses completeness or structure. The loop was returning the last round's content unconditionally — even if it was the worst round produced.

**count_check_retry drag:** 31/123 runs (25%) triggered the count retry. Mean r1 with retry = 7.53 vs 7.92 without — a 0.39 score penalty. The penalty came from the first synthesis (using SYNTH_INSTRUCTION) producing the wrong count, then a second synthesis (using SYNTH_INSTRUCTION_COUNT, session-1-era quality) replacing it as the final output.

**Search rounds vs r1:** runs with 5 search rounds scored mean r1 = 8.12 vs 7.85 for 2-round runs. The highest-scoring gap queries in 5-round runs use progressively specific exclusion syntax ("not including X, Y, Z") based on what was already found.

**Novelty scale compression:** in 55 runs with novelty scores, the distribution is {2: 24, 3: 30, 4: 1}. The scale is effectively binary. NOVELTY_THRESHOLD=3 stops on score=2; later search rounds (round 4 mean = 2.83) are borderline and may still contain useful content.

### Fix 1 — Wiggum best-round restoration (`wiggum.py`)

Track `best_score / best_content / best_round` across all rounds. Before returning FAIL at max rounds, restore the best-scoring round's content to disk if a later round scored lower. Also fixed a latent bug: the termination gate used the `MAX_ROUNDS` global constant instead of the `max_rounds` local variable — `WIGGUM_MAX_ROUNDS` env override was correctly scoping the loop but not the early-exit check.

### Fix 2 + 3 — Enumerated task synthesis path (`agent.py`)

`expected_count` now extracted before the first `synthesize()` call. Enumerated tasks route directly to `synthesize_with_count()` — no wasted first synthesis pass.

`synthesize_with_count()` was using `SYNTH_INSTRUCTION_COUNT`, which had never been through the autoresearch optimization loop (session-1-era quality). Ablation run (see below) caught this — ablation outputs scored 6.9 vs 8.8 historical T_D baseline on identical tasks. Root cause: SYNTH_INSTRUCTION_COUNT produces ~1300 byte outputs vs 5000–7000 byte outputs from SYNTH_INSTRUCTION. Fixed: `synthesize_with_count()` now uses `SYNTH_INSTRUCTION` with the count constraint injected as a prefix. `SYNTH_INSTRUCTION_COUNT` is dead code, left in place inside its autoresearch sentinels.

---

## Ablation: Saturation Loop vs Single Search (2026-04-12)

**Goal:** determine whether `compress_knowledge()` in the saturation loop is worth its cost, or whether it introduces lossy compression that hurts synthesis quality. Motivated by the observation that April 7 runs (pre-saturation-loop) produced r1=9.0, while current runs peak at 8.8.

**Design:** same task (T_D — top 3 context window management strategies), `NOVELTY_THRESHOLD=0` to force all rounds, two runs:
- Run 1: `MAX_SEARCH_ROUNDS=1` (single search, no compress_knowledge)
- Run 2: `MAX_SEARCH_ROUNDS=5` (up to 5 rounds, compress_knowledge active rounds 2+)

**First run (confounded):** both runs scored r1=6.9 with identical dimension profiles. The confound was Fix 3 above — our code change routed both runs through SYNTH_INSTRUCTION_COUNT, depressing all scores below baseline. The comparison was bad-vs-bad.

**Rerun in progress** after Fix 3. Preliminary signal from the confounded run: both 1-round and 5-round produced identical r1 scores, suggesting extra search rounds may not lift synthesis quality independently of instruction quality. Result pending clean rerun.

---

## MagenticOne Architecture Review (2026-04-12)

Reviewed Microsoft's MagenticOne (AutoGen v0.4.4) — a 5-agent orchestrator (Orchestrator, WebSurfer, FileSurfer, Coder, ComputerTerminal) with an LLM-driven ledger for dynamic routing.

**Key MagenticOne mechanisms:**
- **Ledger:** 5-key JSON generated per round: `is_request_satisfied`, `is_in_loop`, `is_progress_being_made`, `next_speaker`, `instruction_or_question`. Updated after every agent action.
- **Stall recovery:** stall counter increments when `is_in_loop=true` or `is_progress_being_made=false`. After 3 stalls: replan (update facts + plan via LLM, broadcast ResetMessage). After 3 replans: terminate and report educated guess.
- **7 orchestrator prompt templates** — closed-book init, plan generation, synthesize, ledger query, update facts, update plan, final answer.

**Mapping to our harness:**

| MagenticOne | Harness equivalent | Gap |
|-------------|-------------------|-----|
| Task Ledger | `planner.py` Plan + `knowledge_state` string | Our state is a flat string; no verified-facts / open-gaps structure |
| Progress Ledger | `assess_novelty()` + wiggum score delta | No cross-pipeline "is progress being made" signal |
| Stall → replan | `NOVELTY_THRESHOLD` + `WIGGUM_MAX_ROUNDS` | Stall detection is per-stage, not pipeline-level |
| `ORCHESTRATOR_CLOSED_BOOK_PROMPT` | **Missing** | We go straight to web search without auditing prior knowledge |
| Dynamic routing | Fixed pipeline | By design — our fixed pipeline enables autoresearch optimization |

**What we do better:** measurable eval rubric (vs vibes-based `is_satisfied`), autoresearch meta-optimization, novelty-based search saturation, panel evaluation for preference data.

**Highest-value borrow: closed-book prior knowledge pass.** Before `gather_research()`, ask the producer: "What do you already know about {task}? List (1) facts you're confident about, (2) gaps you'd need to look up." Gap list seeds `plan_query()` — searches target actual unknowns rather than re-surfacing what the model already knows. This also addresses the synthesis gap identified earlier: a reflect step between planner and search, without needing a full ReAct loop inside synthesis. Roadmapped under Stage 1.

---

## Traces + runs.jsonl Deep Analysis — Experiment Design (2026-04-12)

### Data

- 211 runs total; 138 scored (wiggum_scores present, not ERROR)
- 38 Perfetto traces in `traces/` (T_D/T_E and /annotate sessions, Apr 9–11)

---

### Finding 1 — Time allocation (from traces)

| Stage | Mean % wall time |
|-------|-----------------|
| synthesize | **53%** |
| wiggum (all rounds) | 32% |
|   of which wiggum_revise | ~94% of wiggum time |
|   of which wiggum_eval | ~6% |
| gather_research | 15% |

**Implication:** Synthesis is the single biggest cost center. Wiggum eval is essentially free (6% of wiggum); all the wiggum cost is the revision LLM call. Any experiment that cuts revision rounds or cuts synthesis latency has large wall-time leverage. Gather research is surprisingly cheap at 15% — the research cache optimization saves that, but it's not the dominant term.

---

### Finding 2 — Memory hits confound (DEBUNKED)

The earlier apparent finding that memory_hits=0 scored higher (8.35) than memory_hits=4+ (7.53) is a **confounder, not a signal**:

- All zero-hit runs are from 2026-04-07 (pre-memory implementation)
- April 7 used **glm4:9b evaluator** + pi-qwen 7B producer
- April 8+ used **Qwen3-Coder:30b evaluator** + pi-qwen-32b producer

The evaluator change from glm4:9b to Qwen3-Coder:30b fully explains the score difference. glm4:9b is more lenient. This is **evaluator calibration drift**, not a memory effect.

**Implication:** We cannot directly compare scores across evaluator changes. We need a calibration run: same tasks + same outputs scored by both evaluators to establish a conversion factor. This also motivates Gemma 4 evaluator testing — need to know where it sits on the scale before interpreting autoresearch results.

---

### Finding 3 — Wiggum lift/regression distribution

| Outcome | Count | % | Magnitude |
|---------|-------|---|-----------|
| Lifted (r_final > r1) | 35 | 25% | mean +1.02 |
| Unchanged | 89 | 64% | — |
| Regressed (r_final < r1) | 14 | 10% | mean −0.38 |

Within enumerated tasks specifically: 17 lifts, 10 regressions, 13 unchanged (of 40 multi-round runs).

Best-round restoration fix (2026-04-12) addresses the 10% regression case — should recover those 14 runs to their best-seen score.

---

### Finding 4 — Dimension weakness profile (104 scored runs)

| Dimension | Mean score | Weight |
|-----------|-----------|--------|
| relevance | 8.88 | 0.20 |
| structure | 8.54 | 0.10 |
| completeness | 7.19 | 0.25 |
| depth | 6.87 | 0.30 |
| **specificity** | **6.61** | **0.15** |

Specificity is weakest, depth second. Since depth has the highest weight (0.30), it is the highest-leverage target. Specificity is weakest but lower weight.

Autoresearch session 3's best result (exp 7, "when NOT to use" + input boundaries) targeted applicability — which maps to specificity and completeness. That was the right direction.

**Implication for autoresearch session 4:** prime the PROPOSE_PROMPT explicitly for depth improvements.

---

### Finding 5 — Task type performance + pass rates

| Task type | n | mean_r1 | Pass rate |
|-----------|---|---------|----------|
| unknown (Apr 7, glm4:9b) | 17 | 8.76 | 100% |
| best_practices | 42 | 7.81 | 64% |
| enumerated | 66 | 7.56 | 52% |
| **research (/annotate)** | **13** | **6.91** | **0%** |

Research-type (/annotate arxiv PDFs) has 0% pass rate and mean r1 = 6.91. These runs never pass wiggum. Scores are stuck 6.2–7.8 with no trajectory to 8+. Root cause candidates:
1. Wiggum criteria designed for synthesis tasks, not annotation tasks
2. Output format mismatch — annotation vs. structured research synthesis
3. chunker.py not extracting enough from PDFs (Section 5 truncation issue from session 3 applies here too)

---

### Finding 6 — Search rounds vs r1

| search_rounds | n | mean_r1 |
|--------------|---|---------|
| 0 (cache hit) | 114 | 7.72 |
| 2 | 12 | 7.77 |
| 3 | 4 | 7.20 |
| 4 | 2 | 7.55 |
| 5 | 6 | **8.07** |

The 5-round runs score highest (8.07) but n=6 is too small for confidence. The preliminary ablation finding (1-round = 5-round) was confounded by SYNTH_INSTRUCTION_COUNT; a clean rerun is needed.

---

### Proposed Experiments

**EXP-A: Evaluator calibration (Gemma 4)**
- `ollama pull gemma4:26b`
- Run T_D + T_E with `WIGGUM_MODEL=gemma4:26b` — single run each, compare to Qwen3-Coder scores
- Goal: establish score conversion factor before relying on cross-evaluator comparisons
- Cost: 1–2 hours

**EXP-B: Clean saturation loop ablation (1 vs 5 rounds)**
- Now that SYNTH_INSTRUCTION_COUNT is fixed, this is a clean comparison
- `MAX_SEARCH_ROUNDS=1` vs `MAX_SEARCH_ROUNDS=5` on T_D + T_E
- Confirm or deny: does 5-round search lift r1 vs 1-round?
- Cost: ~2 hours (one research cache warmup, then two evals)

**EXP-C: Annotate task wiggum audit**
- Run `/annotate` with `WIGGUM_MAX_ROUNDS=1`, capture `wiggum_eval_log`
- Inspect: what specific issues does wiggum identify on annotation output?
- If criteria mismatch: design an annotation-specific eval rubric or lower PASS_THRESHOLD for annotate tasks
- Cost: 1 run, 30 min

**EXP-D: Autoresearch session 4 — depth-targeted**
- Prime PROPOSE_PROMPT with depth (weight 0.30) as explicit target dimension
- Add "depth" to Unexplored Angles list; add "completeness" as secondary
- Resume with `python autoresearch.py --tasks T_D,T_E --proposer kimi-k2.5:cloud`
- Goal: beat 8.915 (current best) by improving depth dimension specifically
- Cost: 4–8 hours (autoresearch loop)

**EXP-E: Closed-book prior knowledge pass (roadmap Stage 1)**
- Implement: before `gather_research()`, call producer with task + "what do you already know / what gaps exist?"
- Gap list replaces or augments `plan_query()` output
- Measure r1 delta on T_D + T_E (3 runs each condition, compare means)
- This is the MagenticOne borrow — highest expected ROI from new harness feature
- Cost: 1–2 days implementation + eval

**EXP-F: Synthesis latency reduction**
- Traces show synthesize = 53% of wall time; mean 711s per run
- `num_predict=8192` was added (session 3), but mean synth time is still high
- Investigate: is the bottleneck eval_ms (generation) or prompt_ms (prefill)?
- From trace args: check `prompt_ms` vs `eval_ms` on `llm:synth` events
- If prefill-dominated: context compression before synthesis (reduce total_search_chars)
- Cost: analysis only (read existing traces)

**Priority order: EXP-B (clean ablation, unblocks baseline confidence) → EXP-C (quick annotate audit) → EXP-D (session 4, highest score leverage) → EXP-A (evaluator calibration) → EXP-E (closed-book pass)**

---

## Session 5 — Annotation Pipeline Overhaul + Fine-Tuning Initiation (2026-04-13)

### Root cause: `_clean_pdf_text` infinite loop

All annotation hangs traced to a single bug in `skills.py`. The `else` branch of `_clean_pdf_text` extended `cleaned` with short-run lines but never advanced `i` past the current non-short line. Any line with >2 characters caused an infinite loop. Every model tried — Qwen3-Coder, kimi-k2.5, pi-qwen-32b — appeared to hang; they were all waiting on stuck preprocessing. Fixed by advancing `i` in the else branch.

**Lesson:** Before suspecting model behavior, audit preprocessing. The bug predated all model testing in this session and masked every subsequent experiment.

---

### Annotation format: sentence-labeling → generative

The prior `/annotate` implementation labeled existing abstract sentences (`[Topic] We introduce...`). This broke on abstracts that don't contain explicit topic or motivation sentences — e.g., Mistral 7B's abstract never states a topic directly, so those sections simply didn't appear in the output.

Switched to fully generative format: model synthesizes 1-2 prose sentences per section from the full paper content, matching the reference Nanda Annotated Abstract framework. All 8 section headers are bold, on their own lines, with generated prose beneath.

**Changes:**
- `_ANNOTATE_SYSTEM` and `_ANNOTATE_PROMPT` rewritten for generative instruction
- `_ANNOTATE_LABELS` updated to match exact bold header format (`**Topic**`, etc.)
- `_is_valid_annotation()` now requires 6/8 sections present (was checking for bracketed labels)
- `_extract_sections()` added: extracts Abstract, Conclusion, Introduction, Results, Discussion in priority order within a 10k char budget
- `run_annotate_standalone()` updated: retry loop (3×), `/no_think` injected for Qwen3, `<think>` blocks stripped, `num_ctx=8192`

---

### Wiggum annotation eval: tightened threshold + rewritten rubric

- `PASS_THRESHOLD` raised from 8.0 to 9.0 for annotation path
- `EVAL_PROMPT_ANNOTATE` rewritten for generative format: `label_accuracy` dimension replaced with `section_accuracy`, score guide explicitly penalizes sections that merely restate abstract text rather than synthesizing
- `REVISE_PROMPT_ANNOTATE` rewritten to match
- `abbrev` dict updated: `section_accuracy → sec`

**Finding from pre-fix evaluation:** evaluator scored a known-bad annotation 9.3/10 and passed it. Root cause: the annotation had the right structure but section content was direct quote from abstract, not synthesis. The new rubric explicitly distinguishes "recitation" (scores 1-4) from "synthesis" (scores 7-10).

---

### Dashboard: UTC→local timestamps + SSE deduplication

**UTC timestamps:** `dashboard.py` was displaying UTC throughout — run cards, heatmap hour buckets, table columns. Added `fmt_ts()` Python helper using `datetime.astimezone()` for server-side conversion; updated JS `fmtTs` to use `new Date(iso)` with local time components.

**SSE duplicates:** Late-joining SSE clients received both the backlog replay (from `log_lines`) and queued items (from `log_queue`), producing duplicate log lines in run cards. Fixed by removing `log_queue` entirely and replacing with `threading.Event + per-client read index` pattern. Each client tracks its own position in `log_lines`; no message is ever delivered twice.

---

### Fine-tuning pipeline: `finetune_annotate.py`

Initiated a QLoRA fine-tuning experiment to train a dedicated Nanda annotation model.

**Training data:** 142 rows in `annotated-abstracts.csv` (human-curated Nanda annotations). 21 rows have non-arxiv filenames (CVPR PDFs, social media artifacts) and are skipped. 121 valid training examples built by fetching arxiv title + abstract via the arxiv API and joining with the CSV annotations.

**Dataset format:** instruction pairs — `(abstract → 8-section generative annotation)` — formatted as Qwen2.5-Instruct chat templates. 90/10 train/eval split: 108 train, 13 eval.

**Model:** `Qwen/Qwen2.5-7B-Instruct` with LoRA (r=16, alpha=32, target: q/k/v/o/gate/up/down projectors). No quantization — machine has 63.8GB dedicated VRAM (NVIDIA RTX 5000 Ada Generation), so full bf16 is used. 3 epochs, batch size 2, gradient accumulation 4, cosine LR schedule.

**Infrastructure issues encountered:**
- `bitsandbytes` on Windows caused silent CPU offload when used with `device_map="auto"` — model loaded but never reached GPU, hanging at 0% indefinitely
- `device_map="cuda:0"` also failed to place model on GPU correctly
- Root fix: explicit `.to("cuda")` after `from_pretrained()`, removed quantization entirely
- `torch_dtype` → `dtype` API change in newer transformers (then reverted; `torch_dtype` is still the correct param for `from_pretrained`)
- `max_seq_length` removed from both `SFTConfig` and `SFTTrainer` in trl ≥ 0.13; now set via `tokenizer.model_max_length`
- `warmup_ratio` deprecated in trl v5.2; switched to explicit `warmup_steps=4`
- Windows CP1252 encoding: `python -X utf8 finetune_annotate.py` required for trl's Jinja template loading

**TensorBoard:** `report_to=["tensorboard"]` enabled; `logging_steps=1` for step-level loss tracking. View at `http://localhost:6006` during training.

**Status:** training in progress as of 2026-04-13. 42 effective steps (batch_size=2), ~20-30 min estimated.

---

### Annotation corpus expansion: `run_annotations.py`

Rewrote `run_annotations.py` to parse arxiv markdown files and produce Nanda annotation CSVs.

Two markdown corpora identified:
- `arxiv_agentic_papers.md` — 300 papers (agentic / LLM / autonomous systems)
- `arxiv_agentic_harness_engineering_papers.md` — 300 papers (software engineering focus)

Parser extracts: arxiv_id (from abstract URL), title, abstract text, published date, pdf_url. Annotation runner calls `run_annotate_standalone()` directly per paper (no agent.py subprocess), parses 8-section output into CSV columns matching `annotated-abstracts.csv`, appends to output CSV with `--skip-existing` resume support.

Output files: `arxiv_agentic_papers_annotated.csv`, `arxiv_agentic_harness_engineering_papers_annotated.csv`.

**Status:** annotation loop running on both files (600 papers) as of 2026-04-13. These will serve as expanded training data for fine-tuning round 2 once the initial Qwen2.5-7B run completes.

---

### Fine-tuning dataset builder: `build_finetune_from_annotations.py`

New script that converts annotated CSVs into fine-tuning JSONL, merging all sources in one pass:

1. Seeds from existing `finetune_dataset.jsonl` (121 gold examples with arxiv-fetched abstracts)
2. Parses all `arxiv_*.md` markdown files to extract abstracts inline — no API calls needed
3. Reads all `arxiv_*_annotated.csv` files, joins on arxiv_id, deduplicates, validates (≥6 sections)
4. Outputs `finetune_dataset_v2.jsonl`

First run: 167 examples (121 gold + 46 from 47-row partial annotation run). Will grow to 700+ once full annotation run completes. Script is idempotent — re-run after each annotation batch to accumulate examples.

Training on v2 dataset: `python finetune_annotate.py --dataset finetune_dataset_v2.jsonl`

---

### Dashboard: live fine-tuning metrics

Added `DashboardCallback` (trl `TrainerCallback`) to `finetune_annotate.py`:
- Emits `{"type":"metric", step, epoch, loss, grad_norm, learning_rate, mean_token_accuracy, elapsed_s, eta_s}` per step to `finetune_metrics.jsonl`
- Also prints `[EVENT]<json>` to stdout — picked up by SSE stream when launched via `server.py`
- ETA computed from rolling average of last 10 step durations

Server: `GET /api/finetune/metrics` endpoint reads `finetune_metrics.jsonl` and returns JSON array.

Dashboard: new "Fine-tuning — live metrics" section polls every 8s; renders 6 KPI cards (status, loss, token accuracy, grad norm, elapsed, ETA) and 4 sparkline charts (loss, token accuracy, grad norm, learning rate schedule). No page reload required.

---

### /email standalone skill

Built `email_skill.py` — generates personalized `.eml` draft per speaker from a CSV of contacts + stated goal.

Pipeline per row: load slide markdown (pre-converted or fetch via MarkItDown) → generate subject (64 tokens) → generate body (512 tokens) → build `.eml` via `email.mime` with quoted-printable encoding (human-readable file) → save to output directory.

Handles: skip rows with no valid email address, log rows with multiple addresses and use first. `sender_company` and `platform_url` parameters injected into both subject and body prompts for brand-consistent outreach.

CSV tested: `geo-week-talks.csv` (160 rows, 65 with email addresses). Model: `llama3.2:3b` — appropriate for short-form writing, fast, resident in VRAM. Output: `email_drafts/` directory with individual `.eml` files + `manifest.json`.

---

### Session 5 insight: toward a self-improving research intelligence

A crystallising observation from this session's architecture discussions:

The system as built is not just a research harness — it is the scaffolding for a self-improving research intelligence. The compounding cycle:

```
Agent runs → preference data → fine-tune → smarter producer
     ↑                                            ↓
Memory retrieves                          Better annotations
prior observations                        Better curation taste
     ↑                                            ↓
TinyTroupe panel                         Higher quality training
filters weak papers                       data next round
     ↑                                            ↓
Wiggum scores                            Stronger evaluator signal
improve over time                        (reward model from reward.jsonl)
```

Each component feeds the next. Memory means nothing useful is forgotten. Persona curation means the system becomes more selective over time. Fine-tuned annotators produce better training signal for the next round. Wiggum reward models train on their own scoring history and become better judges.

**What makes this different from prompting loops:** model weights actually change (LoRA fine-tuning), memory persists across sessions, and the reward model improves alongside the producer. The loop tightens rather than degrading.

**The taste layer is the critical differentiator.** Most self-improvement loops optimize a scalar metric. TinyTroupe persona curation introduces *diverse* taste — a pragmatic engineer, an academic rigorist, a synthesis thinker, a contrarian. Research standards get encoded into the dataset composition itself, not just into the output format. The model learns *which papers are worth annotating carefully*, not just how to format 8 sections.

**The honest constraint:** the evaluator's blind spots compound. If wiggum has a systematic bias, the whole loop optimizes toward it. Rotating evaluators (Gemma 4 as second evaluator) and diverse persona panels break monoculture before it compounds. Diversity in judgment is a first-class architectural concern, not an afterthought.

**Roadmap implication:** vLLM (7e) closes the training loop continuously; TinyTroupe persona curation (planned, Stage 6 extension) operationalizes taste as a selection function; structured event protocol (7h) gives the critic agent the telemetry it needs to reason about *why* something worked rather than just *that* it did. These three together are what separate a self-improving system from a self-reinforcing one.

---

## Session 6 — nanda-annotator v2, /github skill, token tracking, dashboard fixes (2026-04-13/14)

### /github standalone skill

Built `github_skill.py` — LLM-assisted GitHub operations via the `gh` CLI substrate.

Supported operations: `push` (stage → LLM commit message → commit → push), `pr create/list/view/merge/review`, `issue create/list/view`, `repo view/clone`, `status`.

Key design decisions:
- Default model: `llama3.2:3b` via `GITHUB_MODEL` env var (falls back to `PRODUCER_MODEL`). Commit message generation with pi-qwen-32b took 620 seconds for a generic result; `llama3.2:3b` takes ~8 seconds and produces accurate messages.
- Commit prompt uses `--stat` summary + first 2000 chars of raw diff — the stat carries most signal; the diff excerpt handles detail on the most-changed file.
- All operations return `(text, tokens_in, tokens_out)` tuples so token counts reach the dashboard.
- `_path_optional = {"email", "github"}` added to `agent.py` — standalone skills exempt from `.md` output path requirement.

### Token tracking in standalone skills

Email and GitHub runs were not appearing in dashboard token stats because both skills call `ollama.chat()` directly, outside `RunTrace.log_usage()`. Fixed by:
- `email_skill.py`: `_ollama_chat()` returns `(text, in_tok, out_tok)`; accumulates `total_in`/`total_out` across all per-speaker calls; embeds `_tokens_in`/`_tokens_out` in result dicts.
- `github_skill.py`: all `_llm()` calls return `(text, in_tok, out_tok)`; `_dispatch()` propagates tuples up to `run_github_standalone()`.
- `agent.py`: both dispatch blocks write token totals into `trace.data["input_tokens"]`/`["output_tokens"]` before `trace.finish()`.

### nanda-annotator output cleanup

Three-layer post-processing in `run_annotate_standalone()` (`skills.py`):
1. **Preamble strip** — everything before `# Annotated Abstract` or `**Topic**` removed (catches "Sure, here is…" preamble).
2. **Broad impact truncation** — take at most 600 chars of content after the `**Broad impact**` header line, cut at the last sentence-ending punctuation (`./!/?`). Avoids dependence on blank lines or stop markers the model may not emit. Eliminates conversation loops, `--- EOF ---` fake boundaries, and `[truncated]` hallucinations.
3. **Modelfile stop tokens** — `<|im_end|>`, `<|endoftext|>`, `--- EOF ---`, `--- End` added as Ollama-level stop strings; `num_predict 1200` cap.

Root cause of repetition: model learned `--- EOF ---` as its "done" signal from training data, then continued generating a simulated conversation. The 600-char window cuts the loop at the paragraph level regardless of what the model emits.

### Dashboard: annotate detail rows missing

`log_wiggum()` was never called for annotate+wiggum runs. The annotate path in `agent.py` was doing `trace.data["wiggum"] = wiggum_result` (storing as nested dict) instead of `trace.log_wiggum(wiggum_result)`. Result: `wiggum_dims`, `wiggum_eval_log`, `wiggum_scores` all stayed as empty lists in `runs.jsonl`. Fixed with a one-line change.

### nanda-annotator v2 dataset and training

- Ran `run_annotations.py` on both arxiv markdown files (596 papers total) using `nanda-annotator` as annotator model.
- Result: 251 annotated from `arxiv_agentic_papers.md`, 299 from `arxiv_agentic_harness_engineering_papers.md`, 49 skipped (existing), 1 failed.
- `build_finetune_from_annotations.py` merged all sources: 121 gold + 597 agent-annotated = **718 examples** in `finetune_dataset_v2.jsonl`.
- Training: `python -X utf8 finetune_annotate.py --dataset finetune_dataset_v2.jsonl --epochs 3` — 1938 steps, 646 train / 72 eval examples.
- Added early stopping: `eval_strategy="epoch"`, `EarlyStoppingCallback`, `load_best_model_at_end=True` — stops if eval loss doesn't improve for N epochs (configurable via `--patience`).

**Self-distillation note:** v2 training data includes v1 nanda-annotator's own outputs. This is intentional — v1 provides stylistic consistency while the 121 human-curated gold examples anchor quality. Worth comparing v2 eval loss and wiggum scores against v1 to check whether the self-distillation loop is tightening or degrading.

### Agent dispatch refactor (Karpathy principle: explicit > implicit)

Refactored standalone skill dispatch in `agent.py` from a chain of `if/elif` blocks into inner handler functions + a dispatch table (`_STANDALONE` dict). Motivated by Karpathy's "no magic" guideline — the intent of each branch is now explicit and the table is easy to extend.

```python
def _handle_annotate(): ...
def _handle_email(): ...
def _handle_github(): ...
_STANDALONE = {"annotate": _handle_annotate, "email": _handle_email, "github": _handle_github}
for _skill in explicit_skills:
    if _skill in _STANDALONE:
        _STANDALONE[_skill]()
        return
```

### Paper corpus indexer (`index_papers.py`)

Built `index_papers.py` to bulk-load the annotated paper corpus into ChromaDB memory as background knowledge, so `get_context()` can surface relevant prior papers before web search fires.

- Parses arxiv markdown files → 598 title mappings (arxiv_id → title)
- Loads all `*_annotated.csv` files; gold CSV rows take precedence over agent rows
- Each paper stored with: `task_type="paper"`, `task="paper: {arxiv_id}"`, narrative = topic + motivation + contribution (≤600 chars), facts = ["Contribution: ...", "Evidence: ...", "Broad impact: ..."]
- Fixed timestamp `2026-01-01T00:00:00+00:00` so papers sort before run observations in retrieval
- Added `store_direct()` to `memory.py` — bulk import path bypassing LLM compression, idempotent by task key
- Result: **739 papers indexed**, memory now contains 861 total observations

`--dry-run` and `--stats` flags for inspection. Re-running is safe (idempotent).

### Failure pattern aggregator (`failure_patterns.py`)

Built `failure_patterns.py` to surface recurring wiggum issues across `runs.jsonl` without LLM or embeddings.

Pipeline: extract all issue strings from `wiggum_eval_log` → normalize + tokenize to keyword/bigram sets → greedy single-linkage clustering by Jaccard similarity (threshold 0.15) → rank by frequency → write `wiki/failure-patterns.md`.

Results: **645 issues extracted, 107 recurring clusters** found. Top failure patterns:
1. Missing implementation notes / concrete steps (56×)
2. Unclosed or malformed code fences (31×)
3. Shallow synthesis without cross-paper synthesis (24×)
4. Missing quantitative evidence (19×)
5. Overly broad conclusions (14×)

### SYNTH_INSTRUCTION updates

Two targeted fixes to `SYNTH_INSTRUCTION` (both regular and count variants in `agent.py`) based on top failure patterns:

1. **Implementation notes** — added explicit requirement: *"Each section MUST include concrete implementation notes — not just what was done but how: algorithms, hyperparameters, design decisions."*
2. **Code fences** — added: *"Every section MUST include a complete runnable code example with both opening and closing triple-backtick fences — never leave a code block unclosed."*

Also added a belt-and-suspenders fence repair in `clean_synthesis_output()`: counts triple-backtick markers; if odd (unclosed), appends a closing ` ``` ` before the output is returned. Catches cases where the model truncates mid-block.

### Dynamic keep_alive (`_estimate_keep_alive`)

`keep_alive=60` was arbitrary and blocked Ollama concurrency when models ran longer than the estimate. Replaced with a two-stage dynamic system in `agent.py`:

**Stage 1** (after skill parsing, before planning): estimate from explicit_skills heuristic
- Standalone `github`/`email`: 90s fixed (short LLM calls)
- Otherwise: base 300s + 150s if wiggum + 200s if panel skill + ×1.5 if task contains "deep"

**Stage 2** (after `make_plan()` + `merge_skills()`): refine from historical p90
- Read last 100 `runs.jsonl` entries, filter to matching `task_type`
- Compute p90 of wall-clock durations, add 20% buffer
- Fall back to Stage 1 heuristic if <5 matching runs

`OLLAMA_KEEP_ALIVE` env var overrides both stages at module load time (`_KEEP_ALIVE_OVERRIDE`). Ollama itself handles eviction; the estimate just sets the initial TTL so the model stays loaded through the full run without blocking indefinitely.

### Ollama concurrency: `OLLAMA_NUM_PARALLEL=4`

Root cause of concurrency blocking: `OLLAMA_NUM_PARALLEL` was unset (default 1 — single concurrent request). Set via `setx OLLAMA_NUM_PARALLEL 4` + Ollama restart via tray icon. Verified with `echo %OLLAMA_NUM_PARALLEL%`.

The dynamic keep_alive + `OLLAMA_NUM_PARALLEL=4` together address the blocking pattern: models stay loaded long enough to serve concurrent requests without re-loading between tasks.

---

## Session 7 — /review skill (2026-04-14)

### /review standalone skill

Built `review_skill.py` — pre-push diff review against a mechanical code quality rubric. Runs on `Qwen3-Coder:30b` (override via `REVIEW_MODEL` env var).

**Scope options** (parsed from task string):
- `staged` — `git diff --cached` (default; falls back to last commit if nothing staged)
- `unstaged` — `git diff`
- `last` — `git diff HEAD~1..HEAD`
- `all` — `git diff origin/main...HEAD`

**Rubric — four anti-patterns only:**
1. Dead code — symbol defined but never used (dict/list values are exempt — that's intentional indirection)
2. Bare `except` — empty body or `pass` that silently swallows errors
3. Backwards-compat shims — re-export aliases with `# deprecated` / `# TODO remove`
4. Unreachable branches — condition always True/False given surrounding code

Output format: one `WARN FILE:LINE — description` per finding, then `SUMMARY: N warnings`. Clean diffs get `SUMMARY: 0 warnings — looks good`.

**Model selection lesson:** `llama3.2:3b` and `phi4:14b` both hallucinated warnings on a clean diff — confusing string literals for symbol references and flagging dispatch table entries as "used once" abstractions. `Qwen3-Coder:30b` correctly returned 0 warnings on the same diff. Code review requires a model that actually understands code structure, not just instruction following.

Rubric iteration: started with 8 rules + INFO/WARN severity, progressively narrowed to 4 concrete anti-patterns with WARN only. The key insight was that small models follow mechanical checklists ("does this string literal appear as a dict value?") better than semantic judgements ("is this abstraction speculative?"). Wider rubrics = more hallucinated findings.

Wired into `agent.py` alongside `/github` and `/email` — dispatch table entry `_handle_review`, `_path_optional` set, keep_alive heuristic returns 90s (short bounded LLM call).

---

## Session 8 — curator.py, eval_suite T_ANN+T_MEM, autoresearch Session 4 (2026-04-14)

### Persona curator (`curator.py`)

Built `curator.py` — a 5-persona paper filter that gates what goes into the fine-tuning dataset. Each paper annotation is scored by five LLM personas; papers that don't earn collective approval are excluded from training.

**Personas:**
- Pragmatic Engineer — values actionable implementation insights
- Academic Rigorist — values methodological soundness and evidence quality
- Synthesis Thinker — values cross-paper connectivity and conceptual clarity
- Contrarian — looks for oversold claims and trivial contributions
- Newcomer — values accessibility and field-entry value

**Scoring:** each persona gives 1–5. Paper passes if mean ≥ 3.5 AND no single score < 2 (veto floor). Thresholds configurable via `--mean-threshold` / `--veto-floor`.

**Output:** `*_curated.csv` (filtered rows, same columns as input) + `curation_log.jsonl` (per-paper decisions with per-persona scores and reasons). Idempotent — already-scored papers are skipped. `--dry-run` scores without writing CSV. `--stats` shows pass/fail counts and veto breakdown by persona.

`build_finetune_from_annotations.py` updated to prefer `*_curated.csv` over `*_annotated.csv` when available — v3 dataset will automatically use curated papers if curation has been run.

**Role in the self-improvement cycle:** the taste layer. Without curation, self-distillation loops can reinforce mediocre papers alongside strong ones. The Contrarian persona is the critical differentiator — it specifically hunts for overclaiming and incremental contributions that would dilute the training signal.

### eval_suite: T_ANN and T_MEM

Added two new regression tests:

**T_ANN** — `/annotate` regression against `eval_suite_fixtures/ann_fixture.md` (ReAct paper abstract). Checks: all core Nanda sections present (Topic, Motivation, Contribution, Evidence/Broad impact), no conversation-loop artifacts (`--- EOF ---`, `[truncated]`), no placeholders, minimum length.

**T_MEM** — memory retrieval smoke test (runs inline, no agent.py call). Checks: 739 papers indexed, `get_context()` returns results for a domain query, paper observations surface in the formatted output. Catches memory corruption or index wipe between sessions.

New criterion helpers: `has_nanda_sections()`, `no_annotate_artifacts()`.

### autoresearch Session 4 + keep_alive hang fix

Updated `autoresearch_program.md` with what kills scores, unexplored angles for Session 4, and session history table. Session 4 running: `kimi-k2.5:cloud` proposer, tasks T_D + T_E, baseline 8.915.

**Keep_alive hang:** `run_eval()` was passing `OLLAMA_KEEP_ALIVE=-1` to the eval subprocess, keeping producer and evaluator models loaded indefinitely and stalling the proposer call next iteration. Fixed to `OLLAMA_KEEP_ALIVE=120` — models release ~2 minutes after eval completes.

Session 4 uncovered two hang modes. First: `OLLAMA_KEEP_ALIVE=-1` in the eval subprocess kept the producer and evaluator models loaded permanently, blocking the proposer from loading on the next iteration. Fixed by setting `OLLAMA_KEEP_ALIVE=120` in `autoresearch.py`'s eval env. Second: GPU VRAM fully consumed by concurrent v2 fine-tuning job — Ollama couldn't load `pi-qwen-32b` for eval at all. Root cause is GPU contention, not a code bug. Paused autoresearch until training completes.

---

## Session 9 — DPO dataset builder (2026-04-14)

### Signal audit

Inspected `runs.jsonl` (239 runs, 141 with wiggum, 45 with `final_content`) to understand what preference signal was available. Key findings:

- `wiggum_eval_log` carries `{round, score, dims, issues, feedback}` per round but **no synthesis text** — only the final content (`final_content`, truncated 16k) was stored
- 35 runs show improving wiggum scores across rounds (useful revision signal, but text unavailable historically)
- 3 cross-run pairs exist: same task, same producer, different final scores (delta 0.8–1.0)
- `wiggum_dims` available on recent runs (per-dimension scores: relevance, completeness, depth, specificity, structure)

### wiggum.py: capture synthesis text per round

Added `"content": content[:8_000]` to `round_record` in both the standard and annotate wiggum loops. Updated `logger.py` to propagate `content` into `wiggum_eval_log` entries. Going forward, each round in `wiggum_eval_log` carries the actual synthesis text at that revision step — enabling within-run chosen/rejected pairs from the best-scoring round vs round 1.

This is a zero-cost observability change: it adds ~8k chars per round to runs.jsonl but unlocks high-quality revision pairs that would otherwise require re-running historical tasks.

### build_dpo_dataset.py

Built `build_dpo_dataset.py` with two signal sources:

**Source 1 — cross_run** (available now): groups runs by normalized task (first 120 chars, /skill prefixes stripped), emits chosen/rejected pairs where both have `final_content`, same `producer_model`, and score delta ≥ `--min-delta`. 3 pairs in current corpus.

**Source 2 — wiggum_revision** (available for runs post 2026-04-14): within a single run, uses round 1 content as rejected and the best-scoring round's content as chosen. Includes `wiggum_feedback` from the evaluator — the signal that triggered the revision. 0 pairs currently (no runs yet with content-per-round).

**Output schema** (`hf_datasets/dpo.jsonl`):
```
prompt, chosen, rejected, chosen_score, rejected_score, score_delta,
source, task_type, producer_model, evaluator_model,
chosen_dims, rejected_dims, wiggum_feedback, timestamp
```

**Design notes:**
- Cross-run pairs filtered to same producer_model — avoids conflating model quality differences with output quality differences
- Revision pairs prefer round 1 as rejected (maximally divergent from final, captures the full improvement arc)
- `--min-delta` defaults to 0.5; set to 1.0+ for cleaner signal at the cost of fewer pairs
- Stats mode (`--stats`) is non-destructive — useful for checking yield before committing

**Growth trajectory:** corpus is currently thin for DPO. The revision path will grow automatically as wiggum runs accumulate. The cross-run path grows when the same task is retried (eval_suite, autoresearch reruns). After 10-20 autoresearch sessions on the same task set, cross-run pairs will become the dominant source.

---

## Session 10 — Dashboard fixes, batch annotation logging, arxiv_fetch, /lit-review (2026-04-14)

### Dashboard: stub run flood + wiggum backfill

Two issues found when inspecting the recent runs table:

**Wiggum backfill**: 10 annotate runs stored the raw wiggum trace as `trace.data["wiggum"]` instead of going through `trace.log_wiggum()`. These runs had `wiggum_rounds=0` and no `wiggum_eval_log` in `runs.jsonl` despite having real evaluation data in the raw dict. Wrote a one-time backfill that processed the raw `wiggum` dict and populated `wiggum_rounds`, `wiggum_scores`, `wiggum_dims`, and `wiggum_eval_log` for all 10 runs.

**Stub run filter**: 128 runs had `input_tokens=0`, `wiggum_rounds=0`, and no output — standalone skill calls (github status, review on empty diff) and autoresearch eval-suite sub-checks that wrote minimal trace data. These were flooding the recent runs table, pushing real research runs out of the 30-run window. Fixed with a `_is_substantive()` filter: only show runs with `input_tokens > 0` OR `wiggum_rounds > 0` OR `output_bytes > 0`. Window extended from 30 → 50.

### Batch annotation logging

`run_annotations.py` and `annotate_abstracts.py` both called LLM directly without creating a `RunTrace`, so batch annotation runs were completely invisible to `runs.jsonl` and the dashboard. Fixed:

- `skills.py`: added `_trace=None` to `run_annotate_standalone()` — calls `trace.log_usage(resp, stage="annotate")` per attempt when a trace is provided
- `run_annotations.py`: creates a `RunTrace` per paper with `task_type="annotate"`, passes it through, logs `output_bytes`/`output_lines`, calls `trace.finish(PASS/FAIL)`
- `annotate_abstracts.py`: same pattern — `annotate()` gets `_trace` param, main loop creates and finishes a trace per paper

Going forward every batch annotation run is visible in the dashboard as a substantive run with token counts, output size, and task type.

### arxiv_fetch.py

Built `arxiv_fetch.py` as a proper harness tool replacing the ad-hoc Jupyter notebook approach. Same column schema as existing `arxiv_agentic_papers.csv` so output feeds directly into `run_annotations.py` and `annotate_abstracts.py`.

Key additions over the notebook: `--after`/`--before` date filters, `--append` deduplication (won't re-add papers already in the CSV), `--field ti` for title-only search, `--sort` for newest-first ordering, `--stats` for inspecting existing CSVs. The main motivation was recovering from missing data from previous batch runs by being able to fetch papers after a specific date.

### semantic_scholar.py

The core insight: arXiv papers cite each other, and tracking those citations turns a flat list of annotations into a connected knowledge graph. Built `semantic_scholar.py` against the Semantic Scholar Graph API (free, no auth key required).

**What it produces for a corpus:**
- `hub_scores`: in-corpus citation count per paper — which papers are foundational (cited by many others in the corpus)
- `gap_candidates`: papers cited by corpus papers but not yet annotated, ranked by citation frequency — the corpus's known unknowns
- `adjacency`: within-corpus citation edges (who cites whom)
- `all_refs`: full reference list per paper including unresolved entries (books, proceedings without arXiv IDs)

SQLite cache with 30-day TTL means re-running on the same corpus is free. CLI: enrich CSV with hub_score/ref_count columns, print hub rankings and gap table, optionally fetch gap paper metadata and append to the corpus CSV.

**The compounding mechanism**: fetch 100 papers → run S2 enrichment → top 20 gap candidates are the papers the literature depends on most → `--fetch-gaps 20 --append` adds them to the corpus → annotate those too → repeat. Each iteration expands outward from the initial seed via citation chaining rather than keyword search.

### /lit-review skill

Built a 7-step literature review pipeline as a standalone skill:

```
fetch (arxiv_fetch.py)
  → S2 enrich (hub scores, gap candidates)
    → curate (curator.py — persona filter, hubs prioritized)
      → annotate+wiggum (run_annotate_standalone + wiggum_annotate_loop, checkpointed)
        → cluster (LLM groups into 3-5 thematic clusters)
          → synthesize (cluster summaries + cross-cluster overview + open questions)
            → render (Jinja2 template → .md)
```

**Design decisions:**

*Checkpointing*: each paper's annotation is saved to `.lit_review_cache/{arxiv_id}.json`. A crash at paper 15 of 30 resumes at paper 16 — no wasted annotation budget.

*Hub prioritization*: after curation, papers are sorted by `hub_score` descending so foundational papers get annotated first and with highest wiggum budget.

*Jinja templates*: separates data (annotations, scores, graph) from rendering. `lit_review_survey.j2` produces academic-style output with hub callouts, cluster narratives, citation links, and a gap table. `lit_review_gaps.j2` focuses on open questions and what to read next. Adding new output formats is a file drop — no code change.

*Synthesis as a separate LLM pass*: after all papers are annotated, a cluster-level synthesis pass writes a connecting paragraph per cluster (what the papers share, how they relate, what they disagree on). Then a cross-cluster pass writes the overview and surfaces open research questions. This is what makes the output a review rather than a dump of summaries.

**The data flywheel**: every `/lit-review` run generates wiggum annotation pairs (→ DPO training data via `build_dpo_dataset.py`), curated CSV (→ fine-tuning dataset), and synthesized review (→ memory observations). The skill compounds each time it runs.

**Registered as `/lit-review` in skills.py** with `hook="standalone"`. Agent dispatch in `_handle_lit_review` parses flags from the task string. Keep_alive set to -1 (indefinite) since the pipeline can run for minutes to hours depending on corpus size.

---

## Session 11 — 2026-04-14: /recall skill + MSYS2 path fix

### /recall — semantic memory search slash command

Added `/recall <query> [--n N] [--facts] [--scores]` as a standalone skill. Motivation: the agent's memory store (`memory.db`) has 862 observations accumulated across all runs — paper annotations, research tasks, eval results — but there was no way to query it directly from the command line. Previously the only access was automatic (injected into the synthesis context before each run via `get_context()`).

**Implementation:**
- `skills.py`: added `"recall"` to REGISTRY with `hook="standalone"`
- `memory.py`: added `search()` as a public alias for `_search()` — semantic + quality ranked retrieval via ChromaDB, FTS5 fallback
- `agent.py`: added `_handle_recall()` standalone handler; parses `--n`, `--facts`, `--scores` flags from task string; added `"recall"` to `_path_optional` set

**Output format:** ranked hit list with title, date, narrative, and optionally facts bullets and wiggum score. Confirmed working — `/recall trading multi-agent` surfaced *TradingAgents* and *When Agents Trade* papers that had been annotated in the batch corpus.

### MSYS2 path mangling fix — affects all /skill tokens from bash

**Root cause:** Git Bash (MSYS2) converts any argument starting with `/` to a Windows absolute path. `/recall trading multi-agent` → `C:/Program Files/Git/recall trading multi-agent`. This split across two tokens when Python splits the arg by spaces: `["C:/Program", "Files/Git/recall", "trading", ...]`.

This was a latent bug affecting every skill invoked from the bash terminal (vs the dashboard server which passes tasks via `AGENT_TASK` env var, bypassing shell expansion).

**Fix in `parse_skills()`:**
- Added a second branch: if a token contains `/` or `\` and its basename (last path segment) is a registered skill name, treat it as a mangled skill token and strip it
- Also pops the preceding `C:/...` drive fragment from the clean list if present

**Diagnosis method:** `python -c "import sys; print(sys.argv)"` revealed the conversion in action.

**Side note:** `-X utf8` Python flag (UTF-8 mode) eliminates the cp1252 `UnicodeEncodeError` on the `→` character in logger.py's `trace.finish()` print — should be added to any bash invocation wrapper.

---

## Session 12 — 2026-04-15: training interruption + checkpointing fix

### OS update killed v2 fine-tune mid-run

The v2 training run (`finetune_dataset_v2.jsonl`, 3 epochs, 1938 steps) was stopped at **step 1237 (epoch 1.9149, 63.8% complete)** by a Windows OS update reboot. ~20.4h of compute elapsed; ~15.2h remaining at time of interruption.

**Root cause of total loss:** `save_strategy="epoch"` only writes checkpoints at epoch boundaries (steps 646, 1292, 1938). The run was 55 steps short of completing epoch 2. `finetune_output/checkpoints/` contained no recoverable checkpoint from this run — likely the epoch 1 checkpoint was either flushed incomplete by the sudden reboot, or cleaned up as epoch 2 began writing.

**`finetune_metrics.jsonl`** preserved the full loss/accuracy history (1237 entries). Loss was trending well (~0.56 on last step, mean_token_accuracy ~0.84).

### Fix: step-based checkpointing + `--resume`

Changed `finetune_annotate.py` to save checkpoints every N steps rather than at epoch end only:

- `save_strategy="steps"`, `save_steps=100` (default) — checkpoint every ~15 min at current step rate, giving 19 recovery points across a 1938-step run instead of 2
- `save_total_limit=3` — keeps only the 3 most recent checkpoints to bound disk usage (~8GB per LoRA checkpoint)
- Removed `load_best_model_at_end=True` — requires `save_strategy` and `eval_strategy` to match; since eval remains epoch-based this would error
- Added `--resume` flag — auto-detects the latest `checkpoint-*` in `finetune_output/checkpoints/` and passes it to `trainer.train(resume_from_checkpoint=...)`; metrics file is preserved (not wiped) on resume
- Added `--save-steps N` CLI arg to tune interval
- `METRICS_OUT` is only cleared on fresh (non-resume) runs

**Usage going forward:**
```bash
# Fresh run
python -X utf8 finetune_annotate.py --dataset finetune_dataset_v2.jsonl

# Resume after interruption
python -X utf8 finetune_annotate.py --dataset finetune_dataset_v2.jsonl --resume

# Coarser checkpoints (every 200 steps, ~30 min)
python -X utf8 finetune_annotate.py --dataset finetune_dataset_v2.jsonl --save-steps 200
```

---

## Session 13 — 2026-04-15: /email JSON output, per-draft traces, dashboard fixes, v2 finetune restart

### /email: .eml → JSON output

Switched `/email` output from `.eml` files to per-contact `.json` files. `.eml` couldn't be opened by the target email app and was harder to consume downstream. Each draft now writes `{name}.json` with structured fields: `name`, `affiliation`, `to_email`, `sender_name`, `sender_email`, `subject`, `body`, `generated_at` (UTC ISO 8601). `manifest.json` (array of all drafts) unchanged. Removed `_build_eml()` and the `email.mime`/`quopri` imports it required.

### Per-draft trace logging

Each email draft now emits its own `runs.jsonl` entry (`task_type="email_draft"`) so every contact gets a full dashboard row with reasoning details. Fields logged: recipient name/affiliation/email, subject, full body, subject prompt, body prompt (as `tool_calls`), token counts, duration. Batch email runs continue logging their aggregate entry (`task_type="email"`) alongside.

### Dashboard: email run rendering

- `email_draft` rows show `Email draft: {Name} <email>` with an expanded detail panel: recipient header, subject (green), full body block, and both prompts rendered as monospace blocks
- `email` batch rows show `Email batch: {csv} → {dir} ({n} drafts)` instead of the MSYS2-mangled task string
- `dashboard.py` passes `email_*` fields through to `recent_runs` for rendering

### .env + SENDER_NAME/SENDER_EMAIL

Created `.env` in project root (gitignored). Added `.env` loader to `agent.py` startup (`os.environ.setdefault` so shell vars always win). `SENDER_NAME=Nick McCarty` and `SENDER_EMAIL=nick@upskilled.consulting` now populate email JSON output automatically.

### v2 finetune: EarlyStoppingCallback removed, run restarted

Previous v2 run died at step 1237 (OS update). Restarting with fixed config:
- `EarlyStoppingCallback` removed — it requires `load_best_model_at_end=True` which conflicts with `save_strategy="steps"`. Attempting to use it raised `AssertionError: EarlyStoppingCallback requires metric_for_best_model`.
- `--patience` flag kept in CLI but documented as unused
- Run started: `python -X utf8 finetune_annotate.py --skip-fetch --dataset finetune_dataset_v2.jsonl`
- Checkpoints every 100 steps (~15 min), `save_total_limit=3`

---

## Session 14 — 2026-04-15: token accounting fixes + vLLM integration + WSL2 setup

### Token accounting fixes

Two bugs fixed in the token/tok-s pipeline:

**1. Planner tokens not counted.** `planner.py` called `ollama.chat()` but never returned the response for logging — typically 5-10 LLM calls per run were completely absent from `tokens_by_stage`. Fixed: `make_plan()` return type changed to `tuple[Plan, object]`. `agent.py` unpacks the response and calls `trace.log_usage(_planner_resp, stage="planner")`.

**2. tok/s wrong denominator.** Dashboard was dividing total tokens by `total_ms`, which includes model load time (cold start). Fixed: `logger.py` now accumulates `eval_ms` (generation only) and `prompt_ms` (prompt-eval only) per stage. Dashboard uses `eval_ms` for output tok/s and `prompt_ms` for input tok/s, with `or total_ms` fallback for older runs. Cold-start inflation no longer deflates displayed tok/s.

### vLLM integration

**Problem:** Ollama serializes all `ollama.chat()` calls per model — `ThreadPoolExecutor(max_workers=4)` in the orchestrator gives process concurrency, but Ollama collapses it to a serial LLM queue. Three out of four parallel subtasks block waiting.

**Solution:** `inference.py` — unified backend shim that routes all calls to either Ollama (default) or vLLM based on `INFERENCE_BACKEND` env var. Drop-in for the `_OllamaShim` pattern already in `agent.py`, `wiggum.py`, `autoresearch.py`:

```python
from inference import OllamaLike
ollama = OllamaLike(keep_alive=_KEEP_ALIVE)   # keep_alive silently dropped for vLLM
```

`_OllamaResponse` wraps OpenAI ChatCompletion to expose the same attribute interface (`prompt_eval_count`, `eval_count`, `total_duration`, `eval_duration`, `prompt_eval_duration`, `message.thinking`) that `logger._extract_usage()` expects — no changes needed downstream.

`VLLM_MODEL_MAP` env var (JSON dict) overrides the built-in Ollama-tag → HF-ID map at runtime, so the same `.env` works on both 16GB (one model) and 63.8GB (separate producer/evaluator) hardware.

### WSL2 Ubuntu setup

vLLM does not support native Windows pip installs (platform check + MAX_PATH build failure). WSL2 Ubuntu 24.04 is the correct path.

Setup (from scratch on 2026-04-15):
```bash
# Install Miniconda in WSL2
bash Miniconda3-latest-Linux-x86_64.sh -b -p ~/miniconda3
~/miniconda3/bin/conda init bash && exec bash
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

conda create -n vllm python=3.12 -y && conda activate vllm
pip install torch==2.6.0+cu124 --index-url https://download.pytorch.org/whl/cu124
pip install vllm==0.7.3
pip install "transformers==4.49.0"   # 4.50+ removed all_special_tokens_extended from Qwen2Tokenizer

export HF_HOME=/mnt/c/Users/nicho/.cache/huggingface
vllm serve Qwen/Qwen2.5-14B-Instruct-AWQ \
  --dtype half --quantization awq \
  --max-model-len 16384 \
  --enable-prefix-caching \
  --gpu-memory-utilization 0.85
```

Model loads in ~15min on first run (downloads ~10GB), ~2min thereafter from cache. 9.4GB VRAM loaded, 9.7GB free for KV cache at `max-model-len 16384`.

**Key gotcha:** `transformers==5.5.4` (installed by vLLM 0.7.3) removed `all_special_tokens_extended` from `Qwen2Tokenizer`, crashing the tokenizer init. Pin to `transformers==4.49.0`.

### End-to-end validation

`test_harness_vllm.bat` passed:
- Inference shim: model map correct, live call returned `'vllm is working'`, all usage fields populated
- Full agent run: 376.6s, in=7013 out=1063 tok — planner, search, novelty, markitdown, security, synthesis, write, memory all worked via vLLM backend
- `runs.jsonl` entry logged correctly; trace written

### Files added this session

| File | Purpose |
|------|---------|
| `inference.py` | Unified Ollama/vLLM backend shim — `OllamaLike`, `_OllamaResponse`, `_MODEL_MAP` |
| `requirements-vllm.txt` | Pinned vLLM dep tree for WSL2 isolated env |
| `test_inference_shim.py` | Unit test: model map resolution, live call, usage field extraction |
| `test_harness_vllm.bat` | End-to-end harness test: shim test + agent run + output check |
| `test_vllm.sh` | WSL2 smoke test: `/health` + `/v1/chat/completions` curl |
