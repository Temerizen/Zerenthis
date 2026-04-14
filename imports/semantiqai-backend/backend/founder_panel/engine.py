from .storage import get_state, get_logs, save_state
from .registry import discover_modules
from .health import health_summary
from .toggles import get_toggles, set_toggle, set_maintenance_mode, set_system_mode
from .notes import get_notes, set_notes
from .controls import founder_overview, register_manual_action

def initialize_registry():
    state = get_state()
    state["module_registry"] = discover_modules()
    save_state(state)
    return state

def panel_snapshot():
    state = get_state()
    state["module_registry"] = discover_modules()
    save_state(state)
    return {
        "state": state,
        "health": health_summary(),
        "logs_tail": get_logs()[-20:]
    }
