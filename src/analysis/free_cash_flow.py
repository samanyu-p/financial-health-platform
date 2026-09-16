import pandas as pd

from src.config import COMPANIES, DEFAULT_COMPANY


company = COMPANIES[DEFAULT_COMPANY]
output_prefix = company["output_prefix"]

operating_cash_flow_path = (
    f"data/processed/{output_prefix}_operating_cash_flow.csv"
)
capex_path = f"data/processed/{output_prefix}_capex.csv"
output_path = f"data/processed/{output_prefix}_free_cash_flow.csv"


def main():
    operating_cash_flow = pd.read_csv(operating_cash_flow_path)
    operating_cash_flow["start"] = pd.to_datetime(operating_cash_flow["start"])
    operating_cash_flow["end"] = pd.to_datetime(operating_cash_flow["end"])

    capex = pd.read_csv(capex_path)
    capex["start"] = pd.to_datetime(capex["start"])
    capex["end"] = pd.to_datetime(capex["end"])

    df = pd.merge(
        operating_cash_flow,
        capex,
        on=["start", "end"],
        how="inner",
    )

    df["free_cash_flow"] = (
        df["operating_cash_flow"] - df["capital_expenditures"]
    )

    df["fcf_margin"] = df["free_cash_flow"] / df["operating_cash_flow"]

    output_columns = [
        "end",
        "operating_cash_flow",
        "capital_expenditures",
        "free_cash_flow",
        "fcf_margin",
    ]

    print(f"\n{company['name']} Free Cash Flow Analysis:\n")
    print(df[output_columns].to_string(index=False))

    df[output_columns].to_csv(output_path, index=False)

    print(f"\nSaved FCF analysis to {output_path}")


if __name__ == "__main__":
    main()