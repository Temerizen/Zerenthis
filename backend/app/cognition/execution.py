def run(context=None):
    context = context or {}
    planning_state = {"task": context.get("task", "unknown"), "plan": context.get("plan", []), "goal": context.get("goal", "balanced_progression")}
    return run_execution(planning_state, context)

# === EXECUTION ENGINE (RESTORED + LOOP BREAKER) ===

def run_execution(planning_state, context=None):
    context = context or {}

    task = planning_state.get("task", "unknown")
    steps = planning_state.get("plan", [])

    recovery_count = context.get("recovery_count", 0)
    last_route = context.get("last_route", "")

    # === LOOP DETECTION ===
    if last_route == "recovery":
        recovery_count += 1
    else:
        recovery_count = 0

    # === FORCE BUILDER ESCALATION ===
    if recovery_count >= 3:
        return {
            "status": "forced_builder_execution",
            "goal": planning_state.get("goal"),
            "task": task,
            "route": "builder",
            "action": "execute_real_builder_task",
            "reason": "recovery_loop_detected",
            "recovery_count": recovery_count,
            "steps_executed": []
        }

    # === NORMAL EXECUTION ===
    executed_steps = []
    for step in steps:
        executed_steps.append({
            "step": step,
            "status": "executed",
            "detail": "normal_execution"
        })

    return {
        "status": "execution_complete",
        "goal": planning_state.get("goal"),
        "task": task,
        "route": "normal",
        "steps_executed": executed_steps,
        "steps_count": len(executed_steps),
        "recovery_count": recovery_count
    }
