"""
panel.py — Multi-persona evaluation panel using TinyTroupe.

Three TinyPerson reviewers evaluate a document from distinct angles:
  1. Domain Practitioner  — technical depth, accuracy, actionability
  2. Critical Reviewer    — coverage gaps, missing context, unsupported claims
  3. Informed Newcomer    — clarity, accessibility, whether a newcomer could act on it

Each reviewer returns a structured score + issues + strengths dict.
Panel results are merged into wiggum's issues list before revision, and
logged to runs.jsonl for downstream distillation / preference learning.

Usage (module):
    from panel import run_panel
    reviews = run_panel(task, content, model="Qwen3-Coder:30b")

Usage (standalone test):
    python panel.py "<task>" path/to/output.md

Enabled in wiggum via WIGGUM_PANEL=1 environment variable.

Environment:
    conda activate ollama-pi
    pip install tinytroupe  (already installed)
"""

import json
import os
import re
import sys

try:
    from tinytroupe.agent import TinyPerson
    from tinytroupe.clients import force_api_type
    TINYTROUPE_AVAILABLE = True
except ImportError:
    TINYTROUPE_AVAILABLE = False

# ---------------------------------------------------------------------------
# Persona definitions
# ---------------------------------------------------------------------------

PANEL_PERSONAS = [
    {
        "name": "Domain Practitioner",
        "occupation": {
            "title": "Senior Software Engineer",
            "description": (
                "I have 10+ years building production systems. "
                "I evaluate whether technical content is actionable and production-ready. "
                "I look for concrete implementation details, not just conceptual descriptions. "
                "I flag when examples are toy-level rather than production-grade."
            ),
        },
        "personality": {
            "traits": [
                "I am rigorous and skeptical of vague claims.",
                "I always ask: could a practitioner act on this today?",
                "I distinguish between knowing a concept and knowing how to implement it.",
            ]
        },
        "focus": "technical depth, accuracy, and practical actionability",
    },
    {
        "name": "Critical Reviewer",
        "occupation": {
            "title": "Technical Editor",
            "description": (
                "I review technical documentation for completeness and intellectual rigor. "
                "I systematically identify gaps — what an expert would expect to see but is missing. "
                "I flag unsupported claims, missing caveats, and one-sided coverage."
            ),
        },
        "personality": {
            "traits": [
                "I am thorough and systematic — I read for what is absent, not just what is present.",
                "I flag assumptions the author made that may not hold.",
                "I check whether multiple angles of a topic are covered, not just the easiest ones.",
            ]
        },
        "focus": "coverage gaps, missing context, and unsupported claims",
    },
    {
        "name": "Informed Newcomer",
        "occupation": {
            "title": "Developer",
            "description": (
                "I have general programming knowledge but am learning this specific topic for the first time. "
                "I test whether a document is comprehensible to someone without prior domain knowledge. "
                "I flag jargon that is not explained and concepts assumed without introduction."
            ),
        },
        "personality": {
            "traits": [
                "I read documents asking: could I act on this after reading it?",
                "I flag any step that requires knowledge the document does not provide.",
                "I value clarity and concrete examples over conceptual completeness.",
            ]
        },
        "focus": "clarity, accessibility, and whether a newcomer could follow and act on this",
    },
]

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

PANEL_SPEECH = """\
Task this document was written for:
{task}

Document:
{content}

Review this document from your perspective, focusing on: {focus}

Be specific — name sections and exact issues. Keep your response concise.

Respond with valid JSON only, no preamble:
{{
  "score": integer 0-10,
  "issues": ["specific issue naming the section and exactly what is missing or wrong"],
  "strengths": ["specific thing done well"]
}}"""


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def _configure_tinytroupe(model: str):
    """Point TinyTroupe at the local Ollama endpoint with the given model."""
    force_api_type("ollama")
    # Override model and base_url in TinyTroupe's live config object
    import tinytroupe
    cfg = tinytroupe.config  # ConfigParser instance
    cfg.set("OpenAI", "model", model)
    cfg.set("OpenAI", "base_url", "http://localhost:11434/v1")


def _create_persona(persona_def: dict) -> "TinyPerson":
    """Create a fresh TinyPerson from a persona definition dict."""
    agent = TinyPerson(persona_def["name"])
    agent.define("occupation", persona_def["occupation"])
    agent.define("personality", persona_def["personality"])
    return agent


