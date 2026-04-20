---
title: Agent Pipeline and Architecture
updated: 2026-04-21
tags: [pipeline, architecture, introspect]
introspect: true
---

# Agent Pipeline and Architecture

## What I Produce

I take a natural-language task string and produce a high-quality Markdown document — research synthesis, literature review, annotated abstract, code review, email drafts, or knowledge graph — saved to a path specified in the task. Outputs are not single-shot model completions: every output is planned, researched, synthesized, evaluated, and revised.

## Single-Focus Pipeline

```
parse_skills()              strip /skill tokens; identify explicit activations
  → auto_activate()         trigger skills by task keywords or plan complexity signals
    → memory.get_context()  retrieve semantically relevant past observations (ChromaDB)
      → make_plan()         prior knowledge pass → plan queries, task type, count constraint
        → gather_research() saturation loop: search → novelty gate → compress
          → synthesize()    producer generates Markdown from research + context
            → count check   Python trim (over-count) or LLM retry (under-count)
              → write()     save output to disk; register in artifacts.jsonl
                → wiggum()  evaluate → revise → verify loop (up to 3 rounds)
                  → panel() 3-persona parallel eval (if complexity=high or explicit)
                    → compress_and_store()  compress run into ChromaDB observation
```

## Prior Knowledge Pass (planner.py)

Before any web search, the planner asks the producer: "What do you already know? What specific gaps need lookup?" Known facts are injected into the synthesis context as a verified block. Identified gaps replace generic topic queries in `plan_query()`, so searches target unknowns rather than well-covered ground.

## Research Loop (gather_research)

Saturation loop — up to `MAX_SEARCH_ROUNDS` (5) rounds:
- Round 1: query derived from task + plan
- Round 2+: gap-targeted queries from the prior knowledge pass
- After round 2: each new result is novelty-scored (0–10) against accumulated knowledge state
- **ε-greedy gate** (`NOVELTY_EPSILON=0.15`): 15% of sub-threshold rounds are passed anyway to prevent search utilization collapse
- Quality floor: 1800 chars minimum; sparse results trigger a fallback search
- Top-N result URLs fetched in full via MarkItDown for richer context
- All results scanned for prompt injection before synthesis

**Skip conditions:** Web search is skipped when:
- Task contains a URL (fetched directly)
- `/introspect` or `/contextualize` is active
- `RESEARCH_CACHE=1` and a cache hit exists (autoresearch mode)

## Count Check (agent.py)

For enumerated tasks ("top N", "N most/common/best"):
1. Python regex counts `##` H2 sections in the output (excludes structural headers)
2. **Over-count**: trim at the `(N+1)`th section boundary — no LLM call, instant
3. **Under-count**: retry `synthesize_with_count()` with explicit count constraint in prompt
4. Post-retry: one more Python trim attempt before proceeding anyway

## Evaluation Loop (wiggum.py)

Each round:
1. Evaluate against task: relevance (0.20), completeness (0.25), depth (0.30), specificity (0.15), structure (0.10)
2. Score ≥ 9.0 → PASS and stop
3. Score < 9.0 → produce revised draft using evaluator feedback
4. **Cycling detection**: identical score+dims across consecutive rounds → early exit, restore best round
5. **Best-round restoration**: always returns the highest-scoring round's content, even on FAIL

Task-type criteria:
- `enumerated` — exact item count; fails if count wrong
- `best_practices` — coverage across dimensions; actionability required
- `research` — synthesis over listing; explain why, not just what

## Compound Tasks (orchestrator.py)

Multi-part tasks: decompose → run each subtask through full `agent.py` pipeline → assemble into final document. Subtask outputs are passed as context to the assembly synthesis step.

## Supervisor (supervisor.py)

Monitors run convergence across recent history. Four signals:
- **Wiggum score variance** — low variance = converged or stuck
- **Output size CV** — coefficient of variation; high = unstable output length
- **Search utilization** — fraction of rounds that add novel content
- **Content similarity** — cosine distance between consecutive outputs

Threshold warnings trigger intervention recommendations (increase ε, force replan, adjust MAX_SEARCH_ROUNDS).

## Data Flow Schema (schema.py)

Every run is associated with a Project > Session > Run > Artifact hierarchy. All JSONL files are append-only and gitignored.

