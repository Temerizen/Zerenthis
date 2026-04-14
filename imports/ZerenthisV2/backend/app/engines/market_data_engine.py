import requests, time

CRYPTO_ASSETS = ["bitcoin","ethereum","solana"]
STOCK_ASSETS = ["NVDA","TSLA","MSFT","SPY"]

def fetch_crypto():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ",".join(CRYPTO_ASSETS),
        "order": "market_cap_desc"
    }

    try:
        res = requests.get(url, params=params, timeout=5)
        data = res.json()

        results = []
        for coin in data:
            results.append({
                "asset": coin["symbol"].upper(),
                "price": coin["current_price"],
                "change": coin["price_change_percentage_24h"] or 0,
                "timestamp": int(time.time()),
                "source": "coingecko"
            })

        return results
    except:
        return []

def fetch_stocks():
    results = []
    try:
        import yfinance as yf

        tickers = yf.Tickers(" ".join(STOCK_ASSETS))
        for t in STOCK_ASSETS:
            info = tickers.tickers[t].history(period="1d")

            if not info.empty:
                open_price = info["Open"].iloc[0]
                close_price = info["Close"].iloc[-1]
                change = ((close_price - open_price) / open_price) * 100

                results.append({
                    "asset": t,
                    "price": float(close_price),
                    "change": round(change, 2),
                    "timestamp": int(time.time()),
                    "source": "yahoo"
                })
    except:
        pass

    return results

def scan_market():
    crypto = fetch_crypto()
    stocks = fetch_stocks()

    combined = crypto + stocks

    # fallback if API fails
    if not combined:
        return [{
            "asset": "SAFE_MODE",
            "price": 100,
            "change": 0,
            "timestamp": int(time.time()),
            "source": "fallback"
        }]

    return combined

