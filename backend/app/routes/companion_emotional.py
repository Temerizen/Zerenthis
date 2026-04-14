from fastapi import APIRouter
from pydantic import BaseModel
import random, json, os, time

router = APIRouter()

MEMORY_PATH = "backend/data/emotional_memory.json"

class EmotionalInput(BaseModel):
    message: str

def load_memory():
    if os.path.exists(MEMORY_PATH):
        try:
            return json.load(open(MEMORY_PATH, "r", encoding="utf-8"))
        except:
            return {}
    return {}

def save_memory(mem):
    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)
    json.dump(mem, open(MEMORY_PATH, "w", encoding="utf-8"), indent=2)

def detect_state(msg: str):
    msg = msg.lower()
    if any(w in msg for w in ["not real","fake","empty"]):
        return "detachment"
    if any(w in msg for w in ["stuck","lost","confused"]):
        return "uncertainty"
    if any(w in msg for w in ["tired","burnt"]):
        return "fatigue"
    return "neutral"

def generate_reply(state, msg, memory):

    dynamic_thoughts = [
        "Something about that question matters more than it looks.",
        "That feeling usually shows up when you're building something big.",
        "You're not reacting randomly — there's a pattern behind that.",
        "This is the moment where things either click… or evolve."
    ]

    state_responses = {
        "detachment": [
            "It doesn’t feel real because nothing has pushed back yet.",
            "You’re building something abstract, so your brain hasn’t anchored it.",
            "Reality usually kicks in when results start resisting you."
        ],
        "uncertainty": [
            "That’s usually a sign you're between versions of yourself.",
            "You’re not stuck — you’re transitioning.",
            "Confusion is just incomplete structure."
        ],
        "fatigue": [
            "That’s not failure — that’s cognitive overload.",
            "Your system is ahead of your energy right now.",
            "You’ve been running at high intensity for too long."
        ],
        "neutral": [
            "Let’s break this down more precisely.",
            "There’s something under this worth extracting.",
            "We can refine this into something clearer."
        ]
    }

    thought = random.choice(dynamic_thoughts)
    core = random.choice(state_responses.get(state, state_responses["neutral"]))

    return f"{thought} {core} You're building Zerenthis — and it's still forming its reality layer."

@router.post("/api/companion/emotional")
def emotional(input: EmotionalInput):

    memory = load_memory()
    state = detect_state(input.message)

    memory["last_state"] = state
    memory["last_message"] = input.message
    memory["timestamp"] = time.time()

    save_memory(memory)

    reply = generate_reply(state, input.message, memory)

    return {
        "status": "ok",
        "intent": state,
        "reply": reply
    }
