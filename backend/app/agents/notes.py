from .storage import get_state, save_state, append_log

def get_notes():
    state = get_state()
    return {"founder_notes": state.get("founder_notes", "")}

def set_notes(text: str):
    state = get_state()
    state["founder_notes"] = text or ""
    save_state(state)
    append_log("set_founder_notes", {"length": len(state["founder_notes"])})
    return {"founder_notes": state["founder_notes"]}

