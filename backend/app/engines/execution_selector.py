def select_top_signals(signals, max_trades=1, min_confidence=1.8):
    if not isinstance(signals, list):
        return []

    cleaned = []
    for s in signals:
        if not isinstance(s, dict):
            continue
        conf = float(s.get("confidence", 0) or 0)
        if conf >= min_confidence:
            cleaned.append(s)

    cleaned.sort(key=lambda x: float(x.get("confidence", 0) or 0), reverse=True)
    return cleaned[:max_trades]

