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
    POST /api/queue               enqueue a task        {task, name?}  → {queue_id, position}
    GET  /api/queue               list pending queue items
    DELETE /api/queue/<queue_id>  remove a pending item
    POST /api/queue/clear         remove all pending items
    POST /api/schedule            create recurring task {task, cron, name?}
    GET  /api/schedule            list scheduled tasks
    DELETE /api/schedule/<id>     remove a scheduled task
"""

import sys, os, uuid, threading, subprocess, argparse, json, atexit, tempfile, time
from datetime import datetime, timezone
from collections import deque
from pathlib import Path

from schema import (
    resolve_project_id, start_session, end_session,
    list_projects, project_stats,
    _read_jsonl,
    PROJECTS_PATH, SESSIONS_PATH, ARTIFACTS_PATH,
)

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

# ── Project / session lifecycle ───────────────────────────────────────────────

_server_project_id : str = ""
_server_session    = None   # schema.Session object

def _init_session():
    global _server_project_id, _server_session
    _server_project_id = resolve_project_id()
    _server_session    = start_session(_server_project_id, triggered_by="server")
    print(f"[server] project={_server_project_id}  session={_server_session.session_id}")

def _close_session():
    if _server_session:
        with _lock:
            total_runs = sum(1 for r in _recent)
        end_session(_server_session, runs=total_runs)

atexit.register(_close_session)

# ── Orientation cache ────────────────────────────────────────────────────────

_orientation_doc  : str   = ""
_orientation_lock         = threading.Lock()
_ORIENTATION_INTERVAL     = 1800  # seconds between refreshes

_ORIENTATION_RAW = os.path.join(tempfile.gettempdir(), "harness_orientation_raw.md")

_ORIENTATION_MAX_AGE = 1800  # seconds — reuse existing file if fresher than this


def _orientation_age() -> float | None:
    """Return seconds since _ORIENTATION_RAW was last written, or None if it doesn't exist."""
    try:
        return time.time() - os.path.getmtime(_ORIENTATION_RAW)
    except OSError:
        return None


def _refresh_orientation(force: bool = False):
    """Launch /orientation as a visible agent subprocess, then read its raw doc into cache.

    If the raw file already exists and is younger than _ORIENTATION_MAX_AGE seconds,
    load it from disk and skip the agent run (unless force=True).
    """
    global _orientation_doc

    age = _orientation_age()
    if not force and age is not None and age < _ORIENTATION_MAX_AGE:
        # Recent enough — just load from disk without re-running the skill
        try:
            doc = open(_ORIENTATION_RAW, encoding="utf-8").read()
            with _orientation_lock:
                _orientation_doc = doc
            print(f"[server] orientation: reusing cached file ({int(age)}s old, {len(doc)} chars)")
        except Exception as e:
            print(f"[server] orientation cache load failed: {e}")
        return

    print("[server] orientation: launching agent subprocess...")
    run_id = _launch("/orientation", triggered_by="orientation_cache")
    # Wait up to 5 minutes for the agent run to finish
    deadline = time.time() + 300
    while time.time() < deadline:
        time.sleep(2)
        with _lock:
            if run_id not in _active:
                break
    # Read raw doc written by agent.py's _handle_orientation()
    try:
        if os.path.exists(_ORIENTATION_RAW):
            doc = open(_ORIENTATION_RAW, encoding="utf-8").read()
            with _orientation_lock:
                _orientation_doc = doc
            print(f"[server] orientation cache refreshed ({len(doc)} chars)")
        else:
            print("[server] orientation raw file not found after run")
    except Exception as e:
        print(f"[server] orientation cache read failed: {e}")

def _get_orientation() -> str:
    with _orientation_lock:
        return _orientation_doc

# ── In-memory state ──────────────────────────────────────────────────────────

_active : dict[str, dict] = {}           # run_id → run
_recent : deque           = deque(maxlen=100)
_queue  : deque           = deque()      # pending queue items (FIFO)
_sched  : dict[str, dict] = {}           # sched_id → schedule
_lock   = threading.Lock()

# ── Task runner ──────────────────────────────────────────────────────────────

def _maybe_launch_next():
    """If the queue has items and nothing is active, launch the next queued task."""
    with _lock:
        if _active or not _queue:
            return
        item = _queue.popleft()
    _launch(item["task"], f"queue:{item['queue_id']}")


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
                 "PYTHONIOENCODING":    "utf-8",
                 "PYTHONUNBUFFERED":    "1",
                 "AGENT_TASK":          task,
                 "HARNESS_PROJECT_ID":  _server_project_id,
                 "HARNESS_SESSION_ID":  _server_session.session_id if _server_session else "",
                 "HARNESS_RUN_ID":      "",   # RunTrace will generate a fresh one
                 },
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

        # Kick off the next queued task now that this slot is free
        _maybe_launch_next()

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