| File | Event types | Written by | When |
|------|-------------|------------|------|
| `projects.jsonl` | `project_create`, `project_update` | schema.py CLI | On project creation |
| `sessions.jsonl` | `session_start`, `session_end` | server.py / agent.py | Session open/close |
| `plans.jsonl` | `OrchestratorPlan` records | agent.py, orchestrator.py | Before execution, after planning |
| `runs.jsonl` | Full run trace per task | logger.py `finish()` | End of every run |
| `artifacts.jsonl` | `artifact_create` | logger.py `log_artifact()` | On every file write |
| `messages.jsonl` | One record per LLM turn | logger.py `log_message()` | Per model call |

### plans.jsonl — pre-execution plan record

Written **before** subtask execution begins so plan intent is queryable even on crash. Fields: `plan_id`, `run_id`, `session_id`, `project_id`, `parent_run_id` (set when this plan is itself a subtask), `task`, `plan_type` (`agent` | `orchestrator`), `task_type`, `complexity`, `subtasks`, `known_facts`, `knowledge_gaps`, `search_queries`.

### runs.jsonl — per-run trace

Fields include:
- `parent_run_id` — links subtask runs to their orchestrator parent run
- `synth_cot` — list of thinking-text strings, one per `synthesize()` call
- `planner_cot` — list of thinking-text strings from `make_plan()` calls
- `wiggum_eval_log` — per-round `{round, score, dims, issues, feedback, thinking}` (thinking populated when evaluator model emits CoT)
- `tokens_by_stage` — `{input, output, thinking_chars, calls, total_ms}` per pipeline stage

### Run lineage

Orchestrator runs set `HARNESS_PARENT_RUN_ID` in subtask subprocess environments so each subtask `runs.jsonl` record carries `parent_run_id`. The orchestrator's own plan record in `plans.jsonl` links via `run_id`.

IDs use the format `20260418T100000Z-a1b2c3d4e5f6` (compact UTC ISO + uuid4 hex[:12]) — lexicographic sort equals chronological sort.

## Memory System

After each run, a compressed observation is stored in ChromaDB:
- **Title:** short description of what was produced
- **Narrative:** one-paragraph summary
- **Facts:** extracted key facts
- **Scores:** wiggum scores per round
- **Metadata:** task type, output path, token counts, timestamp

On subsequent runs, semantically similar past observations are retrieved and injected into the synthesis context — giving the agent a persistent, growing understanding of the problem space.

## Tracing

Every run writes a Perfetto-compatible Chrome Trace JSON to `traces/<run_id>_<slug>.json`. Load at `ui.perfetto.dev` to visualize stage latencies, model calls, and parallelism.

## Key Environment Variables

| Variable | Effect |
|----------|--------|
| `INFERENCE_BACKEND` | `vllm` routes all model calls to vLLM OpenAI-compatible API |
| `VLLM_BASE_URL` | vLLM server URL (default: `http://localhost:8000/v1`) |
| `HARNESS_PRODUCER_MODEL` | Override the producer model at runtime |
| `WIGGUM_MAX_ROUNDS` | Cap wiggum revision rounds (default: 3) |
| `WIGGUM_PANEL` | `1` enables the 3-persona panel inside wiggum |
| `RESEARCH_CACHE` | `1` enables SQLite search result cache (autoresearch mode) |
| `NOVELTY_EPSILON` | ε-greedy pass-through rate for sub-threshold search rounds (default: 0.15) |
| `OLLAMA_KEEP_ALIVE` | How long Ollama keeps models hot (e.g. `10m`, `-1` = always) |
| `HARNESS_PROJECT_ID` | Active project ID — set via `python schema.py set-project <id>` |
| `LLAMA_OCR_BASE_URL` | llama-server URL for dedicated OCR model (leave blank to skip) |
| `S2_API_KEY` | Semantic Scholar API key (improves rate limits for lit-review) |

<!-- sync-wiki:start -->
## Implementation Reference

*Auto-generated by `/sync-wiki` on 2026-04-20. Do not edit — re-run `/sync-wiki` to update.*

### Models by Stage

| Stage | Model | Override Env Var |
|-------|-------|------------------|
| Producer (synthesis) | `pi-qwen-32b` | `HARNESS_PRODUCER_MODEL` |
| Wiggum producer (revision) | `pi-qwen-32b` | `WIGGUM_PRODUCER_MODEL` |
| Wiggum evaluator | `Qwen3-Coder:30b` | `WIGGUM_EVALUATOR_MODEL` |
| Planner | `glm4:9b` | — |
| Orchestrator assembly | `pi-qwen` | — |

