import os
import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from backend.core.router import route
from backend.core.safety import check
from backend.core.ratelimit import allow
from backend.core.queue import enqueue, list_queue, clear_queue
from backend.core.presets import list_presets, get_preset
from backend.core.exports import export_bundle, list_exports
from backend.core.templates import list_templates, get_template
from backend.core.healthcheck import run_checks
from backend.core.backups import make_backup, list_backups
from backend.core.manifest import APP_MANIFEST

from backend.db import (
    init, save_history, get_user_by_username, get_user_by_id, create_user, get_history,
    set_memory, get_memory, create_task, update_task, get_tasks,
    save_artifact, get_artifacts,
    add_knowledge, get_knowledge, search_knowledge,
    set_setting, get_settings,
    add_notification, get_notifications, log_request,
    get_profile, update_profile, get_plan_placeholder,
    admin_stats, admin_users, admin_tasks, admin_artifacts, admin_knowledge, admin_request_logs
)
from backend.auth import hash_password, verify_password, create_token, get_user_id, get_user_role

from backend.agents import (
    general, coding, acting, finance, career, health,
    planner, research, execution, critique,
    brand, content, product, synthesize
)

load_dotenv()

PORT = int(os.getenv("PORT", "5000"))
FOUNDER_USERNAME = os.getenv("FOUNDER_USERNAME", "founder")
FOUNDER_PASSWORD = os.getenv("FOUNDER_PASSWORD", "ChangeMeNow_2026!")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app, resources={r"/*": {"origins": CORS_ORIGINS}})

init()

def ensure_founder():
    existing = get_user_by_username(FOUNDER_USERNAME)
    if not existing:
        create_user(FOUNDER_USERNAME, hash_password(FOUNDER_PASSWORD), "founder")

ensure_founder()

@app.after_request
def after_request(response):
    try:
        uid = get_user_id()
        log_request(uid, request.path, request.method, response.status_code)
    except Exception:
        pass
    return response

def require_auth():
    uid = get_user_id()
    if not uid:
        return None, (jsonify({"error": "auth required"}), 401)
    return uid, None

def require_founder():
    uid = get_user_id()
    role = get_user_role()
    if not uid:
        return None, (jsonify({"error": "auth required"}), 401)
    if role != "founder":
        return None, (jsonify({"error": "founder access required"}), 403)
    return uid, None

def apply_limit(uid, path):
    key = f"{uid}:{path}" if uid else f"anon:{path}:{request.remote_addr}"
    ok, retry_after = allow(key, 40, 60)
    if not ok:
        return jsonify({"error": "rate limit exceeded", "retry_after": retry_after}), 429
    return None

def knowledge_for(uid, msg):
    terms = (msg or "").strip()
    if not terms:
        return []
    return search_knowledge(uid, terms[:120], 6)

def agent_dispatch(agent, msg, memory, knowledge):
    if agent == "coding":
        return coding.run(msg, memory, knowledge)
    if agent == "acting":
        return acting.run(msg, memory, knowledge)
    if agent == "finance":
        return finance.run(msg, memory, knowledge)
    if agent == "career":
        return career.run(msg, memory, knowledge)
    if agent == "health":
        return health.run(msg, memory, knowledge)
    if agent == "planner":
        return planner.run(msg, memory, knowledge)
    if agent == "research":
        return research.run(msg, memory, knowledge)
    if agent == "execution":
        return execution.run(msg, memory, knowledge)
    if agent == "brand":
        return brand.run(msg, memory, knowledge)
    if agent == "content":
        return content.run(msg, memory, knowledge)
    if agent == "product":
        return product.run(msg, memory, knowledge)
    return general.run(msg, memory, knowledge)

def _save_bundle_outputs(uid, title, artifact_type, text, obj):
    outputs = export_bundle(title, text, obj)
    for item in outputs:
        save_artifact(uid, title, artifact_type, item["filename"], item["path"])
    return outputs

