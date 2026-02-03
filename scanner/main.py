import json
import yfinance as yf
from nse_symbols import NSE_SYMBOLS

OUTPUT_FILE = "results.json"

def main():
    results = []

    for symbol in NSE_SYMBOLS:
        try:
            ticker = yf.Ticker(symbol + ".NS")
            data = ticker.history(period="1d")

            if data.empty:
                continue

            cmp_price = round(float(data["Close"].iloc[-1]), 2)

            results.append({
                "symbol": symbol,
                "cmp": cmp_price,
                "monthly": "",
                "weekly": "",
                "daily": "",
                "signal": "ALL"
            })

        except Exception:
            continue

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
