import json
import sys

import requests

from src.config import COMPANIES, DEFAULT_COMPANY
from src.data.company_lookup import lookup_company_by_ticker


HEADERS = {
    "User-Agent": (
        "financial-health-platform student project "
        "samanyu.pathak@gmail.com"
    )
}


def get_company_key():
    if len(sys.argv) > 1:
        return sys.argv[1]

    return DEFAULT_COMPANY


def get_company(company_key):
    company_key_lower = company_key.lower()

    if company_key_lower in COMPANIES:
        return COMPANIES[company_key_lower]

    company = lookup_company_by_ticker(company_key)

    if company is None:
        valid_keys = ", ".join(COMPANIES.keys())
        raise ValueError(
            f"Unknown company or ticker '{company_key}'. "
            f"Configured options: {valid_keys}"
        )

    return {
        "name": company["name"],
        "ticker": company["ticker"],
        "cik": company["cik"],
        "output_prefix": company["ticker"].lower(),
        "facts_url": company["facts_url"],
        "tags": {},
    }


def main():
    company_key = get_company_key()
    company = get_company(company_key)

    url = company["facts_url"]
    output_path = f"data/raw/{company['output_prefix']}_companyfacts.json"

    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()

    data = response.json()

    with open(output_path, "w") as file:
        json.dump(data, file)

    print(f"Saved {company['name']} data to {output_path}")


if __name__ == "__main__":
    main()