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

RUNS_PATH        = os.path.join(os.path.dirname(__file__), "runs.jsonl")
OUT_PATH         = os.path.join(os.path.dirname(__file__), "dashboard.html")
CLAUDE_STATS_PATH = os.path.expanduser(r"~\.claude\stats-cache.json")

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


_CLAUDE_MODELS = {"claude-"}  # prefix filter — excludes local gguf/qwen models

def load_claude_stats() -> dict:
    """Load Claude Code stats-cache.json and return chart-ready data."""
    try:
        with open(CLAUDE_STATS_PATH, encoding="utf-8") as f:
            raw = json.load(f)
    except Exception:
        return {}

    activity = sorted(raw.get("dailyActivity", []), key=lambda x: x["date"])
    model_usage = raw.get("modelUsage", {})

    # Filter to Claude-only models
    claude_usage = {k: v for k, v in model_usage.items() if k.startswith("claude-")}

    total_input  = sum(v.get("inputTokens", 0) for v in claude_usage.values())
    total_output = sum(v.get("outputTokens", 0) for v in claude_usage.values())
    total_cache  = sum(v.get("cacheReadInputTokens", 0) for v in claude_usage.values())

    # Daily messages / tool calls
    dates         = [a["date"] for a in activity]
    msg_counts    = [a["messageCount"] for a in activity]
    tool_counts   = [a["toolCallCount"] for a in activity]

    # Tokens by model (Claude only)
    model_names   = list(claude_usage.keys())
    model_in      = [claude_usage[m].get("inputTokens", 0) for m in model_names]
    model_out     = [claude_usage[m].get("outputTokens", 0) for m in model_names]

    # Daily token totals (Claude models only, from dailyModelTokens)
    daily_tok_map = defaultdict(int)
    for entry in raw.get("dailyModelTokens", []):
        for model, tokens in entry.get("tokensByModel", {}).items():
            if model.startswith("claude-"):
                daily_tok_map[entry["date"]] += tokens
    tok_dates  = sorted(daily_tok_map)
    tok_values = [daily_tok_map[d] for d in tok_dates]

    return {
        "total_sessions":  raw.get("totalSessions", 0),
        "total_messages":  raw.get("totalMessages", 0),
        "total_input":     total_input,
        "total_output":    total_output,
        "total_cache":     total_cache,
        "first_date":      (raw.get("firstSessionDate") or "")[:10],
        "last_date":       raw.get("lastComputedDate", ""),
        "dates":           dates,
        "msg_counts":      msg_counts,
        "tool_counts":     tool_counts,
        "model_names":     model_names,
        "model_in":        model_in,
        "model_out":       model_out,
        "tok_dates":       tok_dates,
        "tok_values":      tok_values,
    }


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
    dag_runs = []
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

        # --- DAG run (richer pipeline record) ---
        raw_tool_calls = r.get("tool_calls") or []
        dag_tool_calls = [
            {
                "name":         tc.get("name") or tc.get("tool") or "search",
                "query":        tc.get("query") or tc.get("input") or "",
                "result_chars": tc.get("result_chars") or len(str(tc.get("result") or "")),
            }
            for tc in raw_tool_calls
        ]

        raw_cot = r.get("synth_cot") or []
        synth_cot_preview = [(c[:800] if isinstance(c, str) else str(c)[:800]) for c in raw_cot]

        dag_runs.append({
            # --- identity ---
            "run_id":     r.get("run_id") or "",
            "session_id": r.get("session_id") or "",
            "project_id": r.get("project_id") or "",
            # --- all recent_run fields ---
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
            "searches": r.get("search_rounds") or len(raw_tool_calls),
            "memory_hits":       r.get("memory_hits") or 0,
            "dims":              dims,
            "issues":            first_issues,
            "feedback":          first_feedback,
            "score_trajectory":  score_trajectory,
            "count_check_retry": bool(r.get("count_check_retry")),
            "novelty_scores":    r.get("novelty_scores") or [],
            "output_bytes":      r.get("output_bytes") or 0,
            "output_lines":      r.get("output_lines") or 0,
            # --- DAG-specific fields ---
            "tool_calls":           dag_tool_calls,
            "tokens_by_stage":      r.get("tokens_by_stage") or {},
            "wiggum_eval_log":      r.get("wiggum_eval_log") or [],
            "plan":                 r.get("plan"),
            "synth_cot":            synth_cot_preview,
            "final_content_preview": (r.get("final_content") or "")[:400],
            "memory_context_titles": r.get("memory_context_titles") or [],
            "run_duration_s":       r.get("run_duration_s") or 0,
            "orchestrated":         bool(r.get("orchestrated")),
            "subtask_count":        r.get("subtask_count") or 0,
            "output_path":          r.get("output_path") or "",
        })

    recent.reverse()
    dag_runs.reverse()

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
        "dag_runs":      dag_runs,
        "cost":          cost,
        "claude_stats":  load_claude_stats(),
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
<script src="https://cdn.jsdelivr.net/npm/marked@12/marked.min.js"></script>
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

  /* ── Hypervisor layout (project/session sidebar + run explorer) ─── */
  #hypervisor-layout {
    display: flex; height: 580px; gap: 0;
    background: var(--card); border: 1px solid var(--border);
    border-radius: 8px; overflow: hidden; margin-bottom: 16px;
  }
  #project-session-panel {
    width: 172px; flex-shrink: 0;
    border-right: 1px solid var(--border);
    overflow-y: auto; background: #0a0f16;
    display: flex; flex-direction: column;
  }
  .psp-section {
    font-size: 9px; font-weight: 700; text-transform: uppercase;
    letter-spacing: .08em; color: var(--muted);
    padding: 8px 10px 4px; border-bottom: 1px solid var(--border);
    position: sticky; top: 0; background: #0a0f16; z-index: 1;
  }
  .psp-project {
    padding: 7px 10px; font-size: 11px; color: var(--text);
    border-bottom: 1px solid var(--border);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .psp-project span { font-size: 9px; color: var(--muted); display: block; margin-top: 1px; }
  .sess-item {
    padding: 6px 10px; cursor: pointer;
    border-left: 3px solid transparent;
    border-bottom: 1px solid rgba(48,54,61,.35);
    transition: background .1s, border-color .1s;
  }
  .sess-item:hover { background: rgba(255,255,255,.03); }
  .sess-item.sel { border-left-color: var(--blue); background: rgba(79,142,247,.06); }
  .sess-item.active-sess { border-left-color: #22d3ee; }
  .sess-ts   { font-size: 9px; color: var(--muted); margin-bottom: 2px; }
  .sess-meta { font-size: 10px; color: var(--text); }
  .sess-dur  { font-size: 9px; color: var(--muted); margin-top: 1px; }

  /* ── Run Explorer (DAG) ─────────────────────────────────────────── */
  #run-explorer {
    flex: 1; display: flex; gap: 0; overflow: hidden;
    background: var(--card);
  }
  #run-list-panel {
    width: 220px; flex-shrink: 0;
    border-right: 1px solid var(--border);
    overflow-y: auto; background: var(--bg);
  }
  #run-list-panel h3 {
    font-size: 10px; font-weight: 700; text-transform: uppercase;
    letter-spacing: .07em; color: var(--muted);
    padding: 10px 12px 6px; border-bottom: 1px solid var(--border);
    position: sticky; top: 0; background: var(--bg); margin: 0;
  }
  .rli {
    padding: 8px 12px; cursor: pointer;
    border-bottom: 1px solid rgba(48,54,61,.45);
    border-left: 3px solid transparent;
    transition: background .1s, border-color .1s;
  }
  .rli:hover { background: rgba(255,255,255,.03); }
  .rli.sel { border-left-color: var(--blue); background: rgba(79,142,247,.07); }
  .rli-ts   { font-size: 10px; color: var(--muted); margin-bottom: 2px; }
  .rli-task { font-size: 11px; color: var(--text); overflow: hidden;
              text-overflow: ellipsis; white-space: nowrap; }
  .rli-foot { display: flex; align-items: center; gap: 6px; margin-top: 3px; }
  .rli-score{ font-size: 10px; color: var(--muted); }

  #dag-canvas-panel {
    flex: 1; overflow: auto; background: #080d12; position: relative;
  }
  #dag-svg { display: block; }

  @keyframes dash-flow { to { stroke-dashoffset: -22; } }
  .dag-edge { animation: dash-flow 1.6s linear infinite; }

  .dag-node { cursor: pointer; }
  .dag-node:hover .node-body { filter: brightness(1.15); }
  .dag-node.sel .node-body  { filter: brightness(1.3); }

  #node-inspector {
    width: 300px; flex-shrink: 0;
    border-left: 1px solid var(--border);
    display: flex; flex-direction: column;
    background: var(--card); overflow: hidden;
  }
  #node-inspector.hidden { display: none; }
  #insp-header {
    display: flex; align-items: center; gap: 8px;
    padding: 9px 12px; border-bottom: 1px solid var(--border);
    background: var(--bg); flex-shrink: 0;
  }
  #insp-type {
    font-size: 9px; font-weight: 700; text-transform: uppercase;
    letter-spacing: .1em; color: var(--muted);
  }
  #insp-title { flex: 1; font-size: 12px; font-weight: 600; color: var(--text); }
  #insp-close {
    background: none; border: none; color: var(--muted);
    cursor: pointer; font-size: 16px; line-height: 1; padding: 0 2px;
  }
  #insp-close:hover { color: var(--text); }
  #insp-body { flex: 1; overflow-y: auto; padding: 12px; font-size: 12px; }
  .insp-row { margin-bottom: 10px; }
  .insp-label { font-size: 10px; font-weight: 700; text-transform: uppercase;
                letter-spacing: .06em; color: var(--muted); margin-bottom: 3px; }
  .insp-val { color: var(--text); line-height: 1.45; word-break: break-word; }
  .insp-pre {
    background: var(--bg); border: 1px solid var(--border); border-radius: 4px;
    padding: 7px 9px; font-family: monospace; font-size: 10.5px;
    line-height: 1.5; white-space: pre-wrap; max-height: 140px; overflow-y: auto;
    color: var(--muted);
  }
  .insp-dim { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }
  .insp-dim-lbl { width: 80px; font-size: 10px; color: var(--muted); flex-shrink: 0; }
  .insp-dim-bar { flex: 1; height: 5px; background: var(--border); border-radius: 3px; overflow: hidden; }
  .insp-dim-fill { height: 100%; border-radius: 3px; }
  .insp-dim-val { width: 18px; font-size: 10px; color: var(--text); text-align: right; flex-shrink: 0; }

  /* ── Voice panel ──────────────────────────────────────────────────────────── */
  #voice-fab {
    position: fixed; bottom: 28px; right: 28px; z-index: 999;
    width: 52px; height: 52px; border-radius: 50%;
    background: var(--blue); border: none; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 14px rgba(0,0,0,.5);
    transition: background .2s, transform .15s;
  }
  #voice-fab:hover { background: #3a7de0; transform: scale(1.07); }
  #voice-fab.recording { background: var(--red); animation: pulse-ring 1.2s ease-out infinite; }
  @keyframes pulse-ring {
    0%   { box-shadow: 0 0 0 0 rgba(248,81,73,.55); }
    70%  { box-shadow: 0 0 0 14px rgba(248,81,73,0); }
    100% { box-shadow: 0 0 0 0 rgba(248,81,73,0); }
  }
  #voice-fab svg { width: 24px; height: 24px; fill: #fff; }

  #voice-panel {
    position: fixed; bottom: 92px; right: 28px; z-index: 998;
    width: 420px; background: var(--card);
    border: 1px solid var(--border); border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0,0,0,.5);
    display: none; flex-direction: column; overflow: hidden;
  }
  #voice-panel.open { display: flex; }
  #voice-panel-header {
    padding: 12px 16px; border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
  }
  #voice-panel-header span { font-size: 13px; font-weight: 600; color: var(--text); }
  #voice-status { font-size: 11px; color: var(--muted); }
  #voice-close { background: none; border: none; color: var(--muted); cursor: pointer; font-size: 18px; line-height:1; padding: 0 2px; }
  #voice-close:hover { color: var(--text); }
  #voice-transcript {
    padding: 12px 16px 0; font-size: 12px; color: var(--muted);
    font-style: italic; min-height: 0; max-height: 80px;
    overflow-y: auto; white-space: pre-wrap; word-break: break-word;
  }
  #voice-response {
    padding: 12px 16px; font-size: 13px; color: var(--text);
    line-height: 1.6; max-height: 340px; overflow-y: auto;
  }
  #voice-response h1,h2,h3 { margin: 8px 0 4px; font-size: 14px; color: var(--text); }
  #voice-response p { margin: 4px 0; }
  #voice-response ul,ol { padding-left: 18px; margin: 4px 0; }
  #voice-response code {
    background: rgba(255,255,255,.07); border-radius: 3px;
    padding: 1px 4px; font-size: 12px; font-family: monospace;
  }
  #voice-response pre { background: rgba(255,255,255,.05); border-radius: 6px; padding: 10px; overflow-x: auto; }
  #voice-response pre code { background: none; padding: 0; }
  #voice-copy-row {
    padding: 8px 16px 12px; display: flex; justify-content: flex-end;
    border-top: 1px solid var(--border);
  }
  #voice-copy-btn {
    display: flex; align-items: center; gap: 5px;
    background: none; border: 1px solid var(--border); border-radius: 6px;
    color: var(--muted); cursor: pointer; font-size: 11px; padding: 4px 10px;
    transition: background .15s, color .15s;
  }
  #voice-copy-btn:hover { background: rgba(255,255,255,.06); color: var(--text); }
  #voice-copy-btn svg { width: 13px; height: 13px; }
