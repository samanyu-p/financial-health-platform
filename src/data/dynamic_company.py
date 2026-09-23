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


def classify_company_profile(selected_tags):
    has_inventory = selected_tags.get("inventory") is not None
    has_cost_of_revenue = selected_tags.get("cost_of_revenue") is not None
    has_accounts_payable = selected_tags.get("accounts_payable") is not None
    has_accounts_receivable = selected_tags.get("accounts_receivable") is not None
    has_capex = selected_tags.get("capital_expenditures") is not None

    if has_inventory and has_cost_of_revenue and has_accounts_payable:
        if has_accounts_receivable:
            return {
                "profile": "Inventory-heavy operating business",
                "fit": (
                    "Strong fit for revenue, profitability, free cash flow, "
                    "and working-capital analysis."
                ),
                "interpretation": (
                    "This company reports the main tags needed for retail-style "
                    "working-capital analysis. Metrics like DIO, DPO, and CCC "
                    "can be useful, but they still need business context."
                ),
            }

        return {
            "profile": (
                "Inventory-heavy operating business with partial "
                "working-capital data"
            ),
            "fit": (
                "Good fit for revenue, profitability, free cash flow, DIO, "
                "and DPO. Full CCC is limited."
            ),
            "interpretation": (
                "This company reports inventory and payables, but not the "
                "accounts receivable tag needed for full cash conversion cycle. "
                "The dashboard can still analyze inventory and supplier payment "
                "efficiency."
            ),
        }

    if has_capex:
        return {
            "profile": "Non-retail operating business",
            "fit": (
                "Good fit for revenue, profitability, free cash flow, and "
                "forecasting. Working-capital metrics may be limited."
            ),
            "interpretation": (
                "This company supports core financial analysis, but retail-style "
                "working-capital metrics may be less complete or less meaningful. "
                "Focus more on growth, margins, cash flow, and forecast behavior."
            ),
        }

    return {
        "profile": "Financial or asset-light company",
        "fit": (
            "Best fit for revenue, profitability, and forecasting. Retail "
            "working-capital metrics are likely not appropriate."
        ),
        "interpretation": (
            "This company does not report the operating tags needed for retail "
            "working-capital analysis. That is common for banks, insurers, and "
            "some asset-light companies. The dashboard should not force metrics "
            "like inventory days or cash conversion cycle when the business "
            "model does not support them."
        ),
    }


def analyze_ticker_support(ticker):
    company, facts = fetch_company_facts_by_ticker(ticker)

    if company is None:
        return None

    us_gaap = facts["facts"]["us-gaap"]
    selected_tags = find_available_tags(us_gaap)
    supported_analyses = get_supported_analyses(selected_tags)
    company_profile = classify_company_profile(selected_tags)

    return {
        "company": company,
        "selected_tags": selected_tags,
        "supported_analyses": supported_analyses,
        "company_profile": company_profile,
    }