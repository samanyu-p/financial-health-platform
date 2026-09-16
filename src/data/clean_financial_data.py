import json
import sys

import pandas as pd

from src.config import COMPANIES, DEFAULT_COMPANY


ANNUAL_DAYS_MIN = 300
ANNUAL_DAYS_MAX = 400
PROCESSED_DIR = "data/processed"


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


def get_us_gaap_records(us_gaap, tag):
    if tag is None:
        return None

    if tag not in us_gaap:
        return None

    return us_gaap[tag]["units"]["USD"]


def save_and_print(df, output_path, title):
    print(f"\n{title}:\n")
    print(df.to_string(index=False))

    df.to_csv(output_path, index=False)

    print(f"\nSaved {title.lower()} to {output_path}")


def clean_and_save_duration_metric(
    us_gaap,
    tag,
    value_column_name,
    output_path,
    title,
):
    records = get_us_gaap_records(us_gaap, tag)

    if records is None:
        print(f"\nSkipping {title}: required SEC tag is missing.")
        return None

    df = clean_duration_metric(records, value_column_name)
    save_and_print(df, output_path, title)

    return df


def clean_and_save_instant_metric(
    us_gaap,
    tag,
    value_column_name,
    output_path,
    title,
):
    records = get_us_gaap_records(us_gaap, tag)

    if records is None:
        print(f"\nSkipping {title}: required SEC tag is missing.")
        return None

    df = clean_instant_metric(records, value_column_name)
    save_and_print(df, output_path, title)

    return df


def main():
    company_key = get_company_key()
    company = get_company(company_key)

    tags = company["tags"]
    output_prefix = company["output_prefix"]
    raw_file_path = f"data/raw/{output_prefix}_companyfacts.json"

    with open(raw_file_path, "r") as file:
        data = json.load(file)

    us_gaap = data["facts"]["us-gaap"]

    revenue_records = get_us_gaap_records(us_gaap, tags["revenue"])

    if revenue_records is None:
        raise ValueError("Revenue tag is required and could not be found.")

    revenue = clean_duration_metric(revenue_records, "revenue")
    revenue["revenue_growth"] = revenue["revenue"].pct_change()

    print(f"\nClean {company['name']} Revenue Data:\n")
    print(revenue[["start", "end", "revenue"]].to_string(index=False))

    print("\nRevenue Growth:\n")
    print(revenue[["end", "revenue", "revenue_growth"]].to_string(index=False))

    revenue_output = f"{PROCESSED_DIR}/{output_prefix}_revenue.csv"
    revenue.to_csv(revenue_output, index=False)
    print(f"\nSaved cleaned data to {revenue_output}")

    clean_and_save_instant_metric(
        us_gaap,
        tags["accounts_receivable"],
        "accounts_receivable",
        f"{PROCESSED_DIR}/{output_prefix}_accounts_receivable.csv",
        f"Clean {company['name']} Accounts Receivable Data",
    )

    clean_and_save_instant_metric(
        us_gaap,
        tags["inventory"],
        "inventory",
        f"{PROCESSED_DIR}/{output_prefix}_inventory.csv",
        f"Clean {company['name']} Inventory Data",
    )

    clean_and_save_instant_metric(
        us_gaap,
        tags["accounts_payable"],
        "accounts_payable",
        f"{PROCESSED_DIR}/{output_prefix}_accounts_payable.csv",
        f"Clean {company['name']} Accounts Payable Data",
    )

    clean_and_save_duration_metric(
        us_gaap,
        tags["operating_income"],
        "operating_income",
        f"{PROCESSED_DIR}/{output_prefix}_operating_income.csv",
        f"Clean {company['name']} Operating Income Data",
    )

    clean_and_save_duration_metric(
        us_gaap,
        tags["operating_cash_flow"],
        "operating_cash_flow",
        f"{PROCESSED_DIR}/{output_prefix}_operating_cash_flow.csv",
        f"{company['name']} Operating Cash Flow",
    )

    clean_and_save_duration_metric(
        us_gaap,
        tags["capital_expenditures"],
        "capital_expenditures",
        f"{PROCESSED_DIR}/{output_prefix}_capex.csv",
        f"{company['name']} Capital Expenditures",
    )


if __name__ == "__main__":
    main()