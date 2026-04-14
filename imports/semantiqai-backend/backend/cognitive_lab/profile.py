import json
from pathlib import Path
from backend.platform.paths import BACKEND_DIR

PROFILE_PATH = BACKEND_DIR / "cognitive_lab" / "profiles.json"

def load_profiles():
    if not PROFILE_PATH.exists():
        return {}
    try:
        return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_profiles(data):
    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def get_profile(user_id):
    profiles = load_profiles()
    return profiles.get(user_id, {
        "memory": 0,
        "logic": 0,
        "speed": 0,
        "creativity": 0,
        "consistency": 0
    })

def update_profile(user_id, category, score):
    profiles = load_profiles()
    profile = profiles.get(user_id, get_profile(user_id))
    if category not in profile:
        profile[category] = 0
    profile[category] += score
    profiles[user_id] = profile
    save_profiles(profiles)
    return profile