@app.route("/api/queue", methods=["POST"])
def api_queue_add():
    body = request.get_json(force=True, silent=True) or {}
    task = (body.get("task") or "").strip()
    if not task:
        return jsonify({"error": "task required"}), 400
    queue_id = uuid.uuid4().hex[:8]
    item = {
        "queue_id":   queue_id,
        "task":       task,
        "name":       (body.get("name") or task[:60]).strip(),
        "queued_at":  datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "triggered_by": "ui",
    }
    with _lock:
        _queue.append(item)
        position = len(_queue)
    # If nothing is running, launch immediately
    _maybe_launch_next()
    return jsonify({"queue_id": queue_id, "position": position}), 202


@app.route("/api/queue", methods=["GET"])
def api_queue_list():
    with _lock:
        items = [
            {**item, "position": i + 1}
            for i, item in enumerate(_queue)
        ]
    return jsonify({"pending": len(items), "items": items})


@app.route("/api/queue/<queue_id>", methods=["DELETE"])
def api_queue_delete(queue_id):
    with _lock:
        before = len(_queue)
        new_q  = deque(item for item in _queue if item["queue_id"] != queue_id)
        removed = before - len(new_q)
        _queue.clear()
        _queue.extend(new_q)
    if not removed:
        return jsonify({"error": "not found"}), 404
    return jsonify({"deleted": queue_id})


@app.route("/api/queue/clear", methods=["POST"])
def api_queue_clear():
    with _lock:
        count = len(_queue)
        _queue.clear()
    return jsonify({"cleared": count})


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


@app.route("/api/state")
def api_state():
    """
    Full hierarchical state: projects → sessions → recent runs + artifacts.
    The dashboard polls this every 5 s for live updates.
    No messages — those are fetched on demand via /api/messages?run_id=...
    """
    # Projects — latest record per project_id
    proj_records = _read_jsonl(PROJECTS_PATH)
    proj_latest: dict[str, dict] = {}
    for r in proj_records:
        pid = r.get("project_id")
        if pid:
            proj_latest[pid] = r
    projects = list(proj_latest.values())

    # Sessions — merge start + end events into one record per session_id
    sess_records = _read_jsonl(SESSIONS_PATH)
    sess_map: dict[str, dict] = {}
    for r in sess_records:
        sid = r.get("session_id")
        if not sid:
            continue
        if sid not in sess_map:
            sess_map[sid] = dict(r)
        else:
            sess_map[sid].update({k: v for k, v in r.items() if v is not None})
    sessions = sorted(sess_map.values(), key=lambda s: s.get("started_at", ""), reverse=True)

    # Artifacts — last 500
    art_records = _read_jsonl(ARTIFACTS_PATH)
    artifacts = art_records[-500:]

    # Live in-memory state
    with _lock:
        active = [
            {k: v for k, v in r.items() if k not in ("log_event", "proc", "log_lines", "log_done")}
            for r in _active.values()
        ]
        queue = [
            {**item, "position": i + 1} for i, item in enumerate(_queue)
        ]
        schedules = [{k: v for k, v in s.items() if k != "_job"} for s in _sched.values()]

    return jsonify({
        "server_project_id": _server_project_id,
        "server_session_id": _server_session.session_id if _server_session else "",
        "projects":   projects,
        "sessions":   sessions,
        "artifacts":  artifacts,
        "live": {
            "active":    active,
            "queue":     queue,
            "schedules": schedules,
        },
    })


