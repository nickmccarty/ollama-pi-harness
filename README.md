# harness-engineering

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/nickmccarty/ollama-pi-harness)

A local agent harness built incrementally from failure. Research, verify, remember, plan, orchestrate — running on local models via Ollama or vLLM with no external API keys.

The central question: can open-source models running locally approach the utility of frontier models through harness engineering alone? The premise is that the model is not the 80% factor. The harness is.

---

## Architecture

```
orchestrator.py          ← compound tasks: decompose → run subtasks → assemble
    |
    agent.py             ← single-focus tasks: plan → search → synthesize → write
        |
        ├── planner.py       search queries, synthesis notes, subtask decomposition
        ├── memory.py        retrieve relevant past observations (ChromaDB + SQLite)
        ├── wiggum.py        evaluate → revise → verify loop (parallel panel)
        ├── skills.py        skill registry — /annotate /cite /kg /deep /panel
        ├── chunker.py       large-doc context extraction with provenance metadata
        ├── vision.py        image-to-text preprocessing (llama3.2-vision)
        ├── security.py      code scanner, path sandbox, injection scanner
        ├── github_skill.py  /github — push, PR, issue, repo ops via gh CLI
        ├── email_skill.py   /email — personalized .eml drafts from CSV + goal
        ├── review_skill.py  /review — diff review against dead-code/anti-pattern rubric
        └── markitdown       rich document conversion + URL enrichment (optional)

shared: logger.py / runs.jsonl + traces/, memory.py / memory.db

inference.py ← unified backend shim (Ollama default | vLLM via INFERENCE_BACKEND=vllm)
```

**Run lifecycle (single-focus task):**
```
parse_skills()                    strip /skill tokens, collect explicit activations
  → memory.get_context()
    → make_plan()                 glm4:9b analyses task + memory
      → auto_activate()           trigger skills by task keywords / plan.complexity
        → gather_research()       saturation loop: search → novelty gate → compress
          → vision preprocessing  llama3.2-vision if image paths detected
          → read_file injection    text/rich-doc contents; chunker extracts context
            (chunker: section extraction or ChromaDB chunk retrieval + provenance tags)
          → markitdown URL enrich  full page content for top-N novel URLs
          → run_python tool loop   skipped for research/best_practices task types
            → synthesize()         pi-qwen-32b + skill prompt injections (pre_synthesis)
              → count check + retry
                → write output
                  → wiggum loop    evaluate → revise → verify (up to 3 rounds)
                    → panel        3-persona parallel eval (post_wiggum skills)
                      → post_synthesis skills   kg graph generation etc.
                        → compress_and_store()  glm4:9b compresses run into memory
```

**Perfetto tracing:** every run writes `traces/<timestamp>_<slug>.json` — load at `ui.perfetto.dev` to visualise stage latencies and panel parallelism.

---

## Prerequisites

**Ollama models required:**
```bash
ollama pull qwen2.5:7b                    # base model for pi-qwen (default producer)
ollama pull glm4:9b                       # planner + memory compression
ollama pull Qwen3-Coder:30b               # evaluator (must be larger than producer)
ollama pull llama3.2-vision               # vision preprocessing

# Candidate producer upgrades (pull as needed for testing):
ollama pull qwen2.5:32b-instruct-q4_K_M  # ~20GB — recommended upgrade
ollama pull mistral-small3.1:24b          # ~15GB — alternative, different family
ollama pull phi4:14b                      # ~9GB  — compact, strong instruction-following
```

**Create producer models:**
```bash
ollama create pi-qwen -f Modelfile          # default 7B producer
ollama create pi-qwen-32b -f Modelfile.32b  # 32B producer (requires Modelfile.32b)
```

**vLLM (optional — unblocks parallel subtask execution):**

Requires WSL2 Ubuntu or Docker. Does not work via native Windows pip install.

