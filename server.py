"""
server.py — live task runner + dashboard server for harness-engineering.

Install once:
    pip install flask apscheduler

Run:
    python server.py              # http://127.0.0.1:8765
    python server.py --port 9000

Endpoints:
    GET  /                        dashboard (auto-regenerated)
    GET  /api/data                live dashboard JSON
    POST /api/run                 start a task now      {task}  → {run_id}
    GET  /api/stream/<run_id>     SSE: agent stdout line-by-line
    GET  /api/runs                active + recent completed runs
    POST /api/run/<run_id>/cancel kill a running task
    POST /api/schedule            create recurring task {task, cron, name?}
    GET  /api/schedule            list scheduled tasks
    DELETE /api/schedule/<id>     remove a scheduled task
"""

import sys, os, uuid, threading, subprocess, argparse, json
from datetime import datetime, timezone
from collections import deque
from pathlib import Path

try:
    from flask import Flask, Response, request, jsonify
except ImportError:
    sys.exit("[server] Flask not found — run: pip install flask apscheduler")

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    _scheduler = BackgroundScheduler(daemon=True)
    _scheduler.start()
    CRON_OK = True
except ImportError:
    _scheduler = None
    CRON_OK = False
    print("[server] APScheduler not found — cron scheduling disabled (pip install apscheduler)")

HERE = os.path.dirname(os.path.abspath(__file__))
app  = Flask(__name__)

# ── In-memory state ──────────────────────────────────────────────────────────

_active : dict[str, dict] = {}           # run_id → run
_recent : deque           = deque(maxlen=100)
_sched  : dict[str, dict] = {}           # sched_id → schedule
_lock   = threading.Lock()

# ── Task runner ──────────────────────────────────────────────────────────────

def _launch(task: str, triggered_by: str = "manual") -> str:
    """Spawn agent.py, stream its stdout into log_lines. Returns run_id."""
    run_id    = uuid.uuid4().hex[:8]
    log_event = threading.Event()   # signalled on each new line or process exit

    run = {
        "run_id":       run_id,
        "task":         task,
        "triggered_by": triggered_by,
        "status":       "running",
        "start_ts":     datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "end_ts":       None,
        "returncode":   None,
        "log_event":    log_event,
        "log_lines":    [],
        "log_done":     False,
        "proc":         None,
    }

    def _worker():
        # Pass task via env var, not CLI arg — avoids MSYS2/Git Bash POSIX→Windows
        # path conversion which mangles /skill tokens and https:// URLs in argv.
        cmd = [sys.executable, os.path.join(HERE, "agent.py"), "--from-env"]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1, encoding="utf-8", errors="replace",
            cwd=HERE,
            env={**os.environ,
                 "PYTHONIOENCODING": "utf-8",
                 "PYTHONUNBUFFERED": "1",
                 "AGENT_TASK": task},
        )
        with _lock:
            run["proc"] = proc

        for raw in proc.stdout:
            line = raw.rstrip()
            with _lock:
                run["log_lines"].append(line)
            log_event.set()

        proc.wait()

        with _lock:
            run["status"]     = "done" if proc.returncode == 0 else "error"
            run["returncode"] = proc.returncode
            run["end_ts"]     = datetime.now(timezone.utc).isoformat(timespec="seconds")
            run["log_done"]   = True
        log_event.set()

        with _lock:
            snap = {k: v for k, v in run.items() if k not in ("log_event", "proc")}
            _recent.appendleft(snap)
            _active.pop(run_id, None)

    with _lock:
        _active[run_id] = run

    threading.Thread(target=_worker, daemon=True, name=f"run-{run_id}").start()
    return run_id


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/favicon.ico")
def favicon():
    return Response(status=204)


@app.route("/")
def index():
    """Serve the dashboard, regenerated fresh on each load."""
    try:
        import dashboard as db
        data = db.build()
        html = db.render(data)
        return Response(html, mimetype="text/html")
    except Exception as exc:
        return Response(f"<pre>[dashboard error] {exc}</pre>", status=500)


@app.route("/api/data")
def api_data():
    import dashboard as db
    return jsonify(db.build())


@app.route("/api/run", methods=["POST"])
def api_run():
    body  = request.get_json(force=True, silent=True) or {}
    task  = (body.get("task") or "").strip()
    if not task:
        return jsonify({"error": "task required"}), 400
    run_id = _launch(task, "ui")
    return jsonify({"run_id": run_id}), 202


@app.route("/api/stream/<run_id>")
def api_stream(run_id):
    def generate():
        with _lock:
            run = _active.get(run_id)
            if not run:
                yield "data: [run not found]\n\n"
                return
            event = run["log_event"]

        idx = 0
        while True:
            # Drain any newly available lines first
            with _lock:
                new_lines = list(run["log_lines"][idx:])
                done      = run.get("log_done", False)

            if new_lines:
                for line in new_lines:
                    yield f"data: {line}\n\n"
                idx += len(new_lines)
                continue  # immediately check for more before waiting

            if done:
                yield "data: [DONE]\n\n"
                break

            # Nothing new yet — arm the event, then re-check to avoid a race
            # between our check above and the worker calling event.set()
            event.clear()
            with _lock:
                new_lines = list(run["log_lines"][idx:])
                done      = run.get("log_done", False)
            if new_lines or done:
                continue  # process without blocking

            notified = event.wait(timeout=25)
            if not notified:
                yield ": keepalive\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/api/runs")
