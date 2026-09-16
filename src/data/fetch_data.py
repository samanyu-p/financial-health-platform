import json
import sys

import requests

from src.config import COMPANIES, DEFAULT_COMPANY


def get_company_key():
    if len(sys.argv) > 1:
        return sys.argv[1]

    return DEFAULT_COMPANY


def main():
    company_key = get_company_key()

    if company_key not in COMPANIES:
        valid_keys = ", ".join(COMPANIES.keys())
        raise ValueError(f"Unknown company '{company_key}'. Valid options: {valid_keys}")

    company = COMPANIES[company_key]

    url = company["facts_url"]
    output_path = f"data/raw/{company['output_prefix']}_companyfacts.json"

    headers = {
        "User-Agent": (
            "financial-health-platform student project "
            "samanyu.pathak@gmail.com"
        )
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    data = response.json()

    with open(output_path, "w") as file:
        json.dump(data, file)

    print(f"Saved {company['name']} data to {output_path}")


if __name__ == "__main__":
    main()