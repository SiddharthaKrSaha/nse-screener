import json
import csv
import requests
from bs4 import BeautifulSoup
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RESULTS_FILE = ROOT / "results.json"
MASTER_FILE = ROOT / "company_master.csv"
NEWS_FILE = ROOT / "news.json"

GROWW_URL = "https://groww.in/market-news/stocks"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0 Safari/537.36"
    )
}

def load_results():

    with open(RESULTS_FILE, encoding="utf-8") as f:
        data = json.load(f)

    return {x["symbol"] for x in data}

def load_company_master():

    mapping = {}

    with open(MASTER_FILE, encoding="utf-8-sig") as f:

        reader = csv.reader(f)

        next(reader)

        for row in reader:

            if len(row) < 2:
                continue

            symbol = row[0].strip().upper()
            company = row[1].strip().upper()

            mapping[company] = symbol

    return mapping
