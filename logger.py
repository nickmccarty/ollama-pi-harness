"""
logger.py — structured run tracing for the agent pipeline.

Appends one JSON record per run to runs.jsonl.
Writes a Chrome Trace Event JSON to traces/ for each run — load in ui.perfetto.dev.
Import and use RunTrace in agent.py and wiggum.py.
"""

import json
import os
import re
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone

LOG_PATH  = os.path.join(os.path.dirname(__file__), "runs.jsonl")
TRACE_DIR = os.path.join(os.path.dirname(__file__), "traces")


def _extract_usage(response) -> dict:
    """
    Pull token counts, timing, and thinking content from an ollama ChatResponse.
    Returns zeros/empty for any missing fields (safe to call on any response).
    """
    msg = getattr(response, "message", None)
    thinking = (getattr(msg, "thinking", None) or "") if msg is not None else ""
    return {
        "input_tokens":   getattr(response, "prompt_eval_count", 0) or 0,
        "output_tokens":  getattr(response, "eval_count", 0) or 0,
        "total_ms":       round((getattr(response, "total_duration", 0) or 0) / 1e6, 1),
        "eval_ms":        round((getattr(response, "eval_duration",  0) or 0) / 1e6, 1),
        "prompt_ms":      round((getattr(response, "prompt_eval_duration", 0) or 0) / 1e6, 1),
        "thinking":       thinking,
        "thinking_chars": len(thinking),
    }


