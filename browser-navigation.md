# Browser Navigation: Playwright Skill & Dashboard Integration

## Overview

The `/browser` (alias `/playwright`) skill gives the agent LLM-guided web navigation via an ARIA accessibility-tree snapshot loop. It supports persistent browser sessions across tasks, captures screenshots at every navigation step, and surfaces results in the dashboard inspector.

A companion `/sitemap` (alias `/crawl`) skill discovers all pages on a domain before navigation begins, letting the LLM jump directly to the right URL instead of clicking around blind.

---

## CLI Flags

| Flag | Env var set | Effect |
|------|-------------|--------|
| `--headed` | `HARNESS_HEADED=1` | Launch Chromium in a visible window |
| `--keep-browser` | `HARNESS_KEEP_BROWSER=1` | Leave the browser open after the task (implies `--headed`) |
| `--reuse-browser` | `HARNESS_REUSE_BROWSER=1` | Reconnect to an already-running browser via CDP (implies `--headed`) |

```bash
python agent.py --keep-browser "/browser go to amazon.com and search for headphones"
python agent.py --reuse-browser "/browser find the pricing page on stripe.com"
```

---

## Pre-Navigation: Site Discovery (`sitemap_skill.py`)

Before the navigation loop starts, the skill runs `discover_pages()` using the fastest available method:

| Priority | Method | Speed | Notes |
|----------|--------|-------|-------|
| 1 | `GET /robots.txt` → `Sitemap:` directive | ~0.3s | Many sites list their real sitemap path here |
| 2 | Parse sitemap.xml (from robots.txt or `/sitemap.xml`) | ~0.5s | Returns full URL list instantly |
| 3 | DDGS `site:domain` search | ~1-2s | Returns indexed pages with titles + snippets; no crawl needed |
| 4 | BFS HTML crawl | slow | Last resort; skipped in quick mode (navigator always uses quick mode) |

The top 15 pages scored by token overlap with the goal are injected into every `_decide` prompt as a numbered list with titles and snippets. The LLM can `goto` a URL directly from this list rather than clicking through navigation menus.

**Standalone usage:**
```bash
python agent.py "/sitemap docs.anthropic.com find best practices for cost management"
python agent.py "/sitemap stripe.com, save to ~/Desktop/sitemap.md"
```

---

## Browser Persistence

Chromium is launched as a **detached OS process** (Windows: `DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP`; Unix: `start_new_session=True`) so it survives the agent subprocess exiting.

State is written to `{TEMP}/harness_browser_state.json`:
```json
{"active": true, "cdp_port": 9222, "pid": 1234, "last_url": "https://...", "ts": 1714000000}
```

On the next run with `--reuse-browser`, Playwright reconnects via `pw.chromium.connect_over_cdp("http://localhost:9222")`. If that fails (browser was closed), a fresh instance is launched.

`GET /api/browser/status` — server checks PID liveness via `os.kill(pid, 0)` and returns `{active, cdp_port, pid, last_url}`. The dashboard voice panel uses this to offer "Use existing browser / Open new browser" before dispatching browser tasks.

---

## Navigation Loop

`playwright_skill.navigate_and_extract(start_url, goal, model, run_id, ...)` runs up to `max_steps=12` iterations:

1. **Sitemap** — `discover_pages(start_url, quick=True)` runs before the loop; top matches injected into every prompt
2. **Snapshot** — `page.aria_snapshot()` → falls back to `page.inner_text("body")` when ARIA is empty (JS-heavy pages)
3. **Settle** — `page.wait_for_load_state("networkidle", timeout=4s)` after every navigation
4. **Decide** — oracle LLM returns one of: `fill | press | click | goto | backtrack | extract | fail`
5. **Execute** — semantic locators (`get_by_role`, `get_by_text`, `get_by_placeholder`)

### Action Set

| Action | When to use |
|--------|-------------|
| `fill` | Fill a search box or input field |
| `press` | Send a key to the focused element |
| `click` | Follow a link or press a button |
| `goto` | Navigate directly when URL is known (prefer for sitemap hits) |
| `backtrack` | Current page is off-topic — return to the nearest non-dead-end ancestor |
| `extract` | Current page directly answers the goal |
| `fail` | All options exhausted; content not on this site |

