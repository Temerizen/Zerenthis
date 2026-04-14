def _predict(d):
    if not d["causal_links"]:
        return None

    # Count most common effects
    effect_counts = {}

    for link in d["causal_links"]:
        key = str(link["effect"])
        effect_counts[key] = effect_counts.get(key, 0) + 1

    if not effect_counts:
        return None

    # Pick most frequent outcome
    best_effect_str = max(effect_counts, key=effect_counts.get)

    # Convert string back to dict
    import ast
    best_effect = ast.literal_eval(best_effect_str)

    prediction = {
        "expected": best_effect,
        "confidence": effect_counts[best_effect_str] / len(d["causal_links"]),
        "t": time.time()
    }

    d["predictions"].append(prediction)
    return prediction
