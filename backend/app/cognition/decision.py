def run(context=None):
    context = context or {}

    intent = context.get("intent_state", {}).get("intent")

    if intent == "expand_behavior":
        return {
            "status": "decision_made",
            "mode": "agent_expand",
            "action": "branch_and_explore",
            "rationale": ["intent_expand_behavior"]
        }

    if intent == "break_loop":
        return {
            "status": "decision_made",
            "mode": "agent_interrupt",
            "action": "force_new_strategy",
            "rationale": ["intent_break_loop"]
        }

    if intent == "escape_loop":
        return {
            "status": "decision_made",
            "mode": "agent_escape",
            "action": "abandon_current_path",
            "rationale": ["intent_escape_loop"]
        }

    if intent == "optimize":
        return {
            "status": "decision_made",
            "mode": "agent_optimize",
            "action": "refine_current_strategy",
            "rationale": ["intent_optimize"]
        }

    return {
        "status": "decision_made",
        "mode": "agent_explore",
        "action": "probe_new_paths",
        "rationale": ["intent_default"]
    }
