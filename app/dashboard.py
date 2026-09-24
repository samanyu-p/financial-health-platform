import subprocess
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.data.dynamic_analysis import (
    analyze_dynamic_free_cash_flow,
    analyze_dynamic_profitability,
    analyze_dynamic_working_capital,
)
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


@st.cache_data(ttl=3600)
def cached_ticker_support(ticker):
    return analyze_ticker_support(ticker)


@st.cache_data(ttl=3600)
def cached_dynamic_profitability(ticker):
    return analyze_dynamic_profitability(ticker)


@st.cache_data(ttl=3600)
def cached_dynamic_free_cash_flow(ticker):
    return analyze_dynamic_free_cash_flow(ticker)


@st.cache_data(ttl=3600)
def cached_dynamic_working_capital(ticker):
    return analyze_dynamic_working_capital(ticker)


@st.cache_data(ttl=3600)
def cached_revenue_forecast(ticker):
    return forecast_revenue_for_ticker(ticker)


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


def build_dynamic_export(profitability, free_cash_flow, working_capital, forecast):
    export_df = None

    if profitability is not None:
        profitability_export = profitability.copy()
        profitability_export["year"] = profitability_export["end"].dt.year
        profitability_export = profitability_export[
            [
                "year",
                "end",
                "revenue",
                "revenue_growth",
                "operating_income",
                "operating_margin",
            ]
        ]
        export_df = profitability_export

    if free_cash_flow is not None:
        fcf_export = free_cash_flow.copy()
        fcf_export["year"] = fcf_export["end"].dt.year
        fcf_export = fcf_export[
            [
                "year",
                "operating_cash_flow",
                "capital_expenditures",
                "free_cash_flow",
                "fcf_margin",
            ]
        ]
        export_df = (
            fcf_export
            if export_df is None
            else pd.merge(export_df, fcf_export, on="year", how="outer")
        )

    if working_capital is not None:
        wc_export = working_capital.copy()
        wc_export["year"] = wc_export["end"].dt.year
        wc_export = wc_export[
            [
                "year",
                "cost_of_revenue",
                "accounts_receivable",
                "inventory",
                "accounts_payable",
                "dso",
                "dio",
                "dpo",
                "ccc",
            ]
        ]
        export_df = (
            wc_export
            if export_df is None
            else pd.merge(export_df, wc_export, on="year", how="outer")
        )

    if forecast is not None:
        forecast_export = forecast.copy()
        forecast_export = forecast_export.rename(
            columns={
                "actual_revenue_billions": "actual_revenue_forecast_billions",
                "linear_trend_prediction": "linear_trend_revenue_forecast_billions",
            }
        )

        forecast_columns = [
            "year",
            "actual_revenue_forecast_billions",
            "linear_trend_revenue_forecast_billions",
            "data_type",
        ]

        if "naive_prediction" in forecast_export.columns:
            forecast_export = forecast_export.rename(
                columns={"naive_prediction": "naive_revenue_forecast_billions"}
            )
            forecast_columns.insert(3, "naive_revenue_forecast_billions")

        forecast_export = forecast_export[forecast_columns]
        export_df = (
            forecast_export
            if export_df is None
            else pd.merge(export_df, forecast_export, on="year", how="outer")
        )

    if export_df is None:
        return None

    return export_df.sort_values("year")


def show_dynamic_key_takeaways(
    ticker,
    profitability,
    free_cash_flow,
    working_capital,
):
    st.markdown("#### Key Takeaways")

    takeaways = []

    if profitability is not None and len(profitability) >= 2:
        profitability = profitability.sort_values("end")
        latest = profitability.iloc[-1]
        prior = profitability.iloc[-2]

        revenue_change = latest["revenue_growth"]
        margin_change = latest["operating_margin"] - prior["operating_margin"]

        if pd.notna(revenue_change):
            direction = "increased" if revenue_change > 0 else "declined"
            takeaways.append(
                f"{ticker} revenue {direction} by "
                f"{revenue_change * 100:.1f}% in the latest fiscal year."
            )

        margin_direction = "improved" if margin_change > 0 else "declined"
        takeaways.append(
            f"Operating margin {margin_direction} from "
            f"{prior['operating_margin'] * 100:.1f}% to "
            f"{latest['operating_margin'] * 100:.1f}%."
        )
    else:
        takeaways.append(
            "Revenue and operating margin takeaways are limited because "
            "profitability data is unavailable or incomplete."
        )

    if free_cash_flow is not None and len(free_cash_flow) >= 2:
        free_cash_flow = free_cash_flow.sort_values("end")
        latest_fcf = free_cash_flow.iloc[-1]
        prior_fcf = free_cash_flow.iloc[-2]

        fcf_change = latest_fcf["free_cash_flow"] - prior_fcf["free_cash_flow"]
        fcf_direction = "increased" if fcf_change > 0 else "declined"

        takeaways.append(
            f"Free cash flow {fcf_direction} in the latest fiscal year."
        )
    else:
        takeaways.append(
            "Free cash flow analysis is unavailable for this ticker because "
            "the required SEC tags are missing or not appropriate."
        )

    if working_capital is not None:
        if working_capital["ccc"].notna().any():
            takeaways.append(
                "Working-capital metrics are available, including cash "
                "conversion cycle."
            )
        else:
            takeaways.append(
                "Partial working-capital metrics are available, but full cash "
                "conversion cycle is limited."
            )
    else:
        takeaways.append(
            "Working-capital analysis is unavailable or not meaningful for "
            "this company based on available SEC tags."
        )

    for takeaway in takeaways:
        st.write(f"- {takeaway}")


