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
from datetime import datetime

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
    scored_runs = [(r["timestamp"][:19], first_wiggum_score(r), r.get("producer_model", ""))
                   for r in runs if first_wiggum_score(r) is not None]
    score_labels  = [x[0].replace("T", " ") for x in scored_runs]
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
    stage_totals = defaultdict(lambda: {"input": 0, "output": 0, "total_ms": 0, "calls": 0})
    for r in runs:
        for stage, vals in (r.get("tokens_by_stage") or {}).items():
            stage_totals[stage]["input"]    += vals.get("input", 0)
            stage_totals[stage]["output"]   += vals.get("output", 0)
            stage_totals[stage]["total_ms"] += vals.get("total_ms", 0)
            stage_totals[stage]["calls"]    += vals.get("calls", 1)
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
    dur_labels = [(r.get("timestamp") or "")[:19].replace("T", " ") for r in runs if r.get("run_duration_s")]
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
        ms = stage_totals[s]["total_ms"]
        if ms > 0:
            stage_tps_out.append(round(stage_totals[s]["output"] / (ms / 1000), 1))
            stage_tps_in.append(round(stage_totals[s]["input"]  / (ms / 1000), 1))
        else:
            stage_tps_out.append(0)
            stage_tps_in.append(0)

    run_tps_labels = []
    run_tps_out    = []
    run_tps_in     = []
    for r in runs:
        tbs = r.get("tokens_by_stage") or {}
        total_out_tok = sum(v.get("output", 0) for v in tbs.values())
        total_in_tok  = sum(v.get("input",  0) for v in tbs.values())
        total_ms      = sum(v.get("total_ms", 0) for v in tbs.values())
        if total_ms > 0:
            run_tps_labels.append((r.get("timestamp") or "")[:19].replace("T", " "))
            run_tps_out.append(round(total_out_tok / (total_ms / 1000), 1))
            run_tps_in.append(round(total_in_tok  / (total_ms / 1000), 1))

    avg_out_tps = round(sum(run_tps_out) / len(run_tps_out), 1) if run_tps_out else 0

    # --- Runs per hour-of-day heatmap (0-23) ---
    hour_counts = defaultdict(int)
    for r in runs:
        ts = r.get("timestamp") or ""
        if len(ts) >= 13:
            try:
                hour_counts[int(ts[11:13])] += 1
            except ValueError:
                pass
    hour_labels = [f"{h:02d}:00" for h in range(24)]
    hour_values = [hour_counts[h] for h in range(24)]

    # --- Recent runs table (last 30) ---
    recent = []
    for r in runs[-30:]:
        recent.append({
            "ts":       (r.get("timestamp") or "")[:19].replace("T", " "),
            "task":     (r.get("task") or "")[:70],
            "model":    r.get("producer_model") or "",
            "type":     r.get("task_type") or "?",
            "score":    first_wiggum_score(r),
            "rounds":   r.get("wiggum_rounds"),
            "duration": round((r.get("run_duration_s") or 0) / 60, 1),
            "tokens_in":  r.get("input_tokens") or 0,
            "tokens_out": r.get("output_tokens") or 0,
            "final":    r.get("final") or "?",
            "searches": r.get("search_rounds") or len(r.get("tool_calls") or []),
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
        ts = (r.get("timestamp") or "")[:19].replace("T", " ")
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
  tr:hover td { background: rgba(255,255,255,0.03); }

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
// Recent runs table
// ---------------------------------------------------------------------------
const tbl = $('runsTable');
const cols = ['Timestamp','Task','Model','Type','Score','Rounds','Duration','In tok','Out tok','Searches','Result'];
tbl.innerHTML = `<tr>${cols.map(c=>`<th>${c}</th>`).join('')}</tr>`;

DATA.recent_runs.forEach(r => {
  const scoreBar = r.score != null
    ? `<span class="score-bar"><span class="score-fill" style="width:${r.score*10}%"></span></span>${r.score}`
    : '—';
  const badge = r.final === 'PASS'  ? `<span class="badge badge-pass">PASS</span>`
              : r.final === 'FAIL'  ? `<span class="badge badge-fail">FAIL</span>`
              : r.final === 'ERROR' ? `<span class="badge badge-error">ERR</span>`
              : r.final;
  const row = [
    `<td style="color:var(--muted);font-size:11px">${r.ts}</td>`,
    `<td style="max-width:280px;overflow:hidden;text-overflow:ellipsis" title="${r.task.replace(/"/g,'&quot;')}">${r.task}</td>`,
    `<td style="color:var(--muted)">${r.model}</td>`,
    `<td style="color:var(--muted)">${r.type}</td>`,
    `<td>${scoreBar}</td>`,
    `<td style="color:var(--muted);text-align:center">${r.rounds ?? '—'}</td>`,
    `<td style="color:var(--orange)">${r.duration}m</td>`,
    `<td style="color:var(--muted)">${fmtK(r.tokens_in)}</td>`,
    `<td style="color:var(--muted)">${fmtK(r.tokens_out)}</td>`,
    `<td style="text-align:center;color:var(--muted)">${r.searches}</td>`,
    `<td>${badge}</td>`,
  ];
  tbl.innerHTML += `<tr>${row.join('')}</tr>`;
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
</script>
</body>
</html>
"""


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
