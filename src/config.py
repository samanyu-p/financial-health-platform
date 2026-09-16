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
    }
}


DEFAULT_COMPANY = "walmart"