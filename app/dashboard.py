import subprocess
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.data.dynamic_analysis import analyze_dynamic_profitability
from src.data.dynamic_company import analyze_ticker_support
from src.models.dynamic_forecast import forecast_revenue_for_ticker


DATA_PATH = Path("data/processed/company_comparison.csv")
SCENARIO_PATH = Path("data/processed/walmart_scenario_analysis.csv")


st.set_page_config(
    page_title="Corporate Financial Health Dashboard",
    layout="wide",
)


def ensure_dashboard_data():
    if DATA_PATH.exists():
        return

    st.warning("Dashboard data not found. Building data pipeline now...")

    result = subprocess.run(
        [sys.executable, "-m", "src.data.run_pipeline"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        st.error("The data pipeline failed while building dashboard data.")

        with st.expander("Pipeline stdout"):
            st.code(result.stdout or "No stdout captured.")

        with st.expander("Pipeline stderr"):
            st.code(result.stderr or "No stderr captured.")

        st.stop()

    st.success("Dashboard data built successfully. Reloading dashboard...")
    st.rerun()


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["end"] = pd.to_datetime(df["end"])
    df["year"] = df["end"].dt.year
    return df


@st.cache_data
def load_scenario_data():
    if not SCENARIO_PATH.exists():
        return pd.DataFrame()

    scenario = pd.read_csv(SCENARIO_PATH)
    return scenario


def format_billions(value):
    if pd.isna(value):
        return "N/A"

    return f"${value / 1e9:,.1f}B"


def format_percent(value):
    if pd.isna(value):
        return "N/A"

    return f"{value * 100:.1f}%"


def format_days(value):
    if pd.isna(value):
        return "N/A"

    return f"{value:.1f} days"


def section_divider():
    st.markdown("---")


def show_dynamic_ticker_section():
    st.subheader("Analyze Any SEC Ticker")

    ticker = st.text_input(
        "Enter a ticker to analyze",
        value="AAPL",
        help="Examples: AAPL, MSFT, JPM, WMT, COST, TGT",
    )

    if not ticker:
        return

    ticker = ticker.upper().strip()

    if st.button("Analyze ticker"):
        with st.spinner(f"Checking SEC data for {ticker}..."):
            try:
                support_result = analyze_ticker_support(ticker)
            except Exception as error:
                st.error("Could not analyze this ticker.")
                st.code(str(error))
                return

        if support_result is None:
            st.error(f"Could not find SEC company data for ticker: {ticker}")
            return

        company = support_result["company"]
        supported = support_result["supported_analyses"]

        st.write(f"**Company:** {company['name']}")
        st.write(f"**Ticker:** {company['ticker']}")
        st.write(f"**CIK:** {company['cik']}")

        company_profile = support_result.get(
            "company_profile",
            {
                "profile": "General SEC reporting company",
                "fit": (
                    "Core revenue and profitability analysis may be available, "
                    "but industry-specific metrics depend on reported SEC tags."
                ),
                "interpretation": (
                    "This company can be analyzed using the SEC tags available "
                    "in its filings. Some metrics may be unavailable if the "
                    "company does not report the required data."
                ),
            },
        )

        st.info(
            f"**Company Profile:** {company_profile['profile']}\n\n"
            f"**Analysis Fit:** {company_profile['fit']}\n\n"
            f"{company_profile['interpretation']}"
        )

        support_rows = []
        for analysis_name, details in supported.items():
            missing = details.get("missing_metrics", [])
            support_rows.append(
                {
                    "Analysis": analysis_name,
                    "Supported": "Yes" if details["is_supported"] else "No",
                    "Missing metrics": ", ".join(missing) if missing else "",
                }
            )

        st.dataframe(
            pd.DataFrame(support_rows),
            width="stretch",
            hide_index=True,
        )

        st.info(
            "Different industries report different SEC tags. A bank may support "
            "revenue and profitability analysis but not retail working-capital "
            "metrics like inventory days or cash conversion cycle."
        )

        try:
            profitability_result = analyze_dynamic_profitability(ticker)
            profitability = profitability_result["data"].copy()
            profitability["year"] = profitability["end"].dt.year
            profitability["revenue_billions"] = profitability["revenue"] / 1e9

            st.markdown("#### Revenue and Operating Margin")

            fig = go.Figure()

            fig.add_trace(
                go.Bar(
                    x=profitability["year"],
                    y=profitability["revenue_billions"],
                    name="Revenue ($B)",
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=profitability["year"],
                    y=profitability["operating_margin"] * 100,
                    name="Operating Margin (%)",
                    mode="lines+markers",
                    yaxis="y2",
                )
            )

            fig.update_layout(
                xaxis_title="Fiscal Year",
                yaxis=dict(title="Revenue ($B)"),
                yaxis2=dict(
                    title="Operating Margin (%)",
                    overlaying="y",
                    side="right",
                ),
                legend=dict(orientation="h"),
            )

            st.plotly_chart(fig, width="stretch")

            latest = profitability.sort_values("end").iloc[-1]

            col1, col2, col3 = st.columns(3)
            col1.metric("Latest Revenue", format_billions(latest["revenue"]))
            col2.metric(
                "Revenue Growth",
                format_percent(latest["revenue_growth"]),
            )
            col3.metric(
                "Operating Margin",
                format_percent(latest["operating_margin"]),
            )

        except Exception as error:
            st.warning("Profitability analysis is not available for this ticker.")
            st.code(str(error))

        try:
            forecast_result = forecast_revenue_for_ticker(ticker)
            forecast = forecast_result["forecast"].copy()
            metrics = forecast_result["metrics"]

            st.markdown("#### Simple Revenue Forecast")

            forecast_plot = forecast.copy()
            forecast_plot["actual_revenue_billions"] = pd.to_numeric(
                forecast_plot["actual_revenue_billions"],
                errors="coerce",
            )
            forecast_plot["linear_trend_prediction"] = pd.to_numeric(
                forecast_plot["linear_trend_prediction"],
                errors="coerce",
            )

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=forecast_plot["year"],
                    y=forecast_plot["actual_revenue_billions"],
                    name="Actual Revenue",
                    mode="lines+markers",
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=forecast_plot["year"],
                    y=forecast_plot["linear_trend_prediction"],
                    name="Linear Trend Forecast",
                    mode="lines+markers",
                    line=dict(dash="dash"),
                )
            )

            fig.update_layout(
                xaxis_title="Fiscal Year",
                yaxis_title="Revenue ($B)",
                legend=dict(orientation="h"),
            )

            st.plotly_chart(fig, width="stretch")

            col1, col2, col3 = st.columns(3)
            col1.metric("Linear MAE", f"{metrics['linear_mae']:.2f}B")
            col2.metric("Linear RMSE", f"{metrics['linear_rmse']:.2f}B")
            col3.metric("Linear MAPE", f"{metrics['linear_mape']:.2f}%")

            st.caption(
                "This is a simple baseline forecast. It is useful for learning "
                "and comparison, but it should not be treated as a precise "
                "investment prediction."
            )

        except Exception as error:
            st.warning("Revenue forecasting is not available for this ticker.")
            st.code(str(error))


