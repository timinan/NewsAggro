#!/usr/bin/env python3
"""NewsAggro web app.

Serves the latest cached brief at /. Click the in-page Refresh button to
hit POST /api/generate, which runs the agent pipeline and renders new HTML.

Run:
    python server.py
    open http://localhost:8000/
"""
import os
from flask import Flask, send_file, jsonify

from newsaggro.pipeline import run_pipeline
from newsaggro.renderer import render_html
from newsaggro.output import save_brief_html
from newsaggro.config import BRIEFS_DIR

app = Flask(__name__)


@app.route("/")
def index():
    brief_path = os.path.abspath(os.path.join(BRIEFS_DIR, "index.html"))
    empty_path = os.path.abspath(os.path.join(BRIEFS_DIR, "empty.html"))
    if os.path.exists(brief_path):
        return send_file(brief_path)
    return send_file(empty_path)


@app.route("/api/generate", methods=["POST"])
def generate():
    print("\n=== Generating new brief ===")
    result = run_pipeline()
    html = render_html(
        stories=result["stories"],
        date_str=result["date"],
        intro=result["intro"],
    )
    save_brief_html(html)
    print(f"=== Brief ready: {result['date']} ===\n")
    return jsonify({"status": "ok", "date": result["date"]})


if __name__ == "__main__":
    print("\n🗞  NewsAggro server")
    print("    http://localhost:8000/")
    print("    Ctrl+C to stop\n")
    app.run(host="127.0.0.1", port=8000, debug=False)
