"""
dashboard.py — generate a self-contained HTML analytics dashboard from runs.jsonl.

Usage:
    python dashboard.py                  # writes dashboard.html
    python dashboard.py --out my.html    # custom output path
    python dashboard.py --open           # open in browser after writing
"""

import json
import os
import sys
import webbrowser
from collections import defaultdict
from datetime import datetime, timezone


def fmt_ts(ts_str):
    """Convert a UTC ISO timestamp string to local time display string."""
    if not ts_str:
        return ""
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ts_str[:19].replace("T", " ")

RUNS_PATH = os.path.join(os.path.dirname(__file__), "runs.jsonl")
OUT_PATH  = os.path.join(os.path.dirname(__file__), "dashboard.html")

STAGE_COLORS = {
    "synth":              "#4f8ef7",
    "wiggum_eval":        "#a78bfa",
    "wiggum_revise":      "#f472b6",
    "compress_knowledge": "#fb923c",
    "search_query":       "#4ade80",
    "synth_count":        "#38bdf8",
    "tool_loop":          "#fbbf24",
}

# Stage → model role (determines which cloud tier to apply for cost comparison)
STAGE_ROLE = {
    "synth":              "producer",
    "synth_count":        "producer",
    "tool_loop":          "producer",
    "wiggum_eval":        "evaluator",
    "wiggum_revise":      "evaluator",
    "compress_knowledge": "planner",
    "search_query":       "planner",
}

# Cloud pricing per 1M tokens (input, output) — edit to taste
# Roles map to the cloud model you'd realistically substitute
CLOUD_TIERS = [
    # (display name,  input $/1M,  output $/1M,  applies_to_roles)
    ("GPT-4o",        2.50,  10.00, {"producer", "evaluator", "planner"}),
    ("GPT-4o mini",   0.15,   0.60, {"producer", "evaluator", "planner"}),
    ("Claude Sonnet", 3.00,  15.00, {"producer", "evaluator", "planner"}),
    ("Claude Haiku",  0.25,   1.25, {"producer", "evaluator", "planner"}),
    ("Gemini 1.5 Pro",1.25,   5.00, {"producer", "evaluator", "planner"}),
    ("Gemini Flash",  0.075,  0.30, {"producer", "evaluator", "planner"}),
]

# Embedding cost (OpenAI text-embedding-3-small equivalent): $/1M tokens
EMBED_COST_PER_1M = 0.02

# Local electricity config — edit to match your hardware
GPU_WATTS        = 300    # RTX 3090/4090 range under load
SYSTEM_WATTS     = 100    # CPU + rest of system
ELECTRICITY_RATE = 0.12   # USD per kWh (US average)

# ---------------------------------------------------------------------------
# Data loading + transformation
# ---------------------------------------------------------------------------

