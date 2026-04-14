def generate_signals(data):
    signals = []

    for asset in data:
        if not isinstance(asset, dict):
            continue

        price = float(asset.get("price", 0) or 0)
        change = float(asset.get("change", 0) or 0)

        if price <= 0:
            continue

        # === SIMPLE SIGNAL LOGIC ===
        if change > 0.5:
            signals.append({
                "asset": asset.get("asset", "UNK"),
                "action": "buy",
                "price": price,
                "confidence": min(10.0, change * 2)
            })

        elif change < -0.5:
            signals.append({
                "asset": asset.get("asset", "UNK"),
                "action": "sell",
                "price": price,
                "confidence": min(10.0, abs(change) * 2)
            })

    return signals

