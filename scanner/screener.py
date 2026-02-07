def evaluate_stock(data):
    if not data:
        return None

    return {
        "symbol": data.get("symbol"),
        "cmp": data.get("cmp"),
        "monthly": data.get("monthly"),
        "weekly": data.get("weekly"),
        "daily": data.get("daily")
    }
