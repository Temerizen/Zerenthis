import json
import os

PROFILE_PATH = "backend/cognitive_lab/profiles.json"

def load_profiles():
    if not os.path.exists(PROFILE_PATH):
        return {}
    with open(PROFILE_PATH, "r") as f:
        return json.load(f)

def save_profiles(data):
    with open(PROFILE_PATH, "w") as f:
        json.dump(data, f, indent=2)

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
    profile[category] += score
    profiles[user_id] = profile
    save_profiles(profiles)
    return profile