```bash
# In WSL2 Ubuntu:
conda create -n vllm python=3.12 -y && conda activate vllm
pip install torch==2.6.0+cu124 --index-url https://download.pytorch.org/whl/cu124
pip install vllm==0.7.3 "transformers==4.49.0"

export HF_HOME=/mnt/c/Users/<you>/.cache/huggingface
vllm serve Qwen/Qwen2.5-14B-Instruct-AWQ \
  --dtype half --quantization awq_marlin \
  --max-model-len 8192 --enable-prefix-caching \
  --gpu-memory-utilization 0.90
```

Then in `.env` (Windows):
```
INFERENCE_BACKEND=vllm
VLLM_BASE_URL=http://localhost:8000/v1
VLLM_MODEL_MAP={"pi-qwen-32b":"Qwen/Qwen2.5-14B-Instruct-AWQ","pi-qwen":"Qwen/Qwen2.5-14B-Instruct-AWQ","Qwen3-Coder:30b":"Qwen/Qwen2.5-14B-Instruct-AWQ"}
```

See `requirements-vllm.txt` for pinned deps and known version constraints.

**Python environment (conda):**
```bash
conda create -n ollama-pi python=3.11
conda activate ollama-pi
pip install ollama ddgs "markitdown[all]" datasets   # datasets required for --push in hf_export.py
```

---

## Usage

**Single-focus task:**
```bash
python agent.py "Search for the top 5 context engineering techniques and save to ~/Desktop/output.md"
python agent.py --no-wiggum "..."                  # skip verification loop
python agent.py --producer pi-qwen-32b "..."       # use alternative producer model
```

**Skills — prefix task with /skill tokens:**
```bash
python agent.py "/annotate Search for RAG papers and save to output.md"   # Nanda 8-move framework
python agent.py "/annotate /wiggum https://arxiv.org/abs/2308.04079 out.md"  # annotate + evaluate
python agent.py "/cite /deep Comprehensive survey of LoRA fine-tuning techniques..."
python agent.py "/kg Explain transformer attention mechanisms..."           # D3.js knowledge graph

# Standalone skills (no .md path required):
python agent.py "/github push add new feature"       # LLM commit message → git push
python agent.py "/github pr create"                  # LLM PR title+body → gh pr create
python agent.py "/github status"                     # branch + log + working tree
python agent.py "/email speakers.csv reach out about our platform save to drafts/"
python agent.py "/review"                            # review staged changes (Qwen3-Coder:30b)
python agent.py "/review last"                       # review last commit
python agent.py "/review all"                        # review all unpushed vs origin/main

# Literature review pipeline:
python agent.py "/lit-review agentic LLM harness engineering save to review.md"
python agent.py "/lit-review --after 2024-06-01 --max-annotate 30 prompt injection save to gaps.md"
python agent.py "/lit-review --csv arxiv_agentic_papers.csv --no-fetch --template gaps save to gaps.md"
python lit_review_skill.py "RAG retrieval" --max-annotate 20 --out review.md   # standalone
python semantic_scholar.py arxiv_agentic_papers.csv                             # enrich + hub scores
python semantic_scholar.py arxiv_agentic_papers.csv --fetch-gaps 20 --append arxiv_agentic_papers.csv

# Auto-triggered (no prefix needed):
#   /annotate  — task mentions "paper", "abstract", "survey", "review"
#   /deep      — task mentions "comprehensive", "exhaustive", "deep dive"
#   /panel     — plan.complexity == "high"
#   /kg        — task mentions "knowledge graph", "visualize"
```

**Fetch arXiv papers:**
```bash
python arxiv_fetch.py "agentic LLM harness"                         # -> arxiv_agentic_llm_harness.csv (300 papers)
python arxiv_fetch.py "RAG retrieval" --max 500 --out rag.csv        # custom output, more papers
python arxiv_fetch.py "prompt injection" --after 2024-06-01          # date filter — new papers only
python arxiv_fetch.py "multi-agent" --append existing.csv            # append, skip duplicates
python arxiv_fetch.py --stats arxiv_agentic_papers.csv               # inspect existing CSV
```

**Annotated abstracts (batch):**
```bash
python annotate_abstracts.py papers.csv
python annotate_abstracts.py papers.csv --model Qwen3-Coder:30b --out annotated/
python annotate_abstracts.py papers.csv --reprocess   # redo failed/incomplete
```