def load_runs():
    runs = []
    with open(RUNS_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    runs.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return runs


def first_wiggum_score(run):
    scores = run.get("wiggum_scores") or []
    return scores[0] if scores else None


def build_payload(runs):
    """Transform runs into chart-ready data structures."""

    # --- KPI summary ---
    total        = len(runs)
    passed       = sum(1 for r in runs if r.get("final") == "PASS")
    failed       = sum(1 for r in runs if r.get("final") == "FAIL")
    errors       = sum(1 for r in runs if r.get("final") == "ERROR")
    total_input  = sum(r.get("input_tokens", 0) or 0 for r in runs)
    total_output = sum(r.get("output_tokens", 0) or 0 for r in runs)
    scores       = [s for r in runs for s in ([first_wiggum_score(r)] if first_wiggum_score(r) else [])]
    avg_score    = round(sum(scores) / len(scores), 2) if scores else 0
    avg_duration = round(sum(r.get("run_duration_s", 0) or 0 for r in runs) / total, 1) if total else 0

    # --- Score trend (chronological, only runs with a wiggum score) ---
    scored_runs = [(r["timestamp"], first_wiggum_score(r), r.get("producer_model", ""))
                   for r in runs if first_wiggum_score(r) is not None]
    score_labels  = [fmt_ts(x[0]) for x in scored_runs]
    score_values  = [x[1] for x in scored_runs]
    score_models  = [x[2] for x in scored_runs]

    # --- Tokens by date (stacked: input + output) ---
    by_date_input  = defaultdict(int)
    by_date_output = defaultdict(int)
    for r in runs:
        date = (r.get("timestamp") or "")[:10]
        if not date:
            continue
        by_date_input[date]  += r.get("input_tokens", 0) or 0
        by_date_output[date] += r.get("output_tokens", 0) or 0
    dates_sorted = sorted(set(by_date_input) | set(by_date_output))
    token_dates  = dates_sorted
    token_input  = [by_date_input[d]  for d in dates_sorted]
    token_output = [by_date_output[d] for d in dates_sorted]

    # --- Tokens by stage (aggregate across all runs) ---
    stage_totals = defaultdict(lambda: {"input": 0, "output": 0, "total_ms": 0, "eval_ms": 0, "prompt_ms": 0, "calls": 0})
    for r in runs:
        for stage, vals in (r.get("tokens_by_stage") or {}).items():
            stage_totals[stage]["input"]     += vals.get("input", 0)
            stage_totals[stage]["output"]    += vals.get("output", 0)
            stage_totals[stage]["total_ms"]  += vals.get("total_ms", 0)
            stage_totals[stage]["eval_ms"]   += vals.get("eval_ms", 0)
            stage_totals[stage]["prompt_ms"] += vals.get("prompt_ms", 0)
            stage_totals[stage]["calls"]     += vals.get("calls", 1)
    stage_names  = sorted(stage_totals)
    stage_tokens = [stage_totals[s]["input"] + stage_totals[s]["output"] for s in stage_names]
    stage_colors = [STAGE_COLORS.get(s, "#94a3b8") for s in stage_names]
    stage_ms     = [round(stage_totals[s]["total_ms"] / 1000, 1) for s in stage_names]

    # --- Wiggum dimension averages ---
    dim_keys  = ["relevance", "completeness", "depth", "specificity", "structure"]
    dim_sums  = defaultdict(list)
    for r in runs:
        for round_dims in (r.get("wiggum_dims") or []):
            for k in dim_keys:
                if k in round_dims:
                    dim_sums[k].append(round_dims[k])
    dim_avgs = [round(sum(dim_sums[k]) / len(dim_sums[k]), 2) if dim_sums[k] else 0
                for k in dim_keys]

    # --- Run duration trend ---
    dur_labels = [fmt_ts(r.get("timestamp")) for r in runs if r.get("run_duration_s")]
    dur_values = [round(r["run_duration_s"] / 60, 1) for r in runs if r.get("run_duration_s")]

    # --- Model breakdown ---
    model_counts = defaultdict(int)
    for r in runs:
        model_counts[r.get("producer_model") or "unknown"] += 1
    model_names  = list(model_counts)
    model_values = [model_counts[m] for m in model_names]

    # --- Tokens/sec by stage and per-run trend ---
    stage_tps_out = []
    stage_tps_in  = []
    for s in stage_names:
        # Use eval_ms (generation only) for output tok/s; prompt_ms for input tok/s.
        # Fall back to total_ms for runs logged before these fields existed.
        eval_ms   = stage_totals[s]["eval_ms"]   or stage_totals[s]["total_ms"]
        prompt_ms = stage_totals[s]["prompt_ms"] or stage_totals[s]["total_ms"]
        if eval_ms > 0:
            stage_tps_out.append(round(stage_totals[s]["output"] / (eval_ms   / 1000), 1))
        else:
            stage_tps_out.append(0)
        if prompt_ms > 0:
            stage_tps_in.append(round(stage_totals[s]["input"]   / (prompt_ms / 1000), 1))
        else:
            stage_tps_in.append(0)

    run_tps_labels = []
    run_tps_out    = []
    run_tps_in     = []
    for r in runs:
        tbs = r.get("tokens_by_stage") or {}
        total_out_tok = sum(v.get("output", 0) for v in tbs.values())
        total_in_tok  = sum(v.get("input",  0) for v in tbs.values())
        # Use stage-specific eval_ms/prompt_ms sums; fall back to total_ms for older runs
        eval_ms   = sum(v.get("eval_ms",   0) for v in tbs.values())
        prompt_ms = sum(v.get("prompt_ms", 0) for v in tbs.values())
        total_ms  = sum(v.get("total_ms",  0) for v in tbs.values())
        denom_out = eval_ms   or total_ms
        denom_in  = prompt_ms or total_ms
        if denom_out > 0 or denom_in > 0:
            run_tps_labels.append(fmt_ts(r.get("timestamp")))
            run_tps_out.append(round(total_out_tok / (denom_out / 1000), 1) if denom_out > 0 else 0)
            run_tps_in.append(round(total_in_tok   / (denom_in  / 1000), 1) if denom_in  > 0 else 0)

    avg_out_tps = round(sum(run_tps_out) / len(run_tps_out), 1) if run_tps_out else 0

    # --- Runs per hour-of-day heatmap (0-23) ---
    hour_counts = defaultdict(int)
    for r in runs:
        ts = r.get("timestamp") or ""
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                hour_counts[dt.astimezone().hour] += 1
            except (ValueError, AttributeError):
                pass
    hour_labels = [f"{h:02d}:00" for h in range(24)]
    hour_values = [hour_counts[h] for h in range(24)]

    # --- Recent runs table (last 50 substantive runs) ---
    # Exclude stub runs: no LLM tokens, no wiggum evaluation, no output produced.
    # These are typically quick standalone-skill calls (github status, review on empty diff)
    # or eval_suite sub-checks that shouldn't crowd out real research runs.
    def _is_substantive(r: dict) -> bool:
        return bool(
            (r.get("input_tokens") or 0) > 0
            or (r.get("wiggum_rounds") or 0) > 0
            or (r.get("output_bytes") or 0) > 0
        )
    recent = []
    for r in [x for x in runs if _is_substantive(x)][-50:]:
        # Wiggum dims — first round's dimension scores
        dims_raw = r.get("wiggum_dims")
        dims = None
        if isinstance(dims_raw, list) and dims_raw and isinstance(dims_raw[0], dict):
            dims = dims_raw[0]
        elif isinstance(dims_raw, dict):
            dims = dims_raw

        # Eval log — first round's issues + feedback excerpt
        eval_log = r.get("wiggum_eval_log")
        first_issues  = []
        first_feedback = ""
        score_trajectory = []
        if isinstance(eval_log, list) and eval_log:
            first_round = eval_log[0]
            first_issues  = first_round.get("issues") or []
            fb = first_round.get("feedback") or ""
            first_feedback = fb[:300] + ("…" if len(fb) > 300 else "")
        # Score trajectory across all wiggum rounds
        scores = r.get("wiggum_scores") or []
        score_trajectory = [s for s in scores if s is not None]

        task_raw  = r.get("task") or ""
        task_type = r.get("task_type") or "?"
        # For email runs the task string is mangled by MSYS2 path expansion.
        # Build a clean label from the structured fields instead.
        if task_type == "email_draft":
            task_label = (r.get("task") or "")[:70]
        elif task_type == "email":
            drafts  = r.get("email_drafts", 0)
            out_dir = r.get("email_output_dir", "")
            import re as _re
            csv_match = _re.search(r'([\w\-\.]+\.csv)', task_raw)
            csv_name  = csv_match.group(1) if csv_match else "?"
            task_label = f"Email batch: {csv_name} → {out_dir} ({drafts} draft{'s' if drafts != 1 else ''})"
        else:
            task_label = task_raw[:70]

        recent.append({
            "ts":       fmt_ts(r.get("timestamp")),
            "task":     task_label,
            "task_full": task_raw,
            "model":    r.get("producer_model") or "",
            "type":     task_type,
            "score":    first_wiggum_score(r),
            "rounds":   r.get("wiggum_rounds"),
            "duration": round((r.get("run_duration_s") or 0) / 60, 1),
            "tokens_in":  r.get("input_tokens") or 0,
            "tokens_out": r.get("output_tokens") or 0,
            "final":    r.get("final") or "?",
            "searches": r.get("search_rounds") or len(r.get("tool_calls") or []),
            # Detail-row fields
            "memory_hits":       r.get("memory_hits") or 0,
            "dims":              dims,
            "issues":            first_issues,
            "feedback":          first_feedback,
            "score_trajectory":  score_trajectory,
            "count_check_retry": bool(r.get("count_check_retry")),
            "novelty_scores":    r.get("novelty_scores") or [],
            "output_bytes":      r.get("output_bytes") or 0,
            "output_lines":      r.get("output_lines") or 0,
            # Email batch fields
            "email_drafts":     r.get("email_drafts"),
            "email_output_dir": r.get("email_output_dir"),
            # Email draft (per-contact) fields
            "email_to":          r.get("email_to"),
            "email_name":        r.get("email_name"),
            "email_affiliation": r.get("email_affiliation"),
            "email_subject":     r.get("email_subject"),
            "email_body":        r.get("email_body"),
            "email_goal":        r.get("email_goal"),
            "email_subject_prompt": (r.get("tool_calls") or [{}])[0].get("query") if task_type == "email_draft" else None,
            "email_body_prompt":    (r.get("tool_calls") or [{}, {}])[1].get("query") if task_type == "email_draft" and len(r.get("tool_calls") or []) > 1 else None,
        })
    recent.reverse()

    cost = build_cost_data(runs)

    return {
        "kpi": {
            "total": total, "passed": passed, "failed": failed, "errors": errors,
            "total_input": total_input, "total_output": total_output,
            "avg_score": avg_score, "avg_duration": avg_duration,
        },
        "score_trend":   {"labels": score_labels, "values": score_values, "models": score_models},
        "token_by_date": {"dates": token_dates, "input": token_input, "output": token_output},
        "token_by_stage":{"names": stage_names, "tokens": stage_tokens, "colors": stage_colors, "ms": stage_ms},
        "toks_per_sec":  {
            "stage_names":    stage_names,
            "stage_colors":   stage_colors,
            "stage_out":      stage_tps_out,
            "stage_in":       stage_tps_in,
            "run_labels":     run_tps_labels,
            "run_out":        run_tps_out,
            "run_in":         run_tps_in,
            "avg_out_tps":    avg_out_tps,
        },
        "wiggum_dims":   {"labels": [k.capitalize() for k in dim_keys], "values": dim_avgs},
        "duration_trend":{"labels": dur_labels, "values": dur_values},
        "model_split":   {"names": model_names, "values": model_values},
        "hour_dist":     {"labels": hour_labels, "values": hour_values},
        "recent_runs":   recent,
        "cost":          cost,
    }


def build_cost_data(runs: list[dict]) -> dict:
    """Compute cloud-equivalent cost estimates and local electricity cost."""

    # --- Aggregate tokens by role (producer / evaluator / planner / unknown) ---
    role_tokens: dict[str, dict] = defaultdict(lambda: {"input": 0, "output": 0})
    for r in runs:
        for stage, vals in (r.get("tokens_by_stage") or {}).items():
            role = STAGE_ROLE.get(stage, "unknown")
            role_tokens[role]["input"]  += vals.get("input", 0)
            role_tokens[role]["output"] += vals.get("output", 0)

    total_in  = sum(v["input"]  for v in role_tokens.values())
    total_out = sum(v["output"] for v in role_tokens.values())

    # --- Cloud tier comparison ---
    # Each tier applies one rate to all tokens regardless of role
    # (realistic: you'd use the same cloud model for everything)
    tier_rows = []
    for name, price_in, price_out, _ in CLOUD_TIERS:
        cost = (total_in / 1_000_000 * price_in) + (total_out / 1_000_000 * price_out)
        tier_rows.append({
            "name":       name,
            "price_in":   price_in,
            "price_out":  price_out,
            "cost":       round(cost, 4),
        })
    tier_rows.sort(key=lambda x: x["cost"])

    # --- Local electricity cost ---
    total_runtime_s   = sum(r.get("run_duration_s", 0) or 0 for r in runs)
    total_runtime_h   = total_runtime_s / 3600
    total_watts       = GPU_WATTS + SYSTEM_WATTS
    electricity_cost  = round((total_watts / 1000) * total_runtime_h * ELECTRICITY_RATE, 4)

    # --- Savings vs each tier ---
    for row in tier_rows:
        row["savings"] = round(row["cost"] - electricity_cost, 4)

    # --- Cumulative cost over time (cheapest cloud tier vs electricity) ---
    cheapest_in  = min(t[1] for t in CLOUD_TIERS)
    cheapest_out = min(t[2] for t in CLOUD_TIERS)
    cumulative_labels     = []
    cumulative_cloud      = []   # cheapest tier
    cumulative_electric   = []
    cum_in = cum_out = cum_s = 0.0
    for r in runs:
        ts = fmt_ts(r.get("timestamp"))
        cum_in  += r.get("input_tokens",  0) or 0
        cum_out += r.get("output_tokens", 0) or 0
        cum_s   += r.get("run_duration_s", 0) or 0
        cumulative_labels.append(ts)
        cumulative_cloud.append(round(
            cum_in / 1_000_000 * cheapest_in + cum_out / 1_000_000 * cheapest_out, 4
        ))
        cumulative_electric.append(round(
            (total_watts / 1000) * (cum_s / 3600) * ELECTRICITY_RATE, 4
        ))

    # --- Role breakdown for stacked bar ---
    role_order  = ["producer", "evaluator", "planner", "unknown"]
    role_colors = {"producer": "#4f8ef7", "evaluator": "#a78bfa", "planner": "#fb923c", "unknown": "#8b949e"}
    role_data = [
        {
            "role":   role,
            "input":  role_tokens[role]["input"],
            "output": role_tokens[role]["output"],
            "color":  role_colors[role],
        }
        for role in role_order if role_tokens[role]["input"] + role_tokens[role]["output"] > 0
    ]

    return {
        "tier_rows":           tier_rows,
        "electricity_cost":    electricity_cost,
        "total_runtime_h":     round(total_runtime_h, 2),
        "gpu_watts":           total_watts,
        "electricity_rate":    ELECTRICITY_RATE,
        "cumulative_labels":   cumulative_labels,
        "cumulative_cloud":    cumulative_cloud,
        "cumulative_electric": cumulative_electric,
        "cheapest_tier":       tier_rows[0]["name"] if tier_rows else "",
        "role_data":           role_data,
        "total_in":            total_in,
        "total_out":           total_out,
    }


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Harness Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:       #0d1117;
    --card:     #161b22;
    --border:   #30363d;
    --text:     #e6edf3;
    --muted:    #8b949e;
    --blue:     #4f8ef7;
    --green:    #3fb950;
    --orange:   #fb923c;
    --red:      #f85149;
    --purple:   #a78bfa;
    --pink:     #f472b6;
    --yellow:   #e3b341;
  }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 14px;
    line-height: 1.5;
    padding: 24px;
  }

  h1 { font-size: 20px; font-weight: 600; margin-bottom: 4px; }
  .subtitle { color: var(--muted); font-size: 13px; margin-bottom: 28px; }

  /* KPI cards */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 12px;
    margin-bottom: 20px;
  }
  .kpi {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px 18px;
  }
  .kpi-label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
  .kpi-value { font-size: 26px; font-weight: 700; line-height: 1; }
  .kpi-sub   { color: var(--muted); font-size: 12px; margin-top: 4px; }
  .kpi.blue   .kpi-value { color: var(--blue); }
  .kpi.green  .kpi-value { color: var(--green); }
  .kpi.orange .kpi-value { color: var(--orange); }
  .kpi.purple .kpi-value { color: var(--purple); }
  .kpi.red    .kpi-value { color: var(--red); }
  .kpi.yellow .kpi-value { color: var(--yellow); }

  /* Chart grid */
  .chart-grid {
    display: grid;
    gap: 16px;
    margin-bottom: 16px;
  }
  .col-2 { grid-template-columns: 1fr 1fr; }
  .col-3 { grid-template-columns: 1fr 1fr 1fr; }
  .col-1 { grid-template-columns: 1fr; }

  .card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 18px 20px;
  }
  .card-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 14px;
  }
  .chart-wrap { position: relative; }

  /* Table */
  .table-wrap { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
  th {
    text-align: left; padding: 8px 10px;
    color: var(--muted); font-weight: 600;
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
  }
  td { padding: 7px 10px; border-bottom: 1px solid var(--border); white-space: nowrap; }
  tr:last-child td { border-bottom: none; }
  tr.run-row:hover td { background: rgba(255,255,255,0.03); }

  /* Chevron expand */
  .chevron-btn {
    background: none; border: none; color: var(--muted); cursor: pointer;
    padding: 2px 4px; font-size: 11px; line-height: 1;
    transition: transform 0.18s, color 0.18s;
  }
  .chevron-btn:hover { color: var(--text); }
  .chevron-btn.open { transform: rotate(90deg); color: var(--blue); }

  /* RLHF feedback panel */
  .btn-thumb {
    background: none; border: 1px solid var(--border); border-radius: 4px;
    cursor: pointer; font-size: 16px; line-height: 1; padding: 2px 6px;
    transition: background 0.15s, border-color 0.15s;
  }
  .btn-thumb:hover { background: var(--bg2); }
  .btn-thumb-active { background: var(--accent) !important; border-color: var(--accent) !important; }

  /* Detail row */
  .detail-row td { padding: 0; border-bottom: 1px solid var(--border); white-space: normal; }
  .detail-row.hidden { display: none; }
  .detail-inner {
    /* Stick to the left edge of the scroll container so cards stay in the viewport
       even when the table is wider than the screen */
    position: sticky;
    left: 0;
    width: calc(100vw - 48px);   /* full viewport minus body side padding */
    max-width: 1100px;
    box-sizing: border-box;
    padding: 14px 16px 18px 16px;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 10px;
  }
  .detail-card {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 12px 14px;
    font-size: 12px;
    min-width: 0;          /* prevent grid blowout */
    overflow: hidden;
  }
  .detail-card-title {
    font-size: 10px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.07em; color: var(--muted); margin-bottom: 8px;
  }
  /* Dim bars */
  .dim-row { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }
  .dim-label {
    width: 82px; color: var(--muted); font-size: 10px; flex-shrink: 0;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }
  .dim-bar-wrap { flex: 1; height: 5px; background: var(--border); border-radius: 3px; overflow: hidden; min-width: 0; }
  .dim-bar-fill { height: 100%; border-radius: 3px; }
  .dim-value { width: 18px; text-align: right; color: var(--text); font-size: 10px; flex-shrink: 0; }
  /* Score pills */
  .score-pill {
    display: inline-block; padding: 1px 6px; border-radius: 10px;
    font-size: 11px; font-weight: 600; margin: 2px 2px 2px 0;
    background: rgba(79,142,247,.15); color: var(--blue);
  }
  /* Issues list */
  .issues-scroll {
    max-height: 130px; overflow-y: auto;
  }
  .issue-item {
    color: var(--muted); font-size: 11px; line-height: 1.45;
    padding: 3px 0 3px 12px; border-bottom: 1px solid rgba(48,54,61,.6);
    word-break: break-word; white-space: normal;
    position: relative;
  }
  .issue-item:last-child { border-bottom: none; }
  .issue-item::before {
    content: "·"; position: absolute; left: 0;
    color: var(--orange); font-size: 14px; line-height: 1.1;
  }
  /* Feedback text */
  .feedback-text {
    color: var(--muted); font-size: 11px; line-height: 1.5;
    white-space: normal; word-break: break-word;
    max-height: 130px; overflow-y: auto;
  }
  /* Task full text */
  .task-full {
    color: var(--text); font-size: 11px; line-height: 1.5;
    white-space: normal; word-break: break-word;
  }

  .badge {
    display: inline-block; padding: 2px 7px; border-radius: 4px;
    font-size: 11px; font-weight: 600; line-height: 1.6;
  }
  .badge-pass  { background: rgba(63,185,80,.18);  color: var(--green); }
  .badge-fail  { background: rgba(248,81,73,.18);  color: var(--red); }
  .badge-error { background: rgba(139,148,158,.18); color: var(--muted); }

  .score-bar {
    display: inline-block; width: 60px; height: 6px;
    background: var(--border); border-radius: 3px; vertical-align: middle; margin-right: 6px;
  }
  .score-fill { height: 100%; border-radius: 3px; background: var(--blue); }

  .section-heading {
    font-size: 13px; font-weight: 600; color: var(--muted);
    text-transform: uppercase; letter-spacing: 0.05em;
    margin: 28px 0 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
  }

  .saving-pos { color: var(--green); }
  .saving-neg { color: var(--red); }

  @media (max-width: 900px) {
    .col-2, .col-3 { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>

<h1>Harness Engineering — Run Dashboard</h1>
<p class="subtitle" id="subtitle">Loading...</p>

<div class="kpi-grid" id="kpi-grid"></div>

<div class="chart-grid col-1">
  <div class="card">
    <div class="card-title">Wiggum Score — run history</div>
    <div class="chart-wrap" style="height:200px">
      <canvas id="scoreChart"></canvas>
    </div>
  </div>
</div>

<div class="chart-grid col-1">
  <div class="card">
    <div class="card-title">Token usage by date</div>
    <div class="chart-wrap" style="height:180px">
      <canvas id="tokenDateChart"></canvas>
    </div>
  </div>
</div>

<div class="chart-grid col-3">
  <div class="card">
    <div class="card-title">Tokens by stage</div>
    <div class="chart-wrap" style="height:220px">
      <canvas id="stageChart"></canvas>
    </div>
  </div>
  <div class="card">
    <div class="card-title">Wiggum dimensions (avg)</div>
    <div class="chart-wrap" style="height:220px">
      <canvas id="radarChart"></canvas>
    </div>
  </div>
  <div class="card">
    <div class="card-title">Pass / Fail / Error</div>
    <div class="chart-wrap" style="height:220px">
      <canvas id="finalChart"></canvas>
    </div>
  </div>
</div>

<div class="chart-grid col-2">
  <div class="card">
    <div class="card-title">Run duration (minutes)</div>
    <div class="chart-wrap" style="height:180px">
      <canvas id="durationChart"></canvas>
    </div>
  </div>
  <div class="card">
    <div class="card-title">Activity by hour of day</div>
    <div class="chart-wrap" style="height:180px">
      <canvas id="hourChart"></canvas>
    </div>
  </div>
</div>

<h2 class="section-heading">Throughput — tokens / second</h2>

<div class="chart-grid col-2">
  <div class="card">
    <div class="card-title">Output tok/s by stage (generation speed)</div>
    <div class="chart-wrap" style="height:240px">
      <canvas id="tpsStageChart"></canvas>
    </div>
  </div>
  <div class="card">
    <div class="card-title">Output tok/s — run trend</div>
    <div class="chart-wrap" style="height:240px">
      <canvas id="tpsTrendChart"></canvas>
    </div>
  </div>
</div>

<h2 class="section-heading">Cost analysis — local vs cloud equivalent</h2>

<div class="kpi-grid" id="cost-kpi-grid"></div>

<div class="chart-grid col-2">
  <div class="card">
    <div class="card-title">Cloud equivalent cost comparison</div>
    <div class="table-wrap">
      <table id="costTable"></table>
    </div>
  </div>
  <div class="card">
    <div class="card-title">Tokens by model role</div>
    <div class="chart-wrap" style="height:220px">
      <canvas id="roleChart"></canvas>
    </div>
  </div>
</div>

<div class="chart-grid col-1">
  <div class="card">
    <div class="card-title">Cumulative cost over time — cheapest cloud tier vs local electricity</div>
    <div class="chart-wrap" style="height:200px">
      <canvas id="cumulCostChart"></canvas>
    </div>
  </div>
</div>

<h2 class="section-heading">Fine-tuning — live metrics</h2>

<div class="kpi-grid" id="ft-kpi-grid"></div>

<div class="chart-grid col-2">
  <div class="card">
    <div class="card-title">Loss — per step</div>
    <div class="chart-wrap" style="height:200px">
      <canvas id="ftLossChart"></canvas>
    </div>
  </div>
  <div class="card">
    <div class="card-title">Token accuracy — per step</div>
    <div class="chart-wrap" style="height:200px">
      <canvas id="ftAccChart"></canvas>
    </div>
  </div>
</div>

<div class="chart-grid col-2">
  <div class="card">
    <div class="card-title">Gradient norm — per step</div>
    <div class="chart-wrap" style="height:180px">
      <canvas id="ftGradChart"></canvas>
    </div>
  </div>
  <div class="card">
    <div class="card-title">Learning rate schedule</div>
    <div class="chart-wrap" style="height:180px">
      <canvas id="ftLrChart"></canvas>
    </div>
  </div>
</div>

<h2 class="section-heading">Runs</h2>

<div class="chart-grid col-1">
  <div class="card">
    <div class="card-title">Recent runs (last 30)</div>
    <div class="table-wrap">
      <table id="runsTable"></table>
    </div>
  </div>
</div>

<script>
const DATA = __DATA__;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
const $ = id => document.getElementById(id);
const fmtK = n => n >= 1000000 ? (n/1000000).toFixed(1)+'M' : n >= 1000 ? (n/1000).toFixed(1)+'K' : String(n);

const CHART_DEFAULTS = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { ticks: { color: '#8b949e', font: { size: 10 }, maxRotation: 45 }, grid: { color: '#21262d' } },
    y: { ticks: { color: '#8b949e', font: { size: 10 } }, grid: { color: '#21262d' } },
  },
};

// ---------------------------------------------------------------------------
// KPI cards
// ---------------------------------------------------------------------------
const kpi = DATA.kpi;
const passRate = kpi.total ? Math.round(kpi.passed / kpi.total * 100) : 0;
$('subtitle').textContent =
  `${kpi.total} runs · updated ${new Date().toLocaleString()}`;

const cards = [
  { label: 'Total runs',      value: kpi.total,                           cls: 'blue'   },
  { label: 'Pass rate',       value: passRate + '%',  sub: `${kpi.passed} passed`, cls: 'green'  },
  { label: 'Avg score',       value: kpi.avg_score,   sub: 'first wiggum round',   cls: 'yellow' },
  { label: 'Avg duration',    value: kpi.avg_duration + 'm',              cls: 'orange' },
  { label: 'Total input tok', value: fmtK(kpi.total_input),               cls: 'purple' },
  { label: 'Total output tok',value: fmtK(kpi.total_output),              cls: 'blue'   },
  { label: 'Avg output tok/s',value: DATA.toks_per_sec.avg_out_tps,  sub: 'generation speed', cls: 'green' },
  { label: 'Errors',          value: kpi.errors,                          cls: 'red'    },
  { label: 'Failed',          value: kpi.failed,                          cls: 'orange' },
];
$('kpi-grid').innerHTML = cards.map(c => `
  <div class="kpi ${c.cls}">
    <div class="kpi-label">${c.label}</div>
    <div class="kpi-value">${c.value}</div>
    ${c.sub ? `<div class="kpi-sub">${c.sub}</div>` : ''}
  </div>`).join('');

// ---------------------------------------------------------------------------
// Score trend
// ---------------------------------------------------------------------------
new Chart($('scoreChart'), {
  type: 'line',
  data: {
    labels: DATA.score_trend.labels,
    datasets: [{
      data: DATA.score_trend.values,
      borderColor: '#4f8ef7',
      backgroundColor: 'rgba(79,142,247,0.08)',
      pointRadius: 2,
      pointHoverRadius: 5,
      borderWidth: 1.5,
      tension: 0.3,
      fill: true,
    }],
  },
  options: {
    ...CHART_DEFAULTS,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          afterLabel: ctx => 'model: ' + (DATA.score_trend.models[ctx.dataIndex] || ''),
        },
      },
    },
    scales: {
      x: { ...CHART_DEFAULTS.scales.x, ticks: { ...CHART_DEFAULTS.scales.x.ticks, maxTicksLimit: 12 } },
      y: { ...CHART_DEFAULTS.scales.y, min: 0, max: 10 },
    },
  },
});

