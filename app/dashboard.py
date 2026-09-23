import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data.dynamic_analysis import analyze_dynamic_profitability
from src.data.dynamic_company import analyze_ticker_support
from src.models.dynamic_forecast import forecast_revenue_for_ticker


DATA_PATH = "data/processed/company_comparison.csv"
SCENARIO_PATH = "data/processed/walmart_scenario_analysis.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["end"] = pd.to_datetime(df["end"])
    df["year"] = df["end"].dt.year

    df["revenue_billions"] = df["revenue"] / 1e9
    df["free_cash_flow_billions"] = df["free_cash_flow"] / 1e9
    df["operating_margin_percent"] = df["operating_margin"] * 100
    df["fcf_margin_percent"] = df["fcf_margin"] * 100

    return df


@st.cache_data
def load_forecast_data():
    forecast_frames = []

    for ticker, file_name in {
        "WMT": "walmart_revenue_forecast.csv",
        "TGT": "target_revenue_forecast.csv",
        "COST": "costco_revenue_forecast.csv",
    }.items():
        path = Path("data/processed") / file_name

        if not path.exists():
            continue

        df = pd.read_csv(path)
        df["ticker"] = ticker
        forecast_frames.append(df)

    if not forecast_frames:
        return pd.DataFrame()

    forecast = pd.concat(forecast_frames, ignore_index=True)

    return forecast


@st.cache_data
def load_scenario_data():
    path = Path(SCENARIO_PATH)

    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)

    df["revenue_billions"] = df["revenue"] / 1e9
    df["operating_income_billions"] = df["operating_income"] / 1e9
    df["free_cash_flow_billions"] = df["free_cash_flow"] / 1e9
    df["operating_margin_percent"] = df["operating_margin"] * 100
    df["revenue_growth_percent"] = df["revenue_growth"] * 100

    return df


def format_billions(value):
    if pd.isna(value):
        return "N/A"

    return f"${value / 1e9:,.1f}B"


def format_percent(value):
    if pd.isna(value):
        return "N/A"

    return f"{value * 100:.1f}%"