---

## Backtracking

When the LLM issues `backtrack`, the executor walks **backwards through history skipping already-backtracked pages** to find the nearest useful ancestor. Each backtracked page is annotated in history with its reason and the link text that led there:

```
- https://anthropic.com/research/81k-economics  [81k study]
    via: 'What 81,000 people told us about the economics of AI'
    — backtracked: research report, not practitioner guide
```

**Loop prevention** operates at two levels:
1. **Prompt level** — blocked link texts appear explicitly in the `_decide` prompt under "DO NOT click any of these links"
2. **Executor level** — clicks whose `text` led to a backtracked page are silently blocked; a note is injected into the next prompt

**Stuck detection** — if the navigator visits the same URL ≥ 4 times without finding the goal, it auto-fails with `"Stuck: visited <url> N times — content likely not available on this site."`

---

## Action Failure Feedback

When an action doesn't produce the expected result, a note is injected into the next `_decide` prompt:

| Situation | Note injected |
|-----------|--------------|
| `click` didn't navigate (modal opened) | "URL unchanged — act on new ARIA elements; do NOT click X again" |
| `fill` element not found | "Could not find searchbox 'X' — check ARIA tree for available inputs" |
| `click` blocked (led to dead end) | "Previously led to a dead end — choose a different link" |

---

## Screenshots

After each navigated action a viewport PNG is saved to `screenshots/{run_id}/step{N:02d}_{action}_{slug}.png`. The extract step takes a full-page screenshot. On fail, a viewport screenshot is saved before raising.

```
screenshots/
  20260425T235655Z-4b5ea8817333/
    step00_goto_www.anthropic.com.png
    step01_click_best_practices.png
    step02_extract_platform.claude.com_docs_en_agents.png
```

`GET /api/screenshots/<run_id>/<filename>` serves the PNGs. The dashboard inspector filmstrip renders thumbnails for any run with screenshots — click to open full-size in a new tab.

---

## Dashboard Integration

**Content modal** — clicking "View full output" in the synthesis or output DAG node fetches `GET /api/run_content/<run_id>` and renders the markdown in a modal.

**Screenshot filmstrip** — appears in the synthesis and output inspector panels whenever `run.screenshots` is non-empty. Thumbnails are 110×74 px `object-fit: cover` with a blue hover border.

**Voice browser choice panel** — when a voice command is classified as `uses_browser: true` and `/api/browser/status` returns `active: true`, the panel asks "Use existing browser?" before dispatching.

---

## Reliability Patterns

| Problem | Fix |
|---------|-----|
| ARIA empty on JS-heavy pages | Fall back to `inner_text("body")` when `aria_snapshot()` returns empty string |
| Autocomplete intercepts Enter | `page.locator(":focus").press()` so the key lands on the focused element |
| Search re-fill loop | `fill` on `searchbox` role auto-submits immediately; LLM never sees autocomplete state |
| Navigation timeout hang | `wait_for_load_state` wrapped in `try/except` on both `press` and `click` |
| Goal contains `/browser` prefix | `parse_playwright_task` strips `/(playwright|browser)` and any leading `and/then/,` |
| Browser killed on agent exit | Chromium launched as detached OS process, breaking out of Windows Job Object |
| LLM clicks same dead-end link repeatedly | Blocked in executor + explicit "DO NOT click" list in prompt |
| LLM backtracks to another dead-end page | `backtrack` skips already-backtracked history entries |
| Modal opens but LLM re-clicks button | Non-navigating click detected → "URL unchanged, act on new ARIA" note injected |
| `fill` silently fails (wrong ARIA name) | Failed fill detected → "searchbox not found, check ARIA tree" note injected |
| Infinite revisit loop | Auto-fail after 4 visits to same URL without progress |
| Site has no sitemap.xml | robots.txt → DDGS site: search → BFS crawl (pipeline) |
| Slow BFS crawl hangs navigator | Navigator uses `quick=True` — sitemap.xml + DDGS only, never crawls |