// ---------------------------------------------------------------------------
// Tokens by date (stacked bar)
// ---------------------------------------------------------------------------
new Chart($('tokenDateChart'), {
  type: 'bar',
  data: {
    labels: DATA.token_by_date.dates,
    datasets: [
      { label: 'Input tokens',  data: DATA.token_by_date.input,  backgroundColor: 'rgba(79,142,247,0.7)',  stack: 'tok' },
      { label: 'Output tokens', data: DATA.token_by_date.output, backgroundColor: 'rgba(167,139,250,0.7)', stack: 'tok' },
    ],
  },
  options: {
    ...CHART_DEFAULTS,
    plugins: { legend: { display: true, labels: { color: '#8b949e', font: { size: 11 } } } },
    scales: {
      x: { ...CHART_DEFAULTS.scales.x, stacked: true },
      y: { ...CHART_DEFAULTS.scales.y, stacked: true, ticks: { ...CHART_DEFAULTS.scales.y.ticks, callback: v => fmtK(v) } },
    },
  },
});

// ---------------------------------------------------------------------------
// Tokens by stage (donut)
// ---------------------------------------------------------------------------
new Chart($('stageChart'), {
  type: 'doughnut',
  data: {
    labels: DATA.token_by_stage.names,
    datasets: [{
      data:            DATA.token_by_stage.tokens,
      backgroundColor: DATA.token_by_stage.colors,
      borderColor:     '#161b22',
      borderWidth: 2,
    }],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: true, position: 'right', labels: { color: '#8b949e', font: { size: 11 }, padding: 10 } },
      tooltip: {
        callbacks: {
          label: ctx => {
            const total = ctx.dataset.data.reduce((a,b)=>a+b,0);
            const pct = Math.round(ctx.raw / total * 100);
            return ` ${fmtK(ctx.raw)} tok (${pct}%)`;
          },
        },
      },
    },
  },
});