def build_snapshot():
    return {
        "manifest": APP_MANIFEST,
        "stats": admin_stats(),
        "settings": get_settings(),
        "queue_depth": len(list_queue()),
        "checks": run_checks()
    }

@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/manifest")
def manifest():
    return jsonify(APP_MANIFEST)

@app.route("/status")
def status():
    return jsonify({"ok": True, "app": "SemantiqAI", "port": PORT, "stage": APP_MANIFEST["stage"]})

@app.route("/healthz")
def healthz():
    return jsonify(run_checks())

@app.route("/diagnostics")
def diagnostics():
    uid, err = require_founder()
    if err:
        return err
    return jsonify(build_snapshot())

@app.route("/snapshot")
def snapshot():
    uid, err = require_founder()
    if err:
        return err
    return jsonify(build_snapshot())

@app.route("/backup", methods=["POST"])
def backup():
    uid, err = require_founder()
    if err:
        return err
    data = make_backup(build_snapshot())
    return jsonify({"ok": True, "backup": data})

@app.route("/backups")
def backups():
    uid, err = require_founder()
    if err:
        return err
    return jsonify({"items": list_backups()})

@app.route("/signup", methods=["POST"])
def signup():
    limiter = apply_limit(None, "/signup")
    if limiter:
        return limiter

    d = request.get_json(silent=True) or {}
    username = (d.get("username") or "").strip()
    password = d.get("password") or ""

    if len(username) < 3 or len(password) < 8:
        return jsonify({"error": "username must be 3+ chars and password 8+ chars"}), 400

    if get_user_by_username(username):
        return jsonify({"error": "user exists"}), 400

    uid = create_user(username, hash_password(password), "user")
    token = create_token(uid, "user")
    add_notification(uid, "Welcome", "Your SemantiqAI account is ready.")
    return jsonify({"token": token, "user": {"id": uid, "username": username, "role": "user"}})

@app.route("/login", methods=["POST"])
def login():
    limiter = apply_limit(None, "/login")
    if limiter:
        return limiter

    d = request.get_json(silent=True) or {}
    username = (d.get("username") or "").strip()
    password = d.get("password") or ""

    user = get_user_by_username(username)
    if not user or not verify_password(password, user["password_hash"]):
        return jsonify({"error": "invalid credentials"}), 401

    token = create_token(user["id"], user["role"])
    return jsonify({
        "token": token,
        "user": {"id": user["id"], "username": user["username"], "role": user["role"]}
    })

@app.route("/me")
def me():
    uid, err = require_auth()
    if err:
        return err
    limiter = apply_limit(uid, "/me")
    if limiter:
        return limiter
    user = get_user_by_id(uid)
    return jsonify({
        "user": dict(user),
        "memory": get_memory(uid),
        "profile": get_profile(uid),
        "plan": get_plan_placeholder(uid)
    })

@app.route("/profile", methods=["GET", "POST"])
def profile():
    uid, err = require_auth()
    if err:
        return err
    limiter = apply_limit(uid, "/profile")
    if limiter:
        return limiter

    if request.method == "GET":
        return jsonify({"profile": get_profile(uid)})

    d = request.get_json(silent=True) or {}
    current = get_profile(uid) or {}
    display_name = (d.get("display_name") or current.get("display_name") or "").strip()
    bio = (d.get("bio") or current.get("bio") or "").strip()
    goals = d.get("goals") if d.get("goals") is not None else json.loads(current.get("goals_json") or "{}")
    onboarding_state = (d.get("onboarding_state") or current.get("onboarding_state") or "new").strip()

    update_profile(uid, display_name, bio, json.dumps(goals, ensure_ascii=False), onboarding_state)
    return jsonify({"ok": True, "profile": get_profile(uid)})

@app.route("/history")
def history():
    uid, err = require_auth()
    if err:
        return err
    limiter = apply_limit(uid, "/history")
    if limiter:
        return limiter
    return jsonify({"items": get_history(uid, 30)})