**Compound task (orchestrated):**
```bash
python orchestrator.py "Research agent failure modes and context engineering, synthesize into a unified guide and save to ~/Desktop/guide.md"
```

**Regression eval suite:**
```bash
python eval_suite.py              # run all tasks then check criteria
python eval_suite.py --fast       # check existing output files only
python eval_suite.py --no-wiggum  # run tasks, skip verification
python eval_suite.py --generated  # include synthetic tasks from tinytroupe_tasks.py
```

**Autoresearch (autonomous synthesis-instruction optimizer):**
```bash
python autoresearch.py                    # loop indefinitely on T_A + T_B
python autoresearch.py --tasks T_A,T_B   # explicit task subset
python autoresearch.py --delta 0.2       # stricter keep threshold

python tinytroupe_tasks.py               # generate synthetic eval tasks from 8 personas
```

**Inspect memory:**
```bash
python memory.py                           # list recent observations
python memory.py --search "context window" # test retrieval
```

**Search cache:**
```bash
python search_cache.py            # stats: live / expired / total entries + size
python search_cache.py --expired  # evict only expired entries
python search_cache.py --clear    # wipe entire cache
```

**Test the planner:**
```bash
python planner.py "Your task string here"
```

**Analytics:**
```bash
python analytics.py         # cross-run stats
python analytics.py --full  # per-run detail
```

**Skills registry:**
```bash
python skills.py            # list all skills with hook, trigger mode, description
```

**HuggingFace dataset export:**
```bash
python hf_export.py                               # export to hf_datasets/ (sft, preference, reward, trajectory)
python hf_export.py --sft-min-score 8.0           # stricter SFT quality filter
python hf_export.py --push nickmccarty/ollama-pi-harness-datasets  # push to Hub (requires HF_TOKEN)
```

**DPO preference dataset:**
```bash
python build_dpo_dataset.py                       # build hf_datasets/dpo.jsonl (default min_delta=0.5)
python build_dpo_dataset.py --min-delta 1.0       # stricter preference gap
python build_dpo_dataset.py --source cross        # cross-run pairs only
python build_dpo_dataset.py --source revision     # wiggum-revision pairs only (requires runs post 2026-04-14)
python build_dpo_dataset.py --stats               # stats only, no file write
```

**Dashboard:**
```bash
python dashboard.py --open  # generate dashboard.html and open in browser
```

**List available skills:**
```
/annotate   [pre_synthesis ] [auto]    Inject Nanda Annotated Abstract framework
/kg         [post_synthesis] [auto]    Generate D3.js knowledge graph
/panel      [post_wiggum  ] [auto]    3-persona evaluation panel
/deep       [pre_research  ] [auto]    Force MAX_SEARCH_ROUNDS, disable novelty gate
/cite       [pre_synthesis ] [explicit] Require source attribution for each claim
```

**Perfetto traces:**
```bash
# After any run, open the newest trace:
ls traces/
# Drag the .json file to ui.perfetto.dev  → per-stage waterfall + panel parallelism
```

**Inspect runs:**
```bash
python inspect_run.py          # last run (full detail with token breakdown)
python inspect_run.py 3        # last 3 runs
python inspect_run.py --all    # summary table of all runs
```

---

## Models

| Role | Model | Notes |
|------|-------|-------|
| Producer (default) | `pi-qwen-32b` (qwen2.5:32b Q4_K_M) | Custom Modelfile — ~20GB; confirmed upgrade over 7B on depth+specificity |
| Producer (fallback) | `pi-qwen` (qwen2.5:7b) | Faster, lower quality; use with `--producer pi-qwen` |
| Annotator | `nanda-annotator` | QLoRA fine-tuned Qwen2.5-7B on 718 Nanda-annotated abstracts; local GGUF |
| Evaluator | `Qwen3-Coder:30b` | Must be larger/different than producer — drives revision loop |
| Planner / Compressor | `glm4:9b` | Different architecture from producer; fast enough for planning and memory compression |
| Vision | `llama3.2-vision` | Image-to-text preprocessing only; does not replace producer |
| GitHub skill | `llama3.2:3b` | Fast commit/PR/issue generation; override with `GITHUB_MODEL` env var |
| vLLM (16GB laptop) | `Qwen/Qwen2.5-14B-Instruct-AWQ` | AWQ int4, ~9.4GB loaded; all harness tags remapped via `VLLM_MODEL_MAP` |

