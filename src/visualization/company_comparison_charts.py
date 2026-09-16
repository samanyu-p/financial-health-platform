import pandas as pd
import plotly.express as px


INPUT_PATH = "data/processed/company_comparison.csv"


def main():
    df = pd.read_csv(INPUT_PATH)
    df["end"] = pd.to_datetime(df["end"])
    df["year"] = df["end"].dt.year

    df["revenue_billions"] = df["revenue"] / 1e9
    df["free_cash_flow_billions"] = df["free_cash_flow"] / 1e9
    df["operating_margin_percent"] = df["operating_margin"] * 100
    df["fcf_margin_percent"] = df["fcf_margin"] * 100

    revenue_fig = px.line(
        df,
        x="year",
        y="revenue_billions",
        color="ticker",
        markers=True,
        title="Revenue by Company",
        labels={
            "year": "Fiscal Year",
            "revenue_billions": "Revenue ($B)",
            "ticker": "Company",
        },
    )
    revenue_fig.show()

    margin_fig = px.line(
        df,
        x="year",
        y="operating_margin_percent",
        color="ticker",
        markers=True,
        title="Operating Margin by Company",
        labels={
            "year": "Fiscal Year",
            "operating_margin_percent": "Operating Margin (%)",
            "ticker": "Company",
        },
    )
    margin_fig.show()

    working_capital_df = df.melt(
        id_vars=["ticker", "year"],
        value_vars=["dio", "dpo"],
        var_name="metric",
        value_name="days",
    )

    working_capital_fig = px.line(
        working_capital_df,
        x="year",
        y="days",
        color="ticker",
        line_dash="metric",
        markers=True,
        title="Inventory and Payables Days by Company",
        labels={
            "year": "Fiscal Year",
            "days": "Days",
            "ticker": "Company",
            "metric": "Metric",
        },
    )
    working_capital_fig.show()

    fcf_fig = px.bar(
        df,
        x="year",
        y="free_cash_flow_billions",
        color="ticker",
        barmode="group",
        title="Free Cash Flow by Company",
        labels={
            "year": "Fiscal Year",
            "free_cash_flow_billions": "Free Cash Flow ($B)",
            "ticker": "Company",
        },
    )
    fcf_fig.show()

    print("Displayed company comparison charts.")


if __name__ == "__main__":
    main()