def show_dynamic_profitability(profitability):
    profitability = profitability.copy()
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
        yaxis2=dict(title="Operating Margin (%)", overlaying="y", side="right"),
        legend=dict(orientation="h"),
    )

    st.plotly_chart(fig, width="stretch")

    latest = profitability.sort_values("end").iloc[-1]
    col1, col2, col3 = st.columns(3)
    col1.metric("Latest Revenue", format_billions(latest["revenue"]))
    col2.metric("Revenue Growth", format_percent(latest["revenue_growth"]))
    col3.metric("Operating Margin", format_percent(latest["operating_margin"]))


def show_dynamic_free_cash_flow(fcf):
    fcf = fcf.copy()
    fcf["year"] = fcf["end"].dt.year
    fcf["operating_cash_flow_billions"] = fcf["operating_cash_flow"] / 1e9
    fcf["capital_expenditures_billions"] = fcf["capital_expenditures"] / 1e9
    fcf["free_cash_flow_billions"] = fcf["free_cash_flow"] / 1e9

    st.markdown("#### Free Cash Flow")

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=fcf["year"],
            y=fcf["operating_cash_flow_billions"],
            name="Operating Cash Flow",
        )
    )
    fig.add_trace(
        go.Bar(
            x=fcf["year"],
            y=fcf["capital_expenditures_billions"],
            name="CapEx",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=fcf["year"],
            y=fcf["free_cash_flow_billions"],
            name="Free Cash Flow",
            mode="lines+markers",
        )
    )
    fig.update_layout(
        xaxis_title="Fiscal Year",
        yaxis_title="$B",
        legend=dict(orientation="h"),
    )

    st.plotly_chart(fig, width="stretch")

    latest_fcf = fcf.sort_values("end").iloc[-1]
    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Operating Cash Flow",
        format_billions(latest_fcf["operating_cash_flow"]),
    )
    col2.metric("CapEx", format_billions(latest_fcf["capital_expenditures"]))
    col3.metric("Free Cash Flow", format_billions(latest_fcf["free_cash_flow"]))


def show_dynamic_working_capital(working_capital):
    wc = working_capital.copy()
    wc["year"] = wc["end"].dt.year

    st.markdown("#### Working Capital")

    fig = go.Figure()

    if wc["dso"].notna().any():
        fig.add_trace(
            go.Scatter(
                x=wc["year"],
                y=wc["dso"],
                name="DSO",
                mode="lines+markers",
            )
        )

    fig.add_trace(
        go.Scatter(
            x=wc["year"],
            y=wc["dio"],
            name="DIO",
            mode="lines+markers",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=wc["year"],
            y=wc["dpo"],
            name="DPO",
            mode="lines+markers",
        )
    )

    if wc["ccc"].notna().any():
        fig.add_trace(
            go.Scatter(
                x=wc["year"],
                y=wc["ccc"],
                name="CCC",
                mode="lines+markers",
            )
        )

    fig.update_layout(
        xaxis_title="Fiscal Year",
        yaxis_title="Days",
        legend=dict(orientation="h"),
    )

    st.plotly_chart(fig, width="stretch")

    latest_wc = wc.sort_values("end").iloc[-1]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("DSO", format_days(latest_wc["dso"]))
    col2.metric("DIO", format_days(latest_wc["dio"]))
    col3.metric("DPO", format_days(latest_wc["dpo"]))
    col4.metric("CCC", format_days(latest_wc["ccc"]))

    if wc["ccc"].isna().all():
        st.info(
            "Full cash conversion cycle is unavailable because accounts "
            "receivable data is missing or not reported consistently."
        )


