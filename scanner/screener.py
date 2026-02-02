def evaluate_stock(data):
    """
    TEMP MODE (CMP ONLY)

    Always return stock data so website can render:
    - symbol
    - cmp

    High/Low logic will be re-enabled later.
    """

    if not data:
        return None

    # Ensure required keys exist
    return {
        "symbol": data.get("symbol"),
        "cmp": data.get("cmp"),

        # Keep columns for website, but blank
        "monthly_high": "",
        "monthly_low": "",
        "weekly_high": "",
        "weekly_low": "",
        "daily_high": "",
        "daily_low": "",
        "signal": ""
    }
