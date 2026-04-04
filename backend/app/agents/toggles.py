from .storage import get_state, save_state, append_log

def get_toggles():
    state = get_state()
    return state.get("feature_toggles", {})

def set_toggle(name: str, value: bool):
    state = get_state()
    toggles = state.get("feature_toggles", {})
    toggles[name] = bool(value)
    state["feature_toggles"] = toggles
    save_state(state)
    append_log("set_toggle", {"name": name, "value": bool(value)})
    return state

def set_maintenance_mode(value: bool):
    state = get_state()
    state["maintenance_mode"] = bool(value)
    save_state(state)
    append_log("set_maintenance_mode", {"value": bool(value)})
    return state

def set_system_mode(mode: str):
    state = get_state()
    state["system_mode"] = (mode or "ascension").strip().lower()
    save_state(state)
    append_log("set_system_mode", {"mode": state["system_mode"]})
    return state
