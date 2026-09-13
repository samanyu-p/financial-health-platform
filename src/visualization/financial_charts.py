import pandas as pd
import plotly.graph_objects as go


# -----------------------------
# Load financial health data
# -----------------------------

df = pd.read_csv(
    "data/processed/walmart_financial_health.csv"
)

df["end"] = pd.to_datetime(df["end"])
df["year"] = df["end"].dt.year


# -----------------------------
# Chart 1: Revenue + Growth
# -----------------------------

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=df["year"],
        y=df["revenue"] / 1e9,
        name="Revenue"
    )
)

fig.add_trace(
    go.Scatter(
        x=df["year"],
        y=df["revenue_growth"] * 100,
        mode="lines+markers",
        name="Revenue Growth",
        yaxis="y2"
    )
)

fig.update_layout(
    title="Walmart Revenue and Revenue Growth",
    xaxis_title="Year",
    yaxis_title="Revenue ($B)",
    yaxis2=dict(
        title="Revenue Growth (%)",
        overlaying="y",
        side="right"
    )
)

fig.show()


# -----------------------------
# Chart 2: Operating Margin
# -----------------------------

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df["year"],
        y=df["operating_margin"] * 100,
        mode="lines+markers",
        name="Operating Margin"
    )
)

fig.update_layout(
    title="Walmart Operating Margin",
    xaxis_title="Year",
    yaxis_title="Operating Margin (%)"
)

fig.show()


# -----------------------------
# Chart 3: Cash Conversion Cycle
# -----------------------------

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df["year"],
        y=df["ccc"],
        mode="lines+markers",
        name="CCC"
    )
)

fig.add_hline(
    y=0,
    line_dash="dash"
)

fig.update_layout(
    title="Walmart Cash Conversion Cycle",
    xaxis_title="Year",
    yaxis_title="Cash Conversion Cycle (Days)"
)

fig.show()


# -----------------------------
# Chart 4: Cash Flow
# -----------------------------

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=df["year"],
        y=df["operating_cash_flow"] / 1e9,
        name="Operating Cash Flow"
    )
)

fig.add_trace(
    go.Bar(
        x=df["year"],
        y=df["capital_expenditures"] / 1e9,
        name="Capital Expenditures"
    )
)

fig.add_trace(
    go.Scatter(
        x=df["year"],
        y=df["free_cash_flow"] / 1e9,
        mode="lines+markers",
        name="Free Cash Flow"
    )
)

fig.update_layout(
    title="Walmart Operating Cash Flow, CapEx, and FCF",
    xaxis_title="Year",
    yaxis_title="Cash Flow ($B)",
    barmode="group"
)

fig.show()