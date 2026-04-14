from backend.app.cognition.task_selector_guard import apply_task_cooldown
from backend.app.cognition.task_memory import put_on_cooldown, choose_alternate, is_on_cooldown, get_last_audit
from backend.app.cognition.active_intent import update_active_intent, get_active_intent
from backend.app.cognition import world, meta, decision, execution, goal
from backend.app.cognition.evolution_engine import run_evolution, load_evolution_state
from backend.app.cognition.strategy_engine import record_sequence, get_sequence_bonus

from fastapi import APIRouter
import random

router = APIRouter()

_last_tasks = []
MAX_REPEAT = 5

_task_history = []
MAX_HISTORY = 10


def _loop_guard(task):
    global _last_tasks
    _last_tasks.append(task)
    _last_tasks = _last_tasks[-MAX_REPEAT:]
    return len(set(_last_tasks)) == 1


def _update_history(task):
    global _task_history
    _task_history.append(task)
    _task_history = _task_history[-MAX_HISTORY:]


def _safe_strategy_bias(history):
    try:
        from backend.app.cognition.strategy_evaluator import get_strategy_bias
        return float(get_strategy_bias(history))
    except Exception:
        return 0.0


def _safe_goal_mutation(current_goal, active_intent):
    try:
        from backend.app.cognition.goal_mutation_engine import mutate_goal
        result = mutate_goal(current_goal, active_intent)
        if isinstance(result, dict):
            return {
                "goal": result.get("goal", current_goal),
                "goal_bias": float(result.get("goal_bias", 0.0)),
                "reason": result.get("reason", "goal_mutation_engine"),
            }
    except Exception:
        pass
    return {
        "goal": current_goal,
        "goal_bias": 0.0,
        "reason": "fallback",
    }


def _safe_reward_bias(task):
    try:
        from backend.app.cognition.reward_reinforcement_engine import get_reward_bias
        return float(get_reward_bias(task))
    except Exception:
        return 0.0


def _safe_failure_penalty(task):
    try:
        from backend.app.cognition.failure_decay_engine import get_failure_penalty
        return float(get_failure_penalty(task))
    except Exception:
        return 0.0


def _safe_direction_bias(task, active_intent):
    try:
        from backend.app.cognition.long_term_direction_engine import get_direction_bias
        return float(get_direction_bias(task, active_intent))
    except Exception:
        return 0.0


@router.post("/api/brain/run")
def brain():
    evolution_state = run_evolution()
    evo = load_evolution_state()

    world_state = world.update({"tick": "loop"})
    meta_state = meta.run({"event": "cycle"})
    decision_state = decision.run()
    goal_state = goal.run()
    active_intent = get_active_intent()

    base_goal = goal_state.get("active_goal", "balanced_progression")
    goal_shift = _safe_goal_mutation(base_goal, active_intent)
    effective_goal = goal_shift.get("goal", base_goal)

    selection_state = apply_task_cooldown({
        "task": "advance_beyond_handoff",
        "goal": effective_goal
    })

    selected_task = selection_state.get("selected", {})
    task_name = selected_task.get("task", "advance_beyond_handoff")

    weight = float(evo.get("task_weights", {}).get(task_name, 1.0))
    decay = float(evo.get("failure_decay", {}).get(task_name, 0))
    suppression = max(0.5, 1 - (decay * 0.05))

    sequence_bonus = float(get_sequence_bonus(_task_history))
    strategy_bias = _safe_strategy_bias(_task_history)
    reward_bias = _safe_reward_bias(task_name)
    failure_penalty = _safe_failure_penalty(task_name)
    direction_bias = _safe_direction_bias(task_name, active_intent)
    goal_bias = float(goal_shift.get("goal_bias", 0.0))

    effective_weight = max(
        0.25,
        weight
        + sequence_bonus
        + strategy_bias
        + reward_bias
        + direction_bias
        + goal_bias
        - failure_penalty
    )

    execution_state = execution.run_execution({
        "task": task_name,
        "plan": ["analyze_state", "execute", "evaluate"],
        "goal": selected_task.get("goal", effective_goal),
        "weight": effective_weight,
        "suppression": suppression,
        "biases": {
            "sequence_bonus": sequence_bonus,
            "strategy_bias": strategy_bias,
            "reward_bias": reward_bias,
            "failure_penalty": failure_penalty,
            "direction_bias": direction_bias,
            "goal_bias": goal_bias,
        }
    })

    task = execution_state.get("task", task_name)
    _update_history(task)

    if _loop_guard(task):
        put_on_cooldown(task, 120)
        alt_task = choose_alternate(task)
        update_active_intent(alt_task, "loop_detected_reroute")

        execution_state = execution.run_execution({
            "task": alt_task,
            "plan": ["analyze_state", "execute", "evaluate"],
            "goal": effective_goal
        })

        task = execution_state.get("task", alt_task)
        _update_history(task)
        update_active_intent(task, "continuous_execution")

        from backend.app.cognition.outcome_memory import record_outcome
        success = random.uniform(-1, 1)
        record_outcome(task, success)
        record_sequence(_task_history, success)

        return {
            "status": "rerouted",
            "reason": "loop_detected",
            "task": task,
            "execution_status": execution_state.get("status"),
            "route": execution_state.get("route"),
            "cooldown_applied": True,
            "alternate_on_cooldown": is_on_cooldown(task),
            "selection_mode": get_last_audit().get("selection_mode", "unknown"),
            "task_audit": get_last_audit(),
            "active_intent": get_active_intent(),
            "goal_shift": goal_shift,
            "weight": effective_weight,
            "suppression": suppression,
            "biases": {
                "sequence_bonus": sequence_bonus,
                "strategy_bias": strategy_bias,
                "reward_bias": reward_bias,
                "failure_penalty": failure_penalty,
                "direction_bias": direction_bias,
                "goal_bias": goal_bias,
            },
            "evolution": evolution_state
        }

    from backend.app.cognition.outcome_memory import record_outcome
    success = random.uniform(-1, 1)
    record_outcome(task, success)
    record_sequence(_task_history, success)

    return {
        "status": "ok",
        "task": task,
        "goal": effective_goal,
        "original_goal": base_goal,
        "goal_shift": goal_shift,
        "score": meta_state.get("score", 0.5),
        "weight": effective_weight,
        "suppression": suppression,
        "biases": {
            "sequence_bonus": sequence_bonus,
            "strategy_bias": strategy_bias,
            "reward_bias": reward_bias,
            "failure_penalty": failure_penalty,
            "direction_bias": direction_bias,
            "goal_bias": goal_bias,
        },
        "evolution": evolution_state
    }
