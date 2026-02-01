def evaluate_stock(symbol, data):
    """
    Evaluate whether a stock is:
    - HIGH (monthly + weekly + daily highs)
    - LOW  (monthly + weekly + daily lows)

    Returns:
        dict  -> if HIGH or LOW
        None  -> otherwise
    """

    if data is None:
        return None

    monthly = data["monthly"]
    weekly = data["weekly"]
    daily = data["daily"]
    cmp_price = data["cmp"]

    is_monthly_high = cmp_price >= monthly["high"]
    is_weekly_high = cmp_price >= weekly["high"]
    is_daily_high = cmp_price >= daily["high"]

    is_monthly_low = cmp_price <= monthly["low"]
    is_weekly_low = cmp_price <= weekly["low"]
    is_daily_low = cmp_price <= daily["low"]

    # 🟢 ALL HIGHS
    if is_monthly_high and is_weekly_high and is_daily_high:
        status = "HIGH"

    # 🔴 ALL LOWS
    elif is_monthly_low and is_weekly_low and is_daily_low:
        status = "LOW"

    else:
        return None

    return {
        "symbol": symbol,
        "status": status,
        "monthly": monthly,
        "weekly": weekly,
        "daily": daily,
        "cmp": cmp_price
    }
