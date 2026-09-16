import pandas as pd


COMPANY_COMPARISON_PATH = "data/processed/company_comparison.csv"


def test_company_comparison_has_required_columns():
    df = pd.read_csv(COMPANY_COMPARISON_PATH)

    required_columns = {
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
    }

    assert required_columns.issubset(df.columns)


def test_company_comparison_has_no_duplicate_ticker_dates():
    df = pd.read_csv(COMPANY_COMPARISON_PATH)

    duplicate_count = df.duplicated(subset=["ticker", "end"]).sum()

    assert duplicate_count == 0


def test_free_cash_flow_formula():
    df = pd.read_csv(COMPANY_COMPARISON_PATH)

    calculated_fcf = (
        df["operating_cash_flow"] - df["capital_expenditures"]
    )

    assert (calculated_fcf == df["free_cash_flow"]).all()


def test_operating_margin_formula():
    df = pd.read_csv(COMPANY_COMPARISON_PATH)

    calculated_margin = df["operating_income"] / df["revenue"]

    difference = (calculated_margin - df["operating_margin"]).abs()

    assert (difference < 0.000001).all()


def test_cash_conversion_cycle_formula_when_available():
    df = pd.read_csv(COMPANY_COMPARISON_PATH)

    ccc_available = df[df["ccc"].notna()].copy()

    calculated_ccc = (
        ccc_available["dso"] + ccc_available["dio"] - ccc_available["dpo"]
    )

    difference = (calculated_ccc - ccc_available["ccc"]).abs()

    assert (difference < 0.000001).all()


def test_missing_ccc_allowed_for_target_and_costco():
    df = pd.read_csv(COMPANY_COMPARISON_PATH)

    missing_ccc = df[df["ccc"].isna()]

    assert set(missing_ccc["ticker"].unique()).issubset(
        {"TGT", "COST", "WMT"}
    )