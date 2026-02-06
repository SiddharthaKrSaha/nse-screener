import json
import time
import yfinance as yf
from nse_symbols import NSE_SYMBOLS

BATCH_SIZE = 50
SLEEP_BETWEEN_BATCH = 30  # seconds

def ns(symbol):
    return symbol if symbol.endswith(".NS") else symbol + ".NS"

def chunked(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def calculate_trend(data):
    # data = list of {"open": x, "close": y}
    trend = "DOWN"
    for i in range(1, len(data)):
        if data[i]["close"] > data[i - 1]["open"]:
            trend = "UP"
        else:
            trend = "DOWN"
    return trend


def fetch_candles(symbols, interval, period):
    result = []
    tickers = " ".join(symbols)
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
            sdf = sdf.dropna()
            data = []
            for _, row in sdf.iterrows():
                data.append({
                    "open": round(float(row["Open"]), 2),
                    "close": round(float(row["Close"]), 2)
                })

            if len(data) >= 2:
                result.append({
                    "symbol": symbol,
                    "data": data,
                    "trend": calculate_trend(data)
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
        tickers = " ".join(batch)

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
                cmp_data.append({
                    "symbol": symbol,
                    "cmp": round(float(close_price), 2)
                })
            except Exception:
                continue

        # Monthly / Weekly / Daily
        monthly_data.extend(fetch_candles(batch, "1mo", "6mo"))
        weekly_data.extend(fetch_candles(batch, "1wk", "6wk"))
        daily_data.extend(fetch_candles(batch, "1d", "6d"))

        time.sleep(SLEEP_BETWEEN_BATCH)

    # Write files
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
