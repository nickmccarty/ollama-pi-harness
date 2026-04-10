"""
skills.py — skill registry and invocation layer for the harness agent.

Skills extend the agent pipeline at defined hook points:

  pre_research   — modify search behaviour (e.g. force deep search)
  pre_synthesis  — inject additional instructions into the synthesis prompt
  post_synthesis — transform or augment the synthesized output
  post_wiggum    — run additional evaluation after the verification loop

Invocation — explicit slash commands in the task string:
    python agent.py "/annotate /cite Search for RAG papers and save to output.md"

Invocation — automatic, via per-skill trigger predicates:
    Planner complexity="high"   → panel auto-activates
    Task mentions "paper"       → annotate auto-activates
    Task mentions "exhaustive"  → deep auto-activates

Skills are loaded lazily — importing skills.py does not import kg_gen, panel, etc.
"""

import os
import re

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
# Each entry:
#   description  — shown in /skills listing
#   hook         — pipeline stage: pre_research | pre_synthesis | post_synthesis | post_wiggum
#   prompt       — text injected into synthesis prompt (pre_synthesis only); None otherwise
#   auto         — callable(task: str, plan) -> bool; None = explicit-only
# ---------------------------------------------------------------------------

REGISTRY: dict[str, dict] = {

    "annotate": {
        "description": "Inject the 8-move Nanda Annotated Abstract framework into synthesis",
        "hook":        "pre_synthesis",
        "prompt": (
            "Structure your output using the Nanda Annotated Abstract framework. "
            "For each major finding or concept, address these eight dimensions: "
            "**Topic** (what this is), **Motivation** (why it matters), "
            "**Contribution** (what is new or key), **Detail/Nuance** (important specifics or caveats), "
            "**Evidence/Contribution 2** (supporting findings), **Weaker result** (limitations), "
            "**Narrow impact** (immediate application), **Broad impact** (wider implications). "
            "Use the bold header for each dimension on its own line."
        ),
        "auto": lambda task, plan: any(
            w in task.lower() for w in ["paper", "abstract", "literature", "survey", "review"]
        ),
    },

    "kg": {
        "description": "Generate a D3.js knowledge graph from the synthesized content",
        "hook":        "post_synthesis",
        "prompt":      None,
        "auto": lambda task, plan: bool(re.search(
            r"knowledge graph|\bkg\b|visuali[sz]e", task, re.IGNORECASE
        )),
    },

    "panel": {
        "description": "Run the 3-persona evaluation panel (Domain Practitioner, Critical Reviewer, Informed Newcomer)",
        "hook":        "post_wiggum",
        "prompt":      None,
        "auto": lambda task, plan: plan.complexity == "high",
    },

    "deep": {
        "description": "Force MAX_SEARCH_ROUNDS, disable novelty saturation gate",
        "hook":        "pre_research",
        "prompt":      None,
        "auto": lambda task, plan: bool(re.search(
            r"\bcomprehensive\b|\bthorough\b|\bexhaustive\b|\bin.depth\b|\bdeep.dive\b",
            task, re.IGNORECASE
        )),
    },

    "cite": {
        "description": "Require source attribution and citations for each claim",
        "hook":        "pre_synthesis",
        "prompt": (
            "For each significant claim, technique, or recommendation, include a source reference "
            "in parentheses (e.g. the URL or publication name from the research context). "
            "If a claim cannot be attributed to the provided sources, flag it explicitly as inferred."
        ),
        "auto": None,   # explicit only — too broad to auto-trigger
    },

    "annotated-abstract": {
        "description": "Alias for /annotate",
        "hook":        "pre_synthesis",
        "prompt":      None,   # resolved to "annotate" at parse time
        "auto":        None,
    },

}

