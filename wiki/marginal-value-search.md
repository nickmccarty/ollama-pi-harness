---
title: Marginal Value Search
updated: 2026-04-09
sources: []
tags: [research, gather_research, search, implemented]
---

# Marginal Value Search

**Status: implemented** in `agent.py`. See `gather_research()`, `compress_knowledge()`, `plan_query()`, `enrich_with_page_content()`.
First autoresearch session with this enabled is session 3 (2026-04-10+).

Design spec for replacing the fixed N-search loop in `gather_research()` with a
saturation-based loop that stops when new results contribute below a novelty threshold.

## Problem

`gather_research()` currently runs exactly 2 searches (+ optional quality-floor fallback)
regardless of topic complexity. This causes two failure modes:

- **Over-search**: Simple topics saturate after 1 query; rounds 2+ repeat the same facts,
  inflating context and slowing synthesis.
- **Under-search**: Complex topics have meaningful signal beyond round 2 that never gets
  retrieved; the agent synthesizes from an incomplete picture.

URL enrichment has the same problem: fetching full pages for results whose snippet content
is already covered wastes ~30-60s per URL and adds noise to synthesis context.

## Design

### Saturation loop (replaces fixed 2-query loop)

```
knowledge_state = ""        # compressed summary of everything gathered so far
all_results    = []         # deduplicated raw result dicts

for round in 1..MAX_SEARCH_ROUNDS:
    query   = plan_query(task, knowledge_state, round)
    results = web_search(query)
    novelty = assess_novelty(results, knowledge_state)   # 0–10
    log("[search {round}] novelty={novelty} query={query}")

    if novelty < NOVELTY_THRESHOLD and round > 1:
        log("  saturation reached — stopping search")
        break

    all_results     = merge(all_results, results)
    knowledge_state = compress_knowledge(knowledge_state, results)

# URL enrichment — only fetch URLs not already covered
enriched = enrich_novel_urls(all_results, knowledge_state)

return format_results(all_results) + enriched
```

### Config constants (in agent.py)

```python
MAX_SEARCH_ROUNDS   = 5      # hard cap regardless of novelty
NOVELTY_THRESHOLD   = 3      # 0–10; stop if new results score below this
KNOWLEDGE_MAX_CHARS = 1500   # cap on rolling knowledge state fed to novelty prompt
```

Existing `SEARCHES_PER_TASK = 2` becomes the **minimum** — loop always runs at least
`min(2, MAX_SEARCH_ROUNDS)` rounds before novelty gating kicks in. This preserves
current baseline behavior for simple tasks.

---

## Functions

### `assess_novelty(new_results, knowledge_state) -> int`

**Options** (choose one per implementation):

**Option A — heuristic (fast, no model call)**
Compute word-level overlap between new result bodies and knowledge_state.
Returns 0–10 based on fraction of new n-grams not already in knowledge_state.

```python
def assess_novelty_heuristic(new_results: list[dict], knowledge_state: str) -> int:
    new_words = set(w for r in new_results for w in r.get("body","").lower().split())
    known_words = set(knowledge_state.lower().split())
    if not new_words:
        return 0
    novel_fraction = len(new_words - known_words) / len(new_words)
    return round(novel_fraction * 10)
```

Pros: ~0ms, no model call, deterministic.
Cons: vocabulary overlap is a weak proxy for semantic novelty.

**Option B — model-based (slower, smarter)**

```python
NOVELTY_PROMPT = """\
What is already known:
{knowledge_state}

New search results:
{new_results}

Do these results add genuinely new information not already covered above?
Score 0–10 where 0 = completely redundant, 10 = entirely new information.
Output ONLY the integer score, nothing else."""

def assess_novelty_model(new_results, knowledge_state, model) -> int:
    snippet = format_results(new_results)[:800]
    prompt  = NOVELTY_PROMPT.format(
        knowledge_state=knowledge_state[:800],
        new_results=snippet,
    )
    response = ollama.chat(model=model, messages=[{"role":"user","content":prompt}],
                           options={"temperature": 0, "num_predict": 3})
    raw = response["message"]["content"].strip()
    match = re.search(r'\d+', raw)
    return int(match.group()) if match else 5   # default to neutral on parse failure
```

Pros: semantic understanding, catches paraphrased duplicates.
Cons: adds ~10-15s per round (prefill dominated; only 1-3 output tokens).

**Recommendation**: start with Option A for autoresearch (latency sensitive). Switch
to Option B if novelty gating proves too coarse (e.g. misses paraphrase duplicates).

---

### `compress_knowledge(current_state, new_results) -> str`

Maintains a rolling compressed summary of everything gathered. Called after each
accepted search round.

