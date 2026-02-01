import yfinance as yf


def get_price_data(symbol: str):
    """
    Logic implemented exactly as specified:

    Monthly High  : Highest HIGH of last 30 trading days
    Weekly High   : Highest HIGH of last 7 trading days
    Daily High    : Previous day's HIGH

    Monthly Low   : Lowest LOW of last 30 trading days
    Weekly Low    : Lowest LOW of last 7 trading days
    Daily Low     : Previous day's LOW

    CMP           : Latest closing price
    """

    try:
        df = yf.download(
            symbol,
            period="3mo",        # enough data to safely get 30 sessions
            interval="1d",
            progress=False
        )

        if df.empty or len(df) < 31:
            return None

        df = df.dropna()

        # ---------------- CMP ----------------
        cmp_price = float(df["Close"].iloc[-1])

        # ---------------- PREVIOUS DAY ----------------
        prev_day = df.iloc[-2]
        prev_day_high = float(prev_day["High"])
        prev_day_low = float(prev_day["Low"])

        # ---------------- WEEKLY (last 7 sessions, excluding today) ----------------
        weekly_df = df.iloc[-8:-1]
        weekly_high = float(weekly_df["High"].max())
        weekly_low = float(weekly_df["Low"].min())

        # ---------------- MONTHLY (last 30 sessions, excluding today) ----------------
        monthly_df = df.iloc[-31:-1]
        monthly_high = float(monthly_df["High"].max())
        monthly_low = float(monthly_df["Low"].min())

        return {
            "symbol": symbol.replace(".NS", ""),

            "cmp": round(cmp_price, 2),

            "monthly": {
                "high": round(monthly_high, 2),
                "low": round(monthly_low, 2)
            },

            "weekly": {
                "high": round(weekly_high, 2),
                "low": round(weekly_low, 2)
            },

            "daily": {
                "high": round(prev_day_high, 2),
                "low": round(prev_day_low, 2)
            }
        }

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None