def show_kpis(company_df):
    latest = company_df.sort_values("end").iloc[-1]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Revenue", format_billions(latest["revenue"]))
    col2.metric("Revenue Growth", format_percent(latest["revenue_growth"]))
    col3.metric("Operating Margin", format_percent(latest["operating_margin"]))
    col4.metric("Free Cash Flow", format_billions(latest["free_cash_flow"]))


def show_revenue_chart(company_df, selected_ticker):
    chart_df = company_df.copy()
    chart_df["revenue_billions"] = chart_df["revenue"] / 1e9

    fig = px.bar(
        chart_df,
        x="year",
        y="revenue_billions",
        title=f"{selected_ticker} Revenue",
        labels={
            "year": "Fiscal Year",
            "revenue_billions": "Revenue ($B)",
        },
    )

    st.plotly_chart(fig, width="stretch")


def show_margin_chart(company_df, selected_ticker):
    chart_df = company_df.copy()
    chart_df["operating_margin_percent"] = chart_df["operating_margin"] * 100

    fig = px.line(
        chart_df,
        x="year",
        y="operating_margin_percent",
        markers=True,
        title=f"{selected_ticker} Operating Margin",
        labels={
            "year": "Fiscal Year",
            "operating_margin_percent": "Operating Margin (%)",
        },
    )

    st.plotly_chart(fig, width="stretch")


