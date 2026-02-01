def evaluate_stock(data):
    """
    Evaluates stock based on clarified logic:

    HIGH:
      CMP > last 30-day high
      CMP > last 7-day high
      CMP > previous day's high

    LOW:
      CMP < last 30-day low
      CMP < last 7-day low
      CMP < previous day's low
    """

    if not data:
        return None

    cmp_price = data["cmp"]

    monthly_high = data["monthly"]["high"]
    weekly_high = data["weekly"]["high"]
    daily_high = data["daily"]["high"]

    monthly_low = data["monthly"]["low"]
    weekly_low = data["weekly"]["low"]
    daily_low = data["daily"]["low"]

    # 🟢 HIGH CONDITION
    if (
        cmp_price > monthly_high and
        cmp_price > weekly_high and
        cmp_price > daily_high
    ):
        data["signal"] = "HIGH"
        return data

    # 🔴 LOW CONDITION
    if (
        cmp_price < monthly_low and
        cmp_price < weekly_low and
        cmp_price < daily_low
    ):
        data["signal"] = "LOW"
        return data

    return None