</style>
</head>
<body>

<h1>Harness Engineering — Run Dashboard</h1>
<p class="subtitle" id="subtitle">Loading...</p>

<!-- Voice FAB -->
<button id="voice-fab" title="Voice query">
  <svg id="voice-icon-mic" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 1a4 4 0 0 1 4 4v6a4 4 0 0 1-8 0V5a4 4 0 0 1 4-4zm-1 17.93V21H9v2h6v-2h-2v-2.07A8 8 0 0 0 20 11h-2a6 6 0 0 1-12 0H4a8 8 0 0 0 7 7.93z"/>
  </svg>
  <svg id="voice-icon-stop" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="display:none">
    <rect x="5" y="5" width="14" height="14" rx="2"/>
  </svg>
</button>

<!-- Voice panel -->
<div id="voice-panel">
  <div id="voice-panel-header">
    <span>Voice Query</span>
    <span id="voice-status">Ready</span>
    <button id="voice-close">&#x2715;</button>
  </div>
  <div id="voice-transcript"></div>
  <div id="voice-response"></div>
  <div id="voice-copy-row" style="display:none">
    <button id="voice-copy-btn">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
      </svg>
      Copy response
    </button>
  </div>
  <div id="voice-confirm" style="display:none">
    <div style="padding:10px 16px 4px;font-size:11px;color:var(--muted);font-weight:600;letter-spacing:.05em">INTERPRETED TASK</div>
    <div style="padding:0 16px 8px;font-size:11px;color:var(--orange);font-style:italic" id="voice-reasoning"></div>
    <div style="padding:0 12px 8px">
      <textarea id="voice-task-input" rows="3"
        style="width:100%;box-sizing:border-box;background:rgba(255,255,255,.06);border:1px solid var(--border);border-radius:6px;color:var(--text);font-size:12px;padding:8px;resize:vertical;font-family:monospace"></textarea>
    </div>
    <div style="padding:0 12px 12px;display:flex;gap:8px">
      <button id="voice-approve-btn"
        style="flex:1;background:var(--green);border:none;border-radius:6px;color:#fff;font-size:12px;font-weight:600;padding:7px;cursor:pointer">
        Run task
      </button>
      <button id="voice-cancel-btn"
        style="flex:1;background:none;border:1px solid var(--border);border-radius:6px;color:var(--muted);font-size:12px;padding:7px;cursor:pointer">
        Cancel
      </button>
    </div>
  </div>
