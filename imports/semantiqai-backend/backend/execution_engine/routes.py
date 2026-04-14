import os
from flask import Blueprint, request, jsonify

from .engine import (
    create_goal_plan,
    add_user_task,
    finish_task,
    add_user_habit,
    finish_habit,
    create_user_workflow,
    execute_workflow
)
from .founder_tools import founder_execution_strategy

execution_engine = Blueprint("execution_engine", __name__)
FOUNDER_KEY = os.getenv("FOUNDER_KEY", "Ascension_Overlord_777")

def is_founder(req):
    return req.headers.get("x-founder-key") == FOUNDER_KEY

@execution_engine.route("/execute/plan", methods=["POST"])
def plan():
    data = request.get_json(silent=True) or {}
    goal = (data.get("goal") or "").strip()
    if not goal:
        return jsonify({"ok": False, "error": "goal required"}), 400
    return jsonify({"ok": True, "data": create_goal_plan(goal)})

@execution_engine.route("/execute/task/add", methods=["POST"])
def add():
    data = request.get_json(silent=True) or {}
    user_id = (data.get("user_id") or "default").strip()
    task = (data.get("task") or "").strip()
    if not task:
        return jsonify({"ok": False, "error": "task required"}), 400
    return jsonify({"ok": True, "data": add_user_task(user_id, task)})

@execution_engine.route("/execute/task/complete", methods=["POST"])
def complete():
    data = request.get_json(silent=True) or {}
    user_id = (data.get("user_id") or "default").strip()
    index = int(data.get("index") or 0)
    return jsonify({"ok": True, "data": finish_task(user_id, index)})

@execution_engine.route("/execute/habit/add", methods=["POST"])
def habit_add():
    data = request.get_json(silent=True) or {}
    user_id = (data.get("user_id") or "default").strip()
    habit = (data.get("habit") or "").strip()
    if not habit:
        return jsonify({"ok": False, "error": "habit required"}), 400
    return jsonify({"ok": True, "data": add_user_habit(user_id, habit)})

@execution_engine.route("/execute/habit/complete", methods=["POST"])
def habit_complete():
    data = request.get_json(silent=True) or {}
    user_id = (data.get("user_id") or "default").strip()
    index = int(data.get("index") or 0)
    return jsonify({"ok": True, "data": finish_habit(user_id, index)})

@execution_engine.route("/execute/workflow/create", methods=["POST"])
def workflow_create():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "workflow").strip()
    steps = data.get("steps") or []
    if not isinstance(steps, list):
        steps = []
    return jsonify({"ok": True, "data": create_user_workflow(name, steps)})

@execution_engine.route("/execute/workflow/run", methods=["POST"])
def workflow_run():
    data = request.get_json(silent=True) or {}
    workflow = data.get("workflow") or {}
    return jsonify({"ok": True, "data": execute_workflow(workflow)})

@execution_engine.route("/founder/execution", methods=["POST"])
def founder():
    if not is_founder(request):
        return jsonify({"ok": False, "error": "unauthorized"}), 403

    data = request.get_json(silent=True) or {}
    goal = (data.get("goal") or "").strip()
    if not goal:
        return jsonify({"ok": False, "error": "goal required"}), 400
    return jsonify({"ok": True, "data": founder_execution_strategy(goal)})