@app.route("/api/messages")
def api_messages():
    """Return messages for a specific run_id from messages.jsonl."""
    run_id = request.args.get("run_id", "").strip()
    if not run_id:
        return jsonify({"error": "run_id required"}), 400
    msgs_path = os.path.join(HERE, "messages.jsonl")
    if not os.path.exists(msgs_path):
        return jsonify([])
    records = []
    with open(msgs_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    r = json.loads(line)
                    if r.get("run_id") == run_id:
                        records.append(r)
                except Exception:
                    pass
    return jsonify(records)


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


# ── Voice endpoint ────────────────────────────────────────────────────────────

@app.route("/api/voice", methods=["POST"])
def api_voice():
    """
    Receive an audio blob, transcribe with whisper, process with LLM, return markdown.
    Body: multipart/form-data with field 'audio' (webm/ogg/wav blob).
    Response: {transcript, response}
    """
    import tempfile, traceback
    from youtube_transcribe import _ensure_ffmpeg, WHISPER_MODEL, WHISPER_DEVICE

    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({"error": "no audio field"}), 400

    try:
        import tempfile as _tmp
        import subprocess as _sp
        import shutil, whisper

        with _tmp.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            tmp_path = tmp.name
            audio_file.save(tmp_path)

        # Resolve ffmpeg: system PATH → imageio_ffmpeg bundled binary
        ffmpeg_exe = shutil.which("ffmpeg")
        if not ffmpeg_exe:
            try:
                import imageio_ffmpeg
                ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            except ImportError:
                ffmpeg_exe = None
        if not ffmpeg_exe:
            raise RuntimeError("ffmpeg not found — install via winget or pip install imageio-ffmpeg")

        # Convert webm → 16kHz mono wav so whisper never needs to call ffmpeg itself
        wav_path = tmp_path + ".wav"
        r = _sp.run(
            [ffmpeg_exe, "-y", "-i", tmp_path, "-ar", "16000", "-ac", "1", "-f", "wav", wav_path],
            capture_output=True,
        )
        os.unlink(tmp_path)
        if r.returncode != 0:
            raise RuntimeError(f"ffmpeg conversion failed: {r.stderr.decode()[:300]}")

        # Load audio as numpy array and pass directly — bypasses whisper's internal ffmpeg call
        import numpy as np
        audio_np = np.frombuffer(
            _sp.run(
                [ffmpeg_exe, "-y", "-i", wav_path, "-f", "s16le", "-ar", "16000", "-ac", "1", "pipe:1"],
                capture_output=True, check=True,
            ).stdout,
            dtype=np.int16,
        ).astype(np.float32) / 32768.0

        os.unlink(wav_path)
        model = whisper.load_model(WHISPER_MODEL, device=WHISPER_DEVICE)
        result = model.transcribe(audio_np)
        transcript = (result.get("text") or "").strip()
    except Exception as e:
        return jsonify({"error": f"transcription failed: {e}"}), 500

    if not transcript:
        return jsonify({"error": "transcript empty"}), 400

    try:
        import inference
        producer = os.environ.get("HARNESS_PRODUCER_MODEL", "pi-qwen-32b").strip()
        active = inference.get_active_vllm_model()
        if active:
            try:
                import urllib.request as _ur
                vllm_base = os.environ.get("VLLM_BASE_URL", "http://localhost:8000/v1").rstrip("/")
                models = json.loads(_ur.urlopen(f"{vllm_base}/models", timeout=2).read())["data"]
                if models and not any(m["id"] == producer for m in models):
                    producer = active
            except Exception:
                pass

        orientation = _get_orientation()
        orientation_block = f"\n\n## Project orientation\n\n{orientation}" if orientation else ""

        system_msg = f"""You are the voice interface for the Harness Engineering agentic research pipeline.

Your job is to interpret the user's spoken request and return a JSON object — nothing else, no markdown fences.

## Classification rules

Classify as **"task"** when the user wants the agent to:
- Search the web, fetch a URL, or find information
- Write, save, or generate a file
- Run an experiment, analysis, or pipeline operation
- Do anything that requires agent.py to execute

Classify as **"answer"** when the user asks a question about:
- The harness itself, its models, experiments, or architecture
- Something answerable from the orientation context without web access

## ASR correction

Speech-to-text often garbles brand names and technical terms. Correct them:
- "lang chain" / "lang chained" / "lang check" → LangChain
- "open a eye" / "open eye" → OpenAI
- "hug in face" → Hugging Face
- "clock post" / "block post" → blog post
- "git hub" → GitHub
- "pie torch" → PyTorch
- "lama" / "llama" → Llama
- "fast api" → FastAPI
Apply similar corrections for any other obvious misrecognitions.

## Output path rule

Agent tasks must end with "save to <path>.md".
If the user didn't specify a path, invent a sensible snake_case filename in the working directory.
Example: "langchain-latest-blog-post.md"

## Response format

Return exactly this JSON, no other text:

{{
  "type": "task" | "answer",
  "corrected_transcript": "<ASR-corrected version of what the user said>",
  "reasoning": "<one sentence: what you understood and any corrections made>",
  "task_string": "<complete agent task string ending in save to X.md — only for type=task>",
  "suggested_path": "<relative filename like langchain-blog.md — only for type=task>",
  "response": "<markdown answer — only for type=answer>"
}}{orientation_block}"""

        resp = inference.chat(
            model=producer,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user",   "content": transcript},
            ],
            options={"temperature": 0.2, "num_predict": 1024},
        )
        raw = resp.message.content.strip()
        # Strip markdown fences if the model wrapped it anyway
        if raw.startswith("```"):
            raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        # Fall back: treat raw as an answer
        parsed = {"type": "answer", "corrected_transcript": transcript,
                  "reasoning": "", "response": raw}
    except Exception as e:
        return jsonify({"transcript": transcript, "error": f"LLM failed: {e}"}), 500

    parsed["transcript"] = transcript
    return jsonify(parsed)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--host", default="127.0.0.1")
    args = p.parse_args()
    _init_session()
    # Build orientation cache in background so startup isn't blocked
    threading.Thread(target=_refresh_orientation, daemon=True).start()
    # Schedule periodic refresh
    if CRON_OK:
        _scheduler.add_job(_refresh_orientation, "interval", seconds=_ORIENTATION_INTERVAL,
                           id="orientation_refresh")
    else:
        # Fallback: simple timer loop if APScheduler unavailable
        def _orientation_loop():
            while True:
                time.sleep(_ORIENTATION_INTERVAL)
                _refresh_orientation()
        threading.Thread(target=_orientation_loop, daemon=True).start()
    print(f"[server] http://{args.host}:{args.port}")
    print(f"[server] cron: {'enabled' if CRON_OK else 'disabled (pip install apscheduler)'}")
    print(f"[server] orientation: building in background, refreshes every {_ORIENTATION_INTERVAL//60}min")
    app.run(host=args.host, port=args.port, debug=False, threaded=True)
