import pandas as pd

from src.config import COMPANIES, DEFAULT_COMPANY


company = COMPANIES[DEFAULT_COMPANY]
output_prefix = company["output_prefix"]

revenue_path = f"data/processed/{output_prefix}_revenue.csv"
operating_income_path = f"data/processed/{output_prefix}_operating_income.csv"
output_path = f"data/processed/{output_prefix}_profitability.csv"


def main():
    revenue_df = pd.read_csv(revenue_path)
    revenue_df["end"] = pd.to_datetime(revenue_df["end"])

    operating_df = pd.read_csv(operating_income_path)
    operating_df["end"] = pd.to_datetime(operating_df["end"])

    df = pd.merge(
        revenue_df,
        operating_df,
        on="end",
        how="inner",
    )

    df = df.sort_values("end")

    df["operating_margin"] = df["operating_income"] / df["revenue"]

    output_columns = [
        "end",
        "revenue",
        "operating_income",
        "operating_margin",
    ]

    print(f"\n{company['name']} Profitability Analysis:\n")
    print(df[output_columns].to_string(index=False))

    df[output_columns].to_csv(output_path, index=False)

    print(f"\nSaved profitability analysis to {output_path}")


if __name__ == "__main__":
    main()