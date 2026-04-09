---
title: Agent Architecture
updated: 2026-04-09
sources: [agent.py, logger.py, planner.py, orchestrator.py, memory.py, wiggum.py]
tags: [architecture, pipeline, agent]
---

# Agent Architecture

## Pipeline stages

```
task
 └─ plan()           planner.py     — classify task_type, generate search queries
 └─ gather_research()  agent.py     — web search → merge → MarkItDown enrichment → injection scan
 └─ synthesize()       agent.py     — producer model writes markdown doc
 └─ wiggum_eval()      wiggum.py    — evaluator scores output, requests revisions (up to 3 rounds)
 └─ write output        agent.py    — save to file, log run to runs.jsonl
```

## Key components

| File | Role |
|------|------|
| `agent.py` | Main entry point; orchestrates all stages |
| `planner.py` | LLM-based task planner; returns `PlanResult` |
| `wiggum.py` | Evaluator/reviser loop; scores on 5 dimensions |
| `logger.py` | Structured run logging to `runs.jsonl` |
| `memory.py` | SQLite-backed memory; hit on every run |
| `orchestrator.py` | Multi-step task orchestration |
| `security.py` | Prompt injection detection and stripping |
| `vision.py` | Image reading via LLaVA |
| `eval_suite.py` | Batch eval runner; computes composite score |
| `autoresearch.py` | Autonomous synthesis instruction improvement loop |

## Models

| Role | Model | Notes |
|------|-------|-------|
| Producer (default) | `pi-qwen-32b` (Qwen2.5-32B) | Runs on Pi; accessed via `OLLAMA_HOST` |
| Producer (fallback) | `qwen2.5:7b` | Local |
| Evaluator / proposer | `Qwen3-Coder:30b` | Local |
| Embeddings | `nomic-embed-text` | For memory retrieval (Stage 5b) |

## MarkItDown integration

- `RICH_EXTENSIONS`: `.pdf .docx .xlsx .pptx .epub .htm` — routed through MarkItDown
- `URL_ENRICH_COUNT = 2`: top-N search result URLs fetched as full markdown
- Fallback: graceful no-op if `markitdown` not installed

## Composite eval score

```
composite = 0.7 * mean_wiggum_r1 + 0.3 * criteria_rate * 10
```

Wiggum dimensions (weights): relevance (0.20), completeness (0.25), depth (0.30), specificity (0.15), structure (0.10).
