import json
import sys
from pathlib import Path

import requests


SEC_TICKER_URL = "https://www.sec.gov/files/company_tickers.json"
CACHE_PATH = Path("data/raw/sec_company_tickers.json")

HEADERS = {
    "User-Agent": (
        "financial-health-platform student project "
        "samanyu.pathak@gmail.com"
    )
}


def download_ticker_data():
    response = requests.get(SEC_TICKER_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    data = response.json()

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CACHE_PATH, "w") as file:
        json.dump(data, file)

    return data


def load_ticker_data():
    if CACHE_PATH.exists():
        with open(CACHE_PATH, "r") as file:
            return json.load(file)

    return download_ticker_data()


def format_cik(cik_number):
    return str(cik_number).zfill(10)


def lookup_company_by_ticker(ticker):
    ticker = ticker.upper()
    data = load_ticker_data()

    for company in data.values():
        if company["ticker"].upper() == ticker:
            cik = format_cik(company["cik_str"])

            return {
                "ticker": company["ticker"],
                "name": company["title"],
                "cik": cik,
                "facts_url": (
                    "https://data.sec.gov/api/xbrl/companyfacts/"
                    f"CIK{cik}.json"
                ),
            }

    return None


def main():
    if len(sys.argv) < 2:
        raise ValueError("Please provide a ticker, like: AAPL")

    ticker = sys.argv[1]
    company = lookup_company_by_ticker(ticker)

    if company is None:
        print(f"No SEC company found for ticker: {ticker}")
        return

    print("Company Lookup Result")
    print("---------------------")
    print(f"Name: {company['name']}")
    print(f"Ticker: {company['ticker']}")
    print(f"CIK: {company['cik']}")
    print(f"Company Facts URL: {company['facts_url']}")


if __name__ == "__main__":
    main()