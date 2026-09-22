import requests

from src.data.check_tags import ANALYSIS_REQUIREMENTS, find_available_tags
from src.data.company_lookup import lookup_company_by_ticker


HEADERS = {
    "User-Agent": (
        "financial-health-platform student project "
        "samanyu.pathak@gmail.com"
    )
}


def fetch_company_facts_by_ticker(ticker):
    company = lookup_company_by_ticker(ticker)

    if company is None:
        return None, None

    response = requests.get(
        company["facts_url"],
        headers=HEADERS,
        timeout=30,
    )
    response.raise_for_status()

    return company, response.json()


def get_supported_analyses(selected_tags):
    supported = {}

    for analysis_name, required_metrics in ANALYSIS_REQUIREMENTS.items():
        missing_metrics = [
            metric for metric in required_metrics if not selected_tags[metric]
        ]

        supported[analysis_name] = {
            "is_supported": len(missing_metrics) == 0,
            "missing_metrics": missing_metrics,
        }

    return supported


def analyze_ticker_support(ticker):
    company, facts = fetch_company_facts_by_ticker(ticker)

    if company is None:
        return None

    us_gaap = facts["facts"]["us-gaap"]
    selected_tags = find_available_tags(us_gaap)
    supported_analyses = get_supported_analyses(selected_tags)

    return {
        "company": company,
        "selected_tags": selected_tags,
        "supported_analyses": supported_analyses,
    }