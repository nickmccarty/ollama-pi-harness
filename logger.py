"""
logger.py — structured run tracing for the agent pipeline.

Appends one JSON record per run to runs.jsonl.
Import and use RunTrace in agent.py and wiggum.py.
"""

import json
import os
from datetime import datetime, timezone

LOG_PATH = os.path.join(os.path.dirname(__file__), "runs.jsonl")


class RunTrace:
    def __init__(self, task: str, producer_model: str, evaluator_model: str):
        self.data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task": task,
            "producer_model": producer_model,
            "evaluator_model": evaluator_model,
            "tool_calls": [],
            "vision_images": [],
            "total_search_chars": 0,
            "quality_floor_hit": False,
            "files_read": [],
            "code_executions": 0,
            "injection_stripped": 0,
            "memory_hits": 0,
            "plan": None,
            "orchestrated": False,
            "subtask_count": 0,
            "synth_forced": False,
            "output_path": None,
            "output_lines": None,
            "output_bytes": None,
            "wiggum_rounds": 0,
            "wiggum_scores": [],
            "count_check_retry": False,
            "final": None,
        }

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
        self.data["wiggum_dims"] = [r.get("dims", {}) for r in rounds]
        self.data["task_type"] = wiggum_trace.get("task_type")
        self.data["final"] = wiggum_trace.get("final")

    def finish(self, final: str = None):
        if final:
            self.data["final"] = final
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(self.data) + "\n")
        print(f"  [log] appended to {LOG_PATH}")
