import time
import traceback
from backend.app.cognition.thought_engine import generate_thought
from backend.app.cognition.identity_engine import update_identity
from backend.app.cognition.reflection_engine import run_reflection
from backend.app.cognition.goal_generator import run_goal_generation
from backend.app.cognition.goal_arbiter import select_active_goal
from backend.app.cognition.goal_executor import execute_active_goal
from backend.app.cognition.plan_engine import build_active_plan, advance_active_plan
from backend.app.cognition.execution_memory import record_execution
from backend.app.cognition.feedback_engine import apply_feedback
from backend.app.cognition.mission_engine import build_or_update_mission, advance_mission_progress
from backend.app.cognition.conflict_engine import resolve_conflicts
from backend.app.cognition.initiative_engine import build_initiative_goals
import threading
from backend.app.execution.runner import execute_all

RUNNING = False
THREAD = None
STATE = {
    "running": False,
    "interval": 2.0,
    "cycle_count": 0,
    "last_cycle_at": None,
    "last_error": None
}

def loop(interval=2.0):
    global RUNNING
    STATE["running"] = True
    STATE["interval"] = interval
    print("[AUTONOMY] Loop started")

    while RUNNING:
        try:
            results = execute_all(limit=5)
            STATE["cycle_count"] += 1
            STATE["last_cycle_at"] = time.time()

            try:
                generate_thought(
                    current_goal="autonomy_cycle",
                    chosen_task=results[0].get("task", "unknown") if results else "no_task",
                    result="success",
                    reasoning="Completed autonomy execution cycle and recorded internal state.",
                    reflection="Cycle completed; cognition layer updated.",
                    extra={"results": results, "cycle_count": STATE["cycle_count"]}
                )
                update_identity(
                    current_goal="autonomy_cycle",
                    chosen_task=results[0].get("task", "unknown") if results else "no_task",
                    result="success",
                    goal_aligned=True
                )
                if STATE["cycle_count"] % 3 == 0:
                    run_reflection(10)

                if STATE["cycle_count"] % 4 == 0:
                    run_goal_generation()
                    build_initiative_goals()
                    select_active_goal()
                    build_active_plan()
                    build_or_update_mission()
                    resolve_conflicts()
                    execute_active_goal()
                    advance_active_plan()
                    record_execution()
                    apply_feedback()
                    advance_mission_progress()
            except Exception as cognition_error:
                print(f"[AUTONOMY][COGNITION] {cognition_error}")
                print(traceback.format_exc())

            STATE["last_error"] = None
            print(f"[AUTONOMY] cycle complete: {len(results)} tasks")

        except Exception as e:
            STATE["last_error"] = str(e)
            print(f"[AUTONOMY] error: {e}")
            print(traceback.format_exc())

        time.sleep(interval)

    STATE["running"] = False
    print("[AUTONOMY] Loop stopped")

def start_loop(interval=2.0):
    global RUNNING, THREAD

    if RUNNING:
        return {"status": "already_running", "state": STATE}

    RUNNING = True
    THREAD = threading.Thread(target=loop, args=(interval,), daemon=True)
    THREAD.start()
    return {"status": "started", "state": STATE}

def stop_loop():
    global RUNNING
    RUNNING = False
    return {"status": "stopping", "state": STATE}

def get_status():
    return {
        "status": "ok",
        "state": STATE
    }