# Aliases — resolved during parse
_ALIASES = {"annotated-abstract": "annotate"}


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_skills(task: str) -> tuple[str, list[str]]:
    """
    Extract /skill_name tokens from the task string.
    Returns (clean_task, deduplicated_list_of_skill_names).
    Tokens not in REGISTRY are left in the task string unchanged.
    """
    parts      = task.split()
    skill_names: list[str] = []
    clean      = []

    for part in parts:
        if part.startswith("/"):
            raw  = part[1:]
            name = _ALIASES.get(raw, raw)
            if name in REGISTRY:
                if name not in skill_names:
                    skill_names.append(name)
                continue   # strip from task
        clean.append(part)

    return " ".join(clean), skill_names


def auto_activate(task: str, plan) -> list[str]:
    """
    Return skill names whose auto-trigger fires for this task + plan.
    Safe — never raises; trigger errors are silently skipped.
    """
    active = []
    for name, skill in REGISTRY.items():
        if name in _ALIASES.values() and name != name:   # skip alias targets
            continue
        trigger = skill.get("auto")
        if not trigger:
            continue
        try:
            if trigger(task, plan):
                active.append(name)
        except Exception:
            pass
    return active


def merge_skills(explicit: list[str], auto: list[str]) -> list[str]:
    """Deduplicate, preserving explicit-first order."""
    seen   = set(explicit)
    merged = list(explicit)
    for s in auto:
        if s not in seen:
            seen.add(s)
            merged.append(s)
    return merged


# ---------------------------------------------------------------------------
# Hook helpers
# ---------------------------------------------------------------------------

def get_prompt_injections(active_skills: list[str], hook: str) -> str:
    """
    Concatenate prompt injections for all active skills at the given hook.
    Returns an empty string if none match.
    """
    parts = []
    for name in active_skills:
        skill = REGISTRY.get(name, {})
        if skill.get("hook") == hook and skill.get("prompt"):
            parts.append(skill["prompt"])
    return "\n\n".join(parts)


def skills_at_hook(active_skills: list[str], hook: str) -> list[str]:
    """Return the subset of active_skills that fire at the given hook."""
    return [n for n in active_skills if REGISTRY.get(n, {}).get("hook") == hook]


# ---------------------------------------------------------------------------
# Post-synthesis handler
# ---------------------------------------------------------------------------

def run_post_synthesis(
    active_skills: list[str],
    content:       str,
    task:          str,
    output_path:   str,
    producer_model: str,
) -> dict:
    """
    Run all post_synthesis skill handlers.
    Returns a dict of results keyed by skill name (e.g. {"kg": "/path/to/graph.html"}).
    """
    results = {}
    for name in skills_at_hook(active_skills, "post_synthesis"):
        if name == "kg":
            results["kg"] = _handle_kg(content, task, output_path, producer_model)
    return results


def _handle_kg(content: str, task: str, output_path: str, producer_model: str) -> str | None:
    """Generate a D3.js knowledge graph from synthesized content."""
    try:
        from kg_gen import generate_kg, render_html
        from pathlib import Path
        from datetime import datetime

        article = content[:4000]
        graph_data = generate_kg(article, producer_model, num_nodes=12, max_edge_density=3)

        ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir   = Path(output_path).parent if output_path else Path("graphs")
        kg_path   = out_dir / f"kg_{ts}.html"

        render_html(graph_data, kg_path, title=task[:60], model=producer_model, article_snippet=article)
        print(f"  [skill:kg] graph → {kg_path.resolve()}")
        return str(kg_path.resolve())
    except Exception as e:
        print(f"  [skill:kg] failed: {e}")
        return None


# ---------------------------------------------------------------------------
# CLI — list available skills
# ---------------------------------------------------------------------------

def _print_registry():
    print("\nAvailable skills (prefix task with /name to activate):\n")
    for name, skill in REGISTRY.items():
        if name in _ALIASES:
            continue
        hook  = skill["hook"]
        desc  = skill["description"]
        auto  = "auto" if skill.get("auto") else "explicit"
        print(f"  /{name:<22} [{hook:<15}] [{auto}]  {desc}")
    print()


if __name__ == "__main__":
    _print_registry()
