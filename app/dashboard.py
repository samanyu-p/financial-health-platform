from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_PATH = "data/processed/company_comparison.csv"


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
        "Retail-focused financial analysis using SEC Company Facts data. "
        "Some metrics may be unavailable when companies do not report the "
        "required XBRL tags."
    )

    with st.expander("Methodology and limitations"):
        st.markdown(
            """
            This dashboard uses SEC Company Facts data to compare financial
            health across selected public retailers.

            **Current scope**
            - The current analysis is retail-focused.
            - Walmart, Target, and Costco are included as initial examples.
            - The pipeline is designed to expand, but not every metric applies
              to every company or industry.

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

            **Limitations**
            SEC XBRL tags can vary across companies, industries, and filing years.
            The project includes tag compatibility checks, but financial metrics
            should still be reviewed before making conclusions. Forecasts and
            scenarios are educational estimates, not investment advice.
            """
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