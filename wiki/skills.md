---
title: Agent Skills
updated: 2026-04-20
tags: [skills, pipeline, introspect]
introspect: true
---

# Agent Skills

Skills extend the pipeline at defined hook points. Invoke explicitly with a `/skill` prefix in the task string, or let the planner auto-activate them based on task signals.

## Skill Registry

### /annotate (standalone)
Reads a research paper — local file or URL — and produces a structured Nanda Annotated Abstract: contribution, method, results, limitations. Bypasses web search entirely; the paper is the sole context. Combine with `/wiggum` to run the evaluation loop on the annotation.

**When activated:** Explicit only.

---

### /cite (pre_synthesis)
Injects a citation requirement into the synthesis prompt: every significant claim must include a source reference from the research context. Claims that cannot be attributed are flagged as inferred.

**When activated:** Explicit only — too broad to auto-trigger.

---

### /contextualize (pre_research — auto)
Detects self-referential tasks ("describe yourself", "what can you do", "explain the agent") and injects wiki self-knowledge pages into the synthesis context. Sets `_skip_research=True` so no web search runs — the answer comes from the wiki and memory. Implemented in `agent.py`.

**When activated:** Auto-triggers on self-referential task patterns (regex). Also available explicitly.

---

### /deep (pre_research)
Disables the ε-greedy novelty saturation gate and forces all `MAX_SEARCH_ROUNDS` (5) of web search to run regardless of novelty scores. Maximum research coverage at the cost of speed.

**When activated:** Auto-triggers on: `comprehensive`, `thorough`, `exhaustive`, `in-depth`, `deep dive`. Also explicit.

---

### /email (standalone)
Generates personalized `.eml` draft files from a CSV of contacts plus a stated outreach goal. Each draft is tailored per-contact. Output directory is configurable.

**When activated:** Explicit only.

---

### /finance (planned — roadmap)
Financial analysis pipeline: ingest (yfinance/EDGAR/FRED) → compute ratios/DCF → research → synthesize → evaluate via finance-specific panel (Fundamental Analyst, Risk Manager, Compliance Reviewer). See `wiki/roadmap.md`.

**When activated:** Not yet implemented.

---

### /github (standalone)
Runs GitHub operations via the `gh` CLI: push, PR create/list/view/merge/review, issue create/list/view, repo view/clone, status checks.

**When activated:** Explicit only.

---

### /introspect (standalone)
Answers questions about the agent itself — capabilities, architecture, pipeline, models — from wiki pages tagged `introspect: true` plus ChromaDB memory observations. No web search. Implemented in `agent.py` and `skills.py`.

**When activated:** Explicit only (use for direct "what are you" questions).

---

### /kg (post_synthesis)
Generates a D3.js force-directed knowledge graph from the synthesized content. Saves as an HTML file to `graphs/`. Optional `--screenshot` flag captures a PNG via Playwright.

**When activated:** Auto-triggers on: `knowledge graph`, `kg`, `visualize`, `visualise`. Also explicit.

---

### /lit-review (standalone)
Full literature review pipeline: fetch arXiv papers → Semantic Scholar citation enrichment → curate → annotate with wiggum → cluster → synthesize → render via Jinja2 template. Flags: `--no-fetch`, `--no-curate`, `--no-wiggum`, `--no-s2`, `--after`, `--before`, `--csv`, `--max-fetch`, `--max-annotate`, `--template`.

**When activated:** Explicit only — long-running pipeline (minutes to hours).

---

### /panel (post_wiggum)
Runs a 3-persona evaluation panel in parallel after the wiggum loop: Domain Practitioner, Critical Reviewer, Informed Newcomer. Each persona scores the output independently. Results logged to `runs.jsonl` as `panel_reviews` for downstream DPO preference learning.

**When activated:** Auto-triggers when planner detects `complexity=high`. Also explicit.

---

### /queue (standalone)
Adds one or more tasks to the `server.py` run queue. Tasks separated by `;;` execute sequentially.

**When activated:** Explicit only. Requires `server.py` running.

---

### /recall (standalone)
Semantic search over the ChromaDB memory store. Returns past observations ranked by relevance to the query. Flags: `--n N`, `--facts`, `--scores`.

**When activated:** Explicit only.

---

### /review (standalone)
Reviews a git diff against the Karpathy rubric: no magic constants, no speculative abstractions, no dead code, functions do one thing. Supports staged, unstaged, last commit, and full diff scopes.

**When activated:** Explicit only.

---

### /wiggum (modifier)
Runs the evaluate → revise → verify loop. Up to 3 rounds; stops early on PASS (score ≥ 9.0). Dimensions: relevance (0.20), completeness (0.25), depth (0.30), specificity (0.15), structure (0.10). Cycling detection exits early if score+dims are identical across consecutive rounds (restores best round). Applied by default in the main pipeline.

**When activated:** Always on by default. Use `--no-wiggum` to skip. Explicit `/wiggum` adds it to `/annotate` runs.

---

## Hook Points

| Hook | When it runs | Skills |
|------|-------------|--------|
| `pre_research` | Before web search | `/deep` |
| `pre_synthesis` | Injected into synthesis prompt | `/cite` |
| `post_synthesis` | After output is written | `/kg` |
| `post_wiggum` | After verification loop | `/panel` |
| `standalone` | Replaces the full pipeline | `/annotate`, `/email`, `/github`, `/introspect`, `/lit-review`, `/recall`, `/queue`, `/review` |
| `auto` | Injected by pattern detection | `/contextualize` |
