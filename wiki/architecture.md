---
title: Agent Architecture
updated: 2026-04-10
sources: [agent.py, logger.py, planner.py, orchestrator.py, memory.py, wiggum.py, skills.py, chunker.py, panel.py, search_cache.py]
tags: [architecture, pipeline, agent]
---

# Agent Architecture

## Pipeline stages

```
task string
 └─ parse_skills()        skills.py   — strip /skill tokens; collect explicit activations
 └─ memory.get_context()  memory.py   — ChromaDB semantic retrieval of relevant past obs
 └─ make_plan()           planner.py  — classify task_type, complexity, generate queries
 └─ auto_activate()       skills.py   — trigger skills by keywords / plan.complexity
 └─ gather_research()     agent.py    — research cache check (RESEARCH_CACHE=1); else:
     └─ web_search_raw()             — DDGS via search_cache (24 h SQLite TTL)
     └─ compress_knowledge()         — rolling LLM knowledge compression
     └─ read_file_context()          — MarkItDown conversion + chunker for large files
     └─ enrich_with_page_content()   — URL enrichment gated on overlap with knowledge_state
 └─ synthesize()          agent.py    — producer model + skill prompt injections
 └─ wiggum_loop()         wiggum.py   — evaluate → revise → verify (up to 3 rounds)
     └─ run_panel()        panel.py   — 3-persona parallel eval (post_wiggum skills)
 └─ run_post_synthesis()  skills.py   — kg graph, etc.
 └─ compress_and_store()  memory.py   — glm4:9b compresses run into persistent memory
```

## Key components

| File | Role |
|------|------|
| `agent.py` | Main entry point; orchestrates all stages |
| `planner.py` | LLM-based task planner; returns `Plan` dataclass |
| `wiggum.py` | Evaluator/reviser loop; scores on 5 dimensions |
| `panel.py` | 3-persona parallel evaluation (Domain Practitioner, Critical Reviewer, Informed Newcomer) |
| `skills.py` | Skill registry; parse/auto-activate/inject at pipeline hooks |
| `chunker.py` | Large-doc context extraction with provenance metadata |
| `annotate_abstracts.py` | Batch Nanda 8-move annotated abstract generator |
| `logger.py` | Structured run logging to `runs.jsonl`; Chrome Trace Events to `traces/` |
| `memory.py` | ChromaDB semantic + SQLite full-text memory |
| `orchestrator.py` | Multi-step task orchestration |
| `security.py` | Prompt injection detection and stripping |
| `vision.py` | Image reading via llama3.2-vision |
| `eval_suite.py` | Batch eval runner; computes composite score |
| `autoresearch.py` | Autonomous synthesis instruction improvement loop |
| `search_cache.py` | SQLite TTL cache: DDGS results (`search_cache` table) + full research contexts (`research_cache` table) |

## Models

| Role | Model | Notes |
|------|-------|-------|
| Producer (default) | `pi-qwen-32b` (Qwen2.5-32B Q4_K_M) | Custom Modelfile; ~20GB |
| Producer (fallback) | `pi-qwen` (qwen2.5:7b) | Faster, lower quality |
| Evaluator | `Qwen3-Coder:30b` | Must differ from producer; drives revision loop |
| Planner / Compressor | `glm4:9b` | Fast; also used as `COMPRESS_MODEL` default |
| Embeddings | `all-MiniLM-L6-v2` | sentence-transformers; memory retrieval + chunker |
| Vision | `llama3.2-vision` | Image-to-text preprocessing only |

`COMPRESS_MODEL` env var overrides the model used for `compress_knowledge()` and
`plan_query()` — set to a lighter model to save VRAM during research.

## Skills system

Skills extend the pipeline at four hook points:

| Hook | When | Example skills |
|------|------|---------------|
| `pre_research` | Before `gather_research()` | `deep` — forces MAX_SEARCH_ROUNDS, disables novelty gate |
| `pre_synthesis` | Injected into synthesis prompt | `annotate`, `cite` |
| `post_synthesis` | After output written | `kg` — generates D3.js knowledge graph |
| `post_wiggum` | After verification loop | `panel` — runs 3-persona evaluation |

**Invocation:**
- Explicit: `/skillname` prefix on task string — `python agent.py "/cite /deep ..."`
- Auto: trigger predicates fire on task keywords or `plan.complexity`

## Chunker — large document context extraction

`read_file_context()` calls `extract_paper_context()` for any file > 12,000 chars.

**Strategy selection:**
- ≥3 markdown headings → section extraction (Abstract, Conclusion, Introduction, Results, …) assembled in priority order within char budget
- Otherwise → overlapping char windows embedded with `all-MiniLM-L6-v2` via ephemeral ChromaDB; top-K by cosine similarity re-sorted to reading order

**Provenance metadata** — each `Chunk` carries: `source` (filename), `url`, `page` (estimated from `page_size` hint), `paragraph` (`\n\n` count before chunk start), `char_offset`, `section` (structured extraction only). Tags are embedded inline so the model can cite specific passages:

```
=== Introduction [source:paper.pdf | p.3 | ¶12 | §Introduction | @4,200] ===
```

## MarkItDown integration

- `RICH_EXTENSIONS`: `.pdf .docx .xlsx .pptx .epub .htm` — routed through MarkItDown
- `URL_ENRICH_COUNT = 2`: top-N novel URLs fetched (gated on word-overlap vs knowledge_state)
- Fallback: graceful no-op if `markitdown` not installed

## Perfetto / Chrome Trace Event instrumentation

`logger.RunTrace` emits `traceEvents` in Chrome Trace Event JSON format to `traces/<timestamp>_<slug>.json`.

- `trace.span("stage_name")` — wall-clock duration event for any pipeline stage
- `trace.name_thread("main")` / `trace.name_thread("panel/Reviewer")` — lane labels
- `trace.log_usage(response, stage=...)` — emits `llm:<stage>` event using Ollama's `total_duration`

Load any trace at **ui.perfetto.dev** → per-stage waterfall + panel thread parallelism.

## Composite eval score

```
composite = 0.7 * mean_wiggum_r1 + 0.3 * criteria_rate * 10
```

Wiggum dimensions (weights): relevance (0.20), completeness (0.25), depth (0.30), specificity (0.15), structure (0.10).
