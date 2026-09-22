import json
import sys
from pathlib import Path

from src.config import COMPANIES, DEFAULT_COMPANY
from src.data.company_lookup import lookup_company_by_ticker


TAG_CANDIDATES = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "SalesRevenueNet",
        "Revenues",
    ],
    "cost_of_revenue": [
        "CostOfRevenue",
        "CostOfGoodsAndServicesSold",
        "CostOfGoodsSold",
    ],
    "accounts_receivable": [
        "AccountsReceivableNet",
        "AccountsReceivableNetCurrent",
    ],
    "inventory": [
        "InventoryNet",
        "InventoryFinishedGoodsNetOfReserves",
        "InventoryRawMaterialsAndSuppliesNetOfReserves",
    ],
    "accounts_payable": [
        "AccountsPayableCurrent",
        "AccountsPayable",
    ],
    "operating_income": [
        "OperatingIncomeLoss",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
    ],
    "operating_cash_flow": [
        "NetCashProvidedByUsedInOperatingActivities",
        "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
    ],
    "capital_expenditures": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
    ],
}


ANALYSIS_REQUIREMENTS = {
    "profitability": [
        "revenue",
        "operating_income",
    ],
    "free_cash_flow": [
        "operating_cash_flow",
        "capital_expenditures",
    ],
    "working_capital_partial": [
        "revenue",
        "cost_of_revenue",
        "inventory",
        "accounts_payable",
    ],
    "cash_conversion_cycle_full": [
        "revenue",
        "cost_of_revenue",
        "accounts_receivable",
        "inventory",
        "accounts_payable",
    ],
    "revenue_forecast": [
        "revenue",
    ],
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


def find_available_tags(us_gaap):
    selected_tags = {}

    for metric, candidates in TAG_CANDIDATES.items():
        found_tag = None

        for tag in candidates:
            if tag in us_gaap:
                found_tag = tag
                break

        selected_tags[metric] = found_tag

    return selected_tags


def print_tag_results(selected_tags):
    for metric, tag in selected_tags.items():
        if tag:
            print(f"{metric}: FOUND -> {tag}")
        else:
            print(f"{metric}: MISSING")


def print_supported_analyses(selected_tags):
    print()
    print("Supported analyses:")
    for analysis_name, required_metrics in ANALYSIS_REQUIREMENTS.items():
        missing_metrics = [
            metric for metric in required_metrics if not selected_tags[metric]
        ]

        if missing_metrics:
            missing_text = ", ".join(missing_metrics)
            print(f"- {analysis_name}: NO, missing {missing_text}")
        else:
            print(f"- {analysis_name}: YES")


def print_suggested_config(selected_tags):
    print()
    print("Suggested config tag mapping:")
    print("{")
    for metric, tag in selected_tags.items():
        if tag:
            print(f'    "{metric}": "{tag}",')
        else:
            print(f'    "{metric}": None,')
    print("}")


def main():
    company_key = get_company_key()
    company = get_company(company_key)
    input_path = Path(
        f"data/raw/{company['output_prefix']}_companyfacts.json"
    )

    if not input_path.exists():
        raise FileNotFoundError(
            f"Missing {input_path}. Run fetch_data first for {company_key}."
        )

    with open(input_path, "r") as file:
        data = json.load(file)

    us_gaap = data["facts"]["us-gaap"]

    print(f"Tag Compatibility Check: {company['name']}")
    print("-" * 50)

    selected_tags = find_available_tags(us_gaap)

    print_tag_results(selected_tags)
    print_supported_analyses(selected_tags)
    print_suggested_config(selected_tags)


if __name__ == "__main__":
    main()