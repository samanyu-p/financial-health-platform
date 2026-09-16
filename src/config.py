COMPANIES = {
    "walmart": {
        "name": "Walmart Inc.",
        "ticker": "WMT",
        "cik": "0000104169",
        "output_prefix": "walmart",
        "facts_url": "https://data.sec.gov/api/xbrl/companyfacts/CIK0000104169.json",
        "tags": {
            "revenue": "RevenueFromContractWithCustomerExcludingAssessedTax",
            "cost_of_revenue": "CostOfRevenue",
            "accounts_receivable": "AccountsReceivableNet",
            "inventory": "InventoryNet",
            "accounts_payable": "AccountsPayableCurrent",
            "operating_income": "OperatingIncomeLoss",
            "operating_cash_flow": "NetCashProvidedByUsedInOperatingActivities",
            "capital_expenditures": "PaymentsToAcquirePropertyPlantAndEquipment",
        },
    },
    "target": {
        "name": "Target Corporation",
        "ticker": "TGT",
        "cik": "0000027419",
        "output_prefix": "target",
        "facts_url": "https://data.sec.gov/api/xbrl/companyfacts/CIK0000027419.json",
        "tags": {
            "revenue": "RevenueFromContractWithCustomerExcludingAssessedTax",
            "cost_of_revenue": "CostOfGoodsAndServicesSold",
            "accounts_receivable": None,
            "inventory": "InventoryNet",
            "accounts_payable": "AccountsPayableCurrent",
            "operating_income": "OperatingIncomeLoss",
            "operating_cash_flow": "NetCashProvidedByUsedInOperatingActivities",
            "capital_expenditures": "PaymentsToAcquirePropertyPlantAndEquipment",
        },
    },
    "costco": {
        "name": "Costco Wholesale Corporation",
        "ticker": "COST",
        "cik": "0000909832",
        "output_prefix": "costco",
        "facts_url": "https://data.sec.gov/api/xbrl/companyfacts/CIK0000909832.json",
        "tags": {
            "revenue": "RevenueFromContractWithCustomerExcludingAssessedTax",
            "cost_of_revenue": "CostOfGoodsAndServicesSold",
            "accounts_receivable": None,
            "inventory": "InventoryNet",
            "accounts_payable": "AccountsPayableCurrent",
            "operating_income": "OperatingIncomeLoss",
            "operating_cash_flow": "NetCashProvidedByUsedInOperatingActivities",
            "capital_expenditures": "PaymentsToAcquirePropertyPlantAndEquipment",
        },
    },
}


DEFAULT_COMPANY = "walmart"