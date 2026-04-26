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
import os
import platform
import re
import subprocess
import tempfile
import textwrap
import time
from urllib.parse import urlparse

# Module-level handle prevents GC when keeping the browser alive between tasks.
_persistent_browser_proc: "subprocess.Popen | None" = None

_CDP_PORT        = int(os.environ.get("HARNESS_CDP_PORT", "9222"))
_STATE_FILE      = os.path.join(tempfile.gettempdir(), "harness_browser_state.json")
_SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")


# ---------------------------------------------------------------------------
# Browser state helpers (mirrors agent.py — kept local to avoid circular import)
# ---------------------------------------------------------------------------

def _read_state() -> dict:
    try:
        if os.path.exists(_STATE_FILE):
            return json.loads(open(_STATE_FILE, encoding="utf-8").read())
    except Exception:
        pass
    return {}


def _write_state(data: dict):
    try:
        with open(_STATE_FILE, "w", encoding="utf-8") as f:
            f.write(json.dumps(data))
    except Exception:
        pass


def _clear_state():
    try:
        os.unlink(_STATE_FILE)
    except Exception:
        pass


def _launch_detached(exe: str, port: int) -> "subprocess.Popen":
    """Launch Chromium as a detached OS process so it outlives the agent subprocess."""
    args = [exe, f"--remote-debugging-port={port}",
            "--no-first-run", "--no-default-browser-check",
            "--no-sandbox", "about:blank"]
    if platform.system() == "Windows":
        return subprocess.Popen(
            args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    return subprocess.Popen(
        args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def _settle(page, timeout_ms: int = 4000):
    """Best-effort networkidle wait so JS-rendered ARIA roles are available."""
    try:
        page.wait_for_load_state("networkidle", timeout=timeout_ms)
    except Exception:
        pass


def _wait_for_cdp(port: int, retries: int = 10, delay: float = 0.5):
    import urllib.request as _ur
    for _ in range(retries):
        time.sleep(delay)
        try:
            _ur.urlopen(f"http://localhost:{port}/json/version", timeout=1)
            return
        except Exception:
            pass
    raise RuntimeError(f"CDP endpoint on port {port} did not respond after {retries * delay:.0f}s")


# ---------------------------------------------------------------------------
# Page snapshot
# ---------------------------------------------------------------------------

def _page_snapshot(page) -> dict:
    """Return a compact snapshot of the current page using the ARIA tree."""
    title = page.title() or ""
    url   = page.url

    aria = ""
    try:
        aria = (page.aria_snapshot() or "").strip()
        aria = aria[:4000]
    except Exception:
        pass

    if not aria:
        # ARIA empty (JS-heavy page not yet rendered) — fall back to body text
        try:
            aria = (page.inner_text("body") or "").strip()
            aria = re.sub(r"\n{3,}", "\n\n", aria)[:3000]
        except Exception:
            aria = ""

    return {"title": title, "url": url, "aria": aria}


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
        role  = decision.get("role", "textbox")
        name  = decision.get("name", "")
        value = decision.get("value", "")
        _target = None
        try:
            _loc = page.get_by_role(role, name=name) if name else page.get_by_role(role)
            _target = _loc.first
            _target.fill(value)
        except Exception:
            try:
                _target = page.get_by_placeholder(re.compile(r"search", re.IGNORECASE)).first
                _target.fill(value)
            except Exception:
                try:
                    _target = page.locator(
                        "input[type='search'], input[name*='search'], input[id*='search']"
                    ).first
                    _target.fill(value)
                except Exception:
                    _target = None

        # Auto-submit search inputs so the LLM never needs a separate press step
        # (avoids autocomplete-reopen loops where the model re-fills instead of pressing Enter)
        _is_search = role == "searchbox" or "search" in (name or "").lower()
        if _is_search and _target is not None:
            try:
                _target.press("Enter")
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
                except Exception:
                    pass
                return True
            except Exception:
                pass
        return False

    elif action == "press":
        key = decision.get("key", "Enter")
        # Dispatch to the focused DOM element so autocomplete dropdowns can't
        # steal the keypress; fall back to global keyboard if nothing is focused.
        try:
            focused = page.locator(":focus")
            if focused.count():
                focused.first.press(key)
            else:
                page.keyboard.press(key)
        except Exception:
            page.keyboard.press(key)
        try:
            page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
        except Exception:
            pass  # press may not trigger navigation
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
        try:
            page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
        except Exception:
            pass
        return True

    elif action == "goto":
        url = decision.get("url", "")
        if not url or url in history:
            return False
        page.goto(url, wait_until="domcontentloaded")
        return True

    return False


# ---------------------------------------------------------------------------
# Screenshot helpers
# ---------------------------------------------------------------------------

def _url_slug(url: str) -> str:
    """Turn a URL into a short filename-safe slug."""
    parsed = urlparse(url)
    host = re.sub(r"^www\.", "", parsed.netloc or "page")
    path = re.sub(r"[^\w]", "_", parsed.path.strip("/"))[:30]
    slug = host + ("_" + path if path else "")
    return re.sub(r"_+", "_", slug)[:50]


def _take_screenshot(page, run_id: str, step: int, action: str, full_page: bool = False) -> "str | None":
    """Capture a screenshot; returns the absolute file path or None on failure."""
    if not run_id:
        return None
    try:
        shot_dir = os.path.join(_SCREENSHOTS_DIR, run_id)
        os.makedirs(shot_dir, exist_ok=True)
        filename = f"step{step:02d}_{action}_{_url_slug(page.url)}.png"
        path = os.path.join(shot_dir, filename)
        page.screenshot(path=path, full_page=full_page)
        return path
    except Exception:
        return None


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
    keep:       bool = False,
    run_id:     str  = "",
) -> tuple[str, str, list[str]]:
    """
    Navigate to start_url and find the page matching goal.

    Returns (extracted_text, final_url, screenshots).  Raises RuntimeError on failure.

    keep=True  — leave the Chromium window open after the task completes.
                 The browser is launched as a detached OS process so it survives
                 the agent subprocess exiting.  State written to harness_browser_state.json.
    """
    global _persistent_browser_proc

    _reuse = os.environ.get("HARNESS_REUSE_BROWSER") == "1"

    if not start_url.startswith("http"):
        start_url = "https://" + start_url

    from playwright.sync_api import sync_playwright

    # Use the manual lifecycle form so we control when (and whether) playwright stops.
    # The context-manager form calls stop() on exit which can send Browser.close via CDP.
    _pw_ctx = sync_playwright()
    pw      = _pw_ctx.start()
    _browser_proc = None  # only set when WE launched a detached subprocess

    def _teardown(browser, final_url: str = ""):
        """Close or persist the browser depending on the keep flag."""
        if keep:
            try:
                state = _read_state()
                state.update({"active": True, "last_url": final_url, "last_ts": time.time()})
                _write_state(state)
            except Exception:
                pass
            global _persistent_browser_proc
            _persistent_browser_proc = _browser_proc
            print(f"  [playwright] browser kept alive at {final_url}")
            # Do NOT stop playwright — that sends Browser.close via CDP
        else:
            try:
                browser.close()
            except Exception:
                pass
            if _browser_proc:
                try:
                    _browser_proc.terminate()
                except Exception:
                    pass
            _persistent_browser_proc = None
            _clear_state()
            try:
                _pw_ctx.stop()
            except Exception:
                pass

    try:
        browser = None

        # ── Try reconnecting to an existing browser ──────────────────────────
        if _reuse and headed:
            state = _read_state()
            port  = state.get("cdp_port", _CDP_PORT)
            try:
                browser = pw.chromium.connect_over_cdp(f"http://localhost:{port}")
                print(f"  [playwright] reconnected to browser on CDP port {port}")
            except Exception as _e:
                print(f"  [playwright] CDP reconnect failed ({_e}), launching fresh")
                browser = None

        # ── Launch a fresh browser ────────────────────────────────────────────
        if browser is None:
            if headed and keep:
                # Detached subprocess so Chromium outlives agent.py
                _exe = pw.chromium.executable_path
                if _exe:
                    _browser_proc = _launch_detached(_exe, _CDP_PORT)
                    _wait_for_cdp(_CDP_PORT)
                    browser = pw.chromium.connect_over_cdp(f"http://localhost:{_CDP_PORT}")
                    _write_state({"active": True, "cdp_port": _CDP_PORT,
                                  "pid": _browser_proc.pid, "ts": time.time()})
                    print(f"  [playwright] detached browser on CDP port {_CDP_PORT} (pid={_browser_proc.pid})")
                else:
                    # executable_path unavailable — fall back, persistence disabled
                    keep = False
                    print("  [playwright] executable_path unavailable — persistence disabled")

            if browser is None:
                # Playwright-owned launch (no persistence even if keep was requested)
                browser = pw.chromium.launch(
                    headless=not headed,
                    slow_mo=100 if headed else 0,
                )
                keep = False  # playwright owns this browser; can't keep it

        # ── Build context + page ──────────────────────────────────────────────
        _ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
               "AppleWebKit/537.36 (KHTML, like Gecko) "
               "Chrome/124.0.0.0 Safari/537.36")
        if browser.contexts:
            ctx = browser.contexts[0]
        else:
            ctx = browser.new_context(user_agent=_ua, viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        page.set_default_timeout(timeout_ms)

        history:     list[str] = []
        screenshots: list[str] = []

        print(f"  [playwright] navigating to {start_url}")
        page.goto(start_url, wait_until="domcontentloaded")
        _settle(page)
        history.append(page.url)
        _p = _take_screenshot(page, run_id, 0, "goto")
        if _p:
            screenshots.append(_p)

        for step in range(max_steps):
            snapshot = _page_snapshot(page)
            print(f"  [playwright] step {step+1}/{max_steps}  {snapshot['url'][:70]}")

            decision = _decide(snapshot, goal, history, model)
            action   = decision.get("action", "fail")

            _desc = ""
            if action == "fill":
                _desc = f": {decision.get('role','')} '{decision.get('name','')}' <- {decision.get('value','')!r}"
            elif action in ("click", "press"):
                _desc = f": {decision.get('text') or decision.get('key','')}"
            elif action == "goto":
                _desc = f": {decision.get('url','')[:60]}"
            elif action == "fail":
                _desc = f": {decision.get('reason','')}"
            print(f"  [playwright] decision -> {action}{_desc}")

            if action == "extract":
                _p = _take_screenshot(page, run_id, step + 1, "extract", full_page=True)
                if _p:
                    screenshots.append(_p)
                text      = _clean_full_text(page)
                final_url = page.url
                _teardown(browser, final_url)
                return text, final_url, screenshots

            elif action == "fail":
                _p = _take_screenshot(page, run_id, step + 1, "fail")
                if _p:
                    screenshots.append(_p)
                reason = decision.get("reason", "unknown")
                _teardown(browser, page.url)
                raise RuntimeError(f"navigator gave up: {reason}")

            else:
                navigated = _execute(page, decision, history, timeout_ms)
                if navigated:
                    _settle(page)
                    if page.url not in history:
                        history.append(page.url)
                    _p = _take_screenshot(page, run_id, step + 1, action)
                    if _p:
                        screenshots.append(_p)

        print("  [playwright] max steps reached — extracting current page")
        _p = _take_screenshot(page, run_id, max_steps, "extract", full_page=True)
        if _p:
            screenshots.append(_p)
        text      = _clean_full_text(page)
        final_url = page.url
        _teardown(browser, final_url)
        return text, final_url, screenshots

    except RuntimeError:
        _teardown(browser if "browser" in dir() else None, "")
        raise
    except Exception as e:
        _teardown(browser if "browser" in dir() else None, "")
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
    task = re.sub(r"^/(playwright|browser)\s*", "", task, flags=re.IGNORECASE).strip()

    m = re.search(
        r"(?:go\s+to\s+|visit\s+|navigate\s+to\s+|open\s+)?([a-zA-Z0-9][a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(?:/[^\s,]*)?|https?://\S+)",
        task, re.IGNORECASE,
    )
    if not m:
        raise ValueError(f"No URL found in task: {task!r}")

    url  = m.group(1)
    goal = (task[: m.start()] + " " + task[m.end() :]).strip()
    goal = re.sub(r"^(go\s+to|visit|navigate\s+to|open)\s*", "", goal, flags=re.IGNORECASE).strip(" ,")
    goal = re.sub(r"^(and|then|,)\s+", "", goal, flags=re.IGNORECASE).strip()
    if not goal:
        goal = "Extract the main content of this page"

    return url, goal
