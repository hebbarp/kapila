#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ಕಪಿಲ (Kapila) Web Playground
Flask backend for running Kapila code in the browser.
"""

import contextlib
import io
import os
import sys
import threading
import time
import uuid

from flask import Flask, jsonify, render_template, request

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.vm import VM, KapilaError

# NL engine is optional (requires piconn + pampa)
try:
    from nl_engine import get_engine
    HAS_NL = True
except ImportError:
    HAS_NL = False

# Support running behind a URL prefix (e.g. /kapila)
PREFIX = os.environ.get("SCRIPT_NAME", "")
app = Flask(__name__)
app.config["APPLICATION_ROOT"] = PREFIX or "/"

MAX_CODE_LENGTH = 5000
EXECUTION_TIMEOUT = 5  # seconds

# ---------------------------------------------------------------------------
# Session-based VM pool for Sandarbha (context-aware) mode
# ---------------------------------------------------------------------------
SESSIONS = {}           # session_id → { "vm": VM, "history": [], "last_used": float }
SESSION_TIMEOUT = 600   # 10 minutes
MAX_SESSIONS = 100


def _cleanup_sessions():
    """Background thread: evict sessions idle longer than SESSION_TIMEOUT."""
    while True:
        time.sleep(60)
        now = time.time()
        expired = [
            sid for sid, s in SESSIONS.items()
            if now - s.get("last_used", 0) > SESSION_TIMEOUT
        ]
        for sid in expired:
            SESSIONS.pop(sid, None)

# ---------------------------------------------------------------------------
# Load example programs at startup
# ---------------------------------------------------------------------------
EXAMPLES = {}
EXAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples")
EXAMPLE_FILES = ["hello.kpl", "basics.kpl", "list_test.kpl", "runtime_test.kpl"]

for fname in EXAMPLE_FILES:
    path = os.path.join(EXAMPLE_DIR, fname)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            EXAMPLES[fname] = f.read()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/examples")
def examples():
    return jsonify(
        [{"name": name, "code": code} for name, code in EXAMPLES.items()]
    )


@app.route("/run", methods=["POST"])
def run_code():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "").strip()

    if not code:
        return jsonify({"output": "", "stack": "[]", "error": "ಖಾಲಿ ಕೋಡ್ (empty code)"})

    if len(code) > MAX_CODE_LENGTH:
        return jsonify({
            "output": "",
            "stack": "[]",
            "error": f"ಕೋಡ್ ತುಂಬಾ ಉದ್ದವಾಗಿದೆ (code too long): {len(code)}/{MAX_CODE_LENGTH} chars",
        })

    # Run in a separate thread with timeout
    result = {"output": "", "stack": "[]", "error": None}

    def execute():
        try:
            vm = VM()
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture):
                vm.run(code)
            result["output"] = capture.getvalue()
            result["stack"] = repr(vm.stack)
        except KapilaError as e:
            result["error"] = str(e)
        except Exception as e:
            result["error"] = str(e)

    thread = threading.Thread(target=execute, daemon=True)
    thread.start()
    thread.join(timeout=EXECUTION_TIMEOUT)

    if thread.is_alive():
        result["error"] = "ಸಮಯ ಮೀರಿದೆ (timeout): execution exceeded 5 seconds"

    return jsonify(result)


@app.route("/nl", methods=["POST"])
def nl_to_code():
    if not HAS_NL:
        return jsonify({"error": "NL engine not available on this server"})

    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "ಖಾಲಿ ಇನ್‌ಪುಟ್ (empty input)"})

    engine = get_engine()
    nl_result = engine.process(text)

    if "error" in nl_result:
        return jsonify(nl_result)

    code = nl_result["code"]

    # Execute the generated code
    exec_result = {"output": "", "stack": "[]", "error": None}

    def execute():
        try:
            vm = VM()
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture):
                vm.run(code)
            exec_result["output"] = capture.getvalue()
            exec_result["stack"] = repr(vm.stack)
        except KapilaError as e:
            exec_result["error"] = str(e)
        except Exception as e:
            exec_result["error"] = str(e)

    thread = threading.Thread(target=execute, daemon=True)
    thread.start()
    thread.join(timeout=EXECUTION_TIMEOUT)

    if thread.is_alive():
        exec_result["error"] = "timeout"

    return jsonify({
        "intent": nl_result["intent"],
        "confidence": nl_result["confidence"],
        "code": nl_result["code"],
        "output": exec_result["output"],
        "stack": exec_result["stack"],
        "error": exec_result["error"],
    })


# ---------------------------------------------------------------------------
# Sandarbha (context-aware) endpoints
# ---------------------------------------------------------------------------
@app.route("/run-sandarbha", methods=["POST"])
def run_sandarbha():
    data = request.get_json(silent=True) or {}
    code = data.get("code", "").strip()
    session_id = data.get("session_id")

    if not code:
        return jsonify({
            "session_id": session_id,
            "output": "",
            "stack": "[]",
            "context": {},
            "error": "ಖಾಲಿ ಕೋಡ್ (empty code)",
        })

    if len(code) > MAX_CODE_LENGTH:
        return jsonify({
            "session_id": session_id,
            "output": "",
            "stack": "[]",
            "context": {},
            "error": f"ಕೋಡ್ ತುಂಬಾ ಉದ್ದವಾಗಿದೆ (code too long): {len(code)}/{MAX_CODE_LENGTH} chars",
        })

    # Get or create session
    if session_id and session_id in SESSIONS:
        session = SESSIONS[session_id]
    else:
        if len(SESSIONS) >= MAX_SESSIONS:
            # Evict oldest session
            oldest = min(SESSIONS, key=lambda s: SESSIONS[s].get("last_used", 0))
            SESSIONS.pop(oldest, None)
        session_id = str(uuid.uuid4())
        session = {"vm": VM(enable_sandarbha=True), "history": []}
        SESSIONS[session_id] = session

    session["last_used"] = time.time()
    vm = session["vm"]

    result = {"output": "", "stack": "[]", "context": {}, "error": None}

    def execute():
        try:
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture):
                vm.run(code)
            result["output"] = capture.getvalue()
            result["stack"] = repr(vm.stack)
            # Build context snapshot
            ctx = vm.sandarbha
            if ctx:
                result["context"] = {
                    role: repr(val) for role, val in ctx._roles.items()
                }
        except KapilaError as e:
            result["error"] = str(e)
        except Exception as e:
            result["error"] = str(e)

    thread = threading.Thread(target=execute, daemon=True)
    thread.start()
    thread.join(timeout=EXECUTION_TIMEOUT)

    if thread.is_alive():
        result["error"] = "ಸಮಯ ಮೀರಿದೆ (timeout): execution exceeded 5 seconds"

    session["history"].append({"code": code, "output": result["output"]})
    result["session_id"] = session_id
    return jsonify(result)


@app.route("/reset-sandarbha", methods=["POST"])
def reset_sandarbha():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    if session_id and session_id in SESSIONS:
        del SESSIONS[session_id]
    return jsonify({"status": "ok"})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if HAS_NL:
        print("Training NL engine...")
        get_engine()
    # Start background session cleanup thread
    _cleanup_thread = threading.Thread(target=_cleanup_sessions, daemon=True)
    _cleanup_thread.start()
    print("Kapila Web Playground: http://127.0.0.1:5000")
    app.run(debug=True, host="127.0.0.1", port=5000)
