from flask import Blueprint, jsonify, request
from backend.services.orchestrator import run_prompt
from backend.memory.short_term import recall, clear_memory
from backend.memory.long_term import recall_long_term

ai_bp = Blueprint("ai", __name__)

@ai_bp.post("/ai/run")
def ai_run():
    payload = request.get_json(silent=True) or {}
    prompt = (payload.get("prompt") or "").strip()
    force_agent = payload.get("agent")

    if not prompt:
        return jsonify({"ok": False, "error": "Prompt is required"}), 400

    result = run_prompt(prompt=prompt, force_agent=force_agent, remember_output=True)
    return jsonify({"ok": True, "result": result})

@ai_bp.get("/ai/agents")
def ai_agents():
    return jsonify({
        "ok": True,
        "agents": ["learning", "business", "coding", "cognitive", "strategy"]
    })

@ai_bp.get("/ai/memory/short")
def ai_memory_short():
    return jsonify({
        "ok": True,
        "items": recall(limit=20)
    })

@ai_bp.get("/ai/memory/long")
def ai_memory_long():
    return jsonify({
        "ok": True,
        "items": recall_long_term(limit=20)
    })

@ai_bp.post("/ai/memory/clear")
def ai_memory_clear():
    clear_memory()
    return jsonify({
        "ok": True,
        "message": "Short term memory cleared"
    })
