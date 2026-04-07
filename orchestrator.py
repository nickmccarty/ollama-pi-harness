"""
orchestrator.py — Stage 3: multi-subtask coordination layer.

Decomposes complex tasks into subtasks via the planner, executes each through
agent.run(), then assembles a unified final document from the subtask outputs.

Single-focus tasks (no subtasks in plan) are delegated directly to agent.run()
so the orchestrator is a drop-in replacement for the agent entry point.

Usage:
    python orchestrator.py "Research X and Y, synthesize into a guide and save to ~/Desktop/.../out.md"
    python orchestrator.py --no-wiggum "..."

Architecture:
    orchestrate(task)
        memory.get_context()  →  make_plan()
        if subtasks:
            assign _sub_N.md paths
            agent.run(subtask) × N          # no wiggum per subtask
            assemble(task, subtask_outputs)  # cross-referencing synthesis
            write final output
            wiggum on final output
            store memory + cleanup _sub files
        else:
            agent.run(task)                  # simple passthrough
"""

import os
import sys
import re

import ollama

from agent import (
    extract_path, write_output, count_output_items,
    extract_count_constraint, synthesize_with_count,
)
from memory import MemoryStore
from planner import make_plan
from logger import RunTrace
from wiggum import loop as wiggum_loop, EVALUATOR_MODEL

ASSEMBLY_MODEL = "pi-qwen"


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

ASSEMBLE_PROMPT = """\
Task: {task}

You have the following research documents prepared by specialist agents:

{sources}

Synthesize these into a single unified markdown document.

Requirements:
- Identify themes and patterns that appear across multiple sources
- Cross-reference related findings (e.g. "this mirrors the failure mode described in section X")
- Note any tensions or conflicts between sources
- Produce a structure that emerges from the material — do not simply concatenate the sources
- Output ONLY the markdown document starting with # — no preamble, no commentary
- Each section must include a concrete implementation note or example
- Do not mention subtask file paths or the word "synthesize"
"""


def assemble(task: str, subtask_results: list[dict], memory_context: str = "") -> str:
    """
    Synthesize multiple subtask outputs into a unified final document.
    subtask_results: list of {"desc": str, "path": str, "content": str}
    """
    source_blocks = []
    for i, r in enumerate(subtask_results, 1):
        if r.get("content"):
            source_blocks.append(
                f"### Document {i}: {r['desc']}\n\n{r['content']}"
            )

    if not source_blocks:
        return ""

    sources_text = "\n\n---\n\n".join(source_blocks)
    memory_block = f"\nRelevant past context:\n{memory_context}\n" if memory_context else ""

    prompt = ASSEMBLE_PROMPT.format(task=task, sources=sources_text) + memory_block

    response = ollama.chat(
        model=ASSEMBLY_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.1},
    )
    return response["message"]["content"].strip()


# ---------------------------------------------------------------------------
# Subtask execution
# ---------------------------------------------------------------------------

def _assign_paths(subtask_descs: list[str], workspace: str) -> list[dict]:
    """Convert subtask descriptions to runnable task dicts with assigned output paths."""
    results = []
    for i, desc in enumerate(subtask_descs, 1):
        # Normalise: ensure the description starts with a research directive
        desc = desc.strip().rstrip(".")
        sub_path = os.path.join(workspace, f"_sub_{i}.md")
        # Use forward slashes so agent.py's path regex matches on Windows
        sub_path_fwd = sub_path.replace("\\", "/")
        task_str = f"{desc} and save to {sub_path_fwd}"
        results.append({"desc": desc, "task": task_str, "path": sub_path})
    return results


def _run_subtasks(subtask_defs: list[dict]) -> list[dict]:
    """Execute each subtask through agent.run(). Returns defs enriched with content."""
    import agent  # import here to avoid circular at module level

    for sub in subtask_defs:
        print(f"\n{'='*50}")
        print(f"[orchestrator] subtask: {sub['desc']}")
        print(f"{'='*50}")
        try:
            agent.run(sub["task"], use_wiggum=False)
        except SystemExit:
            print(f"  [orchestrator] subtask exited early — continuing")

        expanded = os.path.expanduser(sub["path"])
        if os.path.exists(expanded):
            with open(expanded, "r", encoding="utf-8") as f:
                sub["content"] = f.read()
            print(f"  [orchestrator] subtask output: {len(sub['content'])} chars")
        else:
            sub["content"] = ""
            print(f"  [orchestrator] subtask produced no output")

    return subtask_defs


def _cleanup_subtask_files(subtask_defs: list[dict]):
    """Remove temporary subtask output files."""
    for sub in subtask_defs:
        expanded = os.path.expanduser(sub["path"])
        try:
            if os.path.exists(expanded):
                os.remove(expanded)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Main orchestration loop
# ---------------------------------------------------------------------------

