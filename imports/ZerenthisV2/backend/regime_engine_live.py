import json, os, time, urllib.request, urllib.error
from statistics import pstdev

DATA_DIR = os.path.join("backend", "data")
REGIME_FILE = os.path.join(DATA_DIR, "regime_state.json")
CACHE_FILE = os.path.join(DATA_DIR, "regime_price_cache.json")

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def fetch_url(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 ZerenthisV2 RegimeEngine/1.0",
            "Accept": "application/json"
        }
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        raw = r.read().decode("utf-8")
        return json.loads(raw)

def get_prices():
    urls = [
        "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=2&interval=hourly",
        "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=3&interval=hourly",
        "https://www.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=2&interval=hourly",
    ]

    errors = []

    for url in urls:
        try:
            data = fetch_url(url)
            prices = [float(p[1]) for p in data.get("prices", []) if isinstance(p, list) and len(p) >= 2]
            if len(prices) >= 50:
                save_json(CACHE_FILE, {
                    "timestamp": int(time.time()),
                    "price_points": len(prices),
                    "prices": prices[-200:]
                })
                return prices, {"source": url, "fetched": len(prices), "errors": errors}
            errors.append(f"{url} -> too_few_points_{len(prices)}")
        except urllib.error.HTTPError as e:
            try:
                body = e.read().decode("utf-8", errors="ignore")[:300]
            except:
                body = ""
            errors.append(f"{url} -> HTTP_{e.code} {body}")
        except Exception as e:
            errors.append(f"{url} -> {type(e).__name__}: {e}")

    cache = load_json(CACHE_FILE, {})
    cached_prices = cache.get("prices", [])
    if len(cached_prices) >= 50:
        return cached_prices, {
            "source": "cache",
            "fetched": len(cached_prices),
            "errors": errors,
            "cache_timestamp": cache.get("timestamp")
        }

    return [], {"source": "none", "fetched": 0, "errors": errors}

def sma(data, n):
    return sum(data[-n:]) / n

def detect_regime(prices, meta):
    if len(prices) < 50:
        return {
            "regime": "UNKNOWN",
            "confidence": 0.0,
            "reason": f"insufficient_data_{len(prices)}",
            "source": meta.get("source", "none"),
            "fetch_meta": meta,
            "timestamp": int(time.time())
        }

    fast = sma(prices, 10)
    slow = sma(prices, 30)

    returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
    vol = pstdev(returns[-30:]) if len(returns) >= 30 else 0.0

    if vol > 0.03:
        vol_state = "HIGH"
    elif vol < 0.008:
        vol_state = "LOW"
    else:
        vol_state = "NORMAL"

    if abs(fast - slow) / max(prices[-1], 1e-9) < 0.002:
        regime = "RANGING"
    elif fast > slow:
        regime = "TRENDING_UP"
    else:
        regime = "TRENDING_DOWN"

    if vol_state == "HIGH":
        regime = "HIGH_VOLATILITY_" + regime
    elif vol_state == "LOW":
        regime = "LOW_VOLATILITY_" + regime

    gap_ratio = abs(fast - slow) / max(prices[-1], 1e-9)
    confidence = min(1.0, gap_ratio * 250)

    return {
        "regime": regime,
        "confidence": round(confidence, 4),
        "volatility_state": vol_state,
        "price_points": len(prices),
        "source": meta.get("source", "unknown"),
        "fetch_meta": meta,
        "timestamp": int(time.time())
    }

if __name__ == "__main__":
    prices, meta = get_prices()
    state = detect_regime(prices, meta)
    save_json(REGIME_FILE, state)
    print(json.dumps(state, indent=2))
