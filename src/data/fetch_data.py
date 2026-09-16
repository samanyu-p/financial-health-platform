import json

import requests

from src.config import COMPANIES, DEFAULT_COMPANY


company = COMPANIES[DEFAULT_COMPANY]

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