def show_cash_flow_chart(company_df, selected_ticker):
    chart_df = company_df.copy()
    chart_df["operating_cash_flow_billions"] = (
        chart_df["operating_cash_flow"] / 1e9
    )
    chart_df["capital_expenditures_billions"] = (
        chart_df["capital_expenditures"] / 1e9
    )
    chart_df["free_cash_flow_billions"] = chart_df["free_cash_flow"] / 1e9

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=chart_df["year"],
            y=chart_df["operating_cash_flow_billions"],
            name="Operating Cash Flow",
        )
    )

    fig.add_trace(
        go.Bar(
            x=chart_df["year"],
            y=chart_df["capital_expenditures_billions"],
            name="CapEx",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df["year"],
            y=chart_df["free_cash_flow_billions"],
            name="Free Cash Flow",
            mode="lines+markers",
        )
    )

    fig.update_layout(
        title=f"{selected_ticker} Cash Flow",
        xaxis_title="Fiscal Year",
        yaxis_title="$B",
        legend=dict(orientation="h"),
    )

    st.plotly_chart(fig, width="stretch")


def show_working_capital_chart(company_df, selected_ticker):
    chart_df = company_df.copy()

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=chart_df["year"],
            y=chart_df["dio"],
            name="DIO",
            mode="lines+markers",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df["year"],
            y=chart_df["dpo"],
            name="DPO",
            mode="lines+markers",
        )
    )

    if chart_df["ccc"].notna().any():
        fig.add_trace(
            go.Scatter(
                x=chart_df["year"],
                y=chart_df["ccc"],
                name="CCC",
                mode="lines+markers",
            )
        )

    fig.update_layout(
        title=f"{selected_ticker} Working Capital Metrics",
        xaxis_title="Fiscal Year",
        yaxis_title="Days",
        legend=dict(orientation="h"),
    )

    st.plotly_chart(fig, width="stretch")

    if chart_df["ccc"].isna().all():
        st.info(
            "Cash conversion cycle is unavailable because this company does "
            "not report all required SEC tags, usually accounts receivable."
        )


def show_company_comparison(df):
    st.subheader("Company Comparison")

    latest_by_company = (
        df.sort_values("end")
        .groupby("ticker", as_index=False)
        .tail(1)
        .sort_values("ticker")
    )

    display = latest_by_company[
        [
            "ticker",
            "end",
            "revenue",
            "operating_margin",
            "dio",
            "dpo",
            "ccc",
            "free_cash_flow",
        ]
    ].copy()

    display["revenue"] = display["revenue"].apply(format_billions)
    display["operating_margin"] = display["operating_margin"].apply(
        format_percent
    )
    display["dio"] = display["dio"].apply(format_days)
    display["dpo"] = display["dpo"].apply(format_days)
    display["ccc"] = display["ccc"].apply(format_days)
    display["free_cash_flow"] = display["free_cash_flow"].apply(
        format_billions
    )

    st.dataframe(display, width="stretch", hide_index=True)

    chart_df = latest_by_company.copy()
    chart_df["revenue_billions"] = chart_df["revenue"] / 1e9
    chart_df["free_cash_flow_billions"] = chart_df["free_cash_flow"] / 1e9

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            chart_df,
            x="ticker",
            y="revenue_billions",
            title="Latest Revenue by Company",
            labels={
                "ticker": "Ticker",
                "revenue_billions": "Revenue ($B)",
            },
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = px.bar(
            chart_df,
            x="ticker",
            y="operating_margin",
            title="Latest Operating Margin by Company",
            labels={
                "ticker": "Ticker",
                "operating_margin": "Operating Margin",
            },
        )
        fig.update_yaxes(tickformat=".1%")
        st.plotly_chart(fig, width="stretch")