@app.route("/memory", methods=["GET", "POST"])
def memory():
    uid, err = require_auth()
    if err:
        return err
    limiter = apply_limit(uid, "/memory")
    if limiter:
        return limiter

    if request.method == "GET":
        return jsonify({"memory": get_memory(uid)})

    d = request.get_json(silent=True) or {}
    key = (d.get("key") or "").strip()
    value = d.get("value")
    if not key:
        return jsonify({"error": "key required"}), 400

    set_memory(uid, key, value)
    return jsonify({"ok": True, "memory": get_memory(uid)})

@app.route("/knowledge", methods=["GET", "POST"])
def knowledge():
    uid, err = require_auth()
    if err:
        return err
    limiter = apply_limit(uid, "/knowledge")
    if limiter:
        return limiter

    if request.method == "GET":
        q = (request.args.get("q") or "").strip()
        if q:
            return jsonify({"items": search_knowledge(uid, q, 20)})
        return jsonify({"items": get_knowledge(uid, 100)})

    d = request.get_json(silent=True) or {}
    title = (d.get("title") or "Knowledge Item").strip()
    content = (d.get("content") or "").strip()
    source_type = (d.get("source_type") or "manual").strip()

    if not content:
        return jsonify({"error": "content required"}), 400

    kid = add_knowledge(uid, title, content, source_type)
    return jsonify({"ok": True, "knowledge_id": kid})

@app.route("/notifications")
def notifications():
    uid, err = require_auth()
    if err:
        return err
    limiter = apply_limit(uid, "/notifications")
    if limiter:
        return limiter
    return jsonify({"items": get_notifications(uid, 50)})

@app.route("/templates")
def templates():
    uid, err = require_auth()
    if err:
        return err
    return jsonify({"items": list_templates()})

@app.route("/template/<name>")
def template(name):
    uid, err = require_auth()
    if err:
        return err
    tpl = get_template(name)
    if not tpl:
        return jsonify({"error": "template not found"}), 404
    return jsonify({"name": name, "content": tpl})

@app.route("/chat", methods=["POST"])
def chat():
    uid, err = require_auth()
    if err:
        return err
    limiter = apply_limit(uid, "/chat")
    if limiter:
        return limiter

    d = request.get_json(silent=True) or {}
    msg = (d.get("message") or "").strip()

    if not msg:
        return jsonify({"error": "message required"}), 400

    if check(msg):
        return jsonify({"agent": "safety", "response": "Blocked for safety."}), 200

    memory = get_memory(uid)
    knowledge = knowledge_for(uid, msg)
    agent = route(msg)
    res = agent_dispatch(agent, msg, memory, knowledge)

    save_history(uid, agent, msg, res)
    return jsonify({"agent": agent, "response": res, "knowledge_hits": len(knowledge)})

@app.route("/plan", methods=["POST"])
def plan():
    uid, err = require_auth()
    if err:
        return err
    limiter = apply_limit(uid, "/plan")
    if limiter:
        return limiter

    d = request.get_json(silent=True) or {}
    msg = (d.get("message") or "").strip()
    if not msg:
        return jsonify({"error": "message required"}), 400

    memory = get_memory(uid)
    knowledge = knowledge_for(uid, msg)
    output = planner.run(msg, memory, knowledge)
    set_memory(uid, "last_plan", output)
    save_history(uid, "planner", msg, output)
    return jsonify({"plan": output})

@app.route("/research", methods=["POST"])
def research_route():
    uid, err = require_auth()
    if err:
        return err
    limiter = apply_limit(uid, "/research")
    if limiter:
        return limiter

    d = request.get_json(silent=True) or {}
    msg = (d.get("message") or "").strip()
    if not msg:
        return jsonify({"error": "message required"}), 400

    memory = get_memory(uid)
    knowledge = knowledge_for(uid, msg)
    output = research.run(msg, memory, knowledge)
    set_memory(uid, "last_research", output)
    save_history(uid, "research", msg, output)
    return jsonify({"research": output})

