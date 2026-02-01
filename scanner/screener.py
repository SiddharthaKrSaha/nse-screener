import json
import time

from scanner.nse_symbols import NSE_SYMBOLS
from scanner.fetch_data import fetch_stock_data


OUTPUT_FILE = "website/results.json"


def run_screener():
    results = []

    for symbol in NSE_SYMBOLS:
        data = fetch_stock_data(symbol)

        # Skip if no data
        if not data:
            continue

        cmp_price = data["cmp"]

        monthly_high = data["monthly"]["high"]
        monthly_low = data["monthly"]["low"]

        weekly_high = data["weekly"]["high"]
        weekly_low = data["weekly"]["low"]

        daily_high = data["daily"]["high"]
        daily_low = data["daily"]["low"]

        status = "NONE"

        # -------- HIGH CONDITION --------
        if (
            cmp_price >= monthly_high
            and cmp_price >= weekly_high
            and cmp_price >= daily_high
        ):
            status = "HIGH"

        # -------- LOW CONDITION --------
        elif (
            cmp_price <= monthly_low
            and cmp_price <= weekly_low
            and cmp_price <= daily_low
        ):
            status = "LOW"

        # -------- SAVE RESULT --------
        results.append({
            "symbol": data["symbol"],
            "monthly": data["monthly"],
            "weekly": data["weekly"],
            "daily": data["daily"],
            "cmp": cmp_price,
            "status": status
        })

        # Be polite to Yahoo Finance
        time.sleep(0.25)

    # Write output for website
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Screener completed. {len(results)} stocks processed.")


if __name__ == "__main__":
    run_screener()

