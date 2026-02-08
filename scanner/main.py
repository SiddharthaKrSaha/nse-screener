import json
import time
import yfinance as yf
from datetime import datetime
from nse_symbols import NSE_SYMBOLS

BATCH_SIZE = 50
SLEEP_BETWEEN_BATCH = 30  # seconds


def ns(symbol):
    return symbol if symbol.endswith(".NS") else symbol + ".NS"


def chunked(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


# --- NEW TREND LOGIC ---

def calculate_monthly_trend(data):
    today = datetime.now().day

    # data is ordered old → new (length = 4)
    if today < 15:
        first_close = data[0]["close"]     # oldest
        last_close = data[-2]["close"]     # exclude current month
    else:
        first_close = data[0]["close"]
        last_close = data[-1]["close"]     # include current month

    return "UP" if last_close > first_close else "DOWN"


def calculate_generic_trend(data):
    return "UP" if data[-1]["close"] > data[0]["close"] else "DOWN"


def fetch_candles(symbols, interval, period, limit):
    result = []
    tickers = " ".join(ns(s) for s in symbols)

    df = yf.download(
        tickers=tickers,
        interval=interval,
        period=period,
        group_by="ticker",
        threads=False,
        progress=False
    )

    for symbol in symbols:
        try:
            sdf = df[ns(symbol)] if len(symbols) > 1 else df
            sdf = sdf.dropna().tail(limit)

            if sdf.empty:
                continue

            data = [
                {
                    "open": round(float(row["Open"]), 2),
                    "close": round(float(row["Close"]), 2)
                }
                for _, row in sdf.iterrows()
            ]

            if len(data) >= 2:
                if interval == "1mo":
                    trend = calculate_monthly_trend(data)
                else:
                    trend = calculate_generic_trend(data)

                result.append({
                    "symbol": symbol,
                    "data": data,
                    "trend": trend
                })

        except Exception:
            continue

    return result


def main():
    cmp_data = []
    monthly_data = []
    weekly_data = []
    daily_data = []

    for batch in chunked(NSE_SYMBOLS, BATCH_SIZE):
        tickers = " ".join(ns(s) for s in batch)

        # CMP
        prices = yf.download(
            tickers=tickers,
            period="1d",
            interval="1d",
            group_by="ticker",
            threads=False,
            progress=False
        )

        for symbol in batch:
            try:
                df = prices[ns(symbol)] if len(batch) > 1 else prices
                close_price = df["Close"].iloc[-1]
                if close_price == close_price:  # NaN check
                    cmp_data.append({
                        "symbol": symbol,
                        "cmp": round(float(close_price), 2)
                    })
            except Exception:
                continue

        # UPDATED PERIODS + LIMIT (4 candles)
        monthly_data.extend(fetch_candles(batch, "1mo", "4mo", 4))
        weekly_data.extend(fetch_candles(batch, "1wk", "1mo", 4))
        daily_data.extend(fetch_candles(batch, "1d", "4d", 4))

        time.sleep(SLEEP_BETWEEN_BATCH)

    with open("cmp.json", "w") as f:
        json.dump(cmp_data, f, indent=2)

    with open("monthly.json", "w") as f:
        json.dump(monthly_data, f, indent=2)

    with open("weekly.json", "w") as f:
        json.dump(weekly_data, f, indent=2)

    with open("daily.json", "w") as f:
        json.dump(daily_data, f, indent=2)


if __name__ == "__main__":
    main()
