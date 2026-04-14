def get_directional_weights(system_state: str):
    system_state = str(system_state or "").lower()

    if system_state == "stable":
        return {
            "maintenance": 0.90,
            "expansion": 1.25,
            "optimization": 1.10,
            "recovery": 0.80
        }

    if system_state in ["warning", "strained"]:
        return {
            "maintenance": 1.05,
            "expansion": 1.05,
            "optimization": 1.05,
            "recovery": 1.10
        }

    return {
        "maintenance": 1.20,
        "expansion": 0.80,
        "optimization": 1.00,
        "recovery": 1.50
    }