def main():
    st.set_page_config(
        page_title="Financial Health Platform",
        layout="wide",
    )

    st.title("Corporate Financial Health Dashboard")

    st.caption(
        "Retail-focused financial analysis using SEC Company Facts data, "
        "with an expanding dynamic ticker analysis tool."
    )

    with st.expander("Methodology and limitations"):
        st.markdown(
            """
            This dashboard uses SEC Company Facts data to compare financial
            health across selected public retailers and to inspect support for
            additional SEC-registered companies.

            **Current scope**
            - Walmart, Target, and Costco are included in the main comparison dataset.
            - The broader ticker analyzer can inspect many SEC filers.
            - Not every metric applies to every company or industry.

            **Key metrics**
            - Revenue growth shows how sales changed year over year.
            - Operating margin measures operating income as a percentage of revenue.
            - DIO estimates how many days inventory is held before sale.
            - DPO estimates how many days the company takes to pay suppliers.
            - CCC normally equals DSO + DIO - DPO.
            - Free cash flow equals operating cash flow minus capital expenditures.

            **Missing metrics**
            Target and Costco do not currently expose the accounts receivable tag
            used by this project. Because DSO requires accounts receivable, full
            CCC is not calculated for those companies.

            **Industry limitations**
            Retail-style working-capital metrics should not be blindly applied to
            banks, insurers, or software companies. The ticker analyzer shows which
            analyses are supported by available SEC tags, but business context is
            still required.

            **Forecast and scenario limitations**
            Forecasts use simple baselines and should not be treated as precise
            predictions. Scenario assumptions are illustrative and not company
            guidance or investment advice.
            """
        )

    st.subheader("Analyze Any SEC Ticker")

    ticker_input = st.text_input(
        "Enter a ticker to analyze",
        value="AAPL",
        help="Examples: AAPL, JPM, MSFT, WMT",
    )

    if st.button("Analyze ticker"):
        with st.spinner("Fetching SEC data and checking available tags..."):
            support_result = analyze_ticker_support(ticker_input)
            profitability_result = analyze_dynamic_profitability(ticker_input)
            forecast_result = forecast_revenue_for_ticker(ticker_input)

        if support_result is None:
            st.error(f"No SEC company found for ticker: {ticker_input}")
        else:
            company = support_result["company"]
            selected_tags = support_result["selected_tags"]
            supported_analyses = support_result["supported_analyses"]

            st.success(
                f"Found {company['name']} "
                f"({company['ticker']}) | CIK {company['cik']}"
            )

            support_rows = []
            for analysis_name, details in supported_analyses.items():
                support_rows.append(
                    {
                        "analysis": analysis_name,
                        "supported": details["is_supported"],
                        "missing_metrics": ", ".join(
                            details["missing_metrics"]
                        ),
                    }
                )

            support_df = pd.DataFrame(support_rows)

            st.write("Supported analyses")
            st.dataframe(support_df, use_container_width=True)

            tag_rows = []
            for metric, tag in selected_tags.items():
                tag_rows.append(
                    {
                        "metric": metric,
                        "selected_sec_tag": tag,
                    }
                )

            tag_df = pd.DataFrame(tag_rows)

            st.write("Selected SEC tags")
            st.dataframe(tag_df, use_container_width=True)

            if (
                profitability_result is not None
                and profitability_result["data"] is not None
            ):
                dynamic_df = profitability_result["data"].copy()
                dynamic_df["year"] = pd.to_datetime(dynamic_df["end"]).dt.year
                dynamic_df["revenue_billions"] = dynamic_df["revenue"] / 1e9
                dynamic_df["operating_margin_percent"] = (
                    dynamic_df["operating_margin"] * 100
                )

                latest_row = dynamic_df.sort_values("end").iloc[-1]

                metric_col_1, metric_col_2 = st.columns(2)

                with metric_col_1:
                    st.metric(
                        "Latest revenue",
                        format_billions(latest_row["revenue"]),
                    )

                with metric_col_2:
                    st.metric(
                        "Latest operating margin",
                        format_percent(latest_row["operating_margin"]),
                    )

                dynamic_revenue_fig = px.line(
                    dynamic_df,
                    x="year",
                    y="revenue_billions",
                    markers=True,
                    title=f"{company['ticker']} Revenue",
                    labels={
                        "year": "Fiscal Year",
                        "revenue_billions": "Revenue ($B)",
                    },
                )
                st.plotly_chart(
                    dynamic_revenue_fig,
                    use_container_width=True,
                )

                dynamic_margin_fig = px.line(
                    dynamic_df,
                    x="year",
                    y="operating_margin_percent",
                    markers=True,
                    title=f"{company['ticker']} Operating Margin",
                    labels={
                        "year": "Fiscal Year",
                        "operating_margin_percent": "Operating Margin (%)",
                    },
                )
                st.plotly_chart(
                    dynamic_margin_fig,
                    use_container_width=True,
                )

                if (
                    forecast_result is not None
                    and forecast_result["forecast"] is not None
                ):
                    st.write("Dynamic revenue forecast")

                    dynamic_forecast = forecast_result["forecast"].copy()

                    forecast_display = dynamic_forecast.melt(
                        id_vars=["year", "data_type"],
                        value_vars=[
                            "actual_revenue_billions",
                            "linear_trend_prediction",
                        ],
                        var_name="series",
                        value_name="revenue_billions",
                    )

                    forecast_display = forecast_display.dropna(
                        subset=["revenue_billions"]
                    )

                    dynamic_forecast_fig = px.line(
                        forecast_display,
                        x="year",
                        y="revenue_billions",
                        color="series",
                        markers=True,
                        title=f"{company['ticker']} Dynamic Revenue Forecast",
                        labels={
                            "year": "Fiscal Year",
                            "revenue_billions": "Revenue ($B)",
                            "series": "Series",
                        },
                    )

                    st.plotly_chart(
                        dynamic_forecast_fig,
                        use_container_width=True,
                    )

                    metrics = forecast_result["metrics"]

                    metric_1, metric_2, metric_3 = st.columns(3)

                    with metric_1:
                        st.metric(
                            "Linear MAE",
                            f"${metrics['linear_mae']:,.1f}B",
                        )

                    with metric_2:
                        st.metric(
                            "Linear MAPE",
                            f"{metrics['linear_mape']:,.1f}%",
                        )

                    with metric_3:
                        st.metric(
                            "Naive MAPE",
                            f"{metrics['naive_mape']:,.1f}%",
                        )

                    st.caption(
                        "The forecast uses a simple linear trend and compares "
                        "against a naive baseline. Lower error is better."
                    )
                elif forecast_result is not None:
                    st.info(
                        "Dynamic revenue forecast unavailable. "
                        f"{forecast_result['error'] or ''}"
                    )

                st.write("Dynamic profitability data")
                st.dataframe(dynamic_df, use_container_width=True)
            else:
                error = None

                if profitability_result is not None:
                    error = profitability_result["error"]

                st.warning(
                    "Dynamic profitability analysis is unavailable for this "
                    f"ticker. {error or ''}"
                )

            st.caption(
                "This panel checks whether the required SEC XBRL tags are "
                "available and runs dynamic profitability and forecasting when "
                "the required data is available."
            )

    df = load_data()

    st.sidebar.header("Filters")

    selected_tickers = st.sidebar.multiselect(
        "Select companies",
        options=sorted(df["ticker"].unique()),
        default=sorted(df["ticker"].unique()),
    )

    filtered = df[df["ticker"].isin(selected_tickers)].copy()

    if filtered.empty:
        st.warning("Select at least one company.")
        return

    latest_rows = (
        filtered.sort_values("end")
        .groupby("ticker")
        .tail(1)
        .sort_values("ticker")
    )

    st.subheader("Latest Company Metrics")

    metric_columns = st.columns(len(latest_rows))

    for column, (_, row) in zip(metric_columns, latest_rows.iterrows()):
        with column:
            st.metric(
                label=f"{row['ticker']} Revenue",
                value=format_billions(row["revenue"]),
            )
            st.caption(
                f"Operating margin: {format_percent(row['operating_margin'])}"
            )
            st.caption(
                f"Free cash flow: {format_billions(row['free_cash_flow'])}"
            )

    st.subheader("Revenue")

    revenue_fig = px.line(
        filtered,
        x="year",
        y="revenue_billions",
        color="ticker",
        markers=True,
        labels={
            "year": "Fiscal Year",
            "revenue_billions": "Revenue ($B)",
            "ticker": "Company",
        },
    )
    st.plotly_chart(revenue_fig, use_container_width=True)

    st.subheader("Operating Margin")

    margin_fig = px.line(
        filtered,
        x="year",
        y="operating_margin_percent",
        color="ticker",
        markers=True,
        labels={
            "year": "Fiscal Year",
            "operating_margin_percent": "Operating Margin (%)",
            "ticker": "Company",
        },
    )
    st.plotly_chart(margin_fig, use_container_width=True)

    st.subheader("Free Cash Flow")

    fcf_fig = px.bar(
        filtered,
        x="year",
        y="free_cash_flow_billions",
        color="ticker",
        barmode="group",
        labels={
            "year": "Fiscal Year",
            "free_cash_flow_billions": "Free Cash Flow ($B)",
            "ticker": "Company",
        },
    )
    st.plotly_chart(fcf_fig, use_container_width=True)

    st.subheader("Revenue Forecast")

    forecast = load_forecast_data()
    forecast = forecast[forecast["ticker"].isin(selected_tickers)].copy()

    if forecast.empty:
        st.info("No revenue forecast data available.")
    else:
        forecast_display = forecast.melt(
            id_vars=["ticker", "year", "data_type"],
            value_vars=[
                "actual_revenue_billions",
                "linear_trend_prediction",
            ],
            var_name="series",
            value_name="revenue_billions",
        )

        forecast_display = forecast_display.dropna(
            subset=["revenue_billions"]
        )

        forecast_fig = px.line(
            forecast_display,
            x="year",
            y="revenue_billions",
            color="ticker",
            line_dash="series",
            markers=True,
            labels={
                "year": "Fiscal Year",
                "revenue_billions": "Revenue ($B)",
                "ticker": "Company",
                "series": "Series",
            },
        )

        st.plotly_chart(forecast_fig, use_container_width=True)

        st.caption(
            "Forecasts use a simple linear trend baseline. They are meant "
            "for learning and comparison, not precise prediction."
        )

    st.subheader("Walmart Scenario Analysis")

    scenario = load_scenario_data()

    if scenario.empty:
        st.info("No scenario data available.")
    else:
        scenario_metric = st.selectbox(
            "Scenario metric",
            options=[
                "revenue_billions",
                "operating_income_billions",
                "free_cash_flow_billions",
                "ccc",
            ],
            format_func={
                "revenue_billions": "Revenue ($B)",
                "operating_income_billions": "Operating Income ($B)",
                "free_cash_flow_billions": "Free Cash Flow ($B)",
                "ccc": "Cash Conversion Cycle (days)",
            }.get,
        )

        scenario_fig = px.bar(
            scenario,
            x="scenario",
            y=scenario_metric,
            color="scenario",
            title="2027 Walmart Scenario Comparison",
            labels={
                "scenario": "Scenario",
                scenario_metric: "Value",
            },
        )
        st.plotly_chart(scenario_fig, use_container_width=True)

        st.caption(
            "Scenario assumptions are illustrative and based loosely on recent "
            "Walmart history. They are not company guidance."
        )

        st.dataframe(
            scenario[
                [
                    "scenario",
                    "revenue_growth",
                    "operating_margin",
                    "dso",
                    "dio",
                    "dpo",
                    "ccc",
                    "free_cash_flow",
                ]
            ],
            use_container_width=True,
        )

    st.subheader("Working Capital Days")

    st.caption(
        "DIO and DPO are available for all current companies. "
        "DSO and full CCC require accounts receivable data, which may be missing."
    )

    working_capital = filtered.melt(
        id_vars=["ticker", "year"],
        value_vars=["dio", "dpo"],
        var_name="metric",
        value_name="days",
    )

    working_capital_fig = px.line(
        working_capital,
        x="year",
        y="days",
        color="ticker",
        line_dash="metric",
        markers=True,
        labels={
            "year": "Fiscal Year",
            "days": "Days",
            "ticker": "Company",
            "metric": "Metric",
        },
    )
    st.plotly_chart(working_capital_fig, use_container_width=True)

    st.subheader("Filtered Data")

    display_columns = [
        "company_name",
        "ticker",
        "end",
        "revenue",
        "revenue_growth",
        "operating_margin",
        "dio",
        "dpo",
        "ccc",
        "free_cash_flow",
        "fcf_margin",
    ]

    st.dataframe(
        filtered[display_columns].sort_values(["ticker", "end"]),
        use_container_width=True,
    )


if __name__ == "__main__":
    main()