// ---------------------------------------------------------------------------
// Wiggum dimensions radar
// ---------------------------------------------------------------------------
new Chart($('radarChart'), {
  type: 'radar',
  data: {
    labels: DATA.wiggum_dims.labels,
    datasets: [{
      data:            DATA.wiggum_dims.values,
      borderColor:     '#4f8ef7',
      backgroundColor: 'rgba(79,142,247,0.15)',
      pointBackgroundColor: '#4f8ef7',
      borderWidth: 2,
      pointRadius: 3,
    }],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      r: {
        min: 0, max: 10,
        ticks:    { color: '#8b949e', font: { size: 10 }, stepSize: 2, backdropColor: 'transparent' },
        grid:     { color: '#30363d' },
        pointLabels: { color: '#e6edf3', font: { size: 12 } },
        angleLines: { color: '#30363d' },
      },
    },
  },
});

// ---------------------------------------------------------------------------
// Pass / Fail / Error donut
// ---------------------------------------------------------------------------
new Chart($('finalChart'), {
  type: 'doughnut',
  data: {
    labels: ['Pass', 'Fail', 'Error'],
    datasets: [{
      data: [kpi.passed, kpi.failed, kpi.errors],
      backgroundColor: ['rgba(63,185,80,0.8)', 'rgba(248,81,73,0.8)', 'rgba(139,148,158,0.5)'],
      borderColor: '#161b22',
      borderWidth: 2,
    }],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: true, position: 'right', labels: { color: '#8b949e', font: { size: 11 }, padding: 12 } },
    },
  },
});

// ---------------------------------------------------------------------------
// Duration trend
// ---------------------------------------------------------------------------
new Chart($('durationChart'), {
  type: 'line',
  data: {
    labels: DATA.duration_trend.labels,
    datasets: [{
      data:            DATA.duration_trend.values,
      borderColor:     '#fb923c',
      backgroundColor: 'rgba(251,146,60,0.08)',
      pointRadius: 1.5,
      borderWidth: 1.5,
      tension: 0.3,
      fill: true,
    }],
  },
  options: {
    ...CHART_DEFAULTS,
    scales: {
      x: { ...CHART_DEFAULTS.scales.x, ticks: { ...CHART_DEFAULTS.scales.x.ticks, maxTicksLimit: 10 } },
      y: { ...CHART_DEFAULTS.scales.y, title: { display: true, text: 'min', color: '#8b949e', font: { size: 10 } } },
    },
  },
});

// ---------------------------------------------------------------------------
// Hour-of-day bar
// ---------------------------------------------------------------------------
new Chart($('hourChart'), {
  type: 'bar',
  data: {
    labels: DATA.hour_dist.labels,
    datasets: [{
      data:            DATA.hour_dist.values,
      backgroundColor: 'rgba(167,139,250,0.7)',
      borderRadius: 3,
    }],
  },
  options: {
    ...CHART_DEFAULTS,
    scales: {
      x: { ...CHART_DEFAULTS.scales.x, ticks: { ...CHART_DEFAULTS.scales.x.ticks, maxTicksLimit: 12 } },
      y: { ...CHART_DEFAULTS.scales.y },
    },
  },
});

// ---------------------------------------------------------------------------
// Throughput — tokens/sec
// ---------------------------------------------------------------------------
const TPS = DATA.toks_per_sec;

// Output tok/s per stage — horizontal bar, sorted descending
const tpsStageOrder = TPS.stage_names
  .map((n, i) => ({ name: n, out: TPS.stage_out[i], inp: TPS.stage_in[i], color: TPS.stage_colors[i] }))
  .filter(d => d.out > 0 || d.inp > 0)
  .sort((a, b) => b.out - a.out);

new Chart($('tpsStageChart'), {
  type: 'bar',
  data: {
    labels: tpsStageOrder.map(d => d.name),
    datasets: [
      {
        label: 'Output tok/s (generation)',
        data:            tpsStageOrder.map(d => d.out),
        backgroundColor: tpsStageOrder.map(d => d.color),
        borderRadius: 3,
      },
      {
        label: 'Input tok/s (prefill)',
        data:            tpsStageOrder.map(d => d.inp),
        backgroundColor: 'rgba(139,148,158,0.3)',
        borderRadius: 3,
      },
    ],
  },
  options: {
    ...CHART_DEFAULTS,
    indexAxis: 'y',
    plugins: {
      legend: { display: true, labels: { color: '#8b949e', font: { size: 11 } } },
      tooltip: { callbacks: { label: ctx => ` ${ctx.raw} tok/s` } },
    },
    scales: {
      x: { ...CHART_DEFAULTS.scales.x, title: { display: true, text: 'tok/s', color: '#8b949e', font: { size: 10 } } },
      y: { ...CHART_DEFAULTS.scales.y, grid: { display: false } },
    },
  },
});

// Per-run output tok/s trend
const tpsStride = Math.max(1, Math.floor(TPS.run_labels.length / 150));
new Chart($('tpsTrendChart'), {
  type: 'line',
  data: {
    labels: TPS.run_labels.filter((_, i) => i % tpsStride === 0),
    datasets: [
      {
        label: 'Output tok/s',
        data:            TPS.run_out.filter((_, i) => i % tpsStride === 0),
        borderColor:     '#4ade80',
        backgroundColor: 'rgba(74,222,128,0.08)',
        pointRadius: 2,
        borderWidth: 1.5,
        tension: 0.3,
        fill: true,
      },
      {
        label: 'Input tok/s',
        data:            TPS.run_in.filter((_, i) => i % tpsStride === 0),
        borderColor:     '#4f8ef7',
        backgroundColor: 'rgba(79,142,247,0.05)',
        pointRadius: 1,
        borderWidth: 1,
        tension: 0.3,
        fill: true,
      },
    ],
  },
  options: {
    ...CHART_DEFAULTS,
    plugins: {
      legend: { display: true, labels: { color: '#8b949e', font: { size: 11 } } },
      tooltip: { callbacks: { label: ctx => ` ${ctx.raw} tok/s` } },
    },
    scales: {
      x: { ...CHART_DEFAULTS.scales.x, ticks: { ...CHART_DEFAULTS.scales.x.ticks, maxTicksLimit: 10 } },
      y: { ...CHART_DEFAULTS.scales.y, title: { display: true, text: 'tok/s', color: '#8b949e', font: { size: 10 } }, min: 0 },
    },
  },
});

// ---------------------------------------------------------------------------
// Recent runs table — with expandable detail rows
// ---------------------------------------------------------------------------
const tbl = $('runsTable');
const cols = ['','Timestamp','Task','Model','Type','Score','Rounds','Duration','In tok','Out tok','Searches','Result'];
tbl.innerHTML = `<tr>${cols.map(c=>`<th>${c}</th>`).join('')}</tr>`;

