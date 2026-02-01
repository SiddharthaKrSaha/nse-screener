import json
from datetime import datetime

from nse_symbols import NSE_SYMBOLS
from fetch_data import get_price_data

OUTPUT_FILE = "results.json"


def main():
    results = []

    for symbol in NSE_SYMBOLS:
        try:
            data = get_price_data(symbol)

            if not data:
                continue

            # ONLY SYMBOL + CMP (everything else blank)
            results.append({
                "symbol": data["symbol"],
                "monthly": {"high": "", "low": ""},
                "weekly": {"high": "", "low": ""},
                "daily": {"high": "", "low": ""},
                "cmp": data["cmp"],
                "signal": "ALL"
            })

        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Saved {len(results)} symbols to {OUTPUT_FILE}")
    print("Run completed at:", datetime.now())


if __name__ == "__main__":
    main()
