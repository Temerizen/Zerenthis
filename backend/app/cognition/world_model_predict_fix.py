def _predict(d):
    if not d["causal_links"]:
        return None

    effect_counts = {}

    for link in d["causal_links"]:
        key = tuple(sorted(link["effect"].items()))
        effect_counts[key] = effect_counts.get(key, 0) + 1

    if not effect_counts:
        return None

    best_key = max(effect_counts, key=effect_counts.get)

    best_effect = dict(best_key)

    prediction = {
        "expected": best_effect,
        "confidence": effect_counts[best_key] / len(d["causal_links"]),
        "t": time.time()
    }

    d["predictions"].append(prediction)
    return prediction