@app.route("/execute", methods=["POST"])
def execute_route():
    uid, err = require_auth()
    if err:
        return err
    limiter = apply_limit(uid, "/execute")
    if limiter:
        return limiter

    d = request.get_json(silent=True) or {}
    msg = (d.get("message") or "").strip()
    if not msg:
        return jsonify({"error": "message required"}), 400

    memory = get_memory(uid)
    knowledge = knowledge_for(uid, msg)
    output = execution.run(msg, memory, knowledge)
    set_memory(uid, "last_execution", output)
    save_history(uid, "execution", msg, output)
    return jsonify({"result": output})

@app.route("/workflow", methods=["POST"])
def workflow():
    uid, err = require_auth()
    if err:
        return err
    limiter = apply_limit(uid, "/workflow")
    if limiter:
        return limiter

    d = request.get_json(silent=True) or {}
    msg = (d.get("message") or "").strip()
    if not msg:
        return jsonify({"error": "message required"}), 400

    memory = get_memory(uid)
    knowledge = knowledge_for(uid, msg)

    queue_item = enqueue("workflow", {"user_id": uid, "message": msg})
    task_id = create_task(uid, "Workflow", "workflow", "running", msg, {"stage": "starting", "queue_id": queue_item["queue_id"]})

    plan_out = planner.run(msg, memory, knowledge)
    research_out = research.run(plan_out, memory, knowledge)
    execution_out = execution.run(
        f"Original request:\n{msg}\n\nPlan:\n{plan_out}\n\nResearch:\n{research_out}",
        memory, knowledge
    )
    critique_out = critique.run(
        f"Original request:\n{msg}\n\nPlan:\n{plan_out}\n\nResearch:\n{research_out}\n\nExecution:\n{execution_out}",
        memory, knowledge
    )
    final_text = synthesize.run(
        f"Original request:\n{msg}\n\nPlan:\n{plan_out}\n\nResearch:\n{research_out}\n\nExecution:\n{execution_out}\n\nCritique:\n{critique_out}",
        memory, knowledge
    )

    final = {
        "queue": queue_item,
        "plan": plan_out,
        "research": research_out,
        "execution": execution_out,
        "critique": critique_out,
        "final": final_text
    }

    update_task(task_id, "completed", final)
    set_memory(uid, "last_workflow", final)
    save_history(uid, "workflow", msg, final_text)
    add_notification(uid, "Workflow Complete", "Your workflow finished successfully.")

    return jsonify(final)

@app.route("/workflow/presets")
def workflow_presets():
    uid, err = require_auth()
    if err:
        return err
    return jsonify({"items": list_presets()})

