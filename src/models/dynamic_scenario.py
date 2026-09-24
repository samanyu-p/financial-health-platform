import pandas as pd

from src.data.dynamic_analysis import (
    analyze_dynamic_free_cash_flow,
    analyze_dynamic_profitability,
)


SCENARIOS = [
    {
        "scenario": "Downside",
        "revenue_growth_adjustment": -0.03,
        "operating_margin_adjustment": -0.01,
        "ocf_margin_adjustment": -0.01,
        "capex_share_adjustment": 0.05,
    },
    {
        "scenario": "Base",
        "revenue_growth_adjustment": 0.00,
        "operating_margin_adjustment": 0.00,
        "ocf_margin_adjustment": 0.00,
        "capex_share_adjustment": 0.00,
    },
    {
        "scenario": "Upside",
        "revenue_growth_adjustment": 0.03,
        "operating_margin_adjustment": 0.01,
        "ocf_margin_adjustment": 0.01,
        "capex_share_adjustment": -0.05,
    },
]


def get_recent_average(series, periods=3):
    recent = series.dropna().tail(periods)

    if recent.empty:
        return None

    return recent.mean()


def analyze_dynamic_scenarios(ticker):
    profitability_result = analyze_dynamic_profitability(ticker)

    if (
        profitability_result is None
        or profitability_result["data"] is None
        or profitability_result["data"].empty
    ):
        return {
            "company": None,
            "data": None,
            "error": "Profitability data is unavailable for scenario analysis.",
        }

    company = profitability_result["company"]
    profitability = profitability_result["data"].copy()
    profitability["end"] = pd.to_datetime(profitability["end"])
    profitability = profitability.sort_values("end")

    latest_profitability = profitability.iloc[-1]
    base_year = latest_profitability["end"].year
    scenario_year = base_year + 1

    latest_revenue = latest_profitability["revenue"]
    recent_revenue_growth = get_recent_average(
        profitability["revenue_growth"],
    )
    recent_operating_margin = get_recent_average(
        profitability["operating_margin"],
    )

    if recent_revenue_growth is None:
        recent_revenue_growth = 0.03

    if recent_operating_margin is None:
        recent_operating_margin = latest_profitability["operating_margin"]

    fcf_result = analyze_dynamic_free_cash_flow(ticker)

    has_fcf_data = (
        fcf_result is not None
        and fcf_result["data"] is not None
        and not fcf_result["data"].empty
    )

    recent_ocf_margin = None
    recent_capex_share = None

    if has_fcf_data:
        fcf = fcf_result["data"].copy()
        fcf["end"] = pd.to_datetime(fcf["end"])
        fcf = fcf.sort_values("end")

        combined = pd.merge(
            profitability[["end", "revenue"]],
            fcf[
                [
                    "end",
                    "operating_cash_flow",
                    "capital_expenditures",
                ]
            ],
            on="end",
            how="inner",
        )

        if not combined.empty:
            combined["ocf_margin"] = (
                combined["operating_cash_flow"] / combined["revenue"]
            )
            combined["capex_share_of_ocf"] = (
                combined["capital_expenditures"]
                / combined["operating_cash_flow"]
            )

            recent_ocf_margin = get_recent_average(combined["ocf_margin"])
            recent_capex_share = get_recent_average(
                combined["capex_share_of_ocf"]
            )

    results = []

    for scenario in SCENARIOS:
        projected_revenue_growth = max(
            recent_revenue_growth
            + scenario["revenue_growth_adjustment"],
            -0.50,
        )
        projected_operating_margin = max(
            recent_operating_margin
            + scenario["operating_margin_adjustment"],
            -0.50,
        )

        projected_revenue = latest_revenue * (1 + projected_revenue_growth)
        projected_operating_income = (
            projected_revenue * projected_operating_margin
        )

        result = {
            "ticker": company["ticker"],
            "company": company["name"],
            "base_year": base_year,
            "scenario_year": scenario_year,
            "scenario": scenario["scenario"],
            "revenue_growth": projected_revenue_growth,
            "revenue": projected_revenue,
            "operating_margin": projected_operating_margin,
            "operating_income": projected_operating_income,
            "operating_cash_flow": pd.NA,
            "capital_expenditures": pd.NA,
            "free_cash_flow": pd.NA,
            "fcf_available": False,
        }

        if recent_ocf_margin is not None and recent_capex_share is not None:
            projected_ocf_margin = max(
                recent_ocf_margin + scenario["ocf_margin_adjustment"],
                -0.50,
            )
            projected_capex_share = min(
                max(
                    recent_capex_share + scenario["capex_share_adjustment"],
                    0,
                ),
                1.50,
            )

            projected_operating_cash_flow = (
                projected_revenue * projected_ocf_margin
            )
            projected_capex = (
                projected_operating_cash_flow * projected_capex_share
            )
            projected_free_cash_flow = (
                projected_operating_cash_flow - projected_capex
            )

            result["operating_cash_flow"] = projected_operating_cash_flow
            result["capital_expenditures"] = projected_capex
            result["free_cash_flow"] = projected_free_cash_flow
            result["fcf_available"] = True

        results.append(result)

    scenario_df = pd.DataFrame(results)

    return {
        "company": company,
        "data": scenario_df,
        "error": None,
    }


if __name__ == "__main__":
    result = analyze_dynamic_scenarios("AAPL")

    if result["error"]:
        print(result["error"])
    else:
        display = result["data"].copy()

        dollar_columns = [
            "revenue",
            "operating_income",
            "operating_cash_flow",
            "capital_expenditures",
            "free_cash_flow",
        ]

        for column in dollar_columns:
            display[column] = display[column] / 1e9

        print(display.to_string(index=False))