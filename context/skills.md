# Agent Skills

Skills extend the pipeline at defined hook points. Invoke explicitly with a `/skill` prefix in the task string, or let the planner auto-activate them based on task signals.

## Skill Registry

### /annotate (standalone)
Reads a research paper — local file or URL — and produces a Nanda Annotated Abstract: structured summary covering contribution, method, results, and limitations. Bypasses web search entirely; the paper is the sole context. Combine with `/wiggum` to run the evaluation loop on the annotation.

**When activated:** Explicit only. Use when the task is to annotate a specific paper.

---

### /cite (pre_synthesis)
Injects a citation requirement into the synthesis prompt: every significant claim must include a source reference from the research context. Claims that cannot be attributed are flagged as inferred.

**When activated:** Explicit only — too broad to auto-trigger. Use when source attribution matters.

---

### /deep (pre_research)
Disables the novelty saturation gate and forces all `MAX_SEARCH_ROUNDS` (5) of web search to run regardless of novelty scores. Ensures maximum research coverage at the cost of speed.

**When activated:** Auto-triggers on keywords: `comprehensive`, `thorough`, `exhaustive`, `in-depth`, `deep dive`. Also available explicitly.

---

### /email (standalone)
Generates personalized `.eml` draft files from a CSV of contacts plus a stated outreach goal. Each draft is tailored per-contact. Output directory is configurable.

**When activated:** Explicit only.

---

### /github (standalone)
Runs GitHub operations via the `gh` CLI: push, pull request create/list/view/merge/review, issue create/list/view, repo view/clone, status checks.

**When activated:** Explicit only.

---

### /kg (post_synthesis)
Generates a D3.js force-directed knowledge graph from the synthesized content. Saves as an HTML file; optional `--screenshot` flag captures a PNG via Playwright.

**When activated:** Auto-triggers on keywords: `knowledge graph`, `kg`, `visualize`, `visualise`. Also available explicitly.

---

### /lit-review (standalone)
Full literature review pipeline: fetch arXiv papers → enrich with Semantic Scholar citation graph → curate → annotate with wiggum → cluster → synthesize → render via Jinja2 template. Supports `--no-fetch`, `--no-curate`, `--no-wiggum`, `--no-s2`, `--after`, `--before`, `--csv`, `--max-fetch`, `--max-annotate`, `--template` flags.

**When activated:** Explicit only — long-running pipeline.

---

### /panel (post_wiggum)
Runs a 3-persona evaluation panel (Domain Practitioner, Critical Reviewer, Informed Newcomer) after the wiggum loop. Each persona scores the output independently; results are logged to `runs.jsonl` as `panel_reviews` for downstream distillation or DPO preference learning.

**When activated:** Auto-triggers when planner detects `complexity=high`. Also available explicitly.

---

### /queue (standalone)
Adds one or more tasks to the server run queue (requires `server.py` running). Tasks separated by `;;` execute sequentially.

**When activated:** Explicit only.

---

### /recall (standalone)
Semantic search over the agent's memory store. Returns past observations ranked by relevance to the query. Flags: `--n N` (number of results), `--facts` (show extracted facts), `--scores` (show similarity scores).

**When activated:** Explicit only.

---

### /review (standalone)
Reviews a git diff against the Karpathy rubric: no magic constants, no speculative abstractions, no dead code, functions do one thing. Supports staged, unstaged, last commit, and full diff scopes.

**When activated:** Explicit only.

---

### /wiggum (modifier)
Runs the evaluate → revise → verify loop on the output. Up to 3 rounds; stops early on PASS (score ≥ 9.0). Scores across: relevance (0.20), completeness (0.25), depth (0.30), specificity (0.15), structure (0.10). Applied by default in the main pipeline; use `--no-wiggum` to skip.

**When activated:** Always on by default. Explicit `/wiggum` is used to add it to `/annotate` runs.

---

## Hook Points

| Hook | When it runs | Skills |
|------|-------------|--------|
| `pre_research` | Before web search | `/deep` |
| `pre_synthesis` | Injected into synthesis prompt | `/cite`, `/annotate` |
| `post_synthesis` | After output is written | `/kg` |
| `post_wiggum` | After verification loop | `/panel` |
| `standalone` | Replaces the full pipeline | `/annotate`, `/email`, `/github`, `/review`, `/lit-review`, `/recall`, `/queue` |

## Planned / In-Development Skills

- `/introspect` — answer questions about the agent from memory + context files; no web search
- `/contextualize` — auto-inject agent self-knowledge into tasks that reference the agent itself
- `/finance` — financial data retrieval and analysis skill (roadmap)
