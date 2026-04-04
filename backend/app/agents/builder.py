def create_plan(user_input):
    return {
        "objective": user_input,
        "tasks": [
            "analyze request",
            "check roadmap",
            "generate implementation steps",
            "prepare code changes"
        ],
        "risk": "medium"
    }
