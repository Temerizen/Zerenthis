from __future__ import annotations
import json, time, random
from pathlib import Path

PATH = Path("backend/data/evolution_state.json")

def _default():
    return {
        "history": [],
        "accepted": 0,
        "rejected": 0,
        "last_evolution": None
    }

def _load():
    if not PATH.exists():
        return _default()
    try:
        d = json.loads(PATH.read_text())
        if "history" not in d:
            d["history"] = []
        return d
    except:
        return _default()

def _save(d):
    PATH.parent.mkdir(parents=True, exist_ok=True)
    PATH.write_text(json.dumps(d, indent=2))

# --- ANALYZE PERFORMANCE ---
def _analyze(execution_state: dict):
    history = execution_state.get("history", [])
    if not history:
        return {"score": 0.5}

    success_count = len([h for h in history if "analyzed" in h.get("result","")])
    total = len(history)

    score = success_count / total if total else 0.5

    return {
        "score": round(score, 3),
        "total_runs": total
    }

# --- GENERATE IMPROVEMENT ---
def _propose_improvement(score):
    if score < 0.5:
        return {"type": "stabilize", "delta": 0.1}
    elif score < 0.8:
        return {"type": "optimize", "delta": 0.05}
    else:
        return {"type": "explore_more", "delta": 0.02}

# --- ACCEPT OR REJECT ---
def _evaluate(proposal):
    threshold = 0.03
    return proposal["delta"] >= threshold

def run(execution_state: dict):
    state = _load()

    analysis = _analyze(execution_state)
    proposal = _propose_improvement(analysis["score"])
    accepted = _evaluate(proposal)

    record = {
        "timestamp": time.time(),
        "analysis": analysis,
        "proposal": proposal,
        "accepted": accepted
    }

    state["history"].append(record)
    state["history"] = state["history"][-200:]

    if accepted:
        state["accepted"] += 1
    else:
        state["rejected"] += 1

    state["last_evolution"] = record

    _save(state)

    return {
        "status": "evolution_cycle_complete",
        "analysis": analysis,
        "proposal": proposal,
        "accepted": accepted,
        "totals": {
            "accepted": state["accepted"],
            "rejected": state["rejected"]
        }
    }

def state():
    return _load()
