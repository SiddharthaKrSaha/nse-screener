import json
from fetch_data import fetch_stock_data
from nse_symbols import NSE_SYMBOLS

results = []

print(f"Total symbols: {len(NSE_SYMBOLS)}")

for symbol in NSE_SYMBOLS[:50]:   # LIMIT to 50 for speed
    data = fetch_stock_data(symbol)

    if data:
        results.append(data)

print(f"Fetched data count: {len(results)}")

# Save directly to root for website
with open("results.json", "w") as f:
    json.dump(results, f, indent=2)

print("Saved results.json")
