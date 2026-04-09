# AGENTS.md — harness-engineering wiki schema

This file tells your LLM agent how to maintain the project wiki.

## Environment

```
conda activate ollama-pi
```

Key dependencies: `ollama`, `ddgs`, `markitdown`, `jinja2`, `chromadb`,
`sentence-transformers`, `torch` (cu118), `graphviz`, `requests`, `Pillow`.

## Directory layout

```
harness-engineering/
├── wiki/                    ← LLM-maintained knowledge base (agent writes this)
│   ├── index.md             ← content catalog; updated by wiki_tools.py
│   ├── log.md               ← append-only operations log
│   ├── architecture.md
│   ├── eval-framework.md
│   ├── experiments.md
│   ├── synthesis-instructions.md
│   ├── marginal-value-search.md   ← design spec: saturation-based search loop
│   └── chromadb-memory-migration.md  ← design spec: semantic memory retrieval
├── graphs/                  ← knowledge graph HTML outputs (gitignored)
├── experiment-*.md          ← raw experiment records (immutable — never edit)
├── runs.jsonl               ← agent run log (immutable — never edit)
├── journal.md               ← dev journal (narrative; append-only)
├── roadmap.md               ← planning and stage tracking
└── README.md                ← public-facing overview
```

## Key modules

| File | Purpose |
|------|---------|
| `agent.py` | Main research + write + verify pipeline |
| `wiggum.py` | Verification loop (WIGGUM_MAX_ROUNDS env var caps rounds) |
| `memory.py` | Observation store — SQLite + ChromaDB semantic retrieval + `assess_novelty()` |
| `autoresearch.py` | Autonomous synthesis instruction improvement loop |
| `search_cache.py` | SQLite TTL cache for DDGS queries |
| `kg_gen.py` | Knowledge graph generator — Ollama → D3.js HTML via Jinja2 |
| `kg_template.html.j2` | D3.js force-directed graph template |
| `eval_suite.py` | Regression harness — `--score --tasks T_D,T_E` for autoresearch |
| `wiki_tools.py` | Python-deterministic wiki maintenance (index / log / lint) |

## Python-for-determinism rule

Structural bookkeeping is done in Python, not by LLM:
- Updating `wiki/index.md` → `python wiki_tools.py index`
- Appending to `wiki/log.md` → `python wiki_tools.py log "ingest | <source>"`
- Checking orphans / broken links → `python wiki_tools.py lint`

The agent writes wiki page *content*. Python handles *structure*.

## Wiki operations

### Ingest
When a new source arrives (experiment result, paper, article, eval output):
1. Read the source
2. Write or update relevant wiki page(s) in `wiki/`
3. `python wiki_tools.py index` — refresh index
4. `python wiki_tools.py log "ingest | <source name>"` — append to log

One source may touch multiple pages (e.g. a new experiment updates both
`experiments.md` and `synthesis-instructions.md`).

### Query
When answering a question that produces a reusable result:
1. Read `wiki/index.md` to find relevant pages
2. Synthesize answer
3. If the result is reusable, write it to `wiki/<topic>.md`
4. Run index + log tools

### Lint
Check for: contradictions, orphan pages, stale claims, missing cross-references.
Run `python wiki_tools.py lint` for a report.

## Page frontmatter

Every wiki page opens with YAML frontmatter:

```yaml
---
title: <page title>
updated: YYYY-MM-DD
sources: [experiment-04.md, runs.jsonl]
tags: [eval, synthesis, architecture]
---
```

## Index format

`wiki/index.md` is machine-maintained — do not edit by hand.

## Log format

Each entry in `wiki/log.md`:
```
## [YYYY-MM-DD] <operation> | <subject>
```
Operations: `ingest`, `query`, `lint`, `update`.

Grep recent entries: `grep "^## \[" wiki/log.md | tail -10`

## What stays out of the wiki

- Raw experiment outputs → `experiment-*.md`
- Agent run data → `runs.jsonl`
- Dev narrative → `journal.md`
- Planning → `roadmap.md`

The wiki is *synthesis*, not storage.
