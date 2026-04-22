"""
playwright_skill.py — LLM-guided website navigation via accessibility-tree snapshots.

Uses playwright's ARIA snapshot (page.aria_snapshot()) to give the LLM a structured,
role/name-based view of the page instead of raw DOM links. Actions use semantic
locators (get_by_role, get_by_text, get_by_placeholder) — more robust than href
matching or CSS selectors.

Decision loop per step:
  1. Snapshot current page: title, URL, ARIA tree (roles + names + refs)
  2. Ask oracle LLM: given goal + history + snapshot, what next?
     Actions: fill | press | click | goto | extract | fail
  3. Execute via semantic locator, repeat up to max_steps
  4. On "extract": return cleaned body text

Install:
    pip install playwright
    playwright install chromium
"""

from __future__ import annotations

import json
import re
import textwrap
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Page snapshot
# ---------------------------------------------------------------------------

def _page_snapshot(page) -> dict:
    """Return a compact snapshot of the current page using the ARIA tree."""
    title = page.title() or ""
    url   = page.url

    # ARIA snapshot — human-readable accessibility tree with roles and names.
    # Falls back to visible text excerpt if aria_snapshot() is unavailable.
    try:
        aria = page.aria_snapshot()
        aria = aria[:4000] if aria else ""
    except Exception:
        try:
            aria = (page.inner_text("body") or "").strip()
            aria = re.sub(r"\n{3,}", "\n\n", aria)[:3000]
        except Exception:
            aria = ""

    return {
        "title": title,
        "url":   url,
        "aria":  aria,
    }


def _clean_full_text(page) -> str:
    """Extract and clean the full body text of the current page."""
    try:
        text = (page.inner_text("body") or "").strip()
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text[:16_000]
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# LLM navigation oracle
# ---------------------------------------------------------------------------

_SYSTEM = textwrap.dedent("""\
    You are a web navigation agent. Given a goal and an ARIA accessibility-tree
    snapshot of the current page, decide the single best next action.
    Reply with a JSON object only — no prose.

    Actions:
      {"action": "fill",    "role": "<ARIA role>", "name": "<element label/placeholder>", "value": "<text to type>"}
          — fill an input field identified by its ARIA role and accessible name
      {"action": "press",   "key": "<key name>"}
          — press a keyboard key (e.g. "Enter", "Tab")
      {"action": "click",   "text": "<visible link or button text>"}
          — click a link or button by its visible text
      {"action": "goto",    "url": "<absolute URL>"}
          — navigate directly (use when you know the URL)
      {"action": "extract"}
          — the current page contains the target content; extract it now
      {"action": "fail",    "reason": "<why you cannot proceed>"}
          — give up after exhausting options

    Rules:
    - Use "fill" for search boxes, inputs. Identify them by role (e.g. "searchbox",
      "textbox") and name (label or placeholder text visible in the snapshot).
    - After filling a search box, always follow with {"action": "press", "key": "Enter"}.
    - Use "click" to follow links or press buttons — match the exact visible text.
    - Use "goto" only when you know the destination URL with high confidence.
    - Use "extract" only when the page content directly answers the goal.
    - Never revisit a URL already in history.
    - Output only the JSON object, nothing else.
""")


def _decide(snapshot: dict, goal: str, history: list[str], model: str) -> dict:
    import inference

    history_str = "\n".join(f"  - {u}" for u in history[-6:]) or "  (none)"
    prompt = textwrap.dedent(f"""\
        Goal: {goal}

        Current page:
          Title: {snapshot['title']}
          URL:   {snapshot['url']}

        ARIA accessibility tree (roles, names, interactive elements):
        {snapshot['aria'] or '  (empty)'}

        Already visited:
        {history_str}

        What is the single best next action?
    """)

    try:
        resp = inference.chat(
            model=model,
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user",   "content": prompt},
            ],
            options={"temperature": 0.1, "num_predict": 256},
        )
        raw = resp.message.content.strip()
        raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()
        return json.loads(raw)
    except Exception as e:
        return {"action": "fail", "reason": f"oracle error: {e}"}


# ---------------------------------------------------------------------------
# Semantic action executor
# ---------------------------------------------------------------------------

