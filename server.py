#!/usr/bin/env python3
"""NewsAggro web app.

GET /              → cached briefs/index.html (or empty.html if none)
POST /api/generate → kicks off the pipeline in a background thread
GET  /api/status   → JSON status of the running pipeline (for client polling)

Run:
    python server.py
    open http://localhost:8000/
"""
import os
import threading
import time
import traceback
from flask import Flask, send_file, jsonify

from newsaggro.pipeline import run_pipeline
from newsaggro.renderer import render_html
from newsaggro.output import save_brief_html
from newsaggro.config import BRIEFS_DIR

app = Flask(__name__)

# Shared status used by the background pipeline thread and the /api/status poll.
_status = {
    "running": False,
    "stage": "idle",
    "info": "",
    "started_at": None,
    "finished_at": None,
    "error": None,
}
_status_lock = threading.Lock()


def _set_status(stage: str, info: str = "") -> None:
    with _status_lock:
        _status["stage"] = stage
        _status["info"] = info


def _pipeline_thread() -> None:
    """Runs the pipeline + render; writes status updates as it goes."""
    with _status_lock:
        _status.update(
            running=True,
            stage="starting",
            info="",
            started_at=time.time(),
            finished_at=None,
            error=None,
        )
    try:
        result = run_pipeline(progress=_set_status)
        _set_status("render", "")
        html = render_html(
            stories=result["stories"],
            date_str=result["date"],
            intro=result["intro"],
        )
        save_brief_html(html)
        _set_status("done", "")
    except Exception as e:
        traceback.print_exc()
        with _status_lock:
            _status["error"] = str(e)
            _status["stage"] = "error"
    finally:
        with _status_lock:
            _status["running"] = False
            _status["finished_at"] = time.time()


@app.route("/")
def index():
    brief_path = os.path.abspath(os.path.join(BRIEFS_DIR, "index.html"))
    empty_path = os.path.abspath(os.path.join(BRIEFS_DIR, "empty.html"))
    if os.path.exists(brief_path):
        return send_file(brief_path)
    return send_file(empty_path)


@app.route("/api/generate", methods=["POST"])
def generate():
    with _status_lock:
        if _status["running"]:
            return jsonify({"status": "already_running"}), 409
    threading.Thread(target=_pipeline_thread, daemon=True).start()
    return jsonify({"status": "started"})


@app.route("/api/status")
def status():
    with _status_lock:
        return jsonify(dict(_status))


if __name__ == "__main__":
    print("\n🗞  NewsAggro server")
    print("    http://localhost:8000/")
    print("    Ctrl+C to stop\n")
    # threaded=True so the status poll endpoint isn't blocked by the pipeline.
    app.run(host="127.0.0.1", port=8000, debug=False, threaded=True)
