import pandas as pd


INPUT_PATH = "data/processed/walmart_financial_health.csv"
OUTPUT_PATH = "data/processed/walmart_scenario_analysis.csv"


SCENARIOS = [
    {
        "scenario": "Downside",
        "revenue_growth": 0.02,
        "operating_margin": 0.038,
        "dso": 2.7,
        "dio": 42.0,
        "dpo": 40.0,
        "ocf_margin": 0.052,
        "capex_as_percent_of_ocf": 0.70,
    },
    {
        "scenario": "Base",
        "revenue_growth": 0.045,
        "operating_margin": 0.042,
        "dso": 2.4,
        "dio": 39.5,
        "dpo": 41.5,
        "ocf_margin": 0.059,
        "capex_as_percent_of_ocf": 0.64,
    },
    {
        "scenario": "Upside",
        "revenue_growth": 0.065,
        "operating_margin": 0.046,
        "dso": 2.2,
        "dio": 38.0,
        "dpo": 42.5,
        "ocf_margin": 0.063,
        "capex_as_percent_of_ocf": 0.58,
    },
]


def main():
    financial_health = pd.read_csv(INPUT_PATH)
    financial_health["end"] = pd.to_datetime(financial_health["end"])
    financial_health = financial_health.sort_values("end")

    latest_year = financial_health.iloc[-1]
    latest_revenue = latest_year["revenue"]
    next_year = latest_year["end"].year + 1

    results = []

    for scenario in SCENARIOS:
        projected_revenue = latest_revenue * (1 + scenario["revenue_growth"])
        projected_operating_income = (
            projected_revenue * scenario["operating_margin"]
        )

        projected_ccc = scenario["dso"] + scenario["dio"] - scenario["dpo"]

        projected_operating_cash_flow = (
            projected_revenue * scenario["ocf_margin"]
        )
        projected_capex = (
            projected_operating_cash_flow
            * scenario["capex_as_percent_of_ocf"]
        )
        projected_free_cash_flow = (
            projected_operating_cash_flow - projected_capex
        )

        results.append(
            {
                "year": next_year,
                "scenario": scenario["scenario"],
                "revenue_growth": scenario["revenue_growth"],
                "revenue": projected_revenue,
                "operating_margin": scenario["operating_margin"],
                "operating_income": projected_operating_income,
                "dso": scenario["dso"],
                "dio": scenario["dio"],
                "dpo": scenario["dpo"],
                "ccc": projected_ccc,
                "ocf_margin": scenario["ocf_margin"],
                "operating_cash_flow": projected_operating_cash_flow,
                "capex_as_percent_of_ocf": scenario[
                    "capex_as_percent_of_ocf"
                ],
                "capital_expenditures": projected_capex,
                "free_cash_flow": projected_free_cash_flow,
            }
        )

    scenario_results = pd.DataFrame(results)
    scenario_results.to_csv(OUTPUT_PATH, index=False)

    display_columns = [
        "year",
        "scenario",
        "revenue_growth",
        "revenue",
        "operating_margin",
        "operating_income",
        "ccc",
        "operating_cash_flow",
        "capital_expenditures",
        "free_cash_flow",
    ]

    display = scenario_results[display_columns].copy()

    dollar_columns = [
        "revenue",
        "operating_income",
        "operating_cash_flow",
        "capital_expenditures",
        "free_cash_flow",
    ]
    for column in dollar_columns:
        display[column] = display[column] / 1e9

    print("Walmart Scenario Analysis")
    print("-------------------------")
    print(f"Base year: {latest_year['end'].year}")
    print(f"Scenario year: {next_year}")
    print()
    print(display.to_string(index=False))
    print()
    print(f"Saved scenario analysis to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()