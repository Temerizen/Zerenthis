def run_control(state):
    if not isinstance(state, dict):
        state = {}

    state["status"] = "ok"
    return state