def show_dynamic_forecast(forecast, metrics):
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
        "This is a simple baseline forecast. It is useful for learning and "
        "comparison, but it should not be treated as a precise investment prediction."
    )


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
        profitability_export = None
        fcf_export = None
        working_capital_export = None
        forecast_export = None
        forecast_metrics = None

        with st.spinner(f"Checking SEC data for {ticker}..."):
            try:
                support_result = cached_ticker_support(ticker)
            except Exception as error:
                st.error("Could not analyze this ticker.")
                st.code(str(error))
                return

        if support_result is None:
            st.error(f"Could not find SEC company data for ticker: {ticker}")
            return

        company = support_result["company"]
        supported = support_result["supported_analyses"]

        try:
            profitability_result = cached_dynamic_profitability(ticker)
            if (
                profitability_result is not None
                and profitability_result["data"] is not None
            ):
                profitability_export = profitability_result["data"].copy()
        except Exception as error:
            profitability_result = {"data": None, "error": str(error)}

        try:
            fcf_result = cached_dynamic_free_cash_flow(ticker)
            if fcf_result is not None and fcf_result["data"] is not None:
                fcf_export = fcf_result["data"].copy()
        except Exception as error:
            fcf_result = {"data": None, "error": str(error)}

        try:
            wc_result = cached_dynamic_working_capital(ticker)
            if wc_result is not None and wc_result["data"] is not None:
                working_capital_export = wc_result["data"].copy()
        except Exception as error:
            wc_result = {"data": None, "error": str(error)}

        try:
            forecast_result = cached_revenue_forecast(ticker)
            forecast_export = forecast_result["forecast"].copy()
            forecast_metrics = forecast_result["metrics"]
        except Exception as error:
            forecast_result = {"forecast": None, "metrics": None, "error": str(error)}

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

        st.dataframe(pd.DataFrame(support_rows), width="stretch", hide_index=True)

        full_export = build_dynamic_export(
            profitability_export,
            fcf_export,
            working_capital_export,
            forecast_export,
        )

        if full_export is not None:
            st.download_button(
                label=f"Download full {ticker} analysis CSV",
                data=full_export.to_csv(index=False),
                file_name=f"{ticker.lower()}_full_analysis.csv",
                mime="text/csv",
            )

        show_dynamic_key_takeaways(
            ticker,
            profitability_export,
            fcf_export,
            working_capital_export,
        )

        st.info(
            "Different industries report different SEC tags. A bank may support "
            "revenue and profitability analysis but not retail working-capital "
            "metrics like inventory days or cash conversion cycle."
        )

        if profitability_export is not None:
            show_dynamic_profitability(profitability_export)
        else:
            st.info(
                "Profitability analysis unavailable: "
                + profitability_result.get("error", "Not available.")
            )

        if fcf_export is not None:
            show_dynamic_free_cash_flow(fcf_export)
        else:
            st.info(
                "Free cash flow analysis unavailable: "
                + fcf_result.get("error", "Not available.")
            )

        if working_capital_export is not None:
            show_dynamic_working_capital(working_capital_export)
        else:
            st.info(
                "Working capital analysis unavailable: "
                + wc_result.get("error", "Not available.")
            )

        if forecast_export is not None and forecast_metrics is not None:
            show_dynamic_forecast(forecast_export, forecast_metrics)
        else:
            st.info(
                "Revenue forecasting unavailable: "
                + forecast_result.get("error", "Not available.")
            )


def show_kpis(company_df):
    latest = company_df.sort_values("end").iloc[-1]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Revenue", format_billions(latest["revenue"]))
    col2.metric("Revenue Growth", format_percent(latest["revenue_growth"]))
    col3.metric("Operating Margin", format_percent(latest["operating_margin"]))
    col4.metric("Free Cash Flow", format_billions(latest["free_cash_flow"]))


