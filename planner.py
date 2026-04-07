"""
planner.py — pre-execution task analysis and query planning.

Uses memory context + glm4:9b to produce a structured Plan before research begins.
The plan informs three downstream stages:
  - gather_research : uses planned search queries instead of auto-generating them
  - synthesize      : injects prior work summary + planner notes as context
  - count check     : uses plan.expected_sections when regex misses the constraint

Usage:
    from planner import make_plan, Plan
    plan = make_plan(task, memory_context)
"""

import json
import re
from dataclasses import dataclass, field, asdict

import ollama

PLANNER_MODEL = "glm4:9b"

PLAN_PROMPT = """\
You are a task planner for an AI research agent.

Task: {task}
{memory_block}
Produce a structured execution plan. Respond with ONLY valid JSON — no explanation, no markdown fences:

{{
  "task_type": "enumerated|best_practices|research",
  "complexity": "low|medium|high",
  "expected_sections": <integer or null>,
  "search_queries": ["query1", "query2"],
  "prior_work_summary": "<one sentence about relevant prior work, or empty string>",
  "notes": "<one actionable sentence for the producer>",
  "subtasks": []
}}

Rules:
- task_type: "enumerated" if task says "top N" or "N most/common/key/best"; "best_practices" if asking for practices/strategies/guidelines; "research" otherwise
- complexity: "low" for simple factual lookups; "medium" for standard research; "high" for tasks requiring synthesis across 2+ distinct domains
- expected_sections: the integer N from "top N" / "N most", null if not specified
- search_queries: exactly 2 specific, complementary queries — make them concrete and distinct from each other
- prior_work_summary: one sentence summarising what the memory shows, or "" if no relevant history
- notes: one specific actionable note (e.g. "specificity was weak last time — include concrete tool names and version numbers")
- subtasks: EMPTY ARRAY [] for single-focus tasks. Populate with 2-3 items ONLY when the task explicitly asks to research multiple distinct domains and combine/synthesize/integrate them. Each item must be a self-contained WEB RESEARCH directive (e.g. "Research the top 3 failure modes in multi-agent AI systems") — NO synthesis, assembly, or writing steps (the orchestrator handles final assembly). NO file paths.
"""


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Plan:
    task_type: str = "research"
    complexity: str = "medium"
    expected_sections: int | None = None
    search_queries: list[str] = field(default_factory=list)
    prior_work_summary: str = ""
    notes: str = ""
    subtasks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def synthesis_context(self) -> str:
        """Build the context block injected into synthesis alongside memory."""
        lines = []
        if self.prior_work_summary:
            lines.append(f"**Prior work:** {self.prior_work_summary}")
        if self.notes:
            lines.append(f"**Planner note:** {self.notes}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Planning
# ---------------------------------------------------------------------------

def make_plan(task: str, memory_context: str = "") -> Plan:
    """
    Analyse the task and memory context to produce a Plan.
    Returns a default Plan on any failure — never raises.
    """
    memory_block = f"Relevant past work:\n{memory_context}\n\n" if memory_context else ""
    prompt = PLAN_PROMPT.format(task=task, memory_block=memory_block)

    try:
        response = ollama.chat(
            model=PLANNER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.1},
        )
        text = response["message"]["content"].strip()
        plan = _parse_plan(text)
        return plan
    except Exception as e:
        print(f"  [planner] failed ({e}) — using defaults")
        return Plan()


def _parse_plan(text: str) -> Plan:
    """Parse the JSON plan response. Falls back to defaults on any error."""
    # Strip markdown code fences if present
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)

    json_match = re.search(r'\{.*\}', text.strip(), re.DOTALL)
    if not json_match:
        return Plan()

    try:
        data = json.loads(json_match.group(0))
    except json.JSONDecodeError:
        return Plan()

    # expected_sections: accept integer or stringified integer, reject anything else
    raw_sections = data.get("expected_sections")
    expected_sections = None
    if raw_sections is not None:
        try:
            expected_sections = int(raw_sections)
        except (ValueError, TypeError):
            pass

    queries = [
        q.strip() for q in data.get("search_queries", [])
        if isinstance(q, str) and q.strip()
    ]

    # Filter out synthesis/assembly subtasks — those are the orchestrator's job
    _ASSEMBLY_WORDS = re.compile(
        r'\b(synthesize|synthesise|assemble|combine|integrate|unify|merge|compile|write|create)\b',
        re.IGNORECASE,
    )
    raw_subtasks = data.get("subtasks", [])
    subtasks = [
        s.strip() for s in raw_subtasks
        if isinstance(s, str) and s.strip() and not _ASSEMBLY_WORDS.search(s)
    ]

    return Plan(
        task_type=data.get("task_type", "research"),
        complexity=data.get("complexity", "medium"),
        expected_sections=expected_sections,
        search_queries=queries,
        prior_work_summary=str(data.get("prior_work_summary", "") or "").strip(),
        notes=str(data.get("notes", "") or "").strip(),
        subtasks=subtasks,
    )


# ---------------------------------------------------------------------------
# CLI — test the planner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    from memory import MemoryStore

    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else (
        "Search for the top 3 context window management strategies for production LLM applications "
        "and save to ~/Desktop/harness-engineering/test-plan.md"
    )

    store = MemoryStore()
    memory_ctx = store.get_context(task)

    print(f"Task: {task}")
    print(f"Memory hits: {memory_ctx.count('**[') if memory_ctx else 0}\n")
    print("[planner] generating plan...")

    plan = make_plan(task, memory_ctx)

    print(f"\nPlan:")
    print(f"  task_type:         {plan.task_type}")
    print(f"  complexity:        {plan.complexity}")
    print(f"  expected_sections: {plan.expected_sections}")
    print(f"  search_queries:")
    for q in plan.search_queries:
        print(f"    - {q}")
    print(f"  prior_work_summary: {plan.prior_work_summary!r}")
    print(f"  notes:              {plan.notes!r}")
    print(f"  subtasks ({len(plan.subtasks)}):")
    for s in plan.subtasks:
        print(f"    - {s}")
