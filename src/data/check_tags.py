import json

from src.config import COMPANIES, DEFAULT_COMPANY


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


def main():
    company = COMPANIES[DEFAULT_COMPANY]
    input_path = f"data/raw/{company['output_prefix']}_companyfacts.json"

    with open(input_path, "r") as file:
        data = json.load(file)

    us_gaap = data["facts"]["us-gaap"]

    print(f"Tag Compatibility Check: {company['name']}")
    print("-" * 50)

    selected_tags = {}

    for metric, candidates in TAG_CANDIDATES.items():
        found_tag = None

        for tag in candidates:
            if tag in us_gaap:
                found_tag = tag
                break

        selected_tags[metric] = found_tag

        if found_tag:
            print(f"{metric}: FOUND -> {found_tag}")
        else:
            print(f"{metric}: MISSING")

    print()
    print("Suggested config tag mapping:")
    print("{")
    for metric, tag in selected_tags.items():
        if tag:
            print(f'    "{metric}": "{tag}",')
        else:
            print(f'    "{metric}": None,')
    print("}")


if __name__ == "__main__":
    main()