const DIM_COLORS = {
  relevance:    '#4f8ef7',
  completeness: '#3fb950',
  depth:        '#a78bfa',
  specificity:  '#fb923c',
  structure:    '#f472b6',
};

function buildDetailInner(r) {
  const cards = [];

  // Card: Task (full text)
  cards.push(`
    <div class="detail-card" style="grid-column: 1 / -1">
      <div class="detail-card-title">Task</div>
      <div class="task-full">${(r.task_full || r.task).replace(/</g,'&lt;')}</div>
    </div>`);

  // Card: Memory
  const memColor = r.memory_hits > 0 ? 'var(--blue)' : 'var(--muted)';
  cards.push(`
    <div class="detail-card">
      <div class="detail-card-title">Memory</div>
      <div style="font-size:22px;font-weight:700;color:${memColor};line-height:1.1">${r.memory_hits}</div>
      <div style="color:var(--muted);font-size:11px;margin-top:4px">${r.memory_hits === 1 ? 'prior observation retrieved' : r.memory_hits > 1 ? 'prior observations retrieved' : 'no prior context'}</div>
    </div>`);

  // Card: Email draft details (per-contact trace)
  if (r.email_subject) {
    const esc = s => (s||'').replace(/</g,'&lt;').replace(/\n/g,'<br>');
    cards.push(`
      <div class="detail-card" style="grid-column: 1 / -1">
        <div class="detail-card-title">Email Draft</div>
        <div style="margin-bottom:8px">
          <span style="color:var(--muted);font-size:11px">To</span>
          <span style="margin-left:8px;font-weight:600">${esc(r.email_name)}</span>
          <span style="color:var(--muted);font-size:11px;margin-left:6px">${esc(r.email_affiliation)}</span>
          <span style="color:var(--blue);font-size:11px;margin-left:8px">&lt;${esc(r.email_to)}&gt;</span>
        </div>
        <div style="margin-bottom:10px">
          <span style="color:var(--muted);font-size:11px">Subject</span>
          <span style="margin-left:8px;font-weight:600;color:var(--green)">${esc(r.email_subject)}</span>
        </div>
        <div style="background:var(--bg2);border-radius:4px;padding:10px;font-size:12px;line-height:1.6;white-space:pre-wrap;border:1px solid var(--border)">${esc(r.email_body)}</div>
      </div>`);

    if (r.email_subject_prompt || r.email_body_prompt) {
      cards.push(`
        <div class="detail-card" style="grid-column: 1 / -1">
          <div class="detail-card-title">Prompts</div>
          ${r.email_subject_prompt ? `
            <div style="color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">Subject prompt</div>
            <div style="background:var(--bg2);border-radius:4px;padding:8px;font-size:11px;font-family:monospace;white-space:pre-wrap;border:1px solid var(--border);margin-bottom:10px">${esc(r.email_subject_prompt)}</div>` : ''}
          ${r.email_body_prompt ? `
            <div style="color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">Body prompt</div>
            <div style="background:var(--bg2);border-radius:4px;padding:8px;font-size:11px;font-family:monospace;white-space:pre-wrap;border:1px solid var(--border)">${esc(r.email_body_prompt)}</div>` : ''}
        </div>`);
    }
  }

  // Card: Email batch summary
  if (r.email_drafts != null) {
    const manifestPath = (r.email_output_dir || '').replace(/\\/g, '/').replace(/\/?$/, '/') + 'manifest.json';
    cards.push(`
      <div class="detail-card">
        <div class="detail-card-title">Email Batch</div>
        <div style="font-size:22px;font-weight:700;color:var(--blue);line-height:1.1">${r.email_drafts}</div>
        <div style="color:var(--muted);font-size:11px;margin-top:4px">draft${r.email_drafts !== 1 ? 's' : ''} generated</div>
        <div style="color:var(--muted);font-size:11px;margin-top:6px">&#128193; ${r.email_output_dir || '—'}</div>
        <div style="margin-top:8px"><a href="${manifestPath}" target="_blank"
          style="font-size:11px;color:var(--blue);text-decoration:none">manifest.json &#8599;</a></div>
      </div>`);
  }

  // Card: Score trajectory + flags
  const trajectory = (r.score_trajectory || []);
  const pills = trajectory.length
    ? trajectory.map((s,i) => {
        const isFirst = i === 0, isLast = i === trajectory.length - 1 && trajectory.length > 1;
        const col = isFirst ? 'rgba(79,142,247,.15)' : isLast ? 'rgba(63,185,80,.2)' : 'rgba(139,148,158,.15)';
        const tcol = isFirst ? 'var(--blue)' : isLast ? 'var(--green)' : 'var(--muted)';
        return `<span class="score-pill" style="background:${col};color:${tcol}">r${i+1}: ${s}</span>`;
      }).join('')
    : '<span style="color:var(--muted);font-size:11px">no scores</span>';
  const flags = [];
  if (r.count_check_retry) flags.push(`<span style="color:var(--orange);font-size:11px">&#9888; count retry</span>`);
  if ((r.novelty_scores||[]).length) flags.push(`<span style="color:var(--muted);font-size:11px">novelty: ${r.novelty_scores.join(', ')}</span>`);
  const outInfo = r.output_bytes > 0
    ? `<div style="color:var(--muted);font-size:11px;margin-top:6px">${(r.output_bytes/1024).toFixed(1)} KB &middot; ${r.output_lines} lines</div>` : '';
  cards.push(`
    <div class="detail-card">
      <div class="detail-card-title">Score trajectory</div>
      <div>${pills}</div>
      ${flags.length ? `<div style="margin-top:6px">${flags.join(' &nbsp; ')}</div>` : ''}
      ${outInfo}
    </div>`);

  // Card: Wiggum dimensions
  if (r.dims && Object.keys(r.dims).length) {
    const dimRows = Object.entries(r.dims).map(([k, v]) => {
      const col = DIM_COLORS[k] || 'var(--blue)';
      return `<div class="dim-row">
        <span class="dim-label">${k}</span>
        <div class="dim-bar-wrap"><div class="dim-bar-fill" style="width:${v*10}%;background:${col}"></div></div>
        <span class="dim-value">${v}</span>
      </div>`;
    }).join('');
    cards.push(`
      <div class="detail-card">
        <div class="detail-card-title">Dimensions (r1)</div>
        ${dimRows}
      </div>`);
  }

  // Card: Evaluator issues (r1)
  if (r.issues && r.issues.length) {
    const issueItems = r.issues.map(iss =>
      `<div class="issue-item">${iss.replace(/</g,'&lt;')}</div>`
    ).join('');
    const countLabel = `<div style="color:var(--muted);font-size:10px;margin-bottom:6px">${r.issues.length} issue${r.issues.length > 1 ? 's' : ''}</div>`;
    cards.push(`
      <div class="detail-card">
        <div class="detail-card-title">Issues (r1)</div>
        ${countLabel}
        <div class="issues-scroll">${issueItems}</div>
      </div>`);
  }

  // Card: Evaluator feedback
  if (r.feedback) {
    cards.push(`
      <div class="detail-card">
        <div class="detail-card-title">Evaluator feedback (r1)</div>
        <div class="feedback-text">${r.feedback.replace(/</g,'&lt;')}</div>
      </div>`);
  }

  // Card: RLHF feedback panel
  const fbKey = 'rlhf_' + (r.run_id || r.ts);
  const savedFb = (() => { try { return JSON.parse(localStorage.getItem(fbKey) || 'null'); } catch(e) { return null; } })();
  const savedRating  = savedFb ? savedFb.rating  : 0;
  const savedEdited  = savedFb ? (savedFb.edited_output || '') : '';
  const savedComment = savedFb ? (savedFb.comment || '') : '';
  const fbSaved      = savedFb != null;
  const thumbUp   = savedRating ===  1 ? 'btn-thumb-active' : '';
  const thumbDown = savedRating === -1 ? 'btn-thumb-active' : '';
  const savedNote = fbSaved ? `<span style="color:var(--green);font-size:10px">saved</span>` : '';
  cards.push(`
    <div class="detail-card detail-card-feedback rlhf-panel" id="fb-card-${fbKey}">
      <div class="detail-card-title" style="display:flex;align-items:center;gap:8px">
        RLHF Feedback ${savedNote}
        <button class="btn-thumb ${thumbUp}"  data-fb="${fbKey}" data-rating="1"  title="Good output">&#128077;</button>
        <button class="btn-thumb ${thumbDown}" data-fb="${fbKey}" data-rating="-1" title="Bad output">&#128078;</button>
      </div>
      <textarea class="fb-edit" id="fb-edit-${fbKey}" rows="4"
        placeholder="Edit or annotate the output here (optional — saved as preferred version for RLHF)"
        style="width:100%;box-sizing:border-box;background:var(--bg2);color:var(--fg);border:1px solid var(--border);border-radius:4px;padding:6px;font-size:11px;font-family:monospace;resize:vertical"
      >${savedEdited.replace(/</g,'&lt;')}</textarea>
      <input class="fb-comment" id="fb-comment-${fbKey}" type="text"
        value="${savedComment.replace(/"/g,'&quot;')}"
        placeholder="Optional comment (e.g. what was wrong)"
        style="width:100%;box-sizing:border-box;margin-top:4px;background:var(--bg2);color:var(--fg);border:1px solid var(--border);border-radius:4px;padding:5px 6px;font-size:11px"
      />
      <button class="btn-save-fb" data-fb="${fbKey}" data-run-id="${r.run_id || ''}" data-task="${(r.task||'').replace(/"/g,'&quot;')}"
        style="margin-top:6px;padding:4px 12px;font-size:11px;cursor:pointer;background:var(--accent);color:#fff;border:none;border-radius:4px">
        Save feedback
      </button>
    </div>`);

  return cards.join('');
}