**Producer candidates on-disk (not yet default):**

| Model | Size | Tool-calling | Notes |
|-------|------|-------------|-------|
| `qwen2.5:32b-instruct-q4_K_M` | ~20GB | Native | Recommended first test — same family as default |
| `mistral-small3.1:24b` | ~15GB | Native | Different family; good headroom for KV cache |
| `phi4:14b` | ~9GB | Needs template override | Best instruction-following per GB; Modelfile workaround required |

---

## Files

| File | Purpose |
|------|---------|
| `agent.py` | Single-agent research + write pipeline |
| `orchestrator.py` | Multi-subtask coordination and assembly |
| `planner.py` | Pre-execution task analysis — search queries, subtask decomposition |
| `memory.py` | ChromaDB + SQLite persistent observation store |
| `wiggum.py` | Evaluate → revise → verify loop (decimalized rubric, task-type criteria) |
| `panel.py` | 3-persona parallel evaluation panel (ThreadPoolExecutor) |
| `skills.py` | Skill registry — /annotate /cite /kg /deep /panel; auto-trigger predicates |
| `chunker.py` | Large-doc context extraction: section extraction or ChromaDB chunk retrieval; provenance metadata |
| `annotate_abstracts.py` | Batch annotated abstract generator — Nanda 8-move framework over CSV of papers |
| `vision.py` | llama3.2-vision routing for image inputs |
| `security.py` | Code scanner, path sandbox, prompt injection scanner |
| `search_cache.py` | SQLite TTL cache for DDGS search results (24 h, SHA-256 keyed) |
| `logger.py` | Structured per-run trace -> `runs.jsonl`; Chrome Trace Events -> `traces/` |
| `eval_suite.py` | Regression harness — 5 fixed tasks + optional generated tasks |
| `autoresearch.py` | Autonomous synthesis-instruction optimizer (Karpathy-style loop) |
| `autoresearch_program.md` | Autoresearch scope, metric, keep rule, and dimension weights |
| `tinytroupe_tasks.py` | Synthetic eval task generator — 8 practitioner personas |
| `analytics.py` | Cross-run analysis from `runs.jsonl` |
| `inspect_run.py` | Pretty-print last N runs with token/stage breakdown |
| `analyze_exp01.py` | Experiment-01 analysis script |
| `analyze_exp02.py` | Experiment-02 analysis script |
| `analyze_exp03.py` | Experiment-03 analysis — model-filtered, cross-experiment comparison |
| `run_exp04.py` | Experiment-04 runner — 9-run CRD for producer upgrade impact |
| `analyze_exp04.py` | Experiment-04 analysis script |
| `hf_export.py` | Export `runs.jsonl` to HuggingFace-ready SFT / preference / reward / trajectory datasets |
| `dashboard.py` | Generate self-contained HTML analytics dashboard from `runs.jsonl` |
| `github_skill.py` | /github standalone skill — push, PR, issue, repo ops via `gh` CLI + LLM |
| `inference.py` | Unified Ollama/vLLM backend shim — `OllamaLike`, `_OllamaResponse`, model map |
| `requirements-vllm.txt` | Pinned vLLM dep tree for WSL2 isolated env (vllm==0.7.3, transformers==4.49.0) |
| `test_inference_shim.py` | Unit test: model map, live vLLM call, usage field extraction |
| `test_harness_vllm.bat` | End-to-end harness test against vLLM: shim + agent run + output check |
| `test_vllm.sh` | WSL2 smoke test: `/health` + `/v1/chat/completions` |
| `email_skill.py` | /email standalone skill — personalized `.eml` drafts from CSV + goal |
| `review_skill.py` | /review standalone skill — diff review against dead-code/anti-pattern rubric (Qwen3-Coder:30b) |
| `curator.py` | 5-persona paper filter — scores each annotation, writes `*_curated.csv` + `curation_log.jsonl` |
| `finetune_annotate.py` | QLoRA fine-tune Qwen2.5-7B on Nanda annotated abstracts; step-based checkpointing (`--save-steps`), `--resume`, early stopping, DashboardCallback |
| `run_annotations.py` | Batch annotation runner — parse arxiv markdown → annotate → CSV |
| `build_finetune_from_annotations.py` | Merge gold + agent CSVs → `finetune_dataset_v2.jsonl` (prefers `*_curated.csv` if available) |
| `build_dpo_dataset.py` | Build DPO preference pairs from `runs.jsonl` — cross-run pairs + wiggum-revision pairs |
| `arxiv_fetch.py` | Fetch arXiv papers to CSV via feedparser — date filters, dedup, append mode; same schema as existing CSVs |
| `semantic_scholar.py` | Enrich corpus with citation graph data (Semantic Scholar API) — hub scores, gap candidates, SQLite cache |
| `lit_review_skill.py` | /lit-review pipeline: fetch → S2 enrich → curate → annotate+wiggum → cluster → synthesize → Jinja render |
| `templates/lit_review_survey.j2` | Full academic-style literature review template |
| `templates/lit_review_gaps.j2` | Gap-focused template: what's missing, what to read next |
| `backfill_metrics.py` | Reconstruct `finetune_metrics.jsonl` from training log output |
| `Modelfile` | Ollama Modelfile for `pi-qwen` (qwen2.5:7b) |
| `Modelfile.32b` | Ollama Modelfile for `pi-qwen-32b` (qwen2.5:32b Q4_K_M) |
| `finetune_output/Modelfile` | Ollama Modelfile for `nanda-annotator` (fine-tuned GGUF + stop tokens) |
| `eval.sh` | Original filesystem-level eval (superseded by `eval_suite.py`) |

