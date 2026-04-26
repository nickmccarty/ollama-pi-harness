# Browser Navigation: Playwright Skill & Dashboard Integration

## Overview

The `/browser` (alias `/playwright`) skill gives the agent LLM-guided web navigation via an ARIA accessibility-tree snapshot loop. It supports persistent browser sessions across tasks, captures screenshots at every navigation step, and surfaces results in the dashboard inspector.

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

1. **Snapshot** — `page.aria_snapshot()` → falls back to `page.inner_text("body")` when ARIA is empty (JS-heavy pages like Amazon haven't populated roles yet)
2. **Settle** — `page.wait_for_load_state("networkidle", timeout=4s)` after every navigation so JS renders before the next snapshot
3. **Decide** — oracle LLM returns one of: `fill | press | click | goto | extract | fail`
4. **Execute** — semantic locators (`get_by_role`, `get_by_text`, `get_by_placeholder`); `fill` on a `searchbox` auto-submits with `.press("Enter")` on the same locator (prevents autocomplete re-open loops); `press` dispatches to `:focus` so autocomplete dropdowns can't intercept the keystroke

---

## Screenshots

After each navigated action a viewport PNG is saved to `screenshots/{run_id}/step{N:02d}_{action}_{slug}.png`. The extract step takes a full-page screenshot. On fail, a viewport screenshot is saved before raising.

```
screenshots/
  20260425T235655Z-4b5ea8817333/
    step00_goto_www.amazon.com.png
    step01_fill_www.amazon.com.png
    step02_extract_www.amazon.com_s.png
```

`GET /api/screenshots/<run_id>/<filename>` serves the PNGs. The dashboard inspector filmstrip renders thumbnails for any run with screenshots — click to open full-size in a new tab.

---

## Dashboard Integration

**Content modal** — clicking "View full output" in the synthesis or output DAG node fetches `GET /api/run_content/<run_id>` and renders the markdown in a modal. Falls back to the inline `final_content_preview` when the server is offline.

**Screenshot filmstrip** — appears in the synthesis and output inspector panels whenever `run.screenshots` is non-empty. Thumbnails are 110×74 px `object-fit: cover` with a blue hover border.

**Voice browser choice panel** — when a voice command is classified as `uses_browser: true` and `/api/browser/status` returns `active: true`, the panel asks "Use existing browser?" before dispatching. Choosing "Use existing" appends `--reuse-browser`; choosing "Open new" appends `--headed --keep-browser`.

---

## Reliability Patterns

| Problem | Fix |
|---------|-----|
| ARIA empty on JS-heavy pages | Fall back to `inner_text("body")` when `aria_snapshot()` returns empty string |
| Autocomplete intercepts Enter | `page.keyboard.press()` → `page.locator(":focus").press()` so the key lands on the focused element |
| Search re-fill loop | `fill` on `searchbox` role auto-submits immediately; LLM never sees autocomplete state |
| Navigation timeout hang | `wait_for_load_state` wrapped in `try/except` on both `press` and `click` |
| Goal contains `/browser` prefix | `parse_playwright_task` strips `/(playwright|browser)` and any leading `and/then/,` |
| Browser killed on agent exit | Chromium launched as detached OS process, breaking out of Windows Job Object |
