def _predict(d):
    if not d["causal_links"]:
        return None

    last = _simplify(d["history"][-1]["data"])

    matches = []

    for link in d["causal_links"]:
        cause = link["cause"]

        score = 0

        if cause["world_signal"] == last["world_signal"]:
            score += 1
        if cause["explore"] == last["explore"]:
            score += 1
        if cause["self_rate"] == last["self_rate"]:
            score += 1

        if score >= 2:
            matches.append((score, link))

    if not matches:
        return None

    best = sorted(matches, key=lambda x: x[0], reverse=True)[0][1]

    prediction = {
        "input": last,
        "expected": best["effect"],
        "confidence": sorted(matches, key=lambda x: x[0], reverse=True)[0][0] / 3,
        "t": time.time()
    }

    d["predictions"].append(prediction)
    return prediction
