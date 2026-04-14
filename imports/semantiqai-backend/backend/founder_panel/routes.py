import os
from flask import Blueprint, request, jsonify

from .engine import initialize_registry, panel_snapshot
from .toggles import get_toggles, set_toggle, set_maintenance_mode, set_system_mode
from .notes import get_notes, set_notes
from .controls import founder_overview, register_manual_action
from .founder_tools import founder_command_pack

founder_panel = Blueprint("founder_panel", __name__)
FOUNDER_KEY = os.getenv("FOUNDER_KEY", "Ascension_Overlord_777")

def is_founder(req):
    return req.headers.get("x-founder-key") == FOUNDER_KEY

@founder_panel.route("/founder/panel/init", methods=["POST"])
def init_panel():
    if not is_founder(request):
        return jsonify({"error": "unauthorized"}), 403
    return jsonify(initialize_registry())

@founder_panel.route("/founder/panel/overview", methods=["GET"])
def overview():
    if not is_founder(request):
        return jsonify({"error": "unauthorized"}), 403
    return jsonify(founder_overview())

@founder_panel.route("/founder/panel/snapshot", methods=["GET"])
def snapshot():
    if not is_founder(request):
        return jsonify({"error": "unauthorized"}), 403
    return jsonify(panel_snapshot())

@founder_panel.route("/founder/panel/toggles", methods=["GET"])
def toggles():
    if not is_founder(request):
        return jsonify({"error": "unauthorized"}), 403
    return jsonify(get_toggles())

@founder_panel.route("/founder/panel/toggle", methods=["POST"])
def toggle():
    if not is_founder(request):
        return jsonify({"error": "unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    value = bool(data.get("value"))

    if not name:
        return jsonify({"error": "name is required"}), 400

    return jsonify(set_toggle(name, value))

@founder_panel.route("/founder/panel/mode", methods=["POST"])
def mode():
    if not is_founder(request):
        return jsonify({"error": "unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    mode = (data.get("mode") or "ascension").strip()
    return jsonify(set_system_mode(mode))

@founder_panel.route("/founder/panel/maintenance", methods=["POST"])
def maintenance():
    if not is_founder(request):
        return jsonify({"error": "unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    value = bool(data.get("value"))
    return jsonify(set_maintenance_mode(value))

@founder_panel.route("/founder/panel/notes", methods=["GET"])
def notes_get():
    if not is_founder(request):
        return jsonify({"error": "unauthorized"}), 403
    return jsonify(get_notes())

@founder_panel.route("/founder/panel/notes", methods=["POST"])
def notes_set():
    if not is_founder(request):
        return jsonify({"error": "unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    text = data.get("text") or ""
    return jsonify(set_notes(text))

@founder_panel.route("/founder/panel/log", methods=["POST"])
def log_action():
    if not is_founder(request):
        return jsonify({"error": "unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    action = (data.get("action") or "manual_action").strip()
    metadata = data.get("metadata") or {}
    return jsonify(register_manual_action(action, metadata))

@founder_panel.route("/founder/panel/command-pack", methods=["POST"])
def command_pack():
    if not is_founder(request):
        return jsonify({"error": "unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    objective = (data.get("objective") or "").strip()

    if not objective:
        return jsonify({"error": "objective is required"}), 400

    return jsonify({
        "objective": objective,
        "command_pack": founder_command_pack(objective)
    })
