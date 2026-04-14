def _simplify(data):
    # compress state into stable features
    return {
        "world_signal": data["world"]["signals"] // 5,
        "meta_level": data["meta"]["history"] // 5,
        "self_rate": round(data["self"]["rate"], 1),
        "explore": data["explore"]["action"]
    }

def _build_causality(d):
    if len(d["history"]) < 2:
        return

    a = _simplify(d["history"][-2]["data"])
    b = _simplify(d["history"][-1]["data"])

    link = {"cause": a, "effect": b}

    if link not in d["causal_links"]:
        d["causal_links"].append(link)

def _predict(d):
    if not d["causal_links"]:
        return None

    last = _simplify(d["history"][-1]["data"])

    for link in reversed(d["causal_links"]):
        if link["cause"] == last:
            prediction = {
                "input": last,
                "expected": link["effect"],
                "t": time.time()
            }
            d["predictions"].append(prediction)
            return prediction

    return None
