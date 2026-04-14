from __future__ import annotations
import json, time, random
from pathlib import Path

PATH = Path("backend/data/modification_state.json")

SAFE_TARGETS = [
    "backend/app/cognition/explore.py",
    "backend/app/cognition/decision.py",
    "backend/app/cognition/planning.py"
]

def _default():
    return {
        "history": [],
        "accepted": 0,
        "rejected": 0,
        "last_proposal": None
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

# --- PROPOSAL GENERATOR ---
def _generate_proposal(evolution_state: dict):
    score = evolution_state.get("analysis", {}).get("score", 0.5)

    if score < 0.5:
        idea = "reduce instability"
    elif score < 0.8:
        idea = "optimize decision weighting"
    else:
        idea = "increase exploration diversity"

    target = random.choice(SAFE_TARGETS)

    confidence = round(random.uniform(0.4, 0.9), 3)

    return {
        "idea": idea,
        "target": target,
        "confidence": confidence
    }

# --- ACCEPTANCE LOGIC ---
def _evaluate(proposal):
    return proposal["confidence"] > 0.6

def run(evolution_state: dict):
    state = _load()

    proposal = _generate_proposal(evolution_state)
    accepted = _evaluate(proposal)

    record = {
        "timestamp": time.time(),
        "proposal": proposal,
        "accepted": accepted
    }

    state["history"].append(record)
    state["history"] = state["history"][-200:]

    if accepted:
        state["accepted"] += 1
    else:
        state["rejected"] += 1

    state["last_proposal"] = record

    _save(state)

    return {
        "status": "proposal_generated",
        "proposal": proposal,
        "accepted": accepted,
        "totals": {
            "accepted": state["accepted"],
            "rejected": state["rejected"]
        }
    }

def state():
    return _load()
