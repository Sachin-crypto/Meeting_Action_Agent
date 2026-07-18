from flask import Flask, jsonify, render_template, request

import config
from jira_agent import file_jira_tickets
from llm_reasoner import reason_over_transcript
from notion_agent import write_notion_summary
from scalekit_setup import get_connection_status
from zoom_agent import fetch_latest_transcript

app = Flask(__name__)

CONNECTOR_NAMES = {
    "zoom": config.ZOOM_CONNECTION_NAME,
    "notion": config.NOTION_CONNECTION_NAME,
    "jira": config.JIRA_CONNECTION_NAME,
}


def _error(message: str, status: int = 400):
    return jsonify({"ok": False, "error": message}), status


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/connectors/status", methods=["POST"])
def connectors_status():
    identifier = (request.json or {}).get("identifier", "").strip()
    if not identifier:
        return _error("identifier is required")

    result = {}
    for key, connection_name in CONNECTOR_NAMES.items():
        try:
            result[key] = get_connection_status(connection_name, identifier)
        except Exception as exc:  # surface per-connector errors, don't kill the whole call
            result[key] = {"connected": False, "status": "ERROR", "error": str(exc)}

    return jsonify({"ok": True, "identifier": identifier, "connectors": result})


@app.route("/api/connect", methods=["POST"])
def connect():
    body = request.json or {}
    identifier = body.get("identifier", "").strip()
    connector = body.get("connector", "").strip()

    if not identifier or connector not in CONNECTOR_NAMES:
        return _error("identifier and a valid connector are required")

    try:
        status = get_connection_status(CONNECTOR_NAMES[connector], identifier)
        return jsonify({"ok": True, **status})
    except Exception as exc:
        return _error(str(exc), status=500)


@app.route("/api/pipeline/transcript", methods=["POST"])
def pipeline_transcript():
    identifier = (request.json or {}).get("identifier", "").strip()
    if not identifier:
        return _error("identifier is required")

    try:
        transcript = fetch_latest_transcript(identifier)
        return jsonify({"ok": True, "transcript": transcript})
    except Exception as exc:
        return _error(str(exc), status=500)


@app.route("/api/pipeline/reason", methods=["POST"])
def pipeline_reason():
    transcript = (request.json or {}).get("transcript", "")
    if not transcript:
        return _error("transcript is required")

    try:
        structured = reason_over_transcript(transcript)
        return jsonify({"ok": True, "structured": structured})
    except Exception as exc:
        return _error(str(exc), status=500)


@app.route("/api/pipeline/notion", methods=["POST"])
def pipeline_notion():
    body = request.json or {}
    identifier = body.get("identifier", "").strip()
    structured = body.get("structured")

    if not identifier or not structured:
        return _error("identifier and structured are required")

    try:
        result = write_notion_summary(identifier, structured)
        return jsonify({"ok": True, "result": result})
    except Exception as exc:
        return _error(str(exc), status=500)


@app.route("/api/pipeline/jira", methods=["POST"])
def pipeline_jira():
    body = request.json or {}
    identifier = body.get("identifier", "").strip()
    action_items = body.get("action_items", [])

    if not identifier:
        return _error("identifier is required")

    try:
        tickets = file_jira_tickets(identifier, action_items)
        return jsonify({"ok": True, "tickets": tickets})
    except Exception as exc:
        return _error(str(exc), status=500)


@app.route("/api/pipeline/run-all", methods=["POST"])
def pipeline_run_all():
    identifier = (request.json or {}).get("identifier", "").strip()
    if not identifier:
        return _error("identifier is required")

    try:
        transcript = fetch_latest_transcript(identifier)
        structured = reason_over_transcript(transcript)
        notion_result = write_notion_summary(identifier, structured)
        tickets = file_jira_tickets(identifier, structured["action_items"])

        return jsonify({
            "ok": True,
            "identifier": identifier,
            "transcript": transcript,
            "structured": structured,
            "notion_result": notion_result,
            "tickets": tickets,
        })
    except Exception as exc:
        return _error(str(exc), status=500)


if __name__ == "__main__":
    app.run(debug=True, port=5000)