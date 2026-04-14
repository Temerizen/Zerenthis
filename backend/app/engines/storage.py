import json
import os

DATA_PATH = "backend/execution_engine/data.json"

def load_data():
    if not os.path.exists(DATA_PATH):
        return {}
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

def get_user(user_id):
    data = load_data()
    return data.get(user_id, {
        "goals": [],
        "tasks": [],
        "habits": [],
        "score": 0
    })

def update_user(user_id, user_data):
    data = load_data()
    data[user_id] = user_data
    save_data(data)

