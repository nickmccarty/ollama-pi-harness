# harness-engineering

A local Ollama agent harness built incrementally from failure. Research, verify, remember, plan, orchestrate — all running on local models with no external API keys.

The central question: can open-source models running locally approach the utility of frontier models through harness engineering alone? The premise is that the model is not the 80% factor. The harness is.

---

## Architecture

```
orchestrator.py          ← compound tasks: decompose → run subtasks → assemble
    |
    agent.py             ← single-focus tasks: plan → search → synthesize → write
        |
        ├── planner.py       search queries, synthesis notes, subtask decomposition
        ├── memory.py        retrieve relevant past observations (SQLite FTS5)
        ├── wiggum.py        evaluate → revise → verify loop
        ├── vision.py        image-to-text preprocessing (llama3.2-vision)
        └── security.py      code scanner, path sandbox, injection scanner

shared: logger.py / runs.jsonl, memory.py / memory.db
```

**Run lifecycle (single-focus task):**
```
memory.get_context()
  → make_plan()                   glm4:9b analyses task + memory
    → gather_research()           2 planned web searches + quality floor fallback
      → vision preprocessing      llama3.2-vision if image paths detected
      → read_file injection        text file contents if file paths detected
      → run_python tool loop       optional pre-synthesis code execution
        → synthesize()             pi-qwen produces markdown document
          → count check + retry   harness-enforced section count
            → write output
              → wiggum loop        evaluate → revise → verify (up to 3 rounds)
                → compress_and_store()   glm4:9b compresses run into memory
```

---

## Prerequisites

**Ollama models required:**
```bash
ollama pull qwen2.5:7b          # base model for pi-qwen
ollama pull glm4:9b             # evaluator + planner + memory compression
ollama pull llama3.2-vision     # vision preprocessing
```

**Create the producer model:**
```bash
ollama create pi-qwen -f Modelfile
```

**Python environment (conda):**
```bash
conda create -n ollama-pi python=3.11
conda activate ollama-pi
pip install ollama ddgs
```

---

## Usage

**Single-focus task:**
```bash
python agent.py "Search for the top 5 context engineering techniques and save to ~/Desktop/output.md"
python agent.py --no-wiggum "..."    # skip verification loop
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
```

**Inspect memory:**
```bash
python memory.py                           # list recent observations
python memory.py --search "context window" # test retrieval
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

---

## Models

| Role | Model | Notes |
|------|-------|-------|
| Producer | `pi-qwen` (qwen2.5:7b) | Custom Modelfile — task-completion focus, tool-capable |
| Evaluator / Planner / Compressor | `glm4:9b` | Different architecture from producer — avoids circular evaluation |
| Vision | `llama3.2-vision` | Image-to-text preprocessing only; does not replace producer |

---

## Files

| File | Purpose |
|------|---------|
| `agent.py` | Single-agent research + write pipeline |
| `orchestrator.py` | Multi-subtask coordination and assembly |
| `planner.py` | Pre-execution task analysis — search queries, subtask decomposition |
| `memory.py` | SQLite + FTS5 persistent observation store |
| `wiggum.py` | Evaluate → revise → verify loop (decimalized rubric, task-type criteria) |
| `vision.py` | llama3.2-vision routing for image inputs |
| `security.py` | Code scanner, path sandbox, prompt injection scanner |
| `logger.py` | Structured per-run trace — appends to `runs.jsonl` |
| `eval_suite.py` | Regression harness — 5 tasks × 6 criteria |
| `analytics.py` | Cross-run analysis from `runs.jsonl` |
| `analyze_exp01.py` | Experiment-01 analysis script |
| `analyze_exp02.py` | Experiment-02 analysis script |
| `Modelfile` | Ollama Modelfile for `pi-qwen` |
| `eval.sh` | Original filesystem-level eval (superseded by `eval_suite.py`) |

**Runtime files (gitignored):**

| File | Purpose |
|------|---------|
| `runs.jsonl` | Structured run logs |
| `memory.db` | SQLite observation store |

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

---

## Design principles

1. **Build for deletion** — every workaround should be trivially removable when models improve
2. **Verify externally at every stage boundary** — model self-report is not verification
3. **Add observability before adding features** — structured traces before new tools
4. **Start with the simplest pattern that meets the requirement** — single agent before orchestration
5. **Evaluator and producer must be different models** — same-model evaluation is circular
6. **The harness is the product** — the model is a commodity input; reliability lives in the harness
