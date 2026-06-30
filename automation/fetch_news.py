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

    for item in news:

        company = item["company"].upper()

        symbol = company_map.get(company)

        if not symbol:
            continue

        if symbol not in screener_symbols:
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

    with open(NEWS_FILE, "w", encoding="utf-8") as f:

        json.dump(
            {
                "last_updated": __import__("datetime").datetime.now().isoformat(),
                "count": len(news),
                "news": news
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