@app.route("/workflow/preset/<name>", methods=["POST"])
def workflow_preset_run(name):
    uid, err = require_auth()
    if err:
        return err
    limiter = apply_limit(uid, "/workflow/preset")
    if limiter:
        return limiter

    preset = get_preset(name)
    if not preset:
        return jsonify({"error": "preset not found"}), 404

    d = request.get_json(silent=True) or {}
    msg = (d.get("message") or "").strip()
    if not msg:
        return jsonify({"error": "message required"}), 400

    memory = get_memory(uid)
    knowledge = knowledge_for(uid, msg)
    title = preset["title"]

    queue_item = enqueue("preset_workflow", {"user_id": uid, "preset": name, "message": msg})
    task_id = create_task(uid, title, "preset_workflow", "running", msg, {"preset": name, "queue_id": queue_item["queue_id"]})

    if name == "product_blueprint":
        plan_out = planner.run("Build a product blueprint for: " + msg, memory, knowledge)
        product_out = product.run("Create a product structure and offer for: " + msg, memory, knowledge)
        critique_out = critique.run(plan_out + "\n\n" + product_out, memory, knowledge)
        final_text = synthesize.run(plan_out + "\n\n" + product_out + "\n\n" + critique_out, memory, knowledge)
        final = {"preset": name, "plan": plan_out, "product": product_out, "critique": critique_out, "final": final_text, "queue": queue_item}
    elif name == "content_pack":
        plan_out = planner.run("Build a content system for: " + msg, memory, knowledge)
        content_out = content.run("Create a content pack for: " + msg, memory, knowledge)
        critique_out = critique.run(plan_out + "\n\n" + content_out, memory, knowledge)
        final_text = synthesize.run(plan_out + "\n\n" + content_out + "\n\n" + critique_out, memory, knowledge)
        final = {"preset": name, "plan": plan_out, "content": content_out, "critique": critique_out, "final": final_text, "queue": queue_item}
    elif name == "brand_strategy":
        plan_out = planner.run("Build a brand strategy for: " + msg, memory, knowledge)
        brand_out = brand.run("Create a brand strategy for: " + msg, memory, knowledge)
        critique_out = critique.run(plan_out + "\n\n" + brand_out, memory, knowledge)
        final_text = synthesize.run(plan_out + "\n\n" + brand_out + "\n\n" + critique_out, memory, knowledge)
        final = {"preset": name, "plan": plan_out, "brand": brand_out, "critique": critique_out, "final": final_text, "queue": queue_item}
    elif name == "research_brief":
        plan_out = planner.run("Build a research brief plan for: " + msg, memory, knowledge)
        research_out = research.run("Research and analyze: " + msg, memory, knowledge)
        critique_out = critique.run(plan_out + "\n\n" + research_out, memory, knowledge)
        final_text = synthesize.run(plan_out + "\n\n" + research_out + "\n\n" + critique_out, memory, knowledge)
        final = {"preset": name, "plan": plan_out, "research": research_out, "critique": critique_out, "final": final_text, "queue": queue_item}
    else:
        plan_out = planner.run("Create a founder operating system for: " + msg, memory, knowledge)
        brand_out = brand.run("Clarify brand and direction for: " + msg, memory, knowledge)
        execution_out = execution.run("Create execution systems for: " + msg, memory, knowledge)
        critique_out = critique.run(plan_out + "\n\n" + brand_out + "\n\n" + execution_out, memory, knowledge)
        final_text = synthesize.run(plan_out + "\n\n" + brand_out + "\n\n" + execution_out + "\n\n" + critique_out, memory, knowledge)
        final = {"preset": name, "plan": plan_out, "brand": brand_out, "execution": execution_out, "critique": critique_out, "final": final_text, "queue": queue_item}

    update_task(task_id, "completed", final)
    set_memory(uid, "last_preset_" + name, final)
    save_history(uid, "preset_" + name, msg, final["final"])
    add_notification(uid, "Preset Complete", title + " is ready.")
    return jsonify(final)

@app.route("/artifact/generate", methods=["POST"])
def artifact_generate():
    uid, err = require_auth()
    if err:
        return err
    limiter = apply_limit(uid, "/artifact/generate")
    if limiter:
        return limiter

    d = request.get_json(silent=True) or {}
    title = (d.get("title") or "Artifact").strip()
    content_text = (d.get("content") or "").strip()
    if not content_text:
        return jsonify({"error": "content required"}), 400

    artifact_type = (d.get("artifact_type") or "manual_export").strip()
    outputs = _save_bundle_outputs(uid, title, artifact_type, content_text, {"title": title, "content": content_text})
    return jsonify({"title": title, "outputs": outputs})

