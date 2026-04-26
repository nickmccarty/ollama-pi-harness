#!/usr/bin/env python3
"""
op — harness agent CLI

Usage:
  op                    interactive REPL
  op <task>             run a single task (no quotes needed)
  op -h / --help        show help
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# ── make sure agent.py is importable ─────────────────────────────────────────
_HERE = Path(__file__).parent.resolve()
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.rule import Rule
from rich import box
import pyfiglet

console = Console()

# ── visual constants ──────────────────────────────────────────────────────────
_LOGO_FONT   = "isometric1"
_ACCENT      = "bold cyan"
_DIM         = "dim"
_PROMPT_STR  = "op ▶  "

_SKILLS = [
    ("/browser <url> <goal>",    "LLM-guided web navigation with saturation extraction"),
    ("/sitemap <url> [goal]",    "Discover all pages on a domain, rank by goal"),
    ("/annotate <url|path>",     "Annotate a paper or document with wiggum eval"),
    ("/email <contact> <goal>",  "Draft and send emails via Gmail"),
    ("/panel",                   "Enable 3-persona wiggum review panel"),
    ("/re-orient",               "Rebuild orientation cache from GitHub state"),
    ("research <topic>",         "Multi-round web research + synthesis"),
    ("summarize <url|path>",     "Fetch and compress a URL or local document"),
]

_FLAGS = [
    ("--no-wiggum",      "Skip quality evaluation loop"),
    ("--headed",         "Show browser window (browser tasks)"),
    ("--keep-browser",   "Leave browser open after task"),
    ("--reuse-browser",  "Reconnect to existing browser session"),
    ("-h / --help",      "Show this help"),
    ("exit / quit",      "Leave the REPL"),
]


# ── logo ──────────────────────────────────────────────────────────────────────

def _logo() -> str:
    return pyfiglet.figlet_format("op", font=_LOGO_FONT)


def _show_splash():
    logo_text = Text(_logo(), style=_ACCENT)
    subtitle   = Text(
        "  agentic research · browser navigation · synthesis · eval\n",
        style="italic dim"
    )
    combined = Text()
    combined.append_text(logo_text)
    combined.append_text(subtitle)

    console.print()
    console.print(Panel(
        combined,
        border_style="cyan",
        box=box.DOUBLE_EDGE,
        padding=(0, 2),
    ))

    try:
        import inference as _inf
        endpoints = _inf.ENDPOINTS if hasattr(_inf, "ENDPOINTS") else []
        ep_str = "  ".join(endpoints) if endpoints else "—"
        console.print(f"  [dim]models:[/dim] [cyan]{ep_str}[/cyan]")
    except Exception:
        pass

    console.print(f"  [dim]type[/dim] [cyan]-h[/cyan] [dim]for help,[/dim] "
                  f"[cyan]exit[/cyan] [dim]to quit[/dim]\n")


# ── help panel ────────────────────────────────────────────────────────────────

def _show_help():
    console.print()
    console.print(Rule("[bold cyan]op — harness agent CLI[/bold cyan]", style="cyan"))
    console.print()

    console.print("[bold]USAGE[/bold]")
    console.print("  [cyan]op[/cyan]                    interactive REPL")
    console.print("  [cyan]op[/cyan] [italic]<task>[/italic]             run a single task (no quotes needed)")
    console.print("  [cyan]op[/cyan] [cyan]-h[/cyan]                  show this help")
    console.print()

    console.print("[bold]SKILLS[/bold]")
    for cmd, desc in _SKILLS:
        console.print(f"  [cyan]{cmd:<30}[/cyan] [dim]{desc}[/dim]")
    console.print()

    console.print("[bold]FLAGS[/bold]")
    for flag, desc in _FLAGS:
        console.print(f"  [cyan]{flag:<20}[/cyan] [dim]{desc}[/dim]")
    console.print()

    console.print("[bold]EXAMPLES[/bold]")
    console.print("  [dim]$[/dim] op research best practices for cost management in AI agents, save to ~/Desktop/out.md")
    console.print("  [dim]$[/dim] op /browser go to docs.anthropic.com and find the pricing page")
    console.print("  [dim]$[/dim] op /sitemap stripe.com find integration guides")
    console.print("  [dim]$[/dim] op --headed /browser go to github.com and summarize recent issues")
    console.print()


# ── task runner ───────────────────────────────────────────────────────────────

def _run(task: str, extra_args: list[str] | None = None):
    """Inject extra CLI flags into sys.argv then call agent.run()."""
    from agent import run as _agent_run

    no_wiggum = extra_args and "--no-wiggum" in extra_args

    # Pass headed/keep/reuse flags via env vars (agent reads them at import time
    # but also re-checks os.environ inside run())
    if extra_args:
        if "--headed"        in extra_args: os.environ["HARNESS_HEADED"]        = "1"
        if "--keep-browser"  in extra_args: os.environ["HARNESS_KEEP_BROWSER"]  = "1"
        if "--reuse-browser" in extra_args: os.environ["HARNESS_REUSE_BROWSER"] = "1"

    console.print(f"\n[dim]▸[/dim] [italic]{task}[/italic]\n")
    t0 = time.monotonic()
    try:
        _agent_run(task, use_wiggum=not no_wiggum)
    except SystemExit:
        pass
    except KeyboardInterrupt:
        console.print("\n[yellow]  interrupted[/yellow]")
    elapsed = time.monotonic() - t0
    console.print(f"\n[dim]  done in {elapsed:.1f}s[/dim]\n")


# ── REPL ──────────────────────────────────────────────────────────────────────

def _repl(extra_args: list[str]):
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.styles import Style

    history_path = Path.home() / ".op_history"
    session = PromptSession(
        history=FileHistory(str(history_path)),
        style=Style.from_dict({"prompt": "ansicyan bold"}),
    )

    _show_splash()

    while True:
        try:
            task = session.prompt(_PROMPT_STR)
        except KeyboardInterrupt:
            console.print("[dim]  (ctrl-c — type exit to quit)[/dim]")
            continue
        except EOFError:
            console.print("[dim]  bye[/dim]")
            break

        task = task.strip()
        if not task:
            continue
        if task.lower() in ("exit", "quit", "q", ":q"):
            console.print("[dim]  bye[/dim]")
            break
        if task.lower() in ("-h", "--help", "help"):
            _show_help()
            continue

        _run(task, extra_args=extra_args)


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    raw = sys.argv[1:]

    if not raw:
        _repl(extra_args=[])
        return

    if raw[0] in ("-h", "--help", "help"):
        _show_help()
        return

    # Split task text from flags
    flags = [a for a in raw if a.startswith("--")]
    words = [a for a in raw if not a.startswith("--")]
    task  = " ".join(words).strip()

    if not task:
        _repl(extra_args=flags)
        return

    _run(task, extra_args=flags)


if __name__ == "__main__":
    main()
