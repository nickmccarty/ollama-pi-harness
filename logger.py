"""
logger.py — structured run tracing for the agent pipeline.

Appends one JSON record per run to runs.jsonl.
Import and use RunTrace in agent.py and wiggum.py.
"""

import json
import os
import time
from datetime import datetime, timezone

LOG_PATH = os.path.join(os.path.dirname(__file__), "runs.jsonl")


def _extract_usage(response) -> dict:
    """
    Pull token counts and timing from an ollama ChatResponse.
    Returns zeros for any missing fields (safe to call on any response).
    """
    return {
        "input_tokens":  getattr(response, "prompt_eval_count", 0) or 0,
        "output_tokens": getattr(response, "eval_count", 0) or 0,
        "total_ms":      round((getattr(response, "total_duration", 0) or 0) / 1e6, 1),
        "eval_ms":       round((getattr(response, "eval_duration",  0) or 0) / 1e6, 1),
        "prompt_ms":     round((getattr(response, "prompt_eval_duration", 0) or 0) / 1e6, 1),
    }


class RunTrace:
    def __init__(self, task: str, producer_model: str, evaluator_model: str):
        self._run_start = time.monotonic()
        self.data = {
            "timestamp":        datetime.now(timezone.utc).isoformat(),
            "task":             task,
            "producer_model":   producer_model,
            "evaluator_model":  evaluator_model,

            # Timing
            "run_duration_s":   None,

            # Token totals (all ollama.chat calls in the run)
            "input_tokens":     0,
            "output_tokens":    0,

            # Per-stage token breakdown
            "tokens_by_stage":  {},   # stage -> {input, output, calls}

            # Tool calls and search quality
            "tool_calls":           [],
            "vision_images":        [],
            "total_search_chars":   0,
            "quality_floor_hit":    False,

            # Context enrichment
            "files_read":           [],
            "code_executions":      0,
            "injection_stripped":   0,
            "memory_hits":          0,
            "plan":                 None,

            # Orchestration
            "orchestrated":         False,
            "subtask_count":        0,

            # Output
            "synth_forced":         False,
            "output_path":          None,
            "output_lines":         None,
            "output_bytes":         None,
            "count_check_retry":    False,

            # Wiggum
            "wiggum_rounds":        0,
            "wiggum_scores":        [],
            "wiggum_dims":          [],

            "final":                None,
        }

    # ------------------------------------------------------------------
    # Token / timing tracking
    # ------------------------------------------------------------------

    def log_usage(self, response, stage: str = "other"):
        """
        Accumulate token counts and latency from one ollama.chat response.
        Call immediately after every ollama.chat() call.
        stage: "search_query" | "synth" | "synth_count" | "tool_loop" |
               "wiggum_eval" | "wiggum_revise" | "planner" | "memory" | "other"
        """
        u = _extract_usage(response)
        self.data["input_tokens"]  += u["input_tokens"]
        self.data["output_tokens"] += u["output_tokens"]

        s = self.data["tokens_by_stage"].setdefault(stage, {"input": 0, "output": 0, "calls": 0, "total_ms": 0})
        s["input"]    += u["input_tokens"]
        s["output"]   += u["output_tokens"]
        s["calls"]    += 1
        s["total_ms"] += u["total_ms"]

    # ------------------------------------------------------------------
    # Existing log methods
    # ------------------------------------------------------------------

    def log_tool_call(self, name: str, query: str, result_chars: int):
        self.data["tool_calls"].append({
            "name": name,
            "query": query,
            "result_chars": result_chars,
        })

    def log_synth_forced(self):
        self.data["synth_forced"] = True

    def log_plan(self, plan_dict: dict):
        self.data["plan"] = plan_dict

    def log_memory_hits(self, count: int):
        self.data["memory_hits"] = count

    def log_injection_stripped(self, count: int):
        self.data["injection_stripped"] += count

    def log_files_read(self, paths: list[str]):
        self.data["files_read"] = paths

    def log_vision(self, image_paths: list[str]):
        self.data["vision_images"] = image_paths

    def log_count_retry(self):
        self.data["count_check_retry"] = True

    def log_search_quality(self, total_chars: int):
        self.data["total_search_chars"] = total_chars
        self.data["quality_floor_hit"] = total_chars < 1800

    def log_write(self, path: str, content: str):
        self.data["output_path"] = os.path.abspath(os.path.expanduser(path))
        self.data["output_lines"] = content.count("\n") + 1
        self.data["output_bytes"] = len(content.encode("utf-8"))

    def log_wiggum(self, wiggum_trace: dict):
        rounds = wiggum_trace.get("rounds", [])
        self.data["wiggum_rounds"] = len(rounds)
        self.data["wiggum_scores"] = [r["score"] for r in rounds]
        self.data["wiggum_dims"]   = [r.get("dims", {}) for r in rounds]
        self.data["task_type"]     = wiggum_trace.get("task_type")
        self.data["final"]         = wiggum_trace.get("final")

        # Merge token stats from wiggum if present
        for stage, vals in wiggum_trace.get("tokens_by_stage", {}).items():
            s = self.data["tokens_by_stage"].setdefault(stage, {"input": 0, "output": 0, "calls": 0, "total_ms": 0})
            s["input"]    += vals.get("input", 0)
            s["output"]   += vals.get("output", 0)
            s["calls"]    += vals.get("calls", 0)
            s["total_ms"] += vals.get("total_ms", 0)
        self.data["input_tokens"]  += wiggum_trace.get("input_tokens", 0)
        self.data["output_tokens"] += wiggum_trace.get("output_tokens", 0)

    def finish(self, final: str = None):
        if final:
            self.data["final"] = final
        self.data["run_duration_s"] = round(time.monotonic() - self._run_start, 1)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(self.data) + "\n")
        tok_in  = self.data["input_tokens"]
        tok_out = self.data["output_tokens"]
        dur     = self.data["run_duration_s"]
        print(f"  [log] {dur}s  in={tok_in} out={tok_out} tok  → {LOG_PATH}")
