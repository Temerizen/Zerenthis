def add_habit(user, habit):
    user["habits"].append({
        "habit": habit,
        "streak": 0
    })
    return user

def complete_habit(user, index):
    if index < len(user["habits"]):
        user["habits"][index]["streak"] += 1
        user["score"] += 2
    return user

