import json
import time
from datetime import datetime

import yfinance as yf
from yfinance.exceptions import YFRateLimitError

from nse_symbols import NSE_SYMBOLS
from screener import evaluate_stock

OUTPUT_FILE = "output/results.json"


def fetch_stock_data(symbol):
    """Fetch last 30 days of data and calculate daily/weekly/monthly high/low and CMP."""

    ticker = yf.Ticker(symbol + ".NS")

    hist = ticker.history(period="30d", interval="1d")

    if hist.empty or len(hist) < 8:
        return None

    cmp_price = hist["Close"].iloc[-1]

    # Previous trading day
    daily_high = hist["High"].iloc[-2]
    daily_low = hist["Low"].iloc[-2]

    weekly_high = hist["High"].iloc[-7:].max()
    weekly_low = hist["Low"].iloc[-7:].min()

    monthly_high = hist["High"].max()
    monthly_low = hist["Low"].min()

    data = {
        "symbol": symbol,
        "monthly": {"high": round(monthly_high, 2), "low": round(monthly_low, 2)},
        "weekly": {"high": round(weekly_high, 2), "low": round(weekly_low, 2)},
        "daily": {"high": round(daily_high, 2), "low": round(daily_low, 2)},
        "cmp": round(cmp_price, 2),
    }

    evaluated = evaluate_stock(data)
    data["signal"] = evaluated["signal"] if evaluated else "ALL"

    return data


def main():
    results = []

    for symbol in NSE_SYMBOLS:
        try:
            stock_data = fetch_stock_data(symbol)

        except YFRateLimitError:
            print(f"Rate limited on {symbol}. Waiting 5 seconds...")
            time.sleep(5)

            try:
                stock_data = fetch_stock_data(symbol)
            except Exception:
                print(f"Skipping {symbol} after retry")
                continue

        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            continue

        time.sleep(1)  # 🔒 CRITICAL: throttle Yahoo requests

        if stock_data:
            results.append(stock_data)

    # Write to output folder
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    # Copy to root for website
    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"Updated {len(results)} symbols")
    print("Run completed at:", datetime.now())


if __name__ == "__main__":
    main()
