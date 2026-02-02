import json

# HARD-CODED TEST (NO NSE_SYMBOLS)
TEST_SYMBOLS = ["RELIANCE", "TCS", "INFY"]

def main():
    results = []

    for sym in TEST_SYMBOLS:
        results.append({
            "symbol": sym,
            "monthly": {"high": "", "low": ""},
            "weekly": {"high": "", "low": ""},
            "daily": {"high": "", "low": ""},
            "cmp": 123.45,
            "signal": "ALL"
        })

    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("Hardcoded test completed")

if __name__ == "__main__":
    main()
