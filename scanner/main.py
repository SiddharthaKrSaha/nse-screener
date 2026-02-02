import json
from datetime import datetime

from nse_symbols import NSE_SYMBOLS

OUTPUT_FILE = "output/results.json"


def main():
    results = []

    for symbol in NSE_SYMBOLS:
        results.append({
            "symbol": symbol.replace(".NS", ""),
            "monthly": {"high": "", "low": ""},
            "weekly": {"high": "", "low": ""},
            "daily": {"high": "", "low": ""},
            "cmp": 123.45,
            "signal": "ALL"
        })

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"FORCED WRITE: {len(results)} symbols")
    print("Run completed at:", datetime.now())


if __name__ == "__main__":
    main()