</div>

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

<h2 class="section-heading">Claude Code usage</h2>

<div class="kpi-grid" id="claude-kpi-grid"></div>

<div class="chart-grid col-2">
  <div class="card">
    <div class="card-title">Daily messages &amp; tool calls</div>
    <div class="chart-wrap" style="height:200px">
      <canvas id="claudeActivityChart"></canvas>
    </div>
  </div>
  <div class="card">
    <div class="card-title">Daily tokens (Claude models)</div>
    <div class="chart-wrap" style="height:200px">
      <canvas id="claudeTokChart"></canvas>
    </div>
  </div>
</div>
<div class="chart-grid col-1">
  <div class="card">
    <div class="card-title">Input vs output tokens by model</div>
    <div class="chart-wrap" style="height:200px">
      <canvas id="claudeModelChart"></canvas>
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

<h2 class="section-heading">Run Explorer</h2>

<div id="hypervisor-layout">
  <div id="project-session-panel">
    <div class="psp-section">Project</div>
    <div class="psp-project" id="psp-project-name">—<span id="psp-project-id"></span></div>
    <div class="psp-section" style="top:auto;position:relative">Sessions</div>
    <div id="psp-session-list"></div>
  </div>
  <div id="run-explorer">
    <div id="run-list-panel">
      <h3>Runs <span id="rl-session-badge" style="font-weight:400;color:var(--blue);text-transform:none;letter-spacing:0"></span></h3>
      <div id="run-list-inner"></div>
    </div>
    <div id="dag-canvas-panel">
      <svg id="dag-svg"></svg>
    </div>
    <div id="node-inspector" class="hidden">
      <div id="insp-header">
        <span id="insp-type"></span>
        <span id="insp-title"></span>
        <button id="insp-close" title="close">&#x2715;</button>
      </div>
      <div id="insp-body"></div>
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
// Run Explorer — DAG-style pipeline visualiser
// ---------------------------------------------------------------------------

