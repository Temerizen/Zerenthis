def get_direction_bias(task: str, active_intent: dict | None = None) -> float:
    active_intent = active_intent or {}

    intent_task = active_intent.get("task")
    direction = active_intent.get("direction", "stay_the_course")
    intent_score = float(active_intent.get("intent_score", 0) or 0)
    repeat_count = int(active_intent.get("repeat_count", 0) or 0)
    stagnating = bool(active_intent.get("stagnating", False))

    bias = 0.0

    if direction == "stay_the_course" and task == intent_task:
        bias += min(0.18, 0.03 * max(1.0, intent_score))

    if direction == "pivot_required" and task != intent_task:
        bias += 0.08

    if stagnating and task == intent_task:
        bias -= 0.12

    if repeat_count >= 3 and task == intent_task:
        bias -= 0.08

    return max(-0.2, min(0.2, bias))
