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


# -------------------------------------------------
# CANDLE TYPE
# -------------------------------------------------

def candle_type(candle):

    if candle["close"] > candle["open"]:
        return "GREEN"

    elif candle["close"] < candle["open"]:
        return "RED"

    return "DOJI"


# -------------------------------------------------
# CUSTOM TREND LOGIC
# -------------------------------------------------

def calculate_custom_trend(data):

    """
    LOGIC:

    1. If today's candle is GREEN:
       today's close >
       open of last formed RED candle

    2. If today's candle is RED:
       today's close <
       open of last formed GREEN candle
    """

    if len(data) < 2:
        return "SIDEWAYS"

    today = data[-1]

    today_type = candle_type(today)

    # -----------------------------------------
    # TODAY GREEN
    # -----------------------------------------

    if today_type == "GREEN":

        for previous in reversed(data[:-1]):

            if candle_type(previous) == "RED":

                if today["close"] > previous["open"]:
                    return "UP"

                return "SIDEWAYS"

        return "SIDEWAYS"

    # -----------------------------------------
    # TODAY RED
    # -----------------------------------------

    elif today_type == "RED":

        for previous in reversed(data[:-1]):

            if candle_type(previous) == "GREEN":

                if today["close"] < previous["open"]:
                    return "DOWN"

                return "SIDEWAYS"

        return "SIDEWAYS"

    return "SIDEWAYS"

# -------------------------------------------------
# LAST GREEN / RED OPEN
# -------------------------------------------------

def get_last_green_red_opens(data):

    last_green_open = None
    last_red_open = None

    # Exclude today's candle
    for candle in reversed(data[:-1]):

        ctype = candle_type(candle)

        if last_green_open is None and ctype == "GREEN":
            last_green_open = candle["open"]

        if last_red_open is None and ctype == "RED":
            last_red_open = candle["open"]

        if (
            last_green_open is not None
            and last_red_open is not None
        ):
            break

    return last_green_open, last_red_open

# -------------------------------------------------
# WEEKLY FILTER
# -------------------------------------------------

def process_weekly_data(data):

    """
    Include current week candle only
    if today is Wednesday-Friday
    """

    weekday = datetime.now().weekday()

    # Monday=0 Tuesday=1 Wednesday=2 Thursday=3 Friday=4

    if weekday >= 2:
        return data

    # Exclude current week candle
    return data[:-1]


# -------------------------------------------------
# MONTHLY FILTER
# -------------------------------------------------

def process_monthly_data(data):

    """
    If date < 16
    exclude current month candle
    """

    today = datetime.now().day

    if today >= 16:
        return data

    return data[:-1]


# -------------------------------------------------
# FETCH CANDLES
# -------------------------------------------------

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

            # -----------------------------------------
            # WEEKLY FILTER
            # -----------------------------------------

            if interval == "1wk":
                data = process_weekly_data(data)

            # -----------------------------------------
            # MONTHLY FILTER
            # -----------------------------------------

            elif interval == "1mo":
                data = process_monthly_data(data)

            if len(data) < 2:
                continue

            trend = calculate_custom_trend(data)

last_green_open, last_red_open = get_last_green_red_opens(data)

result.append({
    "symbol": symbol,
    "data": data,
    "trend": trend,
    "last_green_open": last_green_open,
    "last_red_open": last_red_open
})

        except Exception:
            continue

    return result


# -------------------------------------------------
# MAIN
# -------------------------------------------------

def main():

    cmp_data = []

    monthly_data = []
    weekly_data = []
    daily_data = []

    for batch in chunked(NSE_SYMBOLS, BATCH_SIZE):

        tickers = " ".join(ns(s) for s in batch)

        # -----------------------------------------
        # CMP
        # -----------------------------------------

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

                if close_price == close_price:

                    cmp_data.append({
                        "symbol": symbol,
                        "cmp": round(float(close_price), 2)
                    })

            except Exception:
                continue

        # -----------------------------------------
        # MONTHLY
        # -----------------------------------------

        monthly_data.extend(
            fetch_candles(
                batch,
                interval="1mo",
                period="8mo",
                limit=8
            )
        )

        # -----------------------------------------
        # WEEKLY
        # -----------------------------------------

        weekly_data.extend(
            fetch_candles(
                batch,
                interval="1wk",
                period="4mo",
                limit=16
            )
        )

        # -----------------------------------------
        # DAILY
        # -----------------------------------------

        daily_data.extend(
            fetch_candles(
                batch,
                interval="1d",
                period="20d",
                limit=20
            )
        )

        time.sleep(SLEEP_BETWEEN_BATCH)

    # -------------------------------------------------
    # SAVE FILES
    # -------------------------------------------------

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
