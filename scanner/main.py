import json
from datetime import datetime
import yfinance as yf
from nse_symbols import NSE_SYMBOLS

CHUNK_SIZE = 50
OUTPUT_FILE = "output/results.json"
ROOT_OUTPUT_FILE = "results.json"


def chunk_symbols(symbols, size):
    for i in range(0, len(symbols), size):
        yield symbols[i:i + size]


def main():
    results = []

    for chunk in chunk_symbols(NSE_SYMBOLS, CHUNK_SIZE):
        symbols_str = " ".join([s + ".NS" for s in chunk])

        try:
            df = yf.download(
                symbols_str,
                period="1d",
                interval="1d",
                group_by="ticker",
                progress=False
            )

            for symbol in chunk:
                try:
                    ticker = symbol + ".NS"
                    close_price = df[ticker]["Close"].iloc[-1]

                    results.append({
                        "symbol": symbol,
                        "cmp": round(float(close_price), 2)
                    })

                except Exception:
                    continue

        except Exception:
            continue

    # write to output folder
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    # write to root for website
    with open(ROOT_OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Saved {len(results)} symbols")
    print("Run completed at:", datetime.now())


if __name__ == "__main__":
    main()