### Key Constants

| Constant | Value | File | Effect |
|----------|-------|------|--------|
| `MAX_SEARCH_ROUNDS` | 5 | agent.py | Hard cap on research iterations |
| `NOVELTY_THRESHOLD` | 3 | agent.py | Stop if new results score below this (0–10) |
| `NOVELTY_EPSILON` | 0.15 | agent.py | Pass-through rate for sub-threshold rounds |
| `PASS_THRESHOLD` | 9.0 | wiggum.py | Score required to exit wiggum loop |
| `MAX_ROUNDS` | 3 | wiggum.py | Max wiggum revision rounds |
| `MAX_CONTEXT_OBSERVATIONS` | 4 | memory.py | Observations injected per run |
| `SEMANTIC_CANDIDATES` | 12 | memory.py | Over-fetch count before re-ranking |
| `SUBTASK_MAX_WORKERS` | 4 | orchestrator.py | Parallel subtask threads |
| `SUBTASK_MAX_RETRIES` | 1 | orchestrator.py | Retries per failed subtask |

### Wiggum Evaluation Weights

Composite score formula: `0.20×relevance + 0.25×completeness + 0.30×depth + 0.15×specificity + 0.10×structure`

| Dimension | Weight | What it measures |
|-----------|--------|------------------|
| `depth` | 0.30 | Does each item have a concrete example or implementation note specific enough to |
| `completeness` | 0.25 | Are all required items or practices present, with nothing important missing? |
| `relevance` | 0.20 | Does the output address the correct topic and complete the task as specified? |
| `specificity` | 0.15 | Are claims precise and actionable, or vague and generic? |
| `structure` | 0.10 | Is the document clearly organized and readable? |

### Memory Retrieval Ranking

`rank  = 0.7 × semantic_similarity + 0.3 × quality_score`

- Observations scoring below `7.0` are half-weighted in quality component
- Results deduplicated by title — only the highest-ranked observation per unique title is kept
- `SEMANTIC_CANDIDATES = 12` fetched from ChromaDB, re-ranked, top `4` injected

### Synthesis Instruction (SYNTH_INSTRUCTION)

> Output ONLY the markdown starting with #. Structure each section with 'What', 'Why', 'How' subsections using numbered steps and inline code blocks. Write at least 150 words per subsection with concrete implementation details, ensuring every code snippet is complete, executable with specific tool versions, and includes error handling. Every section MUST include a complete runnable code example with both opening and closing triple-backtick fences — never leave a code block unclosed. Include edge case notes, trade-offs, and library recommendations. For each strategy, state when NOT to use it, identify input boundaries, and specify exact numerical values for all configuration parameters with workload-based justification.

### Model Map (Ollama → vLLM)

Used when `INFERENCE_BACKEND=vllm`. Built-in defaults (overridden by `VLLM_MODEL_MAP` env var):

| Ollama tag | vLLM / HF model ID |
|------------|--------------------|
| `pi-qwen3.6` | `pi-qwen3.6` |
| `qwen3.6:35b-a3b` | `pi-qwen3.6` |
| `pi-qwen-32b` | `Qwen/Qwen2.5-32B-Instruct` |
| `pi-qwen` | `Qwen/Qwen2.5-7B-Instruct` |
| `qwen2.5:32b-instruct-q4_K_M` | `Qwen/Qwen2.5-32B-Instruct` |
| `qwen2.5:7b-instruct` | `Qwen/Qwen2.5-7B-Instruct` |
| `Qwen3-Coder:30b` | `Qwen/QwQ-32B` |
| `gemma4:latest` | `google/gemma-4-9b-it` |
| `gemma4:26b` | `google/gemma-4-26b-it` |
| `glm4:9b` | `THUDM/glm-4-9b-chat` |
| `llama3.2-vision` | `meta-llama/Llama-3.2-11B-Vision-Instruct` |
| `llama3.2:3b` | `meta-llama/Llama-3.2-3B-Instruct` |
| `mistral-small3.1:24b` | `mistralai/Mistral-Small-3.1-24B-Instruct-2503` |
| `phi4:14b` | `microsoft/phi-4` |
| `nomic-embed-text` | `nomic-ai/nomic-embed-text-v1.5` |

<!-- sync-wiki:end -->

<!-- sync-wiki-gaps:start -->
## Gap-Targeted Extractions

*Auto-generated by wiggum gap analysis on 2026-04-20. Re-generated each FAIL cycle.*

