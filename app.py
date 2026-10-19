"""
DevOpsHub - Developer Tools. Simplified.
TechNova Cloud Computing Internship Task 4: Docker Containerization
A production-minded, container-ready Python Flask web application.
"""

import os
import sys
import json
import platform
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template

# Initialize Flask application
app = Flask(__name__)

# Application Constants
APP_NAME = "DevOpsHub"
APP_TAGLINE = "Developer Tools. Simplified."
APP_VERSION = "1.0.0"
APP_DESCRIPTION = (
    "A modern developer utility dashboard built with Flask, Docker, and Gunicorn. "
    "Designed for TechNova Cloud Computing Internship Task 4."
)

# Configuration
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2MB request payload limit
app.config["JSON_SORT_KEYS"] = False

# Track process start time for uptime tracking
PROCESS_START_TIME = datetime.now(timezone.utc)


def is_running_in_docker() -> bool:
    """
    Accurately detects whether the application is running inside a Docker container.
    Checks for the standard /.dockerenv indicator, /run/.containerenv,
    and inspects /proc/1/cgroup without false positives or fabricated metrics.
    """
    if os.path.exists("/.dockerenv") or os.path.exists("/run/.containerenv"):
        return True
    try:
        if os.path.exists("/proc/1/cgroup"):
            with open("/proc/1/cgroup", "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                return any(marker in content for marker in ["docker", "containerd", "kubepods"])
    except Exception:
        pass
    return False


def get_system_info() -> dict:
    """Collects runtime and deployment details."""
    now = datetime.now(timezone.utc)
    uptime_seconds = int((now - PROCESS_START_TIME).total_seconds())
    is_docker = is_running_in_docker()

    return {
        "app_name": APP_NAME,
        "tagline": APP_TAGLINE,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "system": platform.system(),
        "hostname": platform.node(),
        "containerized": is_docker,
        "deployment_environment": "Docker Container (Linux)" if is_docker else f"Host System ({platform.system()})",
        "utc_time": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "utc_time_iso": now.isoformat(),
        "uptime_seconds": uptime_seconds,
        "wsgi_server": "Gunicorn" if "gunicorn" in sys.modules else "Flask Development Server"
    }


# ----------------------------------------------------------------------
# Frontend Views
# ----------------------------------------------------------------------

@app.route("/", methods=["GET"])
def index():
    """Render the main DevOpsHub developer dashboard."""
    sys_info = get_system_info()
    return render_template("index.html", info=sys_info)


# ----------------------------------------------------------------------
# REST API Endpoints
# ----------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def api_health():
    """
    GET /api/health
    Returns application health status, uptime, and current server time.
    """
    now = datetime.now(timezone.utc)
    uptime = int((now - PROCESS_START_TIME).total_seconds())
    return jsonify({
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
        "uptime_seconds": uptime,
        "timestamp": now.isoformat()
    }), 200


@app.route("/api/info", methods=["GET"])
def api_info():
    """
    GET /api/info
    Returns application metadata, runtime specifications, and registered endpoints.
    """
    sys_info = get_system_info()
    endpoints = [
        {"endpoint": "/", "method": "GET", "description": "DevOpsHub Web Dashboard"},
        {"endpoint": "/api/health", "method": "GET", "description": "Application health check and uptime"},
        {"endpoint": "/api/info", "method": "GET", "description": "Application metadata and runtime info"},
        {"endpoint": "/api/text/analyze", "method": "POST", "description": "Calculate text metrics (words, chars, lines)"},
        {"endpoint": "/api/json/validate", "method": "POST", "description": "Validate and format JSON payloads"}
    ]
    return jsonify({
        **sys_info,
        "available_endpoints": endpoints
    }), 200


@app.route("/api/text/analyze", methods=["POST"])
def api_text_analyze():
    """
    POST /api/text/analyze
    Accepts JSON payload: {"text": "<string content>"}
    Returns character count, word count, line count, and byte size.
    """
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Invalid Content-Type. Request body must be JSON."
        }), 400

    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Malformed JSON payload. Expected a JSON object."
        }), 400

    if "text" not in data:
        return jsonify({
            "success": False,
            "error": "Missing required field: 'text'."
        }), 400

    text_value = data["text"]
    if not isinstance(text_value, str):
        return jsonify({
            "success": False,
            "error": "Field 'text' must be a string."
        }), 400

    # Calculate metrics
    char_count = len(text_value)
    char_no_spaces = len(text_value.replace(" ", "").replace("\t", "").replace("\n", "").replace("\r", ""))
    words = text_value.split()
    word_count = len(words)
    lines = text_value.splitlines()
    line_count = len(lines) if text_value else 0
    paragraphs = [p for p in text_value.split("\n\n") if p.strip()]
    paragraph_count = len(paragraphs) if text_value else 0
    byte_size = len(text_value.encode("utf-8"))

    return jsonify({
        "success": True,
        "metrics": {
            "character_count": char_count,
            "character_count_no_spaces": char_no_spaces,
            "word_count": word_count,
            "line_count": line_count,
            "paragraph_count": paragraph_count,
            "byte_size": byte_size
        }
    }), 200


