import pandas as pd

from src.models import dynamic_scenario


def test_dynamic_scenarios_create_downside_base_upside_cases(monkeypatch):
    fake_company = {
        "name": "Example Company",
        "ticker": "EXC",
        "cik": "0000000000",
        "facts_url": "https://example.com",
    }

    profitability = pd.DataFrame(
        {
            "end": pd.to_datetime(
                [
                    "2021-12-31",
                    "2022-12-31",
                    "2023-12-31",
                ]
            ),
            "revenue": [
                1000,
                1100,
                1210,
            ],
            "revenue_growth": [
                None,
                0.10,
                0.10,
            ],
            "operating_income": [
                100,
                132,
                145.2,
            ],
            "operating_margin": [
                0.10,
                0.12,
                0.12,
            ],
        }
    )

    free_cash_flow = pd.DataFrame(
        {
            "end": pd.to_datetime(
                [
                    "2021-12-31",
                    "2022-12-31",
                    "2023-12-31",
                ]
            ),
            "operating_cash_flow": [
                120,
                132,
                145.2,
            ],
            "capital_expenditures": [
                60,
                66,
                72.6,
            ],
            "free_cash_flow": [
                60,
                66,
                72.6,
            ],
            "fcf_margin": [
                0.50,
                0.50,
                0.50,
            ],
        }
    )

    monkeypatch.setattr(
        dynamic_scenario,
        "analyze_dynamic_profitability",
        lambda ticker: {
            "company": fake_company,
            "data": profitability,
            "error": None,
        },
    )

    monkeypatch.setattr(
        dynamic_scenario,
        "analyze_dynamic_free_cash_flow",
        lambda ticker: {
            "company": fake_company,
            "data": free_cash_flow,
            "error": None,
        },
    )

    result = dynamic_scenario.analyze_dynamic_scenarios("EXC")
    scenarios = result["data"]

    assert result["error"] is None
    assert set(scenarios["scenario"]) == {"Downside", "Base", "Upside"}
    assert len(scenarios) == 3
    assert scenarios["revenue"].notna().all()
    assert scenarios["operating_income"].notna().all()
    assert scenarios["free_cash_flow"].notna().all()
    assert scenarios["fcf_available"].all()

    downside = scenarios[scenarios["scenario"] == "Downside"].iloc[0]
    base = scenarios[scenarios["scenario"] == "Base"].iloc[0]
    upside = scenarios[scenarios["scenario"] == "Upside"].iloc[0]

    assert downside["revenue_growth"] < base["revenue_growth"]
    assert upside["revenue_growth"] > base["revenue_growth"]
    assert downside["operating_margin"] < base["operating_margin"]
    assert upside["operating_margin"] > base["operating_margin"]


def test_dynamic_scenarios_handle_missing_profitability(monkeypatch):
    monkeypatch.setattr(
        dynamic_scenario,
        "analyze_dynamic_profitability",
        lambda ticker: {
            "company": None,
            "data": None,
            "error": "Profitability unavailable.",
        },
    )

    result = dynamic_scenario.analyze_dynamic_scenarios("BAD")

    assert result["data"] is None
    assert "Profitability data is unavailable" in result["error"]