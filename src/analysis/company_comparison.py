from pathlib import Path

import pandas as pd

from src.config import COMPANIES


OUTPUT_PATH = "data/processed/company_comparison.csv"


def load_company_financial_health(company_key, company):
    output_prefix = company["output_prefix"]
    input_path = Path(f"data/processed/{output_prefix}_financial_health.csv")

    if not input_path.exists():
        print(f"Skipping {company['name']}: missing {input_path}")
        return None

    df = pd.read_csv(input_path)
    df["company_key"] = company_key
    df["company_name"] = company["name"]
    df["ticker"] = company["ticker"]

    return df


def main():
    company_frames = []

    for company_key, company in COMPANIES.items():
        df = load_company_financial_health(company_key, company)

        if df is not None:
            company_frames.append(df)

    if not company_frames:
        raise FileNotFoundError("No company financial health files were found.")

    comparison = pd.concat(company_frames, ignore_index=True)

    output_columns = [
        "company_key",
        "company_name",
        "ticker",
        "end",
        "revenue",
        "revenue_growth",
        "operating_income",
        "operating_margin",
        "dso",
        "dio",
        "dpo",
        "ccc",
        "operating_cash_flow",
        "capital_expenditures",
        "free_cash_flow",
        "fcf_margin",
    ]

    comparison = comparison[output_columns]
    comparison = comparison.sort_values(["ticker", "end"])

    comparison.to_csv(OUTPUT_PATH, index=False)

    print("Company Comparison Dataset")
    print("--------------------------")
    print(f"Companies included: {comparison['ticker'].nunique()}")
    print(f"Rows saved: {len(comparison)}")
    print()
    print(
        comparison[
            [
                "ticker",
                "end",
                "revenue",
                "operating_margin",
                "dio",
                "dpo",
                "ccc",
                "free_cash_flow",
            ]
        ].tail(15).to_string(index=False)
    )
    print()
    print(f"Saved company comparison dataset to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()