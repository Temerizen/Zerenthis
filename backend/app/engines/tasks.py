def add_task(user, task):
    user["tasks"].append({
        "task": task,
        "status": "pending"
    })
    return user

def complete_task(user, index):
    if index < len(user["tasks"]):
        user["tasks"][index]["status"] = "done"
        user["score"] += 5
    return user