def orchestrate(task: str, use_wiggum: bool = True):
    """
    Main entry point. Decomposes and coordinates multi-subtask runs,
    or delegates to agent.run() for single-focus tasks.
    """
    # Determine output path
    output_path = extract_path(task)
    if not output_path:
        print("[error] no .md output path found in task — include a file path ending in .md")
        sys.exit(1)

    workspace = os.path.dirname(os.path.expanduser(output_path))
    if workspace:
        os.makedirs(workspace, exist_ok=True)

    # Memory + planning
    memory = MemoryStore()
    memory_context = memory.get_context(task)
    if memory_context:
        print(f"[orchestrator] memory: {memory_context.count('**[')} observation(s)")
    else:
        print("[orchestrator] memory: no relevant history")

    print("[orchestrator] planning...")
    plan = make_plan(task, memory_context)
    print(f"[orchestrator] plan: {plan.task_type} / {plan.complexity} / "
          f"{len(plan.subtasks)} subtask(s)")
    if plan.subtasks:
        for i, s in enumerate(plan.subtasks, 1):
            print(f"  {i}. {s}")

    # --- Simple task: no subtasks → delegate to agent ---
    if not plan.subtasks:
        print("[orchestrator] single-focus task — delegating to agent\n")
        import agent
        agent.run(task, use_wiggum=use_wiggum)
        return

    # --- Complex task: orchestrate subtasks ---
    trace = RunTrace(task=task, producer_model=ASSEMBLY_MODEL, evaluator_model=EVALUATOR_MODEL)
    trace.log_plan(plan.to_dict())
    trace.log_memory_hits(memory_context.count("**[") if memory_context else 0)
    trace.data["orchestrated"] = True
    trace.data["subtask_count"] = len(plan.subtasks)

    try:
        subtask_defs = _assign_paths(plan.subtasks, workspace)

        # Execute subtasks
        print(f"\n[orchestrator] executing {len(subtask_defs)} subtask(s)...")
        subtask_defs = _run_subtasks(subtask_defs)

        completed = [s for s in subtask_defs if s.get("content")]
        print(f"\n[orchestrator] {len(completed)}/{len(subtask_defs)} subtasks produced output")

        if not completed:
            print("[error] all subtasks failed — aborting")
            trace.finish("ERROR")
            sys.exit(1)

        # Assemble final output
        print("\n[orchestrator] assembling final document...")
        content = assemble(task, completed, memory_context=memory_context)

        if not content.strip():
            print("[error] assembly produced empty content")
            trace.finish("ERROR")
            sys.exit(1)

        # Count constraint on assembled output
        expected_count = plan.expected_sections or extract_count_constraint(task)
        if expected_count is not None:
            actual_count = count_output_items(content)
            if actual_count != expected_count:
                print(f"[count check] expected {expected_count}, got {actual_count} — retrying assembly")
                content = synthesize_with_count(task, content, expected_count)

        print("\n" + content[:1000] + ("..." if len(content) > 1000 else "") + "\n")
        write_output(content, output_path, trace)

        # Wiggum verification on the final assembled output
        if use_wiggum:
            wiggum_trace = wiggum_loop(task, output_path)
            trace.log_wiggum(wiggum_trace)
            print(f"\n[wiggum] {wiggum_trace['final']} after {len(wiggum_trace['rounds'])} round(s)")
            for r in wiggum_trace["rounds"]:
                print(f"  round {r['round']}: score={r['score']}/10  passed={r['passed']}")
            final_status = wiggum_trace["final"]
        else:
            trace.finish("PASS")
            final_status = "PASS"

        # Store memory for the orchestrated run
        print("\n  [memory] compressing orchestrated run...")
        try:
            obs = memory.compress_and_store(
                task=task,
                task_type=plan.task_type,
                tool_calls=trace.data.get("tool_calls", []),
                output_content=content,
                output_lines=trace.data.get("output_lines"),
                output_bytes=trace.data.get("output_bytes"),
                output_path=trace.data.get("output_path"),
                wiggum_scores=trace.data.get("wiggum_scores", []),
                final=final_status,
            )
            print(f"  [memory] stored: {obs['title']!r}")
        except Exception as e:
            print(f"  [memory] compression failed (non-fatal): {e}")

    except Exception as e:
        print(f"[error] orchestration failed: {e}")
        trace.finish("ERROR")
        raise
    finally:
        _cleanup_subtask_files(subtask_defs if 'subtask_defs' in dir() else [])


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print('usage: python orchestrator.py "<task>"')
        print('       python orchestrator.py --no-wiggum "<task>"')
        sys.exit(1)

    no_wiggum = "--no-wiggum" in args
    task_args = [a for a in args if a != "--no-wiggum"]
    orchestrate(" ".join(task_args), use_wiggum=not no_wiggum)
