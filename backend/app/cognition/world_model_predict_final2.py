def _predict(d):
    if not d["causal_links"]:
        return None

    # just take most recent strong pattern
    recent = d["causal_links"][-5:]

    if not recent:
        return None

    # pick the most recent effect
    best_effect = recent[-1]["effect"]

    prediction = {
        "expected": best_effect,
        "confidence": 0.5 + (len(recent) / 10),
        "t": time.time()
    }

    d["predictions"].append(prediction)
    return prediction