def _parse_response(actions: list, persona_name: str) -> dict:
    """
    Extract score/issues/strengths from a list of TinyPerson actions.
    Falls back to heuristic parsing if the model didn't return JSON.
    """
    raw = ""
    for action in (actions or []):
        if isinstance(action, dict) and action.get("type") == "TALK":
            raw = action.get("content", "")
            break

    # Try direct JSON parse
    try:
        # Strip markdown fences if present
        clean = re.sub(r"^```(?:json)?\s*", "", raw.strip())
        clean = re.sub(r"\s*```$", "", clean)
        data = json.loads(clean)
        return {
            "persona":   persona_name,
            "score":     int(data.get("score", 5)),
            "issues":    [i for i in data.get("issues", []) if i],
            "strengths": [s for s in data.get("strengths", []) if s],
            "raw":       raw,
        }
    except (json.JSONDecodeError, ValueError):
        pass

    # Heuristic fallback — extract bullet points
    issues   = re.findall(r"(?:issue|problem|missing|gap|unclear)[:\s-]+(.+)", raw, re.IGNORECASE)
    strength = re.findall(r"(?:strength|good|well|positive)[:\s-]+(.+)", raw, re.IGNORECASE)
    score_m  = re.search(r"\b(\d(?:\.\d)?)\s*(?:/\s*10|out of 10)\b", raw)
    score    = int(float(score_m.group(1))) if score_m else 5

    return {
        "persona":   persona_name,
        "score":     score,
        "issues":    issues[:5],
        "strengths": strength[:3],
        "raw":       raw,
    }


def run_panel(task: str, content: str, model: str) -> list[dict]:
    """
    Run the three-persona evaluation panel on a document.

    Returns a list of review dicts, one per persona:
        [{"persona": str, "score": int, "issues": [...], "strengths": [...], "raw": str}, ...]

    Returns [] if TinyTroupe is unavailable or all personas fail.
    """
    if not TINYTROUPE_AVAILABLE:
        print("  [panel] TinyTroupe not available — skipping panel")
        return []

    try:
        _configure_tinytroupe(model)
    except Exception as e:
        print(f"  [panel] config failed ({e}) — skipping panel")
        return []

    reviews = []
    content_excerpt = content[:5000]  # cap to keep prompts manageable

    for persona_def in PANEL_PERSONAS:
        name = persona_def["name"]
        print(f"  [panel] {name}...")
        try:
            agent = _create_persona(persona_def)
            speech = PANEL_SPEECH.format(
                task=task,
                content=content_excerpt,
                focus=persona_def["focus"],
            )
            actions = agent.listen_and_act(
                speech=speech,
                return_actions=True,
                communication_display=False,
            )
            review = _parse_response(actions, name)
            print(f"    score={review['score']}/10  issues={len(review['issues'])}")
            reviews.append(review)
        except Exception as e:
            print(f"  [panel] {name} failed ({e}) — skipping")

    return reviews


def panel_issues(reviews: list[dict]) -> list[str]:
    """Flatten panel reviews into a deduplicated issues list prefixed by persona name."""
    seen = set()
    issues = []
    for r in reviews:
        for issue in r.get("issues", []):
            key = issue.lower().strip()
            if key not in seen:
                seen.add(key)
                issues.append(f"[{r['persona']}] {issue}")
    return issues


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('usage: python panel.py "<task>" path/to/output.md [model]')
        sys.exit(1)

    _task    = sys.argv[1]
    _path    = sys.argv[2]
    _model   = sys.argv[3] if len(sys.argv) > 3 else "Qwen3-Coder:30b"

    with open(_path, "r", encoding="utf-8") as _f:
        _content = _f.read()

    print(f"\n[panel] running 3-persona evaluation panel (model={_model})\n")
    _reviews = run_panel(_task, _content, _model)

    for r in _reviews:
        print(f"\n--- {r['persona']} (score={r['score']}/10) ---")
        for i in r.get("issues", []):
            print(f"  issue: {i}")
        for s in r.get("strengths", []):
            print(f"  strength: {s}")

    print(f"\n[panel] merged issues:")
    for i in panel_issues(_reviews):
        print(f"  - {i}")