class RunTrace:
    def __init__(self, task: str, producer_model: str, evaluator_model: str):
        self._run_start  = time.monotonic()
        self._t0_us      = time.monotonic_ns() // 1000   # anchor for Chrome Trace timestamps
        self._pid        = os.getpid()
        self._events     = []                             # Chrome Trace Event list
        self._task       = task
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

            # Chain-of-thought preservation
            # Stores the raw thinking text emitted by the producer model during
            # each synthesis call. One entry per call (initial synth + count-retry).
            # thinking_chars per stage is already tracked in tokens_by_stage; this
            # field preserves the actual text for offline CoT quality analysis.
            "synth_cot":            [],

            # Wiggum
            "wiggum_rounds":        0,
            "wiggum_scores":        [],
            "wiggum_dims":          [],
            "wiggum_eval_log":      [],   # [{round, score, dims, issues, feedback}] per round

            "final":                None,
        }

    # ------------------------------------------------------------------
    # Chrome Trace Event instrumentation
    # ------------------------------------------------------------------

    def _record(self, name: str, start_us: int, dur_us: int, tid: int, args: dict = None):
        """Append one complete (X) Chrome Trace event."""
        event = {
            "name": name,
            "ph":   "X",
            "ts":   start_us - self._t0_us,
            "dur":  max(dur_us, 1),
            "pid":  self._pid,
            "tid":  tid,
        }
        if args:
            event["args"] = args
        self._events.append(event)

    def name_thread(self, name: str):
        """Emit a thread_name metadata event for the calling thread (shows in Perfetto lane labels)."""
        self._events.append({
            "name": "thread_name",
            "ph":   "M",
            "pid":  self._pid,
            "tid":  threading.get_ident(),
            "args": {"name": name},
        })

    @contextmanager
    def span(self, name: str, **args):
        """
        Context manager — records a Chrome Trace 'X' event for the enclosed block.

        Usage:
            with trace.span("synthesize", model="pi-qwen-32b"):
                content = synthesize(...)
        """
        tid      = threading.get_ident()
        start_us = time.monotonic_ns() // 1000
        try:
            yield
        finally:
            dur_us = (time.monotonic_ns() // 1000) - start_us
            self._record(name, start_us, dur_us, tid, args or None)

    def _write_trace(self):
        """Write Chrome Trace JSON to traces/<timestamp>_<slug>.json."""
        if not self._events:
            return
        os.makedirs(TRACE_DIR, exist_ok=True)
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = re.sub(r"[^\w]+", "_", self._task[:50]).strip("_")
        path = os.path.join(TRACE_DIR, f"{ts}_{slug}.json")
        payload = {
            "traceEvents":     self._events,
            "displayTimeUnit": "ms",
            "otherData":       {"task": self._task},
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f)
        print(f"  [trace] {path}")

    # ------------------------------------------------------------------
    # Token / timing tracking
    # ------------------------------------------------------------------

    def log_usage(self, response, stage: str = "other"):
        """
        Accumulate token counts, latency, and thinking chars from one ollama.chat response.
        Also emits a Chrome Trace event using Ollama's own reported total_duration.

        stage: "search_query" | "synth" | "synth_count" | "tool_loop" |
               "wiggum_eval" | "wiggum_revise" | "planner" | "memory" | "compress_knowledge" | "other"
        """
        u = _extract_usage(response)
        self.data["input_tokens"]  += u["input_tokens"]
        self.data["output_tokens"] += u["output_tokens"]

        s = self.data["tokens_by_stage"].setdefault(
            stage, {"input": 0, "output": 0, "thinking_chars": 0, "calls": 0,
                    "total_ms": 0, "eval_ms": 0, "prompt_ms": 0}
        )
        s["input"]          += u["input_tokens"]
        s["output"]         += u["output_tokens"]
        s["thinking_chars"] += u["thinking_chars"]
        s["calls"]          += 1
        s["total_ms"]       += u["total_ms"]
        s["eval_ms"]        += u["eval_ms"]    # generation time only — correct denominator for output tok/s
        s["prompt_ms"]      += u["prompt_ms"]  # prompt-eval time only — correct denominator for input tok/s

        # Emit trace event using Ollama's reported timing (more accurate than wall-clock wrap)
        if u["total_ms"] > 0:
            now_us   = time.monotonic_ns() // 1000
            start_us = now_us - int(u["total_ms"] * 1000)
            self._record(
                f"llm:{stage}",
                start_us,
                int(u["total_ms"] * 1000),
                threading.get_ident(),
                {"in_tok": u["input_tokens"], "out_tok": u["output_tokens"],
                 "prompt_ms": u["prompt_ms"], "eval_ms": u["eval_ms"]},
            )

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

    def log_synth_cot(self, thinking: str):
        """Append one synthesis thinking block. Called once per synthesize() invocation."""
        if thinking:
            self.data["synth_cot"].append(thinking)

    def log_count_retry(self):
        self.data["count_check_retry"] = True

    def log_search_quality(self, total_chars: int):
        self.data["total_search_chars"] = total_chars
        self.data["quality_floor_hit"] = total_chars < 1800

    def log_write(self, path: str, content: str):
        self.data["output_path"]    = os.path.abspath(os.path.expanduser(path))
        self.data["output_lines"]   = content.count("\n") + 1
        self.data["output_bytes"]   = len(content.encode("utf-8"))
        self.data["final_content"]  = content[:16_000]  # inline for HF export; truncated at 16k chars

    def log_wiggum(self, wiggum_trace: dict):
        rounds = wiggum_trace.get("rounds", [])
        self.data["wiggum_rounds"] = len(rounds)
        self.data["wiggum_scores"] = [r["score"] for r in rounds]
        self.data["wiggum_dims"]   = [r.get("dims", {}) for r in rounds]
        self.data["task_type"]     = wiggum_trace.get("task_type")
        self.data["final"]         = wiggum_trace.get("final")
        self.data["wiggum_eval_log"] = [
            {
                "round":    r["round"],
                "score":    r["score"],
                "dims":     r.get("dims", {}),
                "issues":   r.get("issues", []),
                "feedback": r.get("feedback", ""),
                **({"content": r["content"]} if r.get("content") else {}),
                **({"thinking": r["thinking"]} if r.get("thinking") else {}),
            }
            for r in rounds
        ]

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
        self._write_trace()
