from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List

STATE_PATH = "backend/data/task_selection_state.json"
QUEUE_PATH = "backend/data/task_queue.json"
ACTIVE_TASK_PATH = "backend/data/active_task.json"

DEFAULT_STATE: Dict[str, Any] = {
    "last_selected_at": None,
    "last_selected_task": None,
    "selection_count": 0,
    "history": [],
}

DEFAULT_QUEUE: Dict[str, Any] = {
    "tasks": []
}


def _safe_load(path: str, default: Any) -> Any:
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _safe_save(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def get_state() -> Dict[str, Any]:
    state = _safe_load(STATE_PATH, DEFAULT_STATE.copy())
    merged = DEFAULT_STATE.copy()
    if isinstance(state, dict):
        merged.update(state)
    if not isinstance(merged.get("history"), list):
        merged["history"] = []
    return merged


def save_state(state: Dict[str, Any]) -> Dict[str, Any]:
    _safe_save(STATE_PATH, state)
    return state


def get_queue() -> Dict[str, Any]:
    queue = _safe_load(QUEUE_PATH, DEFAULT_QUEUE.copy())
    if not isinstance(queue, dict):
        queue = DEFAULT_QUEUE.copy()
    if not isinstance(queue.get("tasks"), list):
        queue["tasks"] = []
    return queue


def save_queue(queue: Dict[str, Any]) -> Dict[str, Any]:
    _safe_save(QUEUE_PATH, queue)
    return queue


def get_active_task() -> Dict[str, Any]:
    active = _safe_load(ACTIVE_TASK_PATH, {})
    return active if isinstance(active, dict) else {}


def save_active_task(task: Dict[str, Any]) -> Dict[str, Any]:
    _safe_save(ACTIVE_TASK_PATH, task)
    return task


def _extract_active_mission(active_mission: Dict[str, Any] | None) -> Dict[str, Any]:
    active_mission = active_mission or {}
    if isinstance(active_mission.get("mission"), dict):
        return active_mission["mission"]
    return active_mission if isinstance(active_mission, dict) else {}


def generate_candidates(
    active_mission: Dict[str, Any] | None = None,
    reflection_state: Dict[str, Any] | None = None,
    goal_state: Dict[str, Any] | None = None,
    identity_state: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    mission = _extract_active_mission(active_mission)
    reflection_state = reflection_state or {}
    goal_state = goal_state or {}
    identity_state = identity_state or {}

    traits = identity_state.get("traits", {}) if isinstance(identity_state, dict) else {}
    curiosity = _num(traits.get("curiosity", 0.5))
    persistence = _num(traits.get("persistence", 0.5))
    confidence = _num(traits.get("confidence", 0.5))
    stability = _num(traits.get("stability_preference", 0.5))
    risk = _num(traits.get("risk_tolerance", 0.5))

    reflection = reflection_state.get("last_reflection", {}) if isinstance(reflection_state, dict) else {}
    reflection_score = _num(reflection.get("score", 0.5))
    reflection_decision = str(reflection.get("decision", "observe"))
    active_goal = str(goal_state.get("active_goal", mission.get("goal_id", "balanced_progression")))

    focus_task = str(mission.get("focus_task", "")).strip()
    blocked_tasks = mission.get("blocked_tasks", [])
    blocked_tasks = blocked_tasks if isinstance(blocked_tasks, list) else []

    candidates: List[Dict[str, Any]] = []

    if focus_task:
        candidates.append({
            "task_id": f"focus_{focus_task}",
            "type": "mission_focus",
            "task": focus_task,
            "goal": active_goal,
            "reason": "active_mission_focus",
            "base_priority": 0.92,
            "novelty": 0.20,
            "risk": 0.35,
            "stability_fit": 0.85,
        })

    for blocked in blocked_tasks:
        if isinstance(blocked, str) and blocked.strip():
            candidates.append({
                "task_id": f"unblock_{blocked}",
                "type": "unblocker",
                "task": f"resolve_{blocked}",
                "goal": active_goal,
                "reason": "blocked_task_recovery",
                "base_priority": 0.88,
                "novelty": 0.30,
                "risk": 0.45,
                "stability_fit": 0.75,
            })

    candidates.extend([
        {
            "task_id": "analyze_state",
            "type": "analysis",
            "task": "analyze_state",
            "goal": active_goal,
            "reason": "maintain_situational_awareness",
            "base_priority": 0.65 + (0.10 * stability),
            "novelty": 0.15,
            "risk": 0.10,
            "stability_fit": 0.95,
        },
        {
            "task_id": "plan_next_step",
            "type": "planning",
            "task": "plan_next_step",
            "goal": active_goal,
            "reason": "convert_continuity_into_direction",
            "base_priority": 0.70 + (0.10 * persistence),
            "novelty": 0.18,
            "risk": 0.12,
            "stability_fit": 0.92,
        },
        {
            "task_id": "probe_new_paths",
            "type": "exploration",
            "task": "probe_new_paths",
            "goal": active_goal,
            "reason": "expand_capability_surface",
            "base_priority": 0.45 + (0.25 * curiosity),
            "novelty": 0.90,
            "risk": 0.55 - (0.20 * risk),
            "stability_fit": 0.45,
        },
        {
            "task_id": "validate_recent_behavior",
            "type": "validation",
            "task": "validate_recent_behavior",
            "goal": active_goal,
            "reason": "reduce_drift_and_confirm_learning",
            "base_priority": 0.62 + (0.12 * stability),
            "novelty": 0.12,
            "risk": 0.08,
            "stability_fit": 0.98,
        },
        {
            "task_id": "optimize_decision_weights",
            "type": "optimization",
            "task": "optimize_decision_weights",
            "goal": active_goal,
            "reason": "improve_internal_policy_quality",
            "base_priority": 0.58 + (0.15 * confidence),
            "novelty": 0.42,
            "risk": 0.24,
            "stability_fit": 0.80,
        },
    ])

    if reflection_decision == "continue" and reflection_score >= 0.75:
        candidates.append({
            "task_id": "compound_progress",
            "type": "compounding",
            "task": "compound_progress",
            "goal": active_goal,
            "reason": "positive_reflection_push",
            "base_priority": 0.80,
            "novelty": 0.35,
            "risk": 0.18,
            "stability_fit": 0.88,
        })

    return {
        "status": "ok",
        "count": len(candidates),
        "candidates": candidates,
    }


def score_candidates(
    candidates: List[Dict[str, Any]],
    identity_state: Dict[str, Any] | None = None,
    reflection_state: Dict[str, Any] | None = None,
    last_selected_task: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    identity_state = identity_state or {}
    reflection_state = reflection_state or {}
    last_selected_task = last_selected_task or {}

    traits = identity_state.get("traits", {}) if isinstance(identity_state, dict) else {}
    curiosity = _num(traits.get("curiosity", 0.5))
    persistence = _num(traits.get("persistence", 0.5))
    confidence = _num(traits.get("confidence", 0.5))
    stability = _num(traits.get("stability_preference", 0.5))
    reflection = reflection_state.get("last_reflection", {}) if isinstance(reflection_state, dict) else {}
    reflection_score = _num(reflection.get("score", 0.5))

    last_task_name = str(last_selected_task.get("task", ""))

    scored: List[Dict[str, Any]] = []

    for item in candidates:
        base_priority = _num(item.get("base_priority", 0.5))
        novelty = _num(item.get("novelty", 0.0))
        risk = _num(item.get("risk", 0.0))
        stability_fit = _num(item.get("stability_fit", 0.5))
        task_name = str(item.get("task", ""))

        repeat_penalty = 0.18 if task_name and task_name == last_task_name else 0.0
        curiosity_bonus = novelty * curiosity * 0.20
        persistence_bonus = base_priority * persistence * 0.18
        confidence_bonus = confidence * 0.08
        stability_bonus = stability_fit * stability * 0.15
        reflection_bonus = reflection_score * 0.10
        risk_penalty = risk * max(0.20, stability) * 0.15

        score = (
            base_priority
            + curiosity_bonus
            + persistence_bonus
            + confidence_bonus
            + stability_bonus
            + reflection_bonus
            - risk_penalty
            - repeat_penalty
        )

        enriched = dict(item)
        enriched["score"] = round(_clamp(score, 0.0, 1.5), 4)
        enriched["repeat_penalty"] = repeat_penalty
        scored.append(enriched)

    scored.sort(key=lambda x: x.get("score", 0.0), reverse=True)

    return {
        "status": "ok",
        "count": len(scored),
        "scored_candidates": scored,
    }


def select_next_task(
    active_mission: Dict[str, Any] | None = None,
    reflection_state: Dict[str, Any] | None = None,
    goal_state: Dict[str, Any] | None = None,
    identity_state: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    state = get_state()
    last_selected = state.get("last_selected_task") if isinstance(state.get("last_selected_task"), dict) else {}

    generated = generate_candidates(
        active_mission=active_mission,
        reflection_state=reflection_state,
        goal_state=goal_state,
        identity_state=identity_state,
    )
    candidates = generated.get("candidates", [])

    scored = score_candidates(
        candidates=candidates,
        identity_state=identity_state,
        reflection_state=reflection_state,
        last_selected_task=last_selected,
    )
    ranked = scored.get("scored_candidates", [])

    if not ranked:
        return {
            "status": "no_candidates",
            "selected": None,
            "ranked": [],
        }

    selected = dict(ranked[0])
    selected["selected_at"] = time.time()
    selected["status"] = "active"

    queue = get_queue()
    existing = queue.get("tasks", [])
    if not isinstance(existing, list):
        existing = []

    existing.append({
        "task": selected.get("task"),
        "type": selected.get("type"),
        "goal": selected.get("goal"),
        "score": selected.get("score"),
        "created_at": selected["selected_at"],
        "reason": selected.get("reason"),
    })
    queue["tasks"] = existing[-50:]
    save_queue(queue)

    save_active_task(selected)

    state["last_selected_at"] = selected["selected_at"]
    state["last_selected_task"] = selected
    state["selection_count"] = int(state.get("selection_count", 0)) + 1
    history = state.get("history", [])
    if not isinstance(history, list):
        history = []
    history.append({
        "timestamp": selected["selected_at"],
        "task": selected.get("task"),
        "type": selected.get("type"),
        "goal": selected.get("goal"),
        "score": selected.get("score"),
        "reason": selected.get("reason"),
    })
    state["history"] = history[-100:]
    save_state(state)

    return {
        "status": "selected",
        "selected": selected,
        "ranked": ranked[:10],
        "state": state,
    }


def get_selection_snapshot() -> Dict[str, Any]:
    state = get_state()
    queue = get_queue()
    active_task = get_active_task()
    return {
        "status": "ok",
        "state": state,
        "active_task": active_task,
        "queue": queue,
    }