@app.route("/artifact/generate-from-workflow", methods=["POST"])
def artifact_generate_from_workflow():
    uid, err = require_auth()
    if err:
        return err
    limiter = apply_limit(uid, "/artifact/generate-from-workflow")
    if limiter:
        return limiter

    d = request.get_json(silent=True) or {}
    msg = (d.get("message") or "").strip()
    title = (d.get("title") or "Workflow Artifact").strip()

    if not msg:
        return jsonify({"error": "message required"}), 400

    memory = get_memory(uid)
    knowledge = knowledge_for(uid, msg)

    plan_out = planner.run(msg, memory, knowledge)
    research_out = research.run(plan_out, memory, knowledge)
    execution_out = execution.run(msg + "\n\n" + plan_out + "\n\n" + research_out, memory, knowledge)
    critique_out = critique.run(plan_out + "\n\n" + research_out + "\n\n" + execution_out, memory, knowledge)
    final_text = synthesize.run(plan_out + "\n\n" + research_out + "\n\n" + execution_out + "\n\n" + critique_out, memory, knowledge)

    final = {
        "plan": plan_out,
        "research": research_out,
        "execution": execution_out,
        "critique": critique_out,
        "final": final_text
    }

    outputs = _save_bundle_outputs(uid, title, "workflow_export", final_text, final)
    save_history(uid, "artifact_workflow", msg, final_text)
    return jsonify({"title": title, "workflow": final, "outputs": outputs})

@app.route("/artifacts")
def artifacts():
    uid, err = require_auth()
    if err:
        return err
    return jsonify({"items": get_artifacts(uid, 100)})

@app.route("/exports")
def exports():
    uid, err = require_auth()
    if err:
        return err
    return jsonify({"items": list_exports()})

@app.route("/tasks")
def tasks():
    uid, err = require_auth()
    if err:
        return err
    return jsonify({"items": get_tasks(uid, 25)})

@app.route("/queue")
def queue_items():
    uid, err = require_founder()
    if err:
        return err
    return jsonify({"items": list_queue()})

@app.route("/queue/clear", methods=["POST"])
def queue_clear():
    uid, err = require_founder()
    if err:
        return err
    clear_queue()
    return jsonify({"ok": True})

@app.route("/settings", methods=["GET", "POST"])
def settings():
    uid, err = require_founder()
    if err:
        return err

    if request.method == "GET":
        return jsonify({"items": get_settings()})

    d = request.get_json(silent=True) or {}
    key = (d.get("key") or "").strip()
    value = d.get("value")
    if not key:
        return jsonify({"error": "key required"}), 400
    set_setting(key, value)
    return jsonify({"ok": True, "items": get_settings()})

@app.route("/launch-checklist")
def launch_checklist():
    uid, err = require_founder()
    if err:
        return err

    checks = run_checks()
    stats = admin_stats()

    items = [
        {"item": "env_configured", "ok": checks.get("env_ok", False)},
        {"item": "users_table_ready", "ok": stats.get("users", 0) >= 1},
        {"item": "artifacts_ready", "ok": True},
        {"item": "knowledge_ready", "ok": True},
        {"item": "queue_ready", "ok": True},
        {"item": "payments_ready", "ok": False},
        {"item": "public_launch_ready", "ok": False}
    ]
    return jsonify({"items": items})

@app.route("/admin/stats")
def founder_stats():
    uid, err = require_founder()
    if err:
        return err
    return jsonify(admin_stats())

@app.route("/admin/users")
def founder_users():
    uid, err = require_founder()
    if err:
        return err
    return jsonify({"items": admin_users(100)})

@app.route("/admin/tasks")
def founder_tasks():
    uid, err = require_founder()
    if err:
        return err
    return jsonify({"items": admin_tasks(100)})

@app.route("/admin/artifacts")
def founder_artifacts():
    uid, err = require_founder()
    if err:
        return err
    return jsonify({"items": admin_artifacts(200)})

@app.route("/admin/knowledge")
def founder_knowledge():
    uid, err = require_founder()
    if err:
        return err
    return jsonify({"items": admin_knowledge(200)})

@app.route("/admin/request-logs")
def founder_request_logs():
    uid, err = require_founder()
    if err:
        return err
    return jsonify({"items": admin_request_logs(200)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)


