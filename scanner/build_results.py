import json
from nse_symbols import NSE_SYMBOLS


def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return []


def to_map(data, key="symbol"):
    return {item[key]: item for item in data}


def main():
    cmp_data = to_map(load_json("cmp.json"))
    daily_data = to_map(load_json("daily.json"))
    weekly_data = to_map(load_json("weekly.json"))
    monthly_data = to_map(load_json("monthly.json"))

    results = []

    for symbol in NSE_SYMBOLS:
        if (
            symbol not in cmp_data
            or symbol not in daily_data
            or symbol not in weekly_data
            or symbol not in monthly_data
        ):
            continue

        d_trend = daily_data[symbol]["trend"]
        w_trend = weekly_data[symbol]["trend"]
        m_trend = monthly_data[symbol]["trend"]

        # keep only ALL UP or ALL DOWN
        if d_trend == w_trend == m_trend:
            results.append({
                "symbol": symbol,
                "cmp": cmp_data[symbol]["cmp"],
                "monthly": m_trend,
                "weekly": w_trend,
                "daily": d_trend
            })

    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"results.json written with {len(results)} symbols")


if __name__ == "__main__":
    main()

