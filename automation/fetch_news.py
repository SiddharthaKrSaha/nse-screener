from datetime import datetime, timedelta
import json
import csv
import re
from difflib import get_close_matches
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

def normalize_name(name):

    name = name.upper()

    words_to_remove = [
        "LIMITED",
        "LTD",
        "LIMITED.",
        "INDIA",
        "CORPORATION",
        "CORP",
        "COMPANY",
        "CO",
        "TECHNOLOGIES",
        "TECHNOLOGY",
        "INDUSTRIES",
        "INDUSTRY",
        "SERVICES",
        "SERVICE",
        "INTERNATIONAL",
        "INTL",
        "&",
        "AND"
    ]

    name = re.sub(r"[^A-Z0-9 ]", " ", name)

    parts = []

    for word in name.split():

        if word not in words_to_remove:

            parts.append(word)

    return " ".join(parts)


def load_company_master():

    mapping = {}

    with open(MASTER_FILE, encoding="utf-8-sig") as f:

        reader = csv.reader(f)

        next(reader)

        for row in reader:

            if len(row) < 2:
                continue

            symbol = row[0].strip().upper()

            company = normalize_name(row[1])

            mapping[company] = symbol

    return mapping

def fetch_groww_page():

    response = requests.get(
        GROWW_URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.text


def extract_news(html):

    soup = BeautifulSoup(html, "html.parser")

    cards = soup.select("a.stockNewsCard_container__H_UnU")

    news = []

    for card in cards:

        company_tag = card.select_one("a.stockNewsCard_companyName__PxGAY")

        desc_tag = card.select_one(
            "div.stockNewsCard_newsCardDescription__XfSUb span"
        )

        time_tag = card.select_one(
            "div.flex.bodySmall.contentSecondary"
        )

        if not company_tag or not desc_tag:
            continue

        company = company_tag.get_text(strip=True)

        headline = desc_tag.get_text(
            " ",
            strip=True
        )

        href = card.get("href", "")

        if href.startswith("/"):
            href = "https://groww.in" + href

        news.append({
            "company": company,
            "headline": headline,
            "time": time_tag.get_text(strip=True) if time_tag else "",
            "url": href
        })

    return news

def map_symbols(news, company_map, screener_symbols):

    final_news = []

    company_names = list(company_map.keys())

    for item in news:

        company = normalize_name(item["company"])

        symbol = company_map.get(company)

        if not symbol:

            match = get_close_matches(
                company,
                company_names,
                n=1,
                cutoff=0.55
            )

            if match:

                symbol = company_map[match[0]]

                print(
                    "FUZZY MATCH:",
                    item["company"],
                    "->",
                    match[0],
                    "->",
                    symbol
                )

            else:

                print("NOT FOUND:", item["company"])

                continue

        if symbol not in screener_symbols:

            print("NOT IN SCREENER:", symbol)

            continue

        final_news.append({

            "symbol": symbol,

            "company": item["company"],

            "headline": item["headline"],

            "time": item["time"],

            "url": item["url"]

        })

    return final_news

def save_news(news):

    now = datetime.now()

    cutoff = now - timedelta(days=1)

    old_news = []

    if NEWS_FILE.exists():

        try:

            with open(NEWS_FILE, encoding="utf-8") as f:

                data = json.load(f)

                old_news = data.get("news", [])

        except:

            old_news = []

    merged = []

    for item in old_news:

        try:

            created = datetime.fromisoformat(item["created"])

        except:

            continue

        expiry = created + timedelta(days=1)

        expiry = expiry.replace(hour=16,
                                minute=0,
                                second=0,
                                microsecond=0)

        if now < expiry:

            merged.append(item)

    existing_keys = {

        (
            x["symbol"],
            x["headline"]
        )

        for x in merged

    }

    for item in news:

        key = (

            item["symbol"],
            item["headline"]

        )

        if key in existing_keys:

            continue

        item["created"] = now.isoformat()

        merged.append(item)

    with open(NEWS_FILE, "w", encoding="utf-8") as f:

        json.dump(

            {

                "last_updated": now.isoformat(),

                "count": len(merged),

                "news": merged

            },

            f,

            indent=4,

            ensure_ascii=False

        )

def main():

    print("Loading screener symbols...")
    screener_symbols = load_results()

    print("Loading company master...")
    company_map = load_company_master()

    print("Downloading Groww page...")
    html = fetch_groww_page()
    with open(ROOT / "groww_page.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Extracting news...")
    news = extract_news(html)
    
    print("News extracted:", len(news))
    print(news[:10])
    
    print(f"Found {len(news)} Groww news items")

    print("Mapping symbols...")
    mapped_news = map_symbols(
        news,
        company_map,
        screener_symbols
    )

    print(f"Matched {len(mapped_news)} screener stocks")

    save_news(mapped_news)

    print("news.json updated successfully.")


if __name__ == "__main__":
    main()
