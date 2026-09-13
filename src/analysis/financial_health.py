import pandas as pd


# -----------------------------
# Load profitability data
# -----------------------------

profitability_df = pd.read_csv(
    "data/processed/walmart_profitability.csv"
)

profitability_df["end"] = pd.to_datetime(
    profitability_df["end"]
)


# -----------------------------
# Load working capital data
# -----------------------------

working_capital_df = pd.read_csv(
    "data/processed/walmart_working_capital.csv"
)

working_capital_df["end"] = pd.to_datetime(
    working_capital_df["end"]
)


# -----------------------------
# Load free cash flow data
# -----------------------------

fcf_df = pd.read_csv(
    "data/processed/walmart_free_cash_flow.csv"
)

fcf_df["end"] = pd.to_datetime(
    fcf_df["end"]
)


# -----------------------------
# Combine the datasets
# -----------------------------

df = pd.merge(
    profitability_df,
    working_capital_df[
        [
            "end",
            "dso",
            "dio",
            "dpo",
            "ccc"
        ]
    ],
    on="end",
    how="inner"
)

df = pd.merge(
    df,
    fcf_df[
        [
            "end",
            "operating_cash_flow",
            "capital_expenditures",
            "free_cash_flow",
            "fcf_margin"
        ]
    ],
    on="end",
    how="inner"
)


# -----------------------------
# Calculate revenue growth
# -----------------------------

df = df.sort_values("end")

df["revenue_growth"] = (
    df["revenue"].pct_change()
)


# -----------------------------
# Reorder columns
# -----------------------------

df = df[
    [
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
        "fcf_margin"
    ]
]


# -----------------------------
# Display results
# -----------------------------

print("\nWalmart Financial Health Analysis:\n")

print(
    df.to_string(index=False)
)


# -----------------------------
# Save final dataset
# -----------------------------

output_path = (
    "data/processed/walmart_financial_health.csv"
)

df.to_csv(
    output_path,
    index=False
)

print(
    f"\nSaved financial health analysis to {output_path}"
)