@app.route("/api/json/validate", methods=["POST"])
def api_json_validate():
    """
    POST /api/json/validate
    Accepts JSON input to validate and format.
    Payload formats supported:
      1. {"json_string": "{\"key\": \"val\"}", "indent": 2}
      2. {"data": {...}, "indent": 2}
      3. Raw string containing valid or invalid JSON
    """
    indent_size = 2
    raw_input_string = None

    if request.is_json:
        body = request.get_json(silent=True)
        if body is None:
            return jsonify({
                "valid": False,
                "error": "Malformed JSON in request body."
            }), 400

        if isinstance(body, dict):
            # Check for custom indent
            if "indent" in body and isinstance(body["indent"], int) and 1 <= body["indent"] <= 8:
                indent_size = body["indent"]

            if "json_string" in body:
                if not isinstance(body["json_string"], str):
                    return jsonify({
                        "valid": False,
                        "error": "Field 'json_string' must be a string."
                    }), 400
                raw_input_string = body["json_string"]
            elif "data" in body:
                # Direct JSON data provided
                try:
                    formatted = json.dumps(body["data"], indent=indent_size)
                    return jsonify({
                        "valid": True,
                        "formatted": formatted,
                        "type": type(body["data"]).__name__,
                        "size_bytes": len(formatted.encode("utf-8"))
                    }), 200
                except (TypeError, ValueError) as e:
                    return jsonify({
                        "valid": False,
                        "error": str(e)
                    }), 400
            else:
                return jsonify({
                    "valid": False,
                    "error": "JSON object must contain either 'json_string' or 'data' field."
                }), 400
        else:
            raw_input_string = json.dumps(body)
    else:
        # Fallback to plain text or raw data
        raw_text = request.get_data(as_text=True)
        if not raw_text or not raw_text.strip():
            return jsonify({
                "valid": False,
                "error": "Empty request body. Please provide JSON to validate."
            }), 400
        raw_input_string = raw_text

    # Parse and validate the raw input string
    if not raw_input_string.strip():
        return jsonify({
            "valid": False,
            "error": "Input JSON string is empty."
        }), 400

    try:
        parsed_data = json.loads(raw_input_string)
        formatted_str = json.dumps(parsed_data, indent=indent_size)
        data_type = type(parsed_data).__name__
        item_count = len(parsed_data) if isinstance(parsed_data, (dict, list)) else 1

        return jsonify({
            "valid": True,
            "formatted": formatted_str,
            "type": data_type,
            "item_count": item_count,
            "size_bytes": len(formatted_str.encode("utf-8"))
        }), 200

    except json.JSONDecodeError as err:
        return jsonify({
            "valid": False,
            "error": err.msg,
            "line": err.lineno,
            "column": err.colno,
            "char_pos": err.pos,
            "message": f"Syntax error at line {err.lineno}, column {err.colno}: {err.msg}"
        }), 400


# ----------------------------------------------------------------------
# Error Handlers & Security Headers
# ----------------------------------------------------------------------

@app.errorhandler(400)
def bad_request(error):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Bad Request", "message": str(error)}), 400
    return render_template("index.html", info=get_system_info(), error_alert="400 Bad Request"), 400


@app.errorhandler(404)
def not_found(error):
    if request.path.startswith("/api/"):
        return jsonify({
            "success": False,
            "error": "Not Found",
            "message": f"Endpoint '{request.path}' does not exist on this server."
        }), 404
    return render_template("index.html", info=get_system_info(), error_alert="404 Not Found"), 404


@app.errorhandler(405)
def method_not_allowed(error):
    if request.path.startswith("/api/"):
        return jsonify({
            "success": False,
            "error": "Method Not Allowed",
            "message": f"Method {request.method} is not permitted for '{request.path}'."
        }), 405
    return render_template("index.html", info=get_system_info(), error_alert="405 Method Not Allowed"), 405


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        "success": False,
        "error": "Payload Too Large",
        "message": "The uploaded payload exceeds the maximum permitted limit of 2MB."
    }), 413


@app.errorhandler(500)
def internal_server_error(error):
    if request.path.startswith("/api/"):
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "message": "An unexpected server error occurred."
        }), 500
    return render_template("index.html", info=get_system_info(), error_alert="500 Internal Server Error"), 500


@app.after_request
def apply_security_headers(response):
    """Inject standard security headers on all responses."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    print(f"Starting {APP_NAME} v{APP_VERSION} on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
