import json
from datetime import datetime

from nse_symbols import NSE_SYMBOLS
from fetch_data import get_price_data

OUTPUT_FILE = "results.json"


def main():
    results = []

    for symbol in NSE_SYMBOLS:
        try:
            price_data = get_price_data(symbol)

            if not price_data:
                continue

            # TEMP: push ALL symbols with CMP only
            results.append({
                "symbol": symbol.replace(".NS", ""),
                "monthly": {"high": "", "low": ""},
                "weekly": {"high": "", "low": ""},
                "daily": {"high": "", "low": ""},
                "cmp": price_data["cmp"],
                "signal": "ALL"
            })

        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Saved {len(results)} records to {OUTPUT_FILE}")
    print("Run completed at:", datetime.now())


if __name__ == "__main__":
    main()