def _execute(page, decision: dict, history: list[str], timeout_ms: int) -> bool:
    """
    Execute a decision dict against the page using semantic locators.
    Returns True if navigation occurred (history should be updated).
    """
    action = decision.get("action", "fail")

    if action == "fill":
        role  = decision.get("role", "searchbox")
        name  = decision.get("name", "")
        value = decision.get("value", "")
        try:
            if name:
                loc = page.get_by_role(role, name=name)
            else:
                loc = page.get_by_role(role)
            loc.first.fill(value)
        except Exception:
            # Fallback: placeholder or generic text input
            try:
                page.get_by_placeholder(re.compile(r"search", re.IGNORECASE)).first.fill(value)
            except Exception:
                page.locator("input[type='search'], input[name*='search'], input[id*='search']").first.fill(value)
        return False

    elif action == "press":
        key = decision.get("key", "Enter")
        page.keyboard.press(key)
        page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
        return True

    elif action == "click":
        text = decision.get("text", "")
        if not text:
            return False
        try:
            page.get_by_role("link", name=text).first.click()
        except Exception:
            try:
                page.get_by_text(text, exact=False).first.click()
            except Exception:
                return False
        page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
        return True

    elif action == "goto":
        url = decision.get("url", "")
        if not url or url in history:
            return False
        page.goto(url, wait_until="domcontentloaded")
        return True

    return False


# ---------------------------------------------------------------------------
# Main navigation loop
# ---------------------------------------------------------------------------

def navigate_and_extract(
    start_url:  str,
    goal:       str,
    model:      str,
    max_steps:  int  = 12,
    headed:     bool = True,
    timeout_ms: int  = 15_000,
) -> tuple[str, str]:
    """
    Navigate to start_url and find the page matching goal.

    Returns (extracted_text, final_url).
    Raises RuntimeError on failure.
    """
    if not start_url.startswith("http"):
        start_url = "https://" + start_url

    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not headed)
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
        )
        page = ctx.new_page()
        page.set_default_timeout(timeout_ms)

        history: list[str] = []

        try:
            print(f"  [playwright] navigating to {start_url}")
            page.goto(start_url, wait_until="domcontentloaded")
            history.append(page.url)

            for step in range(max_steps):
                snapshot = _page_snapshot(page)
                print(f"  [playwright] step {step+1}/{max_steps}  {snapshot['url'][:70]}")

                decision = _decide(snapshot, goal, history, model)
                action   = decision.get("action", "fail")

                _desc = ""
                if action == "fill":
                    _desc = f": {decision.get('role','')} '{decision.get('name','')}' ← {decision.get('value','')!r}"
                elif action in ("click", "press"):
                    _desc = f": {decision.get('text') or decision.get('key','')}"
                elif action == "goto":
                    _desc = f": {decision.get('url','')[:60]}"
                elif action == "fail":
                    _desc = f": {decision.get('reason','')}"
                print(f"  [playwright] decision → {action}{_desc}")

                if action == "extract":
                    text = _clean_full_text(page)
                    final_url = page.url
                    browser.close()
                    return text, final_url

                elif action == "fail":
                    browser.close()
                    raise RuntimeError(f"navigator gave up: {decision.get('reason','unknown')}")

                else:
                    navigated = _execute(page, decision, history, timeout_ms)
                    if navigated and page.url not in history:
                        history.append(page.url)

            print("  [playwright] max steps reached — extracting current page")
            text = _clean_full_text(page)
            final_url = page.url
            browser.close()
            return text, final_url

        except RuntimeError:
            browser.close()
            raise
        except Exception as e:
            browser.close()
            raise RuntimeError(f"playwright error: {e}") from e


# ---------------------------------------------------------------------------
# Task string parser
# ---------------------------------------------------------------------------

def parse_playwright_task(task: str) -> tuple[str, str]:
    """
    Extract (start_url, goal) from a task string like:
      '/playwright go to flavortotaste.com, find the fruit-flavored water recipe'
      '/playwright https://example.com summarize the pricing page'
    Returns (url, goal).
    """
    task = re.sub(r"^/playwright\s*", "", task, flags=re.IGNORECASE).strip()

    m = re.search(
        r"(?:go\s+to\s+|visit\s+|navigate\s+to\s+|open\s+)?([a-zA-Z0-9][a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(?:/[^\s,]*)?|https?://\S+)",
        task, re.IGNORECASE,
    )
    if not m:
        raise ValueError(f"No URL found in task: {task!r}")

    url  = m.group(1)
    goal = (task[: m.start()] + " " + task[m.end() :]).strip()
    goal = re.sub(r"^(go\s+to|visit|navigate\s+to|open)\s*", "", goal, flags=re.IGNORECASE).strip(" ,")
    if not goal:
        goal = "Extract the main content of this page"

    return url, goal
