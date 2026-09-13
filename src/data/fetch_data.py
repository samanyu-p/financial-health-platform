import json
import requests

url = "https://data.sec.gov/api/xbrl/companyfacts/CIK0000104169.json"

headers = {
    "User-Agent": "financial-health-platform student project samanyu.pathak@gmail.com"
}

response = requests.get(url, headers=headers, timeout=30)
response.raise_for_status()

data = response.json()

output_path = "data/raw/walmart_companyfacts.json"

with open(output_path, "w") as file:
    json.dump(data, file)

print(f"Saved Walmart data to {output_path}")