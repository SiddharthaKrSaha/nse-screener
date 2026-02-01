def evaluate_stock(stock):
    """
    TEMP DEBUG VERSION
    Returns every stock so we can verify pipeline + website
    """

    return {
        "symbol": stock["symbol"],
        "monthly": stock["monthly"],
        "weekly": stock["weekly"],
        "daily": stock["daily"],
        "cmp": stock["cmp"],
        "signal": "TEST"
    }
