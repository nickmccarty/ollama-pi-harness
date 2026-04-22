"""
playwright_skill.py — LLM-guided website navigation and content extraction.

Uses a headed (or headless) Playwright browser to navigate to a site, find a
target page intelligently, and extract its text. Called by agent.py's /playwright
standalone handler.

Strategy per step:
  1. Snapshot current page: title, URL, visible links, search inputs, text excerpt
  2. Ask compress_model: given goal + history + page snapshot, what next?
     Actions: search | click | goto | extract
  3. Execute, repeat up to max_steps
  4. On "extract": return cleaned body text

Install:
    pip install playwright
    playwright install chromium
"""

from __future__ import annotations

import json
import re
import textwrap
from urllib.parse import urljoin, urlparse

# ---------------------------------------------------------------------------
# Page helpers
# ---------------------------------------------------------------------------

def _page_snapshot(page) -> dict:
    """Return a compact snapshot of the current page state."""
    title = page.title() or ""
    url   = page.url

    # All links with visible text (capped at 60)
    links = page.evaluate("""() =>
        Array.from(document.querySelectorAll('a[href]'))
            .filter(a => a.offsetParent !== null && a.innerText.trim().length > 1)
            .map(a => ({text: a.innerText.trim().replace(/\\s+/g, ' ').slice(0, 80),
                        href: a.href}))
            .slice(0, 60)
    """)

    # Search input selector (if any)
    search_selector = page.evaluate("""() => {
        const sel = [
            'input[type="search"]',
            'input[name*="search"]',
            'input[id*="search"]',
            'input[placeholder*="search" i]',
            'input[aria-label*="search" i]',
        ];
        for (const s of sel) {
            const el = document.querySelector(s);
            if (el) return s;
        }
        return null;
    }""")

    # Visible body text excerpt (first 2000 chars)
    try:
        body_text = (page.inner_text("body") or "").strip()
        body_text = re.sub(r"\n{3,}", "\n\n", body_text)[:2000]
    except Exception:
        body_text = ""

    return {
        "title":           title,
        "url":             url,
        "links":           links,
        "search_selector": search_selector,
        "text_excerpt":    body_text,
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
    You are a web navigation agent. Given a goal and a page snapshot, decide the
    single best next action to take. Reply with a JSON object only — no prose.

    Actions:
      {"action": "search",  "query": "<search query to type>"}
          — type a query into the page's search box
      {"action": "click",   "href": "<full URL from the links list>"}
          — navigate to this link
      {"action": "goto",    "url": "<absolute URL>"}
          — navigate directly (use when you know the URL)
      {"action": "extract"}
          — the current page contains the target content; extract it now
      {"action": "fail",    "reason": "<why you cannot proceed>"}
          — give up after exhausting options

    Rules:
    - Prefer "search" when a search box is available and the target is not yet visible.
    - Prefer "click" when a clearly relevant link is visible.
    - Use "extract" only when the page content matches the goal.
    - Never revisit a URL already in history.
    - Output only the JSON object, nothing else.
""")


def _decide(snapshot: dict, goal: str, history: list[str], model: str) -> dict:
    import inference

    history_str = "\n".join(f"  - {u}" for u in history[-6:]) or "  (none)"
    link_str = "\n".join(
        f"  [{i+1}] {l['text'][:60]}  →  {l['href']}"
        for i, l in enumerate(snapshot["links"][:30])
    )
    prompt = textwrap.dedent(f"""\
        Goal: {goal}

        Current page:
          Title: {snapshot['title']}
          URL:   {snapshot['url']}
          Search box available: {'yes (' + snapshot['search_selector'] + ')' if snapshot['search_selector'] else 'no'}

        Visible links (up to 30):
        {link_str or '  (none)'}

        Page text excerpt:
        {snapshot['text_excerpt'][:800]}

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
        # Strip markdown fences if present
        raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()
        return json.loads(raw)
    except Exception as e:
        return {"action": "fail", "reason": f"oracle error: {e}"}


# ---------------------------------------------------------------------------
# Main navigation loop
# ---------------------------------------------------------------------------

def navigate_and_extract(
    start_url:  str,
    goal:       str,
    model:      str,
    max_steps:  int  = 10,
    headed:     bool = True,
    timeout_ms: int  = 15_000,
) -> tuple[str, str]:
    """
    Navigate to start_url and find the page matching goal.

    Returns (extracted_text, final_url).
    Raises RuntimeError on failure.
    """
    # Normalise URL
    if not start_url.startswith("http"):
        start_url = "https://" + start_url

    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not headed)
        ctx  = browser.new_context(
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
                print(f"  [playwright] decision → {action}"
                      + (f": {decision.get('query') or decision.get('href','')[:60] or decision.get('url','')[:60]}" if action != "extract" else ""))

                if action == "extract":
                    text = _clean_full_text(page)
                    final_url = page.url
                    browser.close()
                    return text, final_url

                elif action == "search":
                    query = decision.get("query", goal)
                    sel   = snapshot["search_selector"]
                    if not sel:
                        # Fall back: append query to URL as ?q=
                        parsed = urlparse(page.url)
                        fallback = f"{parsed.scheme}://{parsed.netloc}/search?q={query.replace(' ', '+')}"
                        page.goto(fallback, wait_until="domcontentloaded")
                    else:
                        page.fill(sel, query)
                        page.keyboard.press("Enter")
                        page.wait_for_load_state("domcontentloaded")
                    history.append(page.url)

                elif action == "click":
                    href = decision.get("href", "")
                    if not href or href in history:
                        continue
                    page.goto(href, wait_until="domcontentloaded")
                    history.append(page.url)

                elif action == "goto":
                    url = decision.get("url", "")
                    if not url or url in history:
                        continue
                    page.goto(url, wait_until="domcontentloaded")
                    history.append(page.url)

                elif action == "fail":
                    reason = decision.get("reason", "unknown")
                    browser.close()
                    raise RuntimeError(f"navigator gave up: {reason}")

                else:
                    print(f"  [playwright] unknown action '{action}' — skipping")

            # Max steps hit — try extracting whatever we have
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
    # Strip skill token
    task = re.sub(r"^/playwright\s*", "", task, flags=re.IGNORECASE).strip()

    # Pattern: "go to <url>" or starts with http
    m = re.search(
        r"(?:go\s+to\s+|visit\s+|navigate\s+to\s+|open\s+)?([a-zA-Z0-9][a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(?:/[^\s,]*)?|https?://\S+)",
        task, re.IGNORECASE,
    )
    if not m:
        raise ValueError(f"No URL found in task: {task!r}")

    url  = m.group(1)
    # Everything before and after the URL is the goal context
    goal = (task[: m.start()] + " " + task[m.end() :]).strip()
    goal = re.sub(r"^(go\s+to|visit|navigate\s+to|open)\s*", "", goal, flags=re.IGNORECASE).strip(" ,")
    if not goal:
        goal = "Extract the main content of this page"

    return url, goal