### Planning prompts (planner.py)

**`PRIOR_KNOWLEDGE_PROMPT`** — Prior knowledge pass — asks model what it already knows before any search

```python
You are a research assistant assessing your existing knowledge before running web searches.

Task: {task}

Without searching the web, answer honestly:
1. What specific facts are you CONFIDENT about regarding this topic?
2. What specific aspects would you NEED to look up to answer this authoritatively?

Focus on gaps that a web search would actually resolve — not vague uncertainties.

Respond with ONLY valid JSON — no explanation, no markdown fences:
{{
  "known_facts": ["specific fact 1", "specific fact 2"],
  "gaps": ["specific gap requiring lookup 1", "specific gap requiring lookup 2"]
}}

Rules:
- known_facts: 2-5 concrete, specific facts you are confident about
- gaps: 2-4 specific aspects that need current/authoritative sources to answer well
- Both lists should be concrete enough that they could inform a search query
```

**`PLAN_PROMPT`** — Main planning prompt — produces task_type, complexity, queries

```python
You are a task planner for an AI research agent.

Task: {task}
{memory_block}{knowledge_block}
Produce a structured execution plan. Respond with ONLY valid JSON — no explanation, no markdown fences:

{{
  "task_type": "enumerated|best_practices|research",
  "complexity": "low|medium|high",
  "expected_sections": <integer or null>,
  "search_queries": ["query1", "query2"],
  "prior_work_summary": "<one sentence about relevant prior work, or empty string>",
  "notes": "<one actionable sentence for the producer>",
  "subtasks": []
}}

Rules:
- task_type: "enumerated" if task says "top N" or "N most/common/key/best"; "best_practices" if asking for practices/strategies/guidelines; "research" otherwise
- complexity: "low" for simple factual lookups; "medium" for standard research; "high" for tasks requiring synthesis across 2+ distinct domains
- expected_sections: the integer N from "top N" / "N most", null if not specified
… (4 more lines)
```

### Evaluation prompt (wiggum.py)

**`EVAL_PROMPT`** — Full wiggum evaluation prompt — defines scoring dimensions and format

```python
(could not extract EVAL_PROMPT)
```

### Synthesis prompt construction (agent.py)

**`synthesize`** — synthesize() — builds prompt from task + research + contexts, calls producer

```python
def synthesize(task: str, research_context: str, vision_context: str = "", file_context: str = "", code_context: str = "", memory_context: str = "", skill_context: str = "", producer_model: str = MODEL, trace=None) -> str:
    """Ask the model to synthesize research (and optional contexts) into a markdown document."""
    vision_block = f"\nImage analysis:\n{vision_context}\n" if vision_context else ""
    file_block = f"\nFile contents:\n{file_context}\n" if file_context else ""
    code_block = f"\nCode execution results:\n{code_context}\n" if code_context else ""
    memory_block = f"\n{memory_context}\n" if memory_context else ""
    skill_block  = f"\nAdditional requirements:\n{skill_context}\n" if skill_context else ""
    prompt = (
        f"Task: {task}\n\n"
        f"Research findings:\n{research_context}\n"
        f"{vision_block}{file_block}{code_block}{memory_block}{skill_block}\n"
        f"{SYNTH_INSTRUCTION}"
    )
    response = ollama.chat(
        model=producer_model,
        messages=[{"role": "user", "content": prompt}],
        options=_synth_options(producer_model),
    )
    if trace is not None:
        trace.log_usage(response, stage="synth")
        trace.log_synth_cot(getattr(response.message, "thinking", "") or "")
    return response["message"].get("content", "")

```

### Novelty scoring (memory.py)

**`assess_novelty`** — assess_novelty() — scores new search results 0-10 against accumulated knowledge

```python
def assess_novelty(new_results: list[dict], knowledge_state: str) -> int:
    """
    Score 0–10 how much new_results adds beyond knowledge_state.
    10 = entirely new information, 0 = completely redundant.

    Uses ChromaDB ephemeral collection + sentence-transformers cosine similarity.
    Falls back to word-overlap heuristic if ChromaDB unavailable.
    """
    if not knowledge_state or not new_results:
        return 10

    try:
        import chromadb
        ef = _get_chroma_ef()
        client = chromadb.EphemeralClient()
        col = client.get_or_create_collection(
            name="novelty_session",
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )
    … (36 more lines)
```

<!-- sync-wiki-gaps:end -->