def show_scenario_analysis():
    scenario = load_scenario_data()

    if scenario.empty:
        st.info("Scenario analysis data is not available yet.")
        return

    st.subheader("Example Scenario Analysis: Walmart")

    st.caption(
        "This scenario model is currently built only for Walmart. "
        "Dynamic ticker-specific scenario analysis is a future improvement."
    )

    display = scenario.copy()

    dollar_columns = [
        "revenue",
        "operating_income",
        "operating_cash_flow",
        "capital_expenditures",
        "free_cash_flow",
    ]

    for column in dollar_columns:
        if column in display.columns:
            display[column] = display[column].apply(format_billions)

    if "revenue_growth" in display.columns:
        display["revenue_growth"] = display["revenue_growth"].apply(
            format_percent
        )

    if "operating_margin" in display.columns:
        display["operating_margin"] = display["operating_margin"].apply(
            format_percent
        )

    st.dataframe(display, width="stretch", hide_index=True)

    chart_df = scenario.copy()
    chart_df["free_cash_flow_billions"] = chart_df["free_cash_flow"] / 1e9

    fig = px.bar(
        chart_df,
        x="scenario",
        y="free_cash_flow_billions",
        title="Scenario Free Cash Flow",
        labels={
            "scenario": "Scenario",
            "free_cash_flow_billions": "Free Cash Flow ($B)",
        },
    )

    st.plotly_chart(fig, width="stretch")


def show_methodology():
    st.subheader("Methodology and Limitations")

    st.markdown(
        """
        This dashboard uses SEC Company Facts data. The pipeline fetches raw SEC
        JSON, cleans annual filing data, calculates financial metrics, and builds
        comparison datasets.

        Important limitations:

        - SEC XBRL tags vary by company and industry.
        - Retail working-capital metrics are not always meaningful for banks,
          insurers, software companies, or asset-light businesses.
        - If a company does not report a required tag, the dashboard shows partial
          analysis instead of forcing a misleading metric.
        - Forecasts are simple baselines, not investment advice.
        - Scenario assumptions are illustrative and are not company guidance.
        """
    )


def main():
    ensure_dashboard_data()

    st.title("Corporate Financial Health Dashboard")
    st.write(
        "Retail-focused financial analysis using SEC Company Facts data, with "
        "an expanding dynamic ticker analysis tool."
    )

    show_dynamic_ticker_section()

    section_divider()

    df = load_data()

    st.download_button(
        label="Download company comparison CSV",
        data=df.to_csv(index=False),
        file_name="company_comparison.csv",
        mime="text/csv",
    )

    st.subheader("Configured Company Dashboard")

    tickers = sorted(df["ticker"].dropna().unique())
    selected_ticker = st.selectbox("Select a company", tickers)

    company_df = (
        df[df["ticker"] == selected_ticker]
        .sort_values("end")
        .reset_index(drop=True)
    )

    show_kpis(company_df)

    col1, col2 = st.columns(2)

    with col1:
        show_revenue_chart(company_df, selected_ticker)

    with col2:
        show_margin_chart(company_df, selected_ticker)

    col3, col4 = st.columns(2)

    with col3:
        show_cash_flow_chart(company_df, selected_ticker)

    with col4:
        show_working_capital_chart(company_df, selected_ticker)

    section_divider()

    show_company_comparison(df)

    section_divider()

    show_scenario_analysis()

    section_divider()

    show_methodology()


if __name__ == "__main__":
    main()