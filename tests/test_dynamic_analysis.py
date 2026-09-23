import pandas as pd

from src.data import dynamic_analysis


def make_duration_record(start, end, value):
    return {
        "start": start,
        "end": end,
        "val": value,
        "accn": f"fake-{end}",
        "fy": int(end[:4]),
        "fp": "FY",
        "form": "10-K",
        "filed": f"{int(end[:4]) + 1}-03-01",
        "frame": f"CY{end[:4]}",
    }


def make_instant_record(end, value):
    return {
        "end": end,
        "val": value,
        "accn": f"fake-{end}",
        "fy": int(end[:4]),
        "fp": "FY",
        "form": "10-K",
        "filed": f"{int(end[:4]) + 1}-03-01",
        "frame": f"CY{end[:4]}",
    }


def test_dynamic_working_capital_calculates_expected_metrics(monkeypatch):
    fake_company = {
        "name": "Example Retailer",
        "ticker": "EXR",
        "cik": "0000000000",
        "facts_url": "https://example.com",
    }

    selected_tags = {
        "revenue": "RevenueTag",
        "cost_of_revenue": "CostTag",
        "accounts_receivable": "ReceivableTag",
        "inventory": "InventoryTag",
        "accounts_payable": "PayableTag",
        "operating_income": "OperatingIncomeTag",
        "operating_cash_flow": "OperatingCashFlowTag",
        "capital_expenditures": "CapexTag",
    }

    fake_facts = {
        "facts": {
            "us-gaap": {
                "RevenueTag": {
                    "units": {
                        "USD": [
                            make_duration_record(
                                "2022-01-01",
                                "2022-12-31",
                                1000,
                            ),
                            make_duration_record(
                                "2023-01-01",
                                "2023-12-31",
                                1200,
                            ),
                        ]
                    }
                },
                "CostTag": {
                    "units": {
                        "USD": [
                            make_duration_record(
                                "2022-01-01",
                                "2022-12-31",
                                500,
                            ),
                            make_duration_record(
                                "2023-01-01",
                                "2023-12-31",
                                600,
                            ),
                        ]
                    }
                },
                "ReceivableTag": {
                    "units": {
                        "USD": [
                            make_instant_record("2022-12-31", 50),
                            make_instant_record("2023-12-31", 70),
                        ]
                    }
                },
                "InventoryTag": {
                    "units": {
                        "USD": [
                            make_instant_record("2022-12-31", 100),
                            make_instant_record("2023-12-31", 140),
                        ]
                    }
                },
                "PayableTag": {
                    "units": {
                        "USD": [
                            make_instant_record("2022-12-31", 80),
                            make_instant_record("2023-12-31", 100),
                        ]
                    }
                },
            }
        }
    }

    monkeypatch.setattr(
        dynamic_analysis,
        "fetch_company_facts_by_ticker",
        lambda ticker: (fake_company, fake_facts),
    )
    monkeypatch.setattr(
        dynamic_analysis,
        "find_available_tags",
        lambda us_gaap: selected_tags,
    )

    result = dynamic_analysis.analyze_dynamic_working_capital("EXR")
    df = result["data"]

    latest = df.sort_values("end").iloc[-1]

    assert result["error"] is None
    assert latest["dso"] == 60 / 1200 * 365
    assert latest["dio"] == 120 / 600 * 365
    assert latest["dpo"] == 90 / 600 * 365
    assert latest["ccc"] == latest["dso"] + latest["dio"] - latest["dpo"]


def test_dynamic_working_capital_returns_error_when_required_tags_missing(
    monkeypatch,
):
    fake_company = {
        "name": "Example Bank",
        "ticker": "EXB",
        "cik": "0000000001",
        "facts_url": "https://example.com",
    }

    selected_tags = {
        "revenue": "RevenueTag",
        "cost_of_revenue": None,
        "accounts_receivable": None,
        "inventory": None,
        "accounts_payable": None,
        "operating_income": "OperatingIncomeTag",
        "operating_cash_flow": "OperatingCashFlowTag",
        "capital_expenditures": None,
    }

    fake_facts = {"facts": {"us-gaap": {}}}

    monkeypatch.setattr(
        dynamic_analysis,
        "fetch_company_facts_by_ticker",
        lambda ticker: (fake_company, fake_facts),
    )
    monkeypatch.setattr(
        dynamic_analysis,
        "find_available_tags",
        lambda us_gaap: selected_tags,
    )

    result = dynamic_analysis.analyze_dynamic_working_capital("EXB")

    assert result["data"] is None
    assert "Missing required working-capital tags" in result["error"]
    assert "cost_of_revenue" in result["error"]
    assert "inventory" in result["error"]
    assert "accounts_payable" in result["error"]