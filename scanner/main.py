import json
from datetime import datetime
import yfinance as yf
from nse_symbols import NSE_SYMBOLS
from scanner.screener import evaluate_stock  # Use your existing logic

OUTPUT_FILE = "output/results.json"


def fetch_stock_data(symbol):
    """Fetch last 30 days of data and calculate daily/weekly/monthly high/low and CMP."""
    ticker = yf.Ticker(symbol + ".NS")
    hist = ticker.history(period="30d", interval="1d")

    if hist.empty:
        return None

    cmp_price = hist['Close'][-1]
    daily_high = hist['High'][-2]  # Previous day's high
    daily_low = hist['Low'][-2]

    weekly_high = hist['High'][-7:].max()
    weekly_low = hist['Low'][-7:].min()

    monthly_high = hist['High'].max()
    monthly_low = hist['Low'].min()

    data = {
        "symbol": symbol,
        "monthly": {"high": round(monthly_high, 2), "low": round(monthly_low, 2)},
        "weekly": {"high": round(weekly_high, 2), "low": round(weekly_low, 2)},
        "daily": {"high": round(daily_high, 2), "low": round(daily_low, 2)},
        "cmp": round(cmp_price, 2),
    }

    # Add signal using your existing screener logic
    evaluated = evaluate_stock(data)
    if evaluated:
        data["signal"] = evaluated["signal"]
    else:
        data["signal"] = "ALL"

    return data


def main():
    results = []

    for symbol in NSE_SYMBOLS:
        stock_data = fetch_stock_data(symbol)
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
