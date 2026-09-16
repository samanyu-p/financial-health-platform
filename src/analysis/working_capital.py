import json
import sys
from pathlib import Path

import pandas as pd

from src.config import COMPANIES, DEFAULT_COMPANY


ANNUAL_DAYS_MIN = 300
ANNUAL_DAYS_MAX = 400


def get_company_key():
    if len(sys.argv) > 1:
        return sys.argv[1]

    return DEFAULT_COMPANY


def get_company(company_key):
    if company_key not in COMPANIES:
        valid_keys = ", ".join(COMPANIES.keys())
        raise ValueError(f"Unknown company '{company_key}'. Valid options: {valid_keys}")

    return COMPANIES[company_key]


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


def read_processed_csv(path):
    if not Path(path).exists():
        return None

    df = pd.read_csv(path)
    df["end"] = pd.to_datetime(df["end"])

    return df


def main():
    company_key = get_company_key()
    company = get_company(company_key)

    tags = company["tags"]
    output_prefix = company["output_prefix"]

    raw_file_path = f"data/raw/{output_prefix}_companyfacts.json"

    revenue_path = f"data/processed/{output_prefix}_revenue.csv"
    accounts_receivable_path = (
        f"data/processed/{output_prefix}_accounts_receivable.csv"
    )
    inventory_path = f"data/processed/{output_prefix}_inventory.csv"
    accounts_payable_path = f"data/processed/{output_prefix}_accounts_payable.csv"
    output_path = f"data/processed/{output_prefix}_working_capital.csv"

    revenue = read_processed_csv(revenue_path)
    accounts_receivable = read_processed_csv(accounts_receivable_path)
    inventory = read_processed_csv(inventory_path)
    accounts_payable = read_processed_csv(accounts_payable_path)

    required_inputs = {
        "revenue": revenue,
        "inventory": inventory,
        "accounts_payable": accounts_payable,
    }

    missing_required = [
        name for name, df in required_inputs.items() if df is None
    ]

    if missing_required:
        missing_text = ", ".join(missing_required)
        raise FileNotFoundError(
            f"Cannot calculate working capital for {company['name']}. "
            f"Missing processed files for: {missing_text}"
        )

    with open(raw_file_path, "r") as file:
        data = json.load(file)

    cost_of_revenue = clean_cost_of_revenue(
        data["facts"]["us-gaap"][tags["cost_of_revenue"]]["units"]["USD"]
    )

    df = pd.merge(
        revenue,
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

    has_accounts_receivable = accounts_receivable is not None

    if has_accounts_receivable:
        df = pd.merge(
            df,
            accounts_receivable,
            on="end",
            how="inner",
        )

    df = df.sort_values("end")

    if has_accounts_receivable:
        df["average_ar"] = (
            df["accounts_receivable"] + df["accounts_receivable"].shift(1)
        ) / 2
        df["dso"] = df["average_ar"] / df["revenue"] * 365
    else:
        df["accounts_receivable"] = pd.NA
        df["dso"] = pd.NA

    df["average_inventory"] = (
        df["inventory"] + df["inventory"].shift(1)
    ) / 2
    df["dio"] = df["average_inventory"] / df["cost_of_revenue"] * 365

    df["average_ap"] = (
        df["accounts_payable"] + df["accounts_payable"].shift(1)
    ) / 2
    df["dpo"] = df["average_ap"] / df["cost_of_revenue"] * 365

    if has_accounts_receivable:
        df["ccc"] = df["dso"] + df["dio"] - df["dpo"]
    else:
        df["ccc"] = pd.NA
        print(
            f"\nWarning: {company['name']} is missing accounts receivable data. "
            "DSO and full CCC cannot be calculated."
        )

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

    df[output_columns].to_csv(output_path, index=False)

    print(f"\nSaved working capital analysis to {output_path}")


if __name__ == "__main__":
    main()