def api_runs():
    with _lock:
        active = [
            {k: v for k, v in r.items() if k not in ("log_event", "proc", "log_lines", "log_done")}
            for r in _active.values()
        ]
        recent = list(_recent)
    return jsonify({"active": active, "recent": recent})


@app.route("/api/run/<run_id>/cancel", methods=["POST"])
def api_cancel(run_id):
    with _lock:
        run = _active.get(run_id)
    if not run or not run.get("proc"):
        return jsonify({"error": "not found or already done"}), 404
    run["proc"].terminate()
    return jsonify({"cancelled": run_id})


@app.route("/api/schedule", methods=["GET"])
def api_sched_list():
    with _lock:
        rows = [{k: v for k, v in s.items() if k != "_job"} for s in _sched.values()]
    return jsonify({"cron_available": CRON_OK, "schedules": rows})


@app.route("/api/schedule", methods=["POST"])
def api_sched_create():
    if not CRON_OK:
        return jsonify({"error": "APScheduler not installed — pip install apscheduler"}), 501
    body  = request.get_json(force=True, silent=True) or {}
    task  = (body.get("task") or "").strip()
    cron  = (body.get("cron") or "").strip()
    name  = (body.get("name") or task[:48]).strip()
    if not task or not cron:
        return jsonify({"error": "task and cron required"}), 400
    try:
        trigger = CronTrigger.from_crontab(cron)
    except Exception as exc:
        return jsonify({"error": f"invalid cron expression: {exc}"}), 400
    sched_id = uuid.uuid4().hex[:8]
    job = _scheduler.add_job(
        _launch, trigger=trigger,
        args=[task, f"sched:{sched_id}"],
        id=sched_id, name=name,
    )
    entry = {
        "sched_id": sched_id, "name": name, "task": task, "cron": cron,
        "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
        "_job": job,
    }
    with _lock:
        _sched[sched_id] = entry
    return jsonify({k: v for k, v in entry.items() if k != "_job"}), 201


@app.route("/api/schedule/<sched_id>", methods=["DELETE"])
def api_sched_delete(sched_id):
    with _lock:
        entry = _sched.pop(sched_id, None)
    if not entry:
        return jsonify({"error": "not found"}), 404
    try:
        _scheduler.remove_job(sched_id)
    except Exception:
        pass
    return jsonify({"deleted": sched_id})


_FEEDBACK_JSONL  = Path(__file__).parent / "feedback.jsonl"
_FINETUNE_METRICS = Path(__file__).parent / "finetune_metrics.jsonl"

@app.route("/api/feedback", methods=["POST"])
def api_feedback():
    """
    Save RLHF feedback for a run.
    Body: {run_id, task, rating, original_output, edited_output, comment}
    Appends to feedback.jsonl as a DPO-ready preference record.
    """
    data = request.get_json(force=True, silent=True) or {}
    required = ("run_id", "rating")
    if not all(k in data for k in required):
        return jsonify({"error": f"missing fields: {required}"}), 400

    record = {
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "run_id":          data.get("run_id", ""),
        "task":            data.get("task", ""),
        "rating":          data.get("rating"),        # 1 = good, -1 = bad, 0 = neutral
        "original_output": data.get("original_output", ""),
        "edited_output":   data.get("edited_output", ""),
        "comment":         data.get("comment", ""),
    }
    with open(_FEEDBACK_JSONL, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return jsonify({"saved": True, "timestamp": record["timestamp"]})


@app.route("/api/finetune/metrics")
def api_finetune_metrics():
    """
    Return all per-step metrics from the current (or last) fine-tuning run.
    Each line of finetune_metrics.jsonl is a typed event: train_begin, metric,
    epoch_end, train_end.
    """
    if not _FINETUNE_METRICS.exists():
        return jsonify([])
    records = []
    with open(_FINETUNE_METRICS, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass
    return jsonify(records)


@app.route("/api/feedback", methods=["GET"])
def api_feedback_list():
    """Return all saved feedback records."""
    if not _FEEDBACK_JSONL.exists():
        return jsonify([])
    records = []
    with open(_FEEDBACK_JSONL, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass
    return jsonify(records)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--host", default="127.0.0.1")
    args = p.parse_args()
    print(f"[server] http://{args.host}:{args.port}")
    print(f"[server] cron: {'enabled' if CRON_OK else 'disabled (pip install apscheduler)'}")
    app.run(host=args.host, port=args.port, debug=False, threaded=True)
