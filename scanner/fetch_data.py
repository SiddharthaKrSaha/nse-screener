import yfinance as yf


def get_price_data(symbol: str):
    """
    Fetch last 2 months of DAILY data from Yahoo Finance
    and calculate Monthly / Weekly / Daily High & Low
    """

    try:
        df = yf.download(
            symbol,
            period="2mo",
            interval="1d",
            progress=False
        )

        # If no data returned
        if df.empty:
            return None

        df = df.dropna()

        # ---------------- DAILY ----------------
        daily_high = float(df["High"].iloc[-1])
        daily_low = float(df["Low"].iloc[-1])
        cmp_price = float(df["Close"].iloc[-1])

        # ---------------- WEEKLY (last 5 sessions) ----------------
        weekly_df = df.tail(5)
        weekly_high = float(weekly_df["High"].max())
        weekly_low = float(weekly_df["Low"].min())

        # ---------------- MONTHLY (last ~22 sessions) ----------------
        monthly_df = df.tail(22)
        monthly_high = float(monthly_df["High"].max())
        monthly_low = float(monthly_df["Low"].min())

        return {
            "symbol": symbol,   # keep .NS for consistency

            "monthly": {
                "high": round(monthly_high, 2),
                "low": round(monthly_low, 2)
            },

            "weekly": {
                "high": round(weekly_high, 2),
                "low": round(weekly_low, 2)
            },

            "daily": {
                "high": round(daily_high, 2),
                "low": round(daily_low, 2)
            },

            "cmp": round(cmp_price, 2)
        }

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None
