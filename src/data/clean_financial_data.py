import json

import pandas as pd

from src.config import COMPANIES, DEFAULT_COMPANY


company = COMPANIES[DEFAULT_COMPANY]
tags = company["tags"]

RAW_FILE_PATH = f"data/raw/{company['output_prefix']}_companyfacts.json"
PROCESSED_DIR = "data/processed"
OUTPUT_PREFIX = company["output_prefix"]

ANNUAL_DAYS_MIN = 300
ANNUAL_DAYS_MAX = 400


def keep_latest_period_filing(df, duplicate_columns):
    df = df.copy()
    df["filed"] = pd.to_datetime(df["filed"])

    df = df.sort_values(duplicate_columns + ["filed", "accn"])
    df = df.drop_duplicates(subset=duplicate_columns, keep="last")

    return df


def clean_duration_metric(records, value_column_name):
    df = pd.DataFrame(records)

    df = df[df["form"] == "10-K"].copy()
    df = df[df["start"].notna() & df["end"].notna()].copy()

    df["start"] = pd.to_datetime(df["start"])
    df["end"] = pd.to_datetime(df["end"])

    df["days"] = (df["end"] - df["start"]).dt.days
    df = df[
        (df["days"] >= ANNUAL_DAYS_MIN)
        & (df["days"] <= ANNUAL_DAYS_MAX)
    ].copy()

    df = keep_latest_period_filing(df, ["start", "end"])

    df = df[["start", "end", "val"]]
    df = df.rename(columns={"val": value_column_name})
    df = df.sort_values("end")

    return df


def clean_instant_metric(records, value_column_name):
    df = pd.DataFrame(records)

    df = df[df["form"] == "10-K"].copy()
    df = df[df["end"].notna()].copy()

    df["end"] = pd.to_datetime(df["end"])

    df = keep_latest_period_filing(df, ["end"])

    df = df[["end", "val"]]
    df = df.rename(columns={"val": value_column_name})
    df = df.sort_values("end")

    return df


def save_and_print(df, output_path, title):
    print(f"\n{title}:\n")
    print(df.to_string(index=False))

    df.to_csv(output_path, index=False)

    print(f"\nSaved {title.lower()} to {output_path}")


def main():
    with open(RAW_FILE_PATH, "r") as file:
        data = json.load(file)

    us_gaap = data["facts"]["us-gaap"]

    revenue = clean_duration_metric(
        us_gaap[tags["revenue"]]["units"]["USD"],
        "revenue",
    )
    revenue["revenue_growth"] = revenue["revenue"].pct_change()

    print("\nClean Walmart Revenue Data:\n")
    print(revenue[["start", "end", "revenue"]].to_string(index=False))

    print("\nRevenue Growth:\n")
    print(revenue[["end", "revenue", "revenue_growth"]].to_string(index=False))

    revenue_output = f"{PROCESSED_DIR}/{OUTPUT_PREFIX}_revenue.csv"
    revenue.to_csv(revenue_output, index=False)
    print(f"\nSaved cleaned data to {revenue_output}")

    accounts_receivable = clean_instant_metric(
        us_gaap[tags["accounts_receivable"]]["units"]["USD"],
        "accounts_receivable",
    )
    save_and_print(
        accounts_receivable,
        f"{PROCESSED_DIR}/{OUTPUT_PREFIX}_accounts_receivable.csv",
        "Clean Walmart Accounts Receivable Data",
    )

    inventory = clean_instant_metric(
        us_gaap[tags["inventory"]]["units"]["USD"],
        "inventory",
    )
    save_and_print(
        inventory,
        f"{PROCESSED_DIR}/{OUTPUT_PREFIX}_inventory.csv",
        "Clean Walmart Inventory Data",
    )

    accounts_payable = clean_instant_metric(
        us_gaap[tags["accounts_payable"]]["units"]["USD"],
        "accounts_payable",
    )
    save_and_print(
        accounts_payable,
        f"{PROCESSED_DIR}/{OUTPUT_PREFIX}_accounts_payable.csv",
        "Clean Walmart Accounts Payable Data",
    )

    operating_income = clean_duration_metric(
        us_gaap[tags["operating_income"]]["units"]["USD"],
        "operating_income",
    )
    save_and_print(
        operating_income,
        f"{PROCESSED_DIR}/{OUTPUT_PREFIX}_operating_income.csv",
        "Clean Walmart Operating Income Data",
    )

    operating_cash_flow = clean_duration_metric(
        us_gaap[tags["operating_cash_flow"]]["units"]["USD"],
        "operating_cash_flow",
    )
    save_and_print(
        operating_cash_flow,
        f"{PROCESSED_DIR}/{OUTPUT_PREFIX}_operating_cash_flow.csv",
        "Operating Cash Flow",
    )

    capex = clean_duration_metric(
        us_gaap[tags["capital_expenditures"]]["units"]["USD"],
        "capital_expenditures",
    )
    save_and_print(
        capex,
        f"{PROCESSED_DIR}/{OUTPUT_PREFIX}_capex.csv",
        "Capital Expenditures",
    )


if __name__ == "__main__":
    main()