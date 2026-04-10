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
