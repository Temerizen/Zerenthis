import json, os, time

BRIDGE_PATH = "backend/data/builder_bridge.json"
IMPROVE_PATH = "backend/data/self_improvement.json"

def _safe_load(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def _safe_save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _map_component_to_target(component):
    mapping = {
        "directive": "backend/app/cognition/autonomous_mission_engine.py",
        "memory_reasoning": "backend/app/cognition/memory_depth_engine.py",
        "strategy": "backend/app/cognition/strategic_adjustment_engine.py",
        "reasoning": "backend/app/cognition/reasoning_engine.py",
        "coherence": "backend/app/cognition/coherence_engine.py",
        "mission_continuity": "backend/app/cognition/mission.py",
        "performance": "backend/app/cognition/adaptation.py",
        "completion": "backend/app/cognition/goals.py",
        "builder_bridge": "backend/app/main.py"
    }
    return mapping.get(component, "backend/app/main.py")

def run():
    bridge = _safe_load(BRIDGE_PATH, {"last_bridge": None, "history": []})
    improve = _safe_load(IMPROVE_PATH, {"last_proposal": None, "history": []})

    proposal = improve.get("last_proposal")

    if not proposal:
        return {
            "status": "no_proposal_available"
        }

    if proposal.get("approved") is False:
        # Still not approved — create plan but do not apply
        target_file = _map_component_to_target(proposal.get("component"))

        patch_plan = {
            "timestamp": time.time(),
            "status": "plan_created",
            "component": proposal.get("component"),
            "target_file": target_file,
            "reason": proposal.get("reason"),
            "proposal": proposal.get("proposal"),
            "safe_mode": True,
            "ready_for_builder": True,
            "applied": False
        }

        bridge["last_bridge"] = patch_plan
        bridge["history"].append(patch_plan)
        bridge["history"] = bridge["history"][-50:]
        _safe_save(BRIDGE_PATH, bridge)

        return {
            "status": "builder_plan_ready",
            "plan": patch_plan
        }

    return {
        "status": "proposal_already_approved_waiting_builder"
    }
