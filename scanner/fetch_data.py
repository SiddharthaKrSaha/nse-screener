import yfinance as yf


def get_price_data(symbol: str):
    """
    DEBUG MODE:
    Fetch CMP only for ALL NSE symbols
    """

    try:
        yahoo_symbol = symbol if symbol.endswith(".NS") else symbol + ".NS"

        df = yf.download(
            yahoo_symbol,
            period="5d",
            interval="1d",
            progress=False
        )

        if df.empty:
            return None

        df = df.dropna()

        cmp_price = float(df["Close"].iloc[-1])

        return {
            "symbol": symbol,
            "cmp": round(cmp_price, 2)
        }

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None
