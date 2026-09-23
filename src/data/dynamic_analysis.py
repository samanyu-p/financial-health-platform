import pandas as pd

from src.data.check_tags import find_available_tags
from src.data.dynamic_company import fetch_company_facts_by_ticker


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


def get_usd_records(us_gaap, tag):
    if tag is None:
        return None

    if tag not in us_gaap:
        return None

    units = us_gaap[tag].get("units", {})

    if "USD" not in units:
        return None

    return units["USD"]


def analyze_dynamic_profitability(ticker):
    company, facts = fetch_company_facts_by_ticker(ticker)

    if company is None:
        return None

    us_gaap = facts["facts"]["us-gaap"]
    selected_tags = find_available_tags(us_gaap)

    revenue_tag = selected_tags["revenue"]
    operating_income_tag = selected_tags["operating_income"]

    if revenue_tag is None or operating_income_tag is None:
        return {
            "company": company,
            "selected_tags": selected_tags,
            "data": None,
            "error": "Revenue or operating income tag is missing.",
        }

    revenue_records = get_usd_records(us_gaap, revenue_tag)
    operating_income_records = get_usd_records(us_gaap, operating_income_tag)

    if revenue_records is None or operating_income_records is None:
        return {
            "company": company,
            "selected_tags": selected_tags,
            "data": None,
            "error": "Revenue or operating income USD records are missing.",
        }

    revenue = clean_duration_metric(revenue_records, "revenue")
    operating_income = clean_duration_metric(
        operating_income_records,
        "operating_income",
    )

    df = pd.merge(
        revenue,
        operating_income,
        on="end",
        how="inner",
    )

    df = df.sort_values("end")

    df["revenue_growth"] = df["revenue"].pct_change()
    df["operating_margin"] = df["operating_income"] / df["revenue"]

    output_columns = [
        "end",
        "revenue",
        "revenue_growth",
        "operating_income",
        "operating_margin",
    ]

    return {
        "company": company,
        "selected_tags": selected_tags,
        "data": df[output_columns],
        "error": None,
    }


def analyze_dynamic_free_cash_flow(ticker):
    company, facts = fetch_company_facts_by_ticker(ticker)

    if company is None:
        return None

    us_gaap = facts["facts"]["us-gaap"]
    selected_tags = find_available_tags(us_gaap)

    operating_cash_flow_tag = selected_tags["operating_cash_flow"]
    capital_expenditures_tag = selected_tags["capital_expenditures"]

    if operating_cash_flow_tag is None or capital_expenditures_tag is None:
        return {
            "company": company,
            "selected_tags": selected_tags,
            "data": None,
            "error": (
                "Operating cash flow or capital expenditures tag is missing."
            ),
        }

    operating_cash_flow_records = get_usd_records(
        us_gaap,
        operating_cash_flow_tag,
    )
    capital_expenditures_records = get_usd_records(
        us_gaap,
        capital_expenditures_tag,
    )

    if (
        operating_cash_flow_records is None
        or capital_expenditures_records is None
    ):
        return {
            "company": company,
            "selected_tags": selected_tags,
            "data": None,
            "error": (
                "Operating cash flow or capital expenditures USD records "
                "are missing."
            ),
        }

    operating_cash_flow = clean_duration_metric(
        operating_cash_flow_records,
        "operating_cash_flow",
    )
    capital_expenditures = clean_duration_metric(
        capital_expenditures_records,
        "capital_expenditures",
    )

    df = pd.merge(
        operating_cash_flow,
        capital_expenditures,
        on="end",
        how="inner",
    )

    df = df.sort_values("end")

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

    return {
        "company": company,
        "selected_tags": selected_tags,
        "data": df[output_columns],
        "error": None,
    }