```python
COMPRESS_PROMPT = """\
Current knowledge summary:
{current_state}

New search results to incorporate:
{new_results}

Update the summary to include the new information. Be concise — 5–8 bullet points,
each starting with a key fact. Do not exceed {max_chars} characters total.
Output ONLY the bullet points, nothing else."""

def compress_knowledge(current_state: str, new_results: list[dict],
                       model: str, max_chars: int = KNOWLEDGE_MAX_CHARS) -> str:
    if not current_state:
        # First round: build initial state from results
        bodies = " ".join(r.get("body","") for r in new_results)[:1200]
        return bodies[:max_chars]   # skip model call for first round

    prompt = COMPRESS_PROMPT.format(
        current_state=current_state,
        new_results=format_results(new_results)[:800],
        max_chars=max_chars,
    )
    response = ollama.chat(model=model, messages=[{"role":"user","content":prompt}],
                           options={"temperature": 0.1, "num_predict": 400})
    summary = response["message"]["content"].strip()
    return summary[:max_chars]
```

Note: `compress_knowledge` is only called when a round is *accepted* (novelty ≥ threshold).
No wasted model calls for rejected rounds.

---

### `plan_query(task, knowledge_state, round) -> str`

Replaces `generate_second_query()`. Takes the knowledge gap into account.

```python
PLAN_QUERY_PROMPT = """\
Task: {task}

What is already known:
{knowledge_state}

Generate ONE search query to find important information about the task NOT yet covered
above. Output ONLY the query string, nothing else."""

def plan_query(task, knowledge_state, round, model, trace=None) -> str:
    if round == 1 or not knowledge_state:
        # Round 1: derive query from task as before
        return re.sub(r"(?i)^search\s+(for\s+)?", "", task.split("save to")[0]).strip()

    response = ollama.chat(model=model,
                           messages=[{"role":"user","content":
                               PLAN_QUERY_PROMPT.format(task=task,
                                                        knowledge_state=knowledge_state)}],
                           options={"temperature": 0.3, "num_predict": 60})
    if trace:
        trace.log_usage(response, stage="search_query")
    return response["message"]["content"].strip().strip('"')
```

---

### `enrich_novel_urls(results, knowledge_state) -> str`

URL enrichment gated on novelty — skip URLs whose snippet is already covered.

```python
def enrich_novel_urls(results, knowledge_state, count=URL_ENRICH_COUNT) -> str:
    blocks = []
    fetched = 0
    for r in results:
        if fetched >= count:
            break
        snippet = r.get("body", "")
        # Heuristic: skip if >60% of snippet words are in knowledge_state
        snippet_words = set(snippet.lower().split())
        known_words   = set(knowledge_state.lower().split())
        overlap = len(snippet_words & known_words) / max(len(snippet_words), 1)
        if overlap > 0.6:
            print(f"  [enrich] skipping {r['href'][:50]} — {overlap:.0%} overlap with known")
            continue
        content = fetch_url_content(r["href"])
        if content:
            blocks.append(f"**Full page: {r.get('title','')}**\n{r['href']}\n\n{content}")
            fetched += 1
    return "\n\n---\n\n".join(blocks)
```

---

## Updated `gather_research()` signature

```python
def gather_research(
    task: str,
    trace: RunTrace,
    planned_queries: list[str] = None,   # existing param — still honored for round 1+2
    producer_model: str = MODEL,
    task_type: str = None,               # existing param
) -> str:
```

No signature changes. Behavior changes are internal.

`planned_queries` still works: if provided, they're used as the queries for rounds 1 and 2
before switching to `plan_query()` for subsequent rounds.

---

## Impact on existing code

| File | Change |
|------|--------|
| `agent.py` | Replace loop in `gather_research()`; add 3 new functions; add 3 config constants; remove `generate_second_query()` (folded into `plan_query()`) |
| `logger.py` | Add `log_novelty(round, score)` to RunTrace if telemetry needed |
| `runs.jsonl` | New fields: `novelty_scores: [int]`, `search_rounds: int` |
| `autoresearch.py` | No changes — `gather_research()` is transparent to it |
| `eval_suite.py` | No changes |
| `wiki/experiments.md` | Update after first session with marginal value search enabled |

---

## Rollout

1. Implement with Option A (heuristic novelty) — no latency impact, zero risk
2. Run autoresearch session to verify scores don't regress
3. Log `novelty_scores` to runs.jsonl and inspect: are rejected rounds actually low-value?
4. If heuristic is noisy, switch to Option B for novelty + keep Option A for URL dedup

## Open questions

- Should `MAX_SEARCH_ROUNDS = 5` be per-task-type? (enumerated tasks may saturate faster)
- Should the knowledge state be passed to synthesis directly (replacing raw results)?
  Pros: cleaner, shorter prompt. Cons: loses source URLs, may lose specific quotes.
- Should `compress_knowledge` use a smaller/faster model (e.g. 7b) for the autoresearch loop?