def show_company_comparison_summary(df):
    st.subheader("Company Comparison Summary")

    latest_by_company = (
        df.sort_values("end")
        .groupby("ticker", as_index=False)
        .tail(1)
        .copy()
    )

    highest_revenue = latest_by_company.loc[latest_by_company["revenue"].idxmax()]
    highest_margin = latest_by_company.loc[
        latest_by_company["operating_margin"].idxmax()
    ]
    highest_fcf = latest_by_company.loc[
        latest_by_company["free_cash_flow"].idxmax()
    ]

    ccc_available = latest_by_company[latest_by_company["ccc"].notna()].copy()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Highest Revenue",
        highest_revenue["ticker"],
        format_billions(highest_revenue["revenue"]),
    )
    col2.metric(
        "Highest Operating Margin",
        highest_margin["ticker"],
        format_percent(highest_margin["operating_margin"]),
    )
    col3.metric(
        "Highest Free Cash Flow",
        highest_fcf["ticker"],
        format_billions(highest_fcf["free_cash_flow"]),
    )

    if not ccc_available.empty:
        shortest_ccc = ccc_available.loc[ccc_available["ccc"].idxmin()]
        col4.metric(
            "Shortest CCC",
            shortest_ccc["ticker"],
            format_days(shortest_ccc["ccc"]),
        )
    else:
        col4.metric("Shortest CCC", "N/A", "No full CCC data")

    st.caption(
        "These summary cards use the latest available fiscal year for each "
        "configured company. Because fiscal year-end dates differ, compare them "
        "as directional indicators rather than perfectly synchronized periods."
    )


def show_revenue_chart(company_df, selected_ticker):
    chart_df = company_df.copy()
    chart_df["revenue_billions"] = chart_df["revenue"] / 1e9

    fig = px.bar(
        chart_df,
        x="year",
        y="revenue_billions",
        title=f"{selected_ticker} Revenue",
        labels={"year": "Fiscal Year", "revenue_billions": "Revenue ($B)"},
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
    chart_df["operating_cash_flow_billions"] = chart_df["operating_cash_flow"] / 1e9
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


def show_multi_company_metric_trend(df):
    st.subheader("Multi-Company Metric Trend")

    metric_options = {
        "Revenue": "revenue",
        "Revenue Growth": "revenue_growth",
        "Operating Margin": "operating_margin",
        "Free Cash Flow": "free_cash_flow",
        "DIO": "dio",
        "DPO": "dpo",
        "CCC": "ccc",
    }

    selected_metric_label = st.selectbox(
        "Select a metric to compare",
        list(metric_options.keys()),
    )
    selected_metric = metric_options[selected_metric_label]

    chart_df = df.copy()

    if selected_metric in ["revenue", "free_cash_flow"]:
        chart_df[selected_metric] = chart_df[selected_metric] / 1e9
        y_label = f"{selected_metric_label} ($B)"
    elif selected_metric in ["revenue_growth", "operating_margin"]:
        chart_df[selected_metric] = chart_df[selected_metric] * 100
        y_label = f"{selected_metric_label} (%)"
    else:
        y_label = f"{selected_metric_label} (Days)"

    fig = px.line(
        chart_df,
        x="year",
        y=selected_metric,
        color="ticker",
        markers=True,
        title=f"{selected_metric_label} by Company",
        labels={
            "year": "Fiscal Year",
            selected_metric: y_label,
            "ticker": "Ticker",
        },
    )

    st.plotly_chart(fig, width="stretch")

    st.caption(
        "Companies may have different fiscal year-end dates and different SEC "
        "tag availability. Missing values are left blank instead of forcing a "
        "misleading comparison."
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
    display["operating_margin"] = display["operating_margin"].apply(format_percent)
    display["dio"] = display["dio"].apply(format_days)
    display["dpo"] = display["dpo"].apply(format_days)
    display["ccc"] = display["ccc"].apply(format_days)
    display["free_cash_flow"] = display["free_cash_flow"].apply(format_billions)

    st.dataframe(display, width="stretch", hide_index=True)

    chart_df = latest_by_company.copy()
    chart_df["revenue_billions"] = chart_df["revenue"] / 1e9

    fig = px.bar(
        chart_df,
        x="ticker",
        y="revenue_billions",
        title="Latest Revenue by Company",
        labels={"ticker": "Ticker", "revenue_billions": "Revenue ($B)"},
    )
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
        display["revenue_growth"] = display["revenue_growth"].apply(format_percent)

    if "operating_margin" in display.columns:
        display["operating_margin"] = display["operating_margin"].apply(format_percent)

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
        "Financial analysis using SEC Company Facts data, with dynamic ticker "
        "analysis, company comparison, forecasting, and business-model-aware "
        "metric guidance."
    )

    dynamic_tab, comparison_tab, scenario_tab, methodology_tab = st.tabs(
        [
            "Dynamic Ticker",
            "Company Comparison",
            "Scenario Analysis",
            "Methodology",
        ]
    )

    with dynamic_tab:
        show_dynamic_ticker_section()

    with comparison_tab:
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

        show_company_comparison_summary(df)

        section_divider()

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
        show_multi_company_metric_trend(df)

        section_divider()
        show_company_comparison(df)

    with scenario_tab:
        show_scenario_analysis()

    with methodology_tab:
        show_methodology()


if __name__ == "__main__":
    main()