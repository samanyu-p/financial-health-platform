import json

import pandas as pd

from src.config import COMPANIES, DEFAULT_COMPANY


company = COMPANIES[DEFAULT_COMPANY]
tags = company["tags"]
output_prefix = company["output_prefix"]

RAW_FILE_PATH = f"data/raw/{output_prefix}_companyfacts.json"

REVENUE_PATH = f"data/processed/{output_prefix}_revenue.csv"
ACCOUNTS_RECEIVABLE_PATH = (
    f"data/processed/{output_prefix}_accounts_receivable.csv"
)
INVENTORY_PATH = f"data/processed/{output_prefix}_inventory.csv"
ACCOUNTS_PAYABLE_PATH = f"data/processed/{output_prefix}_accounts_payable.csv"
OUTPUT_PATH = f"data/processed/{output_prefix}_working_capital.csv"

ANNUAL_DAYS_MIN = 300
ANNUAL_DAYS_MAX = 400


def keep_latest_period_filing(df, duplicate_columns):
    df = df.copy()
    df["filed"] = pd.to_datetime(df["filed"])

    df = df.sort_values(duplicate_columns + ["filed", "accn"])
    df = df.drop_duplicates(subset=duplicate_columns, keep="last")

    return df


def clean_cost_of_revenue(records):
    cost = pd.DataFrame(records)

    cost = cost[cost["form"] == "10-K"].copy()
    cost = cost[cost["start"].notna() & cost["end"].notna()].copy()

    cost["start"] = pd.to_datetime(cost["start"])
    cost["end"] = pd.to_datetime(cost["end"])

    cost["days"] = (cost["end"] - cost["start"]).dt.days
    cost = cost[
        (cost["days"] >= ANNUAL_DAYS_MIN)
        & (cost["days"] <= ANNUAL_DAYS_MAX)
    ].copy()

    cost = keep_latest_period_filing(cost, ["start", "end"])

    cost = cost[["end", "val"]]
    cost = cost.rename(columns={"val": "cost_of_revenue"})
    cost = cost.sort_values("end")

    return cost


def main():
    revenue = pd.read_csv(REVENUE_PATH)
    revenue["end"] = pd.to_datetime(revenue["end"])

    accounts_receivable = pd.read_csv(ACCOUNTS_RECEIVABLE_PATH)
    accounts_receivable["end"] = pd.to_datetime(accounts_receivable["end"])

    inventory = pd.read_csv(INVENTORY_PATH)
    inventory["end"] = pd.to_datetime(inventory["end"])

    accounts_payable = pd.read_csv(ACCOUNTS_PAYABLE_PATH)
    accounts_payable["end"] = pd.to_datetime(accounts_payable["end"])

    with open(RAW_FILE_PATH, "r") as file:
        data = json.load(file)

    cost_of_revenue = clean_cost_of_revenue(
        data["facts"]["us-gaap"][tags["cost_of_revenue"]]["units"]["USD"]
    )

    df = pd.merge(
        revenue,
        accounts_receivable,
        on="end",
        how="inner",
    )

    df = pd.merge(
        df,
        inventory,
        on="end",
        how="inner",
    )

    df = pd.merge(
        df,
        accounts_payable,
        on="end",
        how="inner",
    )

    df = pd.merge(
        df,
        cost_of_revenue,
        on="end",
        how="inner",
    )

    df = df.sort_values("end")

    df["average_ar"] = (
        df["accounts_receivable"] + df["accounts_receivable"].shift(1)
    ) / 2
    df["dso"] = df["average_ar"] / df["revenue"] * 365

    df["average_inventory"] = (
        df["inventory"] + df["inventory"].shift(1)
    ) / 2
    df["dio"] = df["average_inventory"] / df["cost_of_revenue"] * 365

    df["average_ap"] = (
        df["accounts_payable"] + df["accounts_payable"].shift(1)
    ) / 2
    df["dpo"] = df["average_ap"] / df["cost_of_revenue"] * 365

    df["ccc"] = df["dso"] + df["dio"] - df["dpo"]

    display_columns = [
        "end",
        "revenue",
        "dso",
        "dio",
        "dpo",
        "ccc",
    ]

    output_columns = [
        "end",
        "revenue",
        "accounts_receivable",
        "inventory",
        "accounts_payable",
        "cost_of_revenue",
        "dso",
        "dio",
        "dpo",
        "ccc",
    ]

    print(f"\n{company['name']} Working Capital Analysis:\n")
    print(df[display_columns].to_string(index=False))

    df[output_columns].to_csv(OUTPUT_PATH, index=False)

    print(f"\nSaved working capital analysis to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()