**Runtime files (gitignored):**

| File | Purpose |
|------|---------|
| `runs.jsonl` | Structured run logs |
| `memory.db` | SQLite observation store |
| `search_cache.db` | SQLite search result cache (24 h TTL; auto-created) |
| `traces/` | Chrome Trace Event JSON files — drag to `ui.perfetto.dev` |

---

## Security

All tool execution passes through `security.py` before running:

- **Code scanner** — AST-based; blocks `os`, `subprocess`, `sys`, `shutil`, `socket`, `requests`, `pathlib`, and dangerous builtins (`exec`, `eval`, `open`, `__import__`)
- **Path sandbox** — `read_file` restricted to `~/Desktop` and `~/Documents`; blocklist for `.env`, SSH keys, credentials, `.pem` files
- **Injection scanner** — web search results and file contents scanned for prompt injection patterns before reaching the synthesis prompt; suspicious lines stripped (not flagged)

---

## Research notes

- [`journal.md`](journal.md) — field notes: failure modes, design decisions, experiment findings
- [`roadmap.md`](roadmap.md) — staged plan from single agent to multimodal swarm
- [`experiment-01.md`](experiment-01.md) — 9-run CRD: baseline pipeline characterisation
- [`experiment-02.md`](experiment-02.md) — 9-run CRD: harness upgrade impact (count constraint, rubric, task-type criteria)
- [`experiment-03.md`](experiment-03.md) — 9-run CRD: evaluator upgrade impact (glm4:9b → Qwen3-Coder:30b)
- [`experiment-04.md`](experiment-04.md) — 9-run CRD: producer upgrade impact (pi-qwen → pi-qwen-32b) — in progress

---

## Design principles

1. **Build for deletion** — every workaround should be trivially removable when models improve
2. **Verify externally at every stage boundary** — model self-report is not verification
3. **Add observability before adding features** — structured traces before new tools
4. **Start with the simplest pattern that meets the requirement** — single agent before orchestration
5. **Evaluator and producer must be different models** — same-model evaluation is circular
6. **The harness is the product** — the model is a commodity input; reliability lives in the harness
