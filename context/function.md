# Agent Function and Pipeline

## What I Do

I take a natural-language task string and produce a high-quality markdown document — research synthesis, literature review, annotated abstract, code review, email drafts, or knowledge graph — saved to a path specified in the task.

My outputs are not single-shot model completions. Every output is planned, researched, synthesized, evaluated, and revised before it is finalized.

## Pipeline (Single-Focus Task)

```
parse_skills()              strip /skill tokens; identify explicit activations
  → memory.get_context()    retrieve semantically relevant past run observations
    → make_plan()           analyse task; generate search queries and synthesis notes
      → auto_activate()     trigger skills by task keywords or plan complexity
        → gather_research() saturation loop: search → novelty gate → compress
          → synthesize()    pi-qwen-32b produces markdown from research + context
            → count check   verify item count if task specifies a number (e.g. "top 5")
              → write()     save output to disk
                → wiggum()  evaluate → revise → verify loop (up to 3 rounds)
                  → panel() 3-persona parallel eval (if complexity=high or explicit)
                    → compress_and_store()  compress run into memory observation
```

## Research Loop (gather_research)

The saturation loop runs up to 5 rounds of web search:
- Round 1 query is derived directly from the task
- Round 2+ queries are gap-targeted: the model identifies what is NOT yet known
- After round 2, each new result is scored for novelty (0–10) against the accumulated knowledge state
- If novelty drops below threshold (3/10), search stops early
- A quality floor check (1800 chars) triggers a fallback search if results are sparse
- Top-N result URLs are fetched in full via MarkItDown for richer context
- All search results are scanned for prompt injection before synthesis

**Skip conditions:** Web search is skipped entirely when:
- The task contains a URL (fetched directly)
- The `/introspect` skill is active (uses memory + context files instead)
- `RESEARCH_CACHE=1` and a cache hit exists (autoresearch mode)

## Evaluation Loop (wiggum)

Each round:
1. Normalize output to markdown
2. Evaluate against task: relevance, completeness, depth, specificity, structure (weighted 0.20 / 0.25 / 0.30 / 0.15 / 0.10)
3. If score ≥ 9.0: PASS and stop
4. If score < 9.0: produce a revised draft using evaluator feedback, write, loop

Task-type criteria:
- `enumerated` — exact item count required; fails if count is wrong
- `best_practices` — coverage across multiple dimensions; actionability required
- `research` — synthesis over listing; explain why, not just what

## Compound Tasks (orchestrator.py)

For multi-part tasks, `orchestrator.py` wraps `agent.py`:
1. Decompose the compound task into subtasks
2. Run each subtask through the full `agent.py` pipeline
3. Assemble subtask outputs into a final document

## Memory System

After each run, a compressed observation is stored:
- **Title:** short description of what was produced
- **Narrative:** one-paragraph summary of the run
- **Facts:** extracted key facts from the output
- **Scores:** wiggum scores per round
- **Metadata:** task type, output path, token counts, timestamp

On the next run, semantically similar past observations are retrieved and injected into the synthesis context. This gives the agent a persistent, growing understanding of the problem space.

## Tracing

Every run writes a Perfetto-compatible trace to `traces/<timestamp>_<slug>.json`. Load at `ui.perfetto.dev` to visualize stage latencies, model calls, and panel parallelism.

## Key Environment Variables

| Variable | Effect |
|----------|--------|
| `OLLAMA_KEEP_ALIVE` | Pin model keep-alive seconds (-1 = always hot) |
| `INFERENCE_BACKEND` | `vllm` switches all model calls to vLLM OpenAI-compatible API |
| `WIGGUM_PANEL` | `1` enables the 3-persona panel inside wiggum |
| `WIGGUM_MAX_ROUNDS` | Cap wiggum revision rounds (default 3) |
| `RESEARCH_CACHE` | `1` enables research result caching (autoresearch mode only) |
| `COMPRESS_MODEL` | Override model used for compress_knowledge and plan_query |
| `WIGGUM_PRODUCER_MODEL` | Override producer model inside wiggum |
| `WIGGUM_EVALUATOR_MODEL` | Override evaluator model inside wiggum |
