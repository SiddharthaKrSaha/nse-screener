import json
from datetime import datetime

from nse_symbols import NSE_SYMBOLS
from fetch_data import get_price_data
from screener import evaluate_stock


OUTPUT_FILE = "results.json"


def main():
    results = []

    for symbol in NSE_SYMBOLS:
        try:
            price_data = get_price_data(symbol)
            result = evaluate_stock(symbol, price_data)

            # result is None if not HIGH or LOW
            if result:
                results.append(result)

        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Saved {len(results)} records to {OUTPUT_FILE}")
    print("Run completed at:", datetime.now())


if __name__ == "__main__":
    main()