DATA.recent_runs.forEach((r, idx) => {
  const scoreBar = r.score != null
    ? `<span class="score-bar"><span class="score-fill" style="width:${r.score*10}%"></span></span>${r.score}`
    : '&mdash;';
  const badge = r.final === 'PASS'  ? `<span class="badge badge-pass">PASS</span>`
              : r.final === 'FAIL'  ? `<span class="badge badge-fail">FAIL</span>`
              : r.final === 'ERROR' ? `<span class="badge badge-error">ERR</span>`
              : r.final;
  const detailId = `run-detail-${idx}`;
  const btnId    = `run-btn-${idx}`;

  const cells = [
    `<td style="width:28px;padding:7px 6px"><button class="chevron-btn" id="${btnId}" data-detail="${detailId}" aria-label="expand">&#x276F;</button></td>`,
    `<td style="color:var(--muted);font-size:11px">${r.ts}</td>`,
    `<td style="max-width:260px;overflow:hidden;text-overflow:ellipsis" title="${r.task.replace(/"/g,'&quot;')}">${r.task}</td>`,
    `<td style="color:var(--muted)">${r.model}</td>`,
    `<td style="color:var(--muted)">${r.type}</td>`,
    `<td>${scoreBar}</td>`,
    `<td style="color:var(--muted);text-align:center">${r.rounds ?? '&mdash;'}</td>`,
    `<td style="color:var(--orange)">${r.duration}m</td>`,
    `<td style="color:var(--muted)">${fmtK(r.tokens_in)}</td>`,
    `<td style="color:var(--muted)">${fmtK(r.tokens_out)}</td>`,
    `<td style="text-align:center;color:var(--muted)">${r.searches}</td>`,
    `<td>${badge}</td>`,
  ];

  const colspan = cols.length;
  tbl.innerHTML += `
    <tr class="run-row">${cells.join('')}</tr>
    <tr class="detail-row hidden" id="${detailId}">
      <td colspan="${colspan}">
        <div class="detail-inner">${buildDetailInner(r)}</div>
      </td>
    </tr>`;
});

// Attach click handlers after DOM is built
tbl.querySelectorAll('.chevron-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const detailRow = document.getElementById(btn.dataset.detail);
    const isHidden = detailRow.classList.toggle('hidden');
    btn.classList.toggle('open', !isHidden);
  });
});

// ---------------------------------------------------------------------------
// RLHF feedback handlers
// ---------------------------------------------------------------------------
tbl.querySelectorAll('.btn-thumb').forEach(btn => {
  btn.addEventListener('click', () => {
    const fbKey  = btn.dataset.fb;
    const rating = parseInt(btn.dataset.rating, 10);
    // Load existing saved state
    let saved = {};
    try { saved = JSON.parse(localStorage.getItem(fbKey) || '{}'); } catch(e) {}
    // Toggle: clicking same thumb again clears rating
    const newRating = saved.rating === rating ? 0 : rating;
    saved.rating = newRating;
    localStorage.setItem(fbKey, JSON.stringify(saved));
    // Update button active state within this detail block
    const parent = btn.closest('.rlhf-panel');
    if (parent) {
      parent.querySelectorAll('.btn-thumb').forEach(b => b.classList.remove('btn-thumb-active'));
      if (newRating !== 0) {
        parent.querySelectorAll(`.btn-thumb[data-rating="${newRating}"]`).forEach(b => b.classList.add('btn-thumb-active'));
      }
    }
  });
});

tbl.querySelectorAll('.btn-save-fb').forEach(btn => {
  btn.addEventListener('click', () => {
    const fbKey  = btn.dataset.fb;
    const runId  = btn.dataset.runId;
    const task   = btn.dataset.task;
    // Read current panel state
    const editArea   = document.getElementById('fb-edit-' + fbKey);
    const commentEl  = document.getElementById('fb-comment-' + fbKey);
    const editedOut  = editArea   ? editArea.value   : '';
    const comment    = commentEl  ? commentEl.value  : '';
    // Get rating from localStorage
    let saved = {};
    try { saved = JSON.parse(localStorage.getItem(fbKey) || '{}'); } catch(e) {}
    const rating = saved.rating || 0;
    // Persist full state to localStorage
    saved.edited_output = editedOut;
    saved.comment       = comment;
    localStorage.setItem(fbKey, JSON.stringify(saved));
    // POST to server
    fetch('/api/feedback', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        run_id:          runId,
        task:            task,
        rating:          rating,
        original_output: saved.original_output || editedOut,
        edited_output:   editedOut,
        comment:         comment,
      }),
    }).then(r => r.json()).then(() => {
      btn.textContent = 'Saved!';
      btn.style.background = 'var(--green)';
      setTimeout(() => { btn.textContent = 'Save feedback'; btn.style.background = ''; }, 1800);
    }).catch(() => {
      btn.textContent = 'Error';
      btn.style.background = 'var(--red)';
      setTimeout(() => { btn.textContent = 'Save feedback'; btn.style.background = ''; }, 1800);
    });
  });
});

// ---------------------------------------------------------------------------
// Cost analysis
// ---------------------------------------------------------------------------
const C = DATA.cost;
const fmt$ = n => '$' + n.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 4});

// KPI cards
const cheapestCloud = C.tier_rows[0];
const savings       = cheapestCloud ? cheapestCloud.savings : 0;
const costCards = [
  { label: 'Local electricity',  value: fmt$(C.electricity_cost),
    sub: `${C.total_runtime_h}h × ${C.gpu_watts}W @ $${C.electricity_rate}/kWh`, cls: 'green' },
  { label: 'Cheapest cloud equiv', value: fmt$(cheapestCloud?.cost ?? 0),
    sub: cheapestCloud?.name ?? '', cls: 'orange' },
  { label: 'Savings vs cheapest',  value: fmt$(savings),
    sub: savings > 0 ? 'kept in your pocket' : 'cloud cheaper', cls: savings > 0 ? 'green' : 'red' },
  { label: 'Most expensive equiv', value: fmt$(C.tier_rows[C.tier_rows.length-1]?.cost ?? 0),
    sub: C.tier_rows[C.tier_rows.length-1]?.name ?? '', cls: 'purple' },
  { label: 'Input tokens',  value: fmtK(C.total_in),  sub: 'across all stages', cls: 'blue' },
  { label: 'Output tokens', value: fmtK(C.total_out), sub: 'across all stages', cls: 'blue' },
];
$('cost-kpi-grid').innerHTML = costCards.map(c => `
  <div class="kpi ${c.cls}">
    <div class="kpi-label">${c.label}</div>
    <div class="kpi-value">${c.value}</div>
    ${c.sub ? `<div class="kpi-sub">${c.sub}</div>` : ''}
  </div>`).join('');

// Cloud tier comparison table
const ctbl = $('costTable');
ctbl.innerHTML = `<tr>
  <th>Provider</th>
  <th>$/1M in</th>
  <th>$/1M out</th>
  <th>Est. total cost</th>
  <th>Savings vs local</th>
</tr>`;
C.tier_rows.forEach(row => {
  const savCls = row.savings > 0 ? 'saving-pos' : 'saving-neg';
  const savStr = (row.savings > 0 ? '+' : '') + fmt$(row.savings);
  ctbl.innerHTML += `<tr>
    <td>${row.name}</td>
    <td style="color:var(--muted)">${fmt$(row.price_in)}</td>
    <td style="color:var(--muted)">${fmt$(row.price_out)}</td>
    <td style="color:var(--yellow);font-weight:600">${fmt$(row.cost)}</td>
    <td class="${savCls}">${savStr}</td>
  </tr>`;
});
// Electricity row at bottom
ctbl.innerHTML += `<tr style="border-top:1px solid var(--border)">
  <td style="color:var(--green);font-weight:600">Local (electricity)</td>
  <td colspan="2" style="color:var(--muted);font-size:11px">${C.gpu_watts}W × ${C.total_runtime_h}h</td>
  <td style="color:var(--green);font-weight:600">${fmt$(C.electricity_cost)}</td>
  <td style="color:var(--muted)">baseline</td>
</tr>`;

// Tokens by role (horizontal stacked bar)
const roleLabels = C.role_data.map(d => d.role);
new Chart($('roleChart'), {
  type: 'bar',
  data: {
    labels: ['Input', 'Output'],
    datasets: C.role_data.map(d => ({
      label:           d.role,
      data:            [d.input, d.output],
      backgroundColor: d.color,
      borderRadius:    3,
    })),
  },
  options: {
    ...CHART_DEFAULTS,
    plugins: {
      legend: { display: true, labels: { color: '#8b949e', font: { size: 11 } } },
    },
    scales: {
      x: { ...CHART_DEFAULTS.scales.x, stacked: true },
      y: { ...CHART_DEFAULTS.scales.y, stacked: true,
           ticks: { ...CHART_DEFAULTS.scales.y.ticks, callback: v => fmtK(v) } },
    },
  },
});

// Cumulative cost chart
// Downsample to at most 200 points so the line renders cleanly
const stride = Math.max(1, Math.floor(C.cumulative_labels.length / 200));
const cumL  = C.cumulative_labels.filter((_,i)  => i % stride === 0);
const cumCl = C.cumulative_cloud.filter((_,i)   => i % stride === 0);
const cumEl = C.cumulative_electric.filter((_,i) => i % stride === 0);

new Chart($('cumulCostChart'), {
  type: 'line',
  data: {
    labels: cumL,
    datasets: [
      {
        label:           C.cheapest_tier,
        data:            cumCl,
        borderColor:     '#fb923c',
        backgroundColor: 'rgba(251,146,60,0.07)',
        borderWidth: 1.5, pointRadius: 0, tension: 0.3, fill: true,
      },
      {
        label:           'Local electricity',
        data:            cumEl,
        borderColor:     '#4ade80',
        backgroundColor: 'rgba(74,222,128,0.07)',
        borderWidth: 1.5, pointRadius: 0, tension: 0.3, fill: true,
      },
    ],
  },
  options: {
    ...CHART_DEFAULTS,
    plugins: {
      legend: { display: true, labels: { color: '#8b949e', font: { size: 11 } } },
      tooltip: { callbacks: { label: ctx => ` ${fmt$(ctx.raw)}` } },
    },
    scales: {
      x: { ...CHART_DEFAULTS.scales.x, ticks: { ...CHART_DEFAULTS.scales.x.ticks, maxTicksLimit: 10 } },
      y: { ...CHART_DEFAULTS.scales.y, ticks: { ...CHART_DEFAULTS.scales.y.ticks, callback: v => fmt$(v) } },
    },
  },
});

