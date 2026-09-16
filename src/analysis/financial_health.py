import sys

import pandas as pd

from src.config import COMPANIES, DEFAULT_COMPANY


def get_company_key():
    if len(sys.argv) > 1:
        return sys.argv[1]

    return DEFAULT_COMPANY


def get_company(company_key):
    if company_key not in COMPANIES:
        valid_keys = ", ".join(COMPANIES.keys())
        raise ValueError(f"Unknown company '{company_key}'. Valid options: {valid_keys}")

    return COMPANIES[company_key]


def main():
    company_key = get_company_key()
    company = get_company(company_key)
    output_prefix = company["output_prefix"]

    profitability_path = f"data/processed/{output_prefix}_profitability.csv"
    working_capital_path = f"data/processed/{output_prefix}_working_capital.csv"
    free_cash_flow_path = f"data/processed/{output_prefix}_free_cash_flow.csv"
    output_path = f"data/processed/{output_prefix}_financial_health.csv"

    profitability = pd.read_csv(profitability_path)
    profitability["end"] = pd.to_datetime(profitability["end"])

    working_capital = pd.read_csv(working_capital_path)
    working_capital["end"] = pd.to_datetime(working_capital["end"])

    free_cash_flow = pd.read_csv(free_cash_flow_path)
    free_cash_flow["end"] = pd.to_datetime(free_cash_flow["end"])

    df = pd.merge(
        profitability,
        working_capital[["end", "dso", "dio", "dpo", "ccc"]],
        on="end",
        how="inner",
    )

    df = pd.merge(
        df,
        free_cash_flow[
            [
                "end",
                "operating_cash_flow",
                "capital_expenditures",
                "free_cash_flow",
                "fcf_margin",
            ]
        ],
        on="end",
        how="inner",
    )

    df = df.sort_values("end")
    df["revenue_growth"] = df["revenue"].pct_change()

    output_columns = [
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

    df = df[output_columns]

    print(f"\n{company['name']} Financial Health Analysis:\n")
    print(df.to_string(index=False))

    df.to_csv(output_path, index=False)

    print(f"\nSaved financial health analysis to {output_path}")


if __name__ == "__main__":
    main()