def _build_causality(d):
    if len(d["history"]) < 2:
        return

    a = _simplify(d["history"][-2]["data"])
    b = _simplify(d["history"][-1]["data"])

    link = {"cause": a, "effect": b}

    if link not in d["causal_links"]:
        d["causal_links"].append(link)