// ---------------------------------------------------------------------------
// Fine-tuning live metrics — polls /api/finetune/metrics every 8s
// ---------------------------------------------------------------------------
(function () {
  if (location.protocol === 'file:') return;

  let ftLossChart = null, ftAccChart = null, ftGradChart = null, ftLrChart = null;

  function mkFtChart(id, label, color) {
    return new Chart($(id), {
      type: 'line',
      data: { labels: [], datasets: [{ label, data: [], borderColor: color,
        backgroundColor: color.replace(')', ',0.08)').replace('rgb', 'rgba'),
        borderWidth: 1.5, pointRadius: 0, tension: 0.3, fill: true }] },
      options: { ...CHART_DEFAULTS, plugins: { legend: { display: false } } },
    });
  }

  function fmtEta(s) {
    if (!s) return '--';
    const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60);
    return h > 0 ? `${h}h ${m}m` : `${m}m`;
  }

  function renderFt(records) {
    const metrics = records.filter(r => r.type === 'metric');
    const begin   = records.find(r  => r.type === 'train_begin');
    const ended   = records.find(r  => r.type === 'train_end');
    if (!metrics.length) return;

    const steps   = metrics.map(r => r.step);
    const losses  = metrics.map(r => r.loss ?? null);
    const accs    = metrics.map(r => r.mean_token_accuracy ?? null);
    const grads   = metrics.map(r => r.grad_norm ?? null);
    const lrs     = metrics.map(r => r.learning_rate ?? null);
    const last    = metrics[metrics.length - 1];
    const maxSteps = begin?.max_steps || last.max_steps || 1;
    const pct     = Math.round((last.step / maxSteps) * 100);

    // KPI cards
    const status  = ended ? 'Complete' : `${pct}% — step ${last.step}/${maxSteps}`;
    const etaStr  = ended ? 'Done' : fmtEta(last.eta_s);
    const elapsed = last.elapsed_s ? fmtEta(last.elapsed_s) : '--';
    $('ft-kpi-grid').innerHTML = [
      { label: 'Status',       value: status,                            cls: ended ? 'green' : 'blue' },
      { label: 'Loss',         value: last.loss?.toFixed(4) ?? '--',     cls: 'yellow' },
      { label: 'Token acc',    value: last.mean_token_accuracy ? (last.mean_token_accuracy * 100).toFixed(1) + '%' : '--', cls: 'purple' },
      { label: 'Grad norm',    value: last.grad_norm?.toFixed(3) ?? '--', cls: 'orange' },
      { label: 'Elapsed',      value: elapsed,                           cls: 'muted' },
      { label: 'ETA',          value: etaStr,                            cls: 'muted' },
    ].map(c => `<div class="kpi ${c.cls}">
      <div class="kpi-label">${c.label}</div>
      <div class="kpi-value" style="font-size:18px">${c.value}</div>
    </div>`).join('');

    // Update or create charts
    function syncChart(chart, id, label, color, data) {
      if (!chart) chart = mkFtChart(id, label, color);
      chart.data.labels = steps;
      chart.data.datasets[0].data = data;
      chart.update('none');
      return chart;
    }
    ftLossChart = syncChart(ftLossChart, 'ftLossChart', 'Loss',       'rgb(251,146,60)',  losses);
    ftAccChart  = syncChart(ftAccChart,  'ftAccChart',  'Token acc',  'rgb(74,222,128)',  accs);
    ftGradChart = syncChart(ftGradChart, 'ftGradChart', 'Grad norm',  'rgb(139,92,246)',  grads);
    ftLrChart   = syncChart(ftLrChart,   'ftLrChart',   'Learn rate', 'rgb(96,165,250)',  lrs);
  }

  function pollFt() {
    fetch('/api/finetune/metrics').then(r => r.json()).then(data => {
      if (data && data.length) renderFt(data);
    }).catch(() => {});
  }

  pollFt();
  setInterval(pollFt, 8000);
})();