const DIM_COLORS = {
  relevance:    '#4f8ef7',
  completeness: '#3fb950',
  depth:        '#a78bfa',
  specificity:  '#fb923c',
  structure:    '#f472b6',
};

// DAG constants
const NW = 150, NH = 58, HGAP = 58, VGAP = 14, PAD = 24;

const NODE_CFG = {
  task:      { color: '#4f8ef7', label: 'TASK'      },
  memory:    { color: '#a78bfa', label: 'MEMORY'    },
  plan:      { color: '#38bdf8', label: 'PLAN'      },
  search:    { color: '#fb923c', label: 'SEARCH'    },
  synthesis: { color: '#22d3ee', label: 'SYNTHESIS' },
  wiggum:    { color: '#e3b341', label: 'EVAL'      },
  output:    { color: '#3fb950', label: 'OUTPUT'    },
};

function xesc(s) { return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function xtrunc(s, n) { s = String(s||''); return s.length > n ? s.slice(0,n)+'…' : s; }

function buildDagNodes(run) {
  const nodes = [];
  let col = 0;

  nodes.push({ id:'task', type:'task', col:col++, row:0,
    title: xtrunc(run.task_full || run.task, 40),
    sub:   (run.ts||'') + ' · ' + (run.model||''),
    data:  run });

  nodes.push({ id:'memory', type:'memory', col:col++, row:0,
    title: (run.memory_hits||0) + ' prior obs.',
    sub:   (run.memory_hits||0) > 0 ? 'context retrieved' : 'no prior context',
    data:  { hits: run.memory_hits||0, titles: run.memory_context_titles||[] } });

  if (run.plan && typeof run.plan === 'object') {
    const queries = run.plan.queries || run.plan.search_queries || [];
    nodes.push({ id:'plan', type:'plan', col:col++, row:0,
      title: queries.length + ' queries planned',
      sub:   xtrunc((queries[0]||''), 40),
      data:  run.plan });
  }

  const searches = (run.tool_calls||[]).filter(tc => tc.name === 'web_search' || tc.name === 'vision');
  if (searches.length) {
    const scol = col++;
    searches.forEach((tc, i) => {
      nodes.push({ id:'search'+i, type:'search', col:scol, row:i,
        title: xtrunc(tc.query||'', 42),
        sub:   (tc.name||'') + ' · ' + Math.round((tc.result_chars||0)/100)/10 + 'k',
        data:  tc });
    });
  }

  const stbs = ((run.tokens_by_stage||{}).synth) || {};
  const cots = run.synth_cot || [];
  nodes.push({ id:'synthesis', type:'synthesis', col:col++, row:0,
    title: ((run.output_bytes||0)/1024).toFixed(1) + ' KB output',
    sub:   stbs.output ? stbs.output + ' out tokens' : 'synthesis',
    data:  { tokens_by_stage: run.tokens_by_stage||{}, cots, output_bytes: run.output_bytes||0,
             final_content_preview: run.final_content_preview||'' } });

  const evalLog = run.wiggum_eval_log || [];
  if (evalLog.length) {
    const wcol = col++;
    evalLog.forEach((ev, i) => {
      nodes.push({ id:'wiggum'+i, type:'wiggum', col:wcol, row:i,
        title: 'Round ' + (ev.round||i+1) + ' · score ' + (ev.score!=null?ev.score:'?'),
        sub:   (ev.issues||[]).length + ' issue' + ((ev.issues||[]).length===1?'':'s'),
        data:  ev });
    });
  }

  nodes.push({ id:'output', type:'output', col:col++, row:0,
    title: run.final || '?',
    sub:   xtrunc(run.output_path||'', 38),
    data:  run,
    color: run.final==='PASS'?'#3fb950':run.final==='FAIL'?'#f85149':'#8b949e' });

  return nodes;
}

function dagLayout(nodes) {
  const colRows = {};
  nodes.forEach(n => { colRows[n.col] = Math.max(colRows[n.col]||0, n.row+1); });
  const maxRows = Math.max(...Object.values(colRows));
  const totalCols = Math.max(...nodes.map(n=>n.col)) + 1;
  const svgH = PAD*2 + maxRows * NH + (maxRows-1) * VGAP;
  const svgW = PAD*2 + totalCols * NW + (totalCols-1) * HGAP;

  nodes.forEach(n => {
    const rows = colRows[n.col];
    const blockH = rows * NH + (rows-1) * VGAP;
    const startY = PAD + (svgH - PAD*2 - blockH) / 2;
    n.x = PAD + n.col * (NW + HGAP) + NW/2;
    n.y = startY + n.row * (NH + VGAP) + NH/2;
  });
  return { nodes, width: svgW, height: svgH };
}

function buildEdges(nodes) {
  const edges = [];
  const colMap = {};
  nodes.forEach(n => { (colMap[n.col] = colMap[n.col]||[]).push(n); });
  const cols = Object.keys(colMap).map(Number).sort((a,b)=>a-b);
  for (let ci = 0; ci < cols.length-1; ci++) {
    const srcs = colMap[cols[ci]], dsts = colMap[cols[ci+1]];
    srcs.forEach(src => dsts.forEach(dst => {
      edges.push({ from: src, to: dst, color: src.color || NODE_CFG[src.type]?.color || '#8b949e' });
    }));
  }
  return edges;
}

function renderDag(run) {
  const svg = document.getElementById('dag-svg');
  svg.innerHTML = '';
  const rawNodes = buildDagNodes(run);
  const { nodes, width, height } = dagLayout(rawNodes);
  const edges = buildEdges(nodes);

  svg.setAttribute('width',  width);
  svg.setAttribute('height', height);
  svg.setAttribute('viewBox', '0 0 ' + width + ' ' + height);

  const defs = document.createElementNS('http://www.w3.org/2000/svg','defs');
  [...new Set(edges.map(e=>e.color))].forEach(col => {
    const mid = document.createElementNS('http://www.w3.org/2000/svg','marker');
    const cid = 'arr' + col.replace('#','');
    mid.setAttribute('id', cid);
    mid.setAttribute('markerWidth','6'); mid.setAttribute('markerHeight','6');
    mid.setAttribute('refX','5'); mid.setAttribute('refY','3');
    mid.setAttribute('orient','auto');
    const poly = document.createElementNS('http://www.w3.org/2000/svg','polygon');
    poly.setAttribute('points','0 0, 6 3, 0 6');
    poly.setAttribute('fill', col); poly.setAttribute('opacity','0.55');
    mid.appendChild(poly); defs.appendChild(mid);
  });
  svg.appendChild(defs);

  edges.forEach(e => {
    const x1 = e.from.x + NW/2, y1 = e.from.y;
    const x2 = e.to.x   - NW/2, y2 = e.to.y;
    const cx = (x1+x2)/2;
    const path = document.createElementNS('http://www.w3.org/2000/svg','path');
    path.setAttribute('d', 'M'+x1+','+y1+' C'+cx+','+y1+' '+cx+','+y2+' '+x2+','+y2);
    path.setAttribute('fill','none');
    path.setAttribute('stroke', e.color);
    path.setAttribute('stroke-opacity','0.4');
    path.setAttribute('stroke-width','1.5');
    path.setAttribute('stroke-dasharray','6 5');
    path.setAttribute('marker-end', 'url(#arr'+e.color.replace('#','')+')');
    path.classList.add('dag-edge');
    svg.appendChild(path);
  });

  nodes.forEach(n => {
    const cfg = NODE_CFG[n.type] || NODE_CFG.task;
    const col = n.color || cfg.color;
    const g = document.createElementNS('http://www.w3.org/2000/svg','g');
    g.classList.add('dag-node');
    g.setAttribute('transform', 'translate('+(n.x-NW/2)+','+(n.y-NH/2)+')');

    const shadow = document.createElementNS('http://www.w3.org/2000/svg','rect');
    shadow.setAttribute('width',NW); shadow.setAttribute('height',NH);
    shadow.setAttribute('rx','7'); shadow.setAttribute('fill','rgba(0,0,0,0.45)');
    shadow.setAttribute('transform','translate(2,2)');
    g.appendChild(shadow);

    const body = document.createElementNS('http://www.w3.org/2000/svg','rect');
    body.setAttribute('width',NW); body.setAttribute('height',NH);
    body.setAttribute('rx','7'); body.setAttribute('fill','#111820');
    body.setAttribute('stroke',col); body.setAttribute('stroke-width','1.5');
    body.classList.add('node-body');
    g.appendChild(body);

    const bar = document.createElementNS('http://www.w3.org/2000/svg','rect');
    bar.setAttribute('width','4'); bar.setAttribute('height',NH-14);
    bar.setAttribute('x','0'); bar.setAttribute('y','7');
    bar.setAttribute('rx','2'); bar.setAttribute('fill',col);
    g.appendChild(bar);

    const tl = document.createElementNS('http://www.w3.org/2000/svg','text');
    tl.setAttribute('x','13'); tl.setAttribute('y','16');
    tl.setAttribute('fill',col); tl.setAttribute('font-size','8');
    tl.setAttribute('font-weight','700'); tl.setAttribute('font-family','monospace');
    tl.setAttribute('letter-spacing','0.08em');
    tl.textContent = cfg.label;
    g.appendChild(tl);

    const maxC = 21;
    const line1 = n.title.slice(0, maxC);
    const line2 = n.title.length > maxC ? n.title.slice(maxC, maxC*2) : '';
    [line1, line2].filter(Boolean).forEach((ln, li) => {
      const t = document.createElementNS('http://www.w3.org/2000/svg','text');
      t.setAttribute('x','13'); t.setAttribute('y', li===0 ? '30' : '41');
      t.setAttribute('fill','#e6edf3'); t.setAttribute('font-size','11');
      t.setAttribute('font-weight', li===0?'600':'400');
      t.setAttribute('font-family','sans-serif');
      t.textContent = ln;
      g.appendChild(t);
    });

    const sl = document.createElementNS('http://www.w3.org/2000/svg','text');
    sl.setAttribute('x','13'); sl.setAttribute('y','52');
    sl.setAttribute('fill','#8b949e'); sl.setAttribute('font-size','9');
    sl.setAttribute('font-family','sans-serif');
    sl.textContent = xtrunc(n.sub, 28);
    g.appendChild(sl);

    const hit = document.createElementNS('http://www.w3.org/2000/svg','rect');
    hit.setAttribute('width',NW); hit.setAttribute('height',NH);
    hit.setAttribute('fill','transparent'); hit.style.cursor='pointer';
    g.appendChild(hit);

    g.addEventListener('click', () => {
      svg.querySelectorAll('.dag-node').forEach(el=>el.classList.remove('sel'));
      g.classList.add('sel');
      openInspector(n, col);
    });
    svg.appendChild(g);
  });
}

function openInspector(node, color) {
  const panel = document.getElementById('node-inspector');
  panel.classList.remove('hidden');
  const typeEl = document.getElementById('insp-type');
  typeEl.textContent = (NODE_CFG[node.type]||{}).label || node.type;
  typeEl.style.color = color;
  document.getElementById('insp-title').textContent = node.title;
  document.getElementById('insp-body').innerHTML = buildInspectorHTML(node);
}

document.getElementById('insp-close').addEventListener('click', () => {
  document.getElementById('node-inspector').classList.add('hidden');
  document.getElementById('dag-svg').querySelectorAll('.dag-node').forEach(el=>el.classList.remove('sel'));
});

function inspRow(label, val) {
  return '<div class="insp-row"><div class="insp-label">'+label+'</div><div class="insp-val">'+val+'</div></div>';
}
function inspPre(text) {
  return '<div class="insp-pre">'+xesc(String(text||''))+'</div>';
}

function buildInspectorHTML(node) {
  const d = node.data || {};
  const parts = [];

  if (node.type === 'task') {
    parts.push(inspRow('Task', xesc(d.task_full||d.task||'')));
    parts.push(inspRow('Timestamp', xesc(d.ts||'')));
    parts.push(inspRow('Model', xesc(d.model||'')));
    parts.push(inspRow('Type', xesc(d.type||'')));
    const dur = d.run_duration_s ? (d.run_duration_s/60).toFixed(1)+'m' : (d.duration||'?')+'m';
    parts.push(inspRow('Duration', dur));
    if (d.orchestrated) parts.push(inspRow('Orchestrated', 'yes · '+(d.subtask_count||'?')+' subtasks'));
  }
  else if (node.type === 'memory') {
    parts.push(inspRow('Hits', String(d.hits||0)));
    parts.push(inspRow('Status', (d.hits||0)>0 ? 'Prior context retrieved' : 'No prior context'));
    const titles = d.titles || [];
    if (titles.length) parts.push(inspRow('Observations', titles.map(t=>'<div style="margin-bottom:3px">• '+xesc(t)+'</div>').join('')));
  }
  else if (node.type === 'plan') {
    const qs = d.queries || d.search_queries || [];
    const qhtml = qs.map((q,i)=>'<div style="margin-bottom:4px">'+(i+1)+'. '+xesc(q)+'</div>').join('');
    parts.push(inspRow('Queries ('+qs.length+')', qhtml||'(none)'));
    if ((d.known_facts||[]).length)
      parts.push(inspRow('Known facts', d.known_facts.map(f=>'<div>• '+xesc(f)+'</div>').join('')));
    if ((d.knowledge_gaps||[]).length)
      parts.push(inspRow('Knowledge gaps', d.knowledge_gaps.map(g=>'<div>• '+xesc(g)+'</div>').join('')));
  }
  else if (node.type === 'search') {
    parts.push(inspRow('Tool', xesc(d.name||'')));
    parts.push(inspRow('Query', xesc(d.query||'')));
    parts.push(inspRow('Result size', (d.result_chars||0).toLocaleString()+' chars'));
  }
  else if (node.type === 'synthesis') {
    const tbs = d.tokens_by_stage || {};
    const s = tbs.synth || {};
    if (s.output) parts.push(inspRow('Output tokens', String(s.output)));
    if (s.total_ms) parts.push(inspRow('Time', (s.total_ms/1000).toFixed(1)+'s'));
    if (s.thinking_chars) parts.push(inspRow('CoT chars', s.thinking_chars.toLocaleString()));
    parts.push(inspRow('Output size', ((d.output_bytes||0)/1024).toFixed(1)+' KB'));
    if (d.final_content_preview) parts.push(inspRow('Output preview', inspPre(d.final_content_preview)));
    const cots = d.cots || [];
    if (cots.length && cots[0]) parts.push(inspRow('Chain-of-thought', inspPre(cots[0])));
  }
  else if (node.type === 'wiggum') {
    parts.push(inspRow('Round', String(d.round||'')));
    parts.push(inspRow('Score', String(d.score!=null?d.score:'?')));
    const dims = d.dims || {};
    if (Object.keys(dims).length) {
      const bars = Object.entries(dims).map(([k,v]) => {
        const c = DIM_COLORS[k]||'#4f8ef7';
        return '<div class="insp-dim"><span class="insp-dim-lbl">'+k+'</span>'
          +'<div class="insp-dim-bar"><div class="insp-dim-fill" style="width:'+(v*10)+'%;background:'+c+'"></div></div>'
          +'<span class="insp-dim-val">'+v+'</span></div>';
      }).join('');
      parts.push(inspRow('Dimensions', bars));
    }
    const issues = d.issues || [];
    if (issues.length) parts.push(inspRow('Issues ('+issues.length+')', issues.map(i=>'<div style="margin-bottom:3px;color:var(--muted)">• '+xesc(i)+'</div>').join('')));
    if (d.feedback) parts.push(inspRow('Feedback', inspPre(d.feedback)));
    if (d.thinking) parts.push(inspRow('Evaluator CoT', inspPre(d.thinking)));
  }
  else if (node.type === 'output') {
    const badge = d.final==='PASS' ? '<span class="badge badge-pass">PASS</span>'
                : d.final==='FAIL' ? '<span class="badge badge-fail">FAIL</span>'
                : '<span class="badge badge-error">'+xesc(d.final||'?')+'</span>';
    parts.push(inspRow('Result', badge));
    if (d.output_path) parts.push(inspRow('File', xesc(d.output_path)));
    if (d.output_bytes) parts.push(inspRow('Size', (d.output_bytes/1024).toFixed(1)+' KB · '+(d.output_lines||'?')+' lines'));
    const scores = d.score_trajectory || d.wiggum_scores || [];
    if (scores.length) parts.push(inspRow('Score trajectory', scores.map((s,i)=>'<span class="score-pill">r'+(i+1)+': '+s+'</span>').join(' ')));
    if (d.final_content_preview) parts.push(inspRow('Output preview', inspPre(d.final_content_preview)));
  }

  return parts.join('');
}

// ---------------------------------------------------------------------------
// State poller — live data from /api/state (only works when server.py is running)
// ---------------------------------------------------------------------------
let _liveState = null;
let _selectedSessionId = null;

function fmtLocalTs(iso) {
  if (!iso) return '';
  try {
    const d = new Date(iso);
    return d.toLocaleString(undefined, {month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false});
  } catch { return iso.slice(0,16).replace('T',' '); }
}

function fmtDur(s) {
  if (!s) return '';
  if (s < 60) return Math.round(s)+'s';
  return Math.round(s/60)+'m '+Math.round(s%60)+'s';
}

function updateSessionNav(state) {
  if (!state) return;
  const projName = document.getElementById('psp-project-name');
  const projId   = document.getElementById('psp-project-id');
  const proj = (state.projects||[]).find(p => p.project_id === state.server_project_id);
  if (proj) {
    projName.childNodes[0].textContent = proj.name || '(unnamed)';
    projId.textContent = state.server_project_id.slice(0,14)+'…';
  }

  const sessions = state.sessions || [];
  const listEl = document.getElementById('psp-session-list');
  const serverSid = state.server_session_id;

  listEl.innerHTML = sessions.map(s => {
    const sid = s.session_id || '';
    const isActive = sid === serverSid;
    const isSel    = sid === _selectedSessionId;
    const ts       = fmtLocalTs(s.started_at);
    const dur      = s.duration_s ? fmtDur(s.duration_s) : (isActive ? 'active' : '');
    const runs     = s.runs != null ? s.runs+' runs' : '';
    return '<div class="sess-item'+(isSel?' sel':'')+(isActive?' active-sess':'')+'" data-sid="'+xesc(sid)+'">'
      +'<div class="sess-ts">'+xesc(ts)+'</div>'
      +'<div class="sess-meta">'+xesc(sid.slice(16,24))+(isActive?' ●':'')+'</div>'
      +'<div class="sess-dur">'+xesc([runs,dur].filter(Boolean).join(' · '))+'</div>'
      +'</div>';
  }).join('');

  listEl.querySelectorAll('.sess-item').forEach(el => {
    el.addEventListener('click', () => {
      _selectedSessionId = el.dataset.sid;
      updateSessionNav(_liveState);
      populateRunList(_selectedSessionId);
    });
  });
}

function pollState() {
  fetch('/api/state')
    .then(r => r.ok ? r.json() : null)
    .then(state => {
      if (!state) return;
      _liveState = state;
      updateSessionNav(state);
    })
    .catch(() => {});
}

pollState();
setInterval(pollState, 5000);

// ---------------------------------------------------------------------------
// Run list
// ---------------------------------------------------------------------------

function populateRunList(sessionIdFilter) {
  let dagRuns = DATA.dag_runs || [];
  if (sessionIdFilter) {
    dagRuns = dagRuns.filter(r => r.session_id === sessionIdFilter);
  }
  const badge_el = document.getElementById('rl-session-badge');
  if (badge_el) badge_el.textContent = sessionIdFilter ? '(filtered)' : '';

  const listEl = document.getElementById('run-list-inner');
  if (!dagRuns.length) {
    listEl.innerHTML = '<div style="padding:12px;color:var(--muted);font-size:12px">'
      +(sessionIdFilter ? 'No runs in this session.' : 'No runs found.')+'</div>';
    return;
  }
  listEl.innerHTML = dagRuns.map((r,i) => {
    const badge = r.final==='PASS' ? '<span class="badge badge-pass">PASS</span>'
                : r.final==='FAIL' ? '<span class="badge badge-fail">FAIL</span>'
                : '<span class="badge badge-error">'+xesc(r.final||'?')+'</span>';
    const score = r.score!=null ? '<span class="rli-score">★ '+r.score+'</span>' : '';
    return '<div class="rli'+(i===0?' sel':'')+'" data-idx="'+i+'" title="'+xesc(r.task_full||r.task||'')+'">'
      +'<div class="rli-ts">'+xesc(r.ts||'')+'</div>'
      +'<div class="rli-task">'+xesc(xtrunc(r.task_full||r.task||'',44))+'</div>'
      +'<div class="rli-foot">'+badge+score+'</div>'
      +'</div>';
  }).join('');

  listEl.querySelectorAll('.rli').forEach(el => {
    el.addEventListener('click', () => {
      listEl.querySelectorAll('.rli').forEach(e=>e.classList.remove('sel'));
      el.classList.add('sel');
      document.getElementById('node-inspector').classList.add('hidden');
      renderDag(dagRuns[parseInt(el.dataset.idx,10)]);
    });
  });

  if (dagRuns.length) renderDag(dagRuns[0]);
}

populateRunList();

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
// Claude Code usage
// ---------------------------------------------------------------------------
(function () {
  const cs = DATA.claude_stats || {};
  if (!cs.total_sessions) return;

  // KPI cards
  const fmt = n => n >= 1e6 ? (n/1e6).toFixed(1)+'M' : n >= 1e3 ? (n/1e3).toFixed(1)+'K' : String(n);
  const kpis = [
    { label: 'Sessions',       value: cs.total_sessions,  cls: 'blue'   },
    { label: 'Messages',       value: fmt(cs.total_messages), cls: 'purple' },
    { label: 'Input tokens',   value: fmt(cs.total_input),   cls: 'green'  },
    { label: 'Output tokens',  value: fmt(cs.total_output),  cls: 'orange' },
    { label: 'Cache reads',    value: fmt(cs.total_cache),   cls: 'yellow' },
    { label: 'Since',          value: cs.first_date,          cls: ''       },
  ];
  document.getElementById('claude-kpi-grid').innerHTML = kpis.map(k =>
    `<div class="kpi ${k.cls}"><div class="kpi-label">${k.label}</div><div class="kpi-value">${k.value}</div></div>`
  ).join('');

  // Daily activity chart
  new Chart(document.getElementById('claudeActivityChart'), {
    type: 'bar',
    data: {
      labels: cs.dates || [],
      datasets: [
        { label: 'Messages',   data: cs.msg_counts  || [], backgroundColor: 'rgba(167,139,250,0.75)', yAxisID: 'y' },
        { label: 'Tool calls', data: cs.tool_counts || [], backgroundColor: 'rgba(79,142,247,0.75)',  yAxisID: 'y' },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { labels: { color: '#8b949e', font: { size: 11 } } } },
      scales: {
        x: { ticks: { color: '#8b949e', maxRotation: 45, font: { size: 10 } }, grid: { color: 'rgba(48,54,61,.5)' } },
        y: { ticks: { color: '#8b949e', font: { size: 10 } }, grid: { color: 'rgba(48,54,61,.5)' } },
      },
    },
  });

  // Daily token trend
  new Chart(document.getElementById('claudeTokChart'), {
    type: 'bar',
    data: {
      labels: cs.tok_dates || [],
      datasets: [{ label: 'Tokens', data: cs.tok_values || [], backgroundColor: 'rgba(79,142,247,0.75)' }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#8b949e', maxRotation: 45, font: { size: 10 } }, grid: { color: 'rgba(48,54,61,.5)' } },
        y: { ticks: { color: '#8b949e', font: { size: 10 }, callback: v => fmt(v) }, grid: { color: 'rgba(48,54,61,.5)' } },
      },
    },
  });

  // Input vs output by model — stacked bar
  const modelNames = (cs.model_names || []).map(n => n.replace('claude-','').replace(/-\d{8}$/,''));
  new Chart(document.getElementById('claudeModelChart'), {
    type: 'bar',
    data: {
      labels: modelNames,
      datasets: [
        { label: 'Input tokens',  data: cs.model_in  || [], backgroundColor: 'rgba(79,142,247,0.8)',  stack: 'tok' },
        { label: 'Output tokens', data: cs.model_out || [], backgroundColor: 'rgba(167,139,250,0.8)', stack: 'tok' },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { labels: { color: '#8b949e', font: { size: 11 } } } },
      scales: {
        x: { ticks: { color: '#8b949e', font: { size: 10 } }, grid: { color: 'rgba(48,54,61,.5)' } },
        y: { ticks: { color: '#8b949e', font: { size: 10 }, callback: v => fmt(v) }, grid: { color: 'rgba(48,54,61,.5)' }, stacked: true },
      },
    },
  });
})();

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
    // Refresh DAG run list so the just-completed run appears immediately
    fetch('/api/data')
      .then(r => r.ok ? r.json() : null)
      .then(d => {
        if (d && d.dag_runs) {
          DATA.dag_runs = d.dag_runs;
          populateRunList(_selectedSessionId);
        }
      })
      .catch(() => {});
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

// ---------------------------------------------------------------------------
// Voice query
// ---------------------------------------------------------------------------
(function () {
  const fab       = document.getElementById('voice-fab');
  const panel     = document.getElementById('voice-panel');
  const statusEl  = document.getElementById('voice-status');
  const transcEl  = document.getElementById('voice-transcript');
  const respEl    = document.getElementById('voice-response');
  const copyRow   = document.getElementById('voice-copy-row');
  const copyBtn   = document.getElementById('voice-copy-btn');
  const closeBtn  = document.getElementById('voice-close');
  const iconMic   = document.getElementById('voice-icon-mic');
  const iconStop  = document.getElementById('voice-icon-stop');

  let recorder = null, chunks = [], recording = false, lastMarkdown = '';

  function setStatus(msg) { statusEl.textContent = msg; }

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      chunks = [];
      recorder = new MediaRecorder(stream);
      recorder.ondataavailable = e => { if (e.data.size) chunks.push(e.data); };
      recorder.onstop = () => {
        stream.getTracks().forEach(t => t.stop());
        sendAudio();
      };
      recorder.start();
      recording = true;
      fab.classList.add('recording');
      iconMic.style.display = 'none';
      iconStop.style.display = '';
      panel.classList.add('open');
      transcEl.textContent = '';
      respEl.innerHTML = '';
      copyRow.style.display = 'none';
      setStatus('Recording…');
    } catch (e) {
      setStatus('Mic error: ' + e.message);
    }
  }

  function stopRecording() {
    if (recorder && recording) {
      recorder.stop();
      recording = false;
      fab.classList.remove('recording');
      iconMic.style.display = '';
      iconStop.style.display = 'none';
      setStatus('Transcribing…');
    }
  }

  const confirmEl   = document.getElementById('voice-confirm');
  const reasoningEl = document.getElementById('voice-reasoning');
  const taskInput   = document.getElementById('voice-task-input');
  const approveBtn  = document.getElementById('voice-approve-btn');
  const cancelBtn   = document.getElementById('voice-cancel-btn');

  function showAnswer(d) {
    transcEl.textContent = (d.corrected_transcript || d.transcript)
      ? '🎤 ' + (d.corrected_transcript || d.transcript) : '';
    if (d.reasoning) transcEl.textContent += '  →  ' + d.reasoning;
    lastMarkdown = d.response || '';
    respEl.innerHTML = marked.parse(lastMarkdown);
    copyRow.style.display = 'flex';
    confirmEl.style.display = 'none';
    setStatus('Done');
  }

  function showTaskConfirm(d) {
    transcEl.textContent = '🎤 ' + (d.corrected_transcript || d.transcript);
    reasoningEl.textContent = d.reasoning || '';
    taskInput.value = d.task_string || '';
    respEl.innerHTML = '';
    copyRow.style.display = 'none';
    confirmEl.style.display = '';
    setStatus('Review task — approve to run');
  }

  async function sendAudio() {
    const blob = new Blob(chunks, { type: 'audio/webm' });
    const fd = new FormData();
    fd.append('audio', blob, 'voice.webm');
    try {
      const r = await fetch('/api/voice', { method: 'POST', body: fd });
      const d = await r.json();
      if (d.error) { setStatus('Error: ' + d.error); return; }
      if (d.type === 'task') { showTaskConfirm(d); }
      else { showAnswer(d); }
    } catch (e) {
      setStatus('Request failed: ' + e.message);
    }
  }

  approveBtn.addEventListener('click', async () => {
    const task = taskInput.value.trim();
    if (!task) return;
    approveBtn.disabled = true;
    approveBtn.textContent = 'Dispatching…';
    try {
      const r = await fetch('/api/run', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({task}),
      });
      const d = await r.json();
      confirmEl.style.display = 'none';
      setStatus('Run started: ' + (d.run_id || ''));
      respEl.innerHTML = marked.parse(`Task dispatched to agent. Check the **Active runs** panel above.`);
    } catch (e) {
      setStatus('Dispatch failed: ' + e.message);
    } finally {
      approveBtn.disabled = false;
      approveBtn.textContent = 'Run task';
    }
  });

  cancelBtn.addEventListener('click', () => {
    confirmEl.style.display = 'none';
    setStatus('Cancelled');
  });

  fab.addEventListener('click', () => {
    if (recording) { stopRecording(); }
    else { startRecording(); }
  });

  closeBtn.addEventListener('click', () => {
    if (recording) stopRecording();
    panel.classList.remove('open');
  });

  copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(lastMarkdown).then(() => {
      copyBtn.querySelector('span') && (copyBtn.querySelector('span').textContent = 'Copied!');
      copyBtn.textContent = '✓ Copied';
      setTimeout(() => { copyBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> Copy response'; }, 1800);
    });
  });
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