// ---------------------------------------------------------------------------
// Live panel — only active when served via server.py (http: protocol)
// Hidden entirely in static file:// mode.
// ---------------------------------------------------------------------------
(function () {
  if (location.protocol === 'file:') return;   // static mode — skip

  // ── Inject Live section into DOM ─────────────────────────────────────────
  const liveSection = document.createElement('div');
  liveSection.id = 'live-section';
  liveSection.innerHTML = `
<style>
  #live-section { margin-top: 32px; }
  .live-heading {
    font-size: 13px; font-weight: 600; color: var(--muted);
    text-transform: uppercase; letter-spacing: 0.05em;
    margin: 0 0 14px; padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; gap: 10px;
  }
  .live-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--green); flex-shrink: 0;
    box-shadow: 0 0 6px var(--green);
    animation: pulse 2s infinite;
  }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }

  /* Submit form */
  .live-form-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 8px; padding: 18px 20px; margin-bottom: 16px;
  }
  .live-form-title {
    font-size: 12px; font-weight: 600; color: var(--muted);
    text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px;
  }
  .live-task-input {
    width: 100%; background: var(--bg); border: 1px solid var(--border);
    border-radius: 6px; color: var(--text); font-size: 13px;
    padding: 10px 12px; resize: vertical; min-height: 60px;
    font-family: inherit; margin-bottom: 10px;
  }
  .live-task-input:focus { outline: none; border-color: var(--blue); }
  .live-form-row { display: flex; gap: 10px; align-items: flex-end; flex-wrap: wrap; }
  .live-cron-wrap { display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 180px; }
  .live-cron-label { font-size: 11px; color: var(--muted); }
  .live-cron-input {
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 6px; color: var(--text); font-size: 12px;
    padding: 8px 10px; font-family: monospace; width: 100%;
  }
  .live-cron-input:focus { outline: none; border-color: var(--purple); }
  .live-cron-hint { font-size: 10px; color: var(--muted); margin-top: 2px; }
  .live-btn {
    padding: 8px 18px; border-radius: 6px; border: none; cursor: pointer;
    font-size: 13px; font-weight: 600; white-space: nowrap;
    transition: opacity .15s;
  }
  .live-btn:hover { opacity: .85; }
  .live-btn:disabled { opacity: .4; cursor: default; }
  .btn-run    { background: var(--blue);   color: #fff; }
  .btn-sched  { background: var(--purple); color: #fff; }
  .live-msg { font-size: 12px; margin-top: 8px; min-height: 18px; }

  /* Active run cards */
  .run-cards { display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px; }
  .run-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 8px; overflow: hidden;
  }
  .run-card-header {
    display: flex; align-items: center; gap: 10px;
    padding: 12px 16px; border-bottom: 1px solid var(--border);
    flex-wrap: wrap; gap: 8px;
  }
  .run-status-dot {
    width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
  }
  .run-status-dot.running { background: var(--blue); animation: pulse 1.5s infinite; }
  .run-status-dot.done    { background: var(--green); }
  .run-status-dot.error   { background: var(--red); }
  .run-id-badge {
    font-family: monospace; font-size: 11px; color: var(--muted);
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 4px; padding: 1px 6px;
  }
  .run-task-label {
    flex: 1; font-size: 12px; color: var(--text);
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0;
  }
  .run-meta { font-size: 11px; color: var(--muted); white-space: nowrap; }
  .btn-cancel {
    font-size: 11px; padding: 3px 10px; border-radius: 4px; border: none;
    background: rgba(248,81,73,.15); color: var(--red); cursor: pointer;
  }
  .btn-cancel:hover { background: rgba(248,81,73,.28); }
  .run-log {
    font-family: monospace; font-size: 11px; line-height: 1.55;
    background: var(--bg); color: var(--muted);
    padding: 10px 16px; max-height: 260px; overflow-y: auto;
    white-space: pre-wrap; word-break: break-all;
  }
  .log-line-stage  { color: var(--blue); }
  .log-line-pass   { color: var(--green); }
  .log-line-fail   { color: var(--red); }
  .log-line-warn   { color: var(--orange); }
  .log-line-done   { color: var(--purple); font-weight: 600; }

  /* Scheduled tasks table */
  .sched-empty { color: var(--muted); font-size: 12px; padding: 8px 0; }
  .btn-del-sched {
    font-size: 11px; padding: 2px 8px; border-radius: 4px; border: none;
    background: rgba(248,81,73,.12); color: var(--red); cursor: pointer;
  }
  .btn-del-sched:hover { background: rgba(248,81,73,.25); }
</style>

<div class="live-heading">
  <span class="live-dot"></span> Live
</div>

<!-- Submit form -->
<div class="live-form-card">
  <div class="live-form-title">Submit Task</div>
  <textarea class="live-task-input" id="liveTaskInput"
    placeholder='Search for the top 3 context window strategies and save to ~/Desktop/harness-engineering/out.md'></textarea>
  <div class="live-form-row">
    <div class="live-cron-wrap">
      <span class="live-cron-label">Schedule (cron) — leave blank to run now</span>
      <input class="live-cron-input" id="liveCronInput" placeholder="0 9 * * 1-5  (weekdays 9am)" />
      <span class="live-cron-hint">min hour day month weekday &nbsp;·&nbsp; * = any</span>
    </div>
    <button class="live-btn btn-run"   id="liveBtnRun">&#9654; Run now</button>
    <button class="live-btn btn-sched" id="liveBtnSched">&#128197; Schedule</button>
  </div>
  <div class="live-msg" id="liveMsg"></div>
</div>

<!-- Active runs -->
<div class="live-heading" style="margin-top:24px;font-size:12px">Active runs</div>
<div class="run-cards" id="activeRunCards">
  <div style="color:var(--muted);font-size:12px" id="noActiveRuns">No active runs.</div>
</div>

<!-- Scheduled tasks -->
<div class="live-heading" style="margin-top:24px;font-size:12px">Scheduled tasks</div>
<div id="schedList" style="margin-bottom:32px">
  <div class="sched-empty" id="noSched">No scheduled tasks.</div>
  <table id="schedTable" style="display:none;width:100%;border-collapse:collapse;font-size:12px">
    <tr>
      <th style="text-align:left;padding:6px 8px;color:var(--muted);border-bottom:1px solid var(--border)">Name</th>
      <th style="text-align:left;padding:6px 8px;color:var(--muted);border-bottom:1px solid var(--border)">Cron</th>
      <th style="text-align:left;padding:6px 8px;color:var(--muted);border-bottom:1px solid var(--border)">Task</th>
      <th style="text-align:left;padding:6px 8px;color:var(--muted);border-bottom:1px solid var(--border)">Next run</th>
      <th style="padding:6px 8px;border-bottom:1px solid var(--border)"></th>
    </tr>
    <tbody id="schedTbody"></tbody>
  </table>
</div>
`;
  document.body.appendChild(liveSection);

  // ── Helpers ──────────────────────────────────────────────────────────────
  const $ = id => document.getElementById(id);
  const fmtTs = iso => {
    if (!iso) return '—';
    try {
      const d = new Date(iso);
      return d.getFullYear() + '-' +
        String(d.getMonth()+1).padStart(2,'0') + '-' +
        String(d.getDate()).padStart(2,'0') + ' ' +
        String(d.getHours()).padStart(2,'0') + ':' +
        String(d.getMinutes()).padStart(2,'0') + ':' +
        String(d.getSeconds()).padStart(2,'0');
    } catch { return iso.replace('T',' '); }
  };

  function elapsed(startIso) {
    const s = Math.round((Date.now() - new Date(startIso)) / 1000);
    return s < 60 ? `${s}s` : `${Math.floor(s/60)}m ${s%60}s`;
  }

  function colorLine(raw) {
    const esc = raw.replace(/</g,'&lt;');
    if (/\[wiggum\]\s*PASS|\bPASS\b/.test(esc))  return `<span class="log-line-pass">${esc}</span>`;
    if (/\[wiggum\]\s*FAIL|\bFAIL\b/.test(esc))  return `<span class="log-line-fail">${esc}</span>`;
    if (/\[error\]/.test(esc))                    return `<span class="log-line-fail">${esc}</span>`;
    if (/\[DONE\]/.test(esc))                     return `<span class="log-line-done">${esc}</span>`;
    if (/\[synth\]|\[wiggum\]|\[skill/.test(esc)) return `<span class="log-line-stage">${esc}</span>`;
    if (/\[warn\]|count retry/.test(esc))         return `<span class="log-line-warn">${esc}</span>`;
    if (/turn \d|turn1|turn2/.test(esc))          return `<span class="log-line-stage">${esc}</span>`;
    return esc;
  }

  function setMsg(txt, color='var(--muted)') {
    $('liveMsg').style.color = color;
    $('liveMsg').textContent = txt;
  }

  // ── Active run card management ────────────────────────────────────────────
  const _cards = {};   // run_id → {el, logEl, es}

  function addRunCard(run) {
    if (_cards[run.run_id]) return;   // already tracked

    $('noActiveRuns').style.display = 'none';

    const card = document.createElement('div');
    card.className = 'run-card';
    card.id = `card-${run.run_id}`;
    card.innerHTML = `
      <div class="run-card-header">
        <span class="run-status-dot running" id="dot-${run.run_id}"></span>
        <span class="run-id-badge">${run.run_id}</span>
        <span class="run-task-label" title="${run.task.replace(/"/g,'&quot;')}">${run.task}</span>
        <span class="run-meta" id="meta-${run.run_id}">started ${fmtTs(run.start_ts)}</span>
        <button class="btn-cancel" onclick="cancelRun('${run.run_id}')">&#9632; Cancel</button>
      </div>
      <div class="run-log" id="log-${run.run_id}"></div>`;

    $('activeRunCards').appendChild(card);

    const logEl = $(`log-${run.run_id}`);

    // SSE stream
    const es = new EventSource(`/api/stream/${run.run_id}`);
    es.onmessage = e => {
      if (e.data === '[DONE]' || e.data === '[run not found]') {
        es.close();
        finishCard(run.run_id);
        return;
      }
      const line = document.createElement('div');
      line.innerHTML = colorLine(e.data);
      logEl.appendChild(line);
      logEl.scrollTop = logEl.scrollHeight;
    };
    es.onerror = () => { es.close(); finishCard(run.run_id); };

    _cards[run.run_id] = { el: card, logEl, es };
  }

  function finishCard(run_id) {
    const dot  = $(`dot-${run_id}`);
    const meta = $(`meta-${run_id}`);
    if (dot)  { dot.classList.remove('running'); dot.classList.add('done'); }
    if (meta) meta.textContent = 'completed';
    // Remove cancel button
    const card = $(`card-${run_id}`);
    if (card) card.querySelector('.btn-cancel')?.remove();
    delete _cards[run_id];
    if (Object.keys(_cards).length === 0) $('noActiveRuns').style.display = '';
  }

  window.cancelRun = function(run_id) {
    fetch(`/api/run/${run_id}/cancel`, {method:'POST'})
      .then(() => finishCard(run_id));
  };

  // ── Submit handlers ───────────────────────────────────────────────────────
  $('liveBtnRun').addEventListener('click', () => {
    const task = $('liveTaskInput').value.trim();
    if (!task) { setMsg('Enter a task first.', 'var(--orange)'); return; }
    $('liveBtnRun').disabled = true;
    setMsg('Starting…');
    fetch('/api/run', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({task}),
    })
    .then(r => r.json())
    .then(d => {
      if (d.error) { setMsg(d.error, 'var(--red)'); return; }
      setMsg(`Run ${d.run_id} started.`, 'var(--green)');
      $('liveTaskInput').value = '';
      addRunCard({run_id: d.run_id, task, start_ts: new Date().toISOString(), status:'running'});
    })
    .catch(e => setMsg(String(e), 'var(--red)'))
    .finally(() => $('liveBtnRun').disabled = false);
  });

  $('liveBtnSched').addEventListener('click', () => {
    const task = $('liveTaskInput').value.trim();
    const cron = $('liveCronInput').value.trim();
    if (!task) { setMsg('Enter a task first.', 'var(--orange)'); return; }
    if (!cron) { setMsg('Enter a cron expression to schedule.', 'var(--orange)'); return; }
    $('liveBtnSched').disabled = true;
    setMsg('Scheduling…');
    fetch('/api/schedule', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({task, cron}),
    })
    .then(r => r.json())
    .then(d => {
      if (d.error) { setMsg(d.error, 'var(--red)'); return; }
      setMsg(`Scheduled (${d.sched_id}) — next: ${fmtTs(d.next_run)}`, 'var(--purple)');
      $('liveTaskInput').value = '';
      $('liveCronInput').value = '';
      refreshSchedule();
    })
    .catch(e => setMsg(String(e), 'var(--red)'))
    .finally(() => $('liveBtnSched').disabled = false);
  });

  // ── Scheduled tasks table ─────────────────────────────────────────────────
  function refreshSchedule() {
    fetch('/api/schedule')
    .then(r => r.json())
    .then(d => {
      const rows = d.schedules || [];
      if (!d.cron_available) {
        $('noSched').textContent = 'APScheduler not installed — pip install apscheduler';
        $('schedTable').style.display = 'none';
        return;
      }
      $('noSched').style.display = rows.length ? 'none' : '';
      $('schedTable').style.display = rows.length ? '' : 'none';
      const tbody = $('schedTbody');
      tbody.innerHTML = '';
      rows.forEach(s => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td style="padding:6px 8px;color:var(--text)">${s.name}</td>
          <td style="padding:6px 8px;font-family:monospace;color:var(--purple)">${s.cron}</td>
          <td style="padding:6px 8px;color:var(--muted);max-width:280px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${s.task}">${s.task}</td>
          <td style="padding:6px 8px;color:var(--muted)">${fmtTs(s.next_run)}</td>
          <td style="padding:6px 8px;text-align:right">
            <button class="btn-del-sched" onclick="deleteSchedule('${s.sched_id}')">&#128465; Remove</button>
          </td>`;
        tbody.appendChild(tr);
      });
    });
  }

  window.deleteSchedule = function(id) {
    fetch(`/api/schedule/${id}`, {method:'DELETE'})
    .then(() => refreshSchedule());
  };

  // ── Polling: pick up runs started externally (autoresearch, CLI, etc.) ────
  function pollActive() {
    fetch('/api/runs')
    .then(r => r.json())
    .then(d => {
      (d.active || []).forEach(run => addRunCard(run));
    })
    .catch(() => {});
  }

  // Initial load + refresh every 10s
  refreshSchedule();
  pollActive();
  setInterval(() => { refreshSchedule(); pollActive(); }, 10_000);

  // Update elapsed time on active cards every second
  setInterval(() => {
    Object.entries(_cards).forEach(([id, {el}]) => {
      const meta = document.getElementById(`meta-${id}`);
      if (meta && el.dataset.startTs) meta.textContent = `running ${elapsed(el.dataset.startTs)}`;
    });
  }, 1000);

})();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Public API — used by server.py
# ---------------------------------------------------------------------------

def build() -> dict:
    """Load runs and return the full dashboard payload dict."""
    runs = load_runs()
    return build_payload(runs)


def render(payload: dict) -> str:
    """Render the HTML template with a pre-built payload dict."""
    payload_json = json.dumps(payload).replace("</", r"<\/")
    return HTML_TEMPLATE.replace("__DATA__", payload_json)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    args = sys.argv[1:]
    out_path  = OUT_PATH
    open_browser = "--open" in args
    if "--out" in args:
        idx = args.index("--out")
        if idx + 1 < len(args):
            out_path = args[idx + 1]

    print(f"[dashboard] reading {RUNS_PATH}...")
    runs = load_runs()
    print(f"[dashboard] {len(runs)} runs loaded")

    payload  = build_payload(runs)
    # Escape closing script tags in JSON to prevent XSS when embedded in <script>
    payload_json = json.dumps(payload).replace("</", r"<\/")
    html     = HTML_TEMPLATE.replace("__DATA__", payload_json)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(out_path) // 1024
    print(f"[dashboard] wrote {out_path} ({size_kb} KB)")

    if open_browser:
        webbrowser.open(f"file:///{os.path.abspath(out_path)}")


if __name__ == "__main__":
    main()
