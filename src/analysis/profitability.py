import pandas as pd

# -----------------------------
# Load Revenue
# -----------------------------

revenue_df = pd.read_csv(
    "data/processed/walmart_revenue.csv"
)

revenue_df["end"] = pd.to_datetime(
    revenue_df["end"]
)

revenue_df = revenue_df.rename(
    columns={"val": "revenue"}
)


# -----------------------------
# Load Operating Income
# -----------------------------

operating_df = pd.read_csv(
    "data/processed/walmart_operating_income.csv"
)

operating_df["end"] = pd.to_datetime(
    operating_df["end"]
)

operating_df = operating_df.rename(
    columns={"val": "operating_income"}
)


# -----------------------------
# Merge Revenue and
# Operating Income
# -----------------------------

df = pd.merge(
    revenue_df,
    operating_df,
    on="end",
    how="inner"
)

df = df.sort_values("end")


# -----------------------------
# Calculate Operating Margin
# -----------------------------

df["operating_margin"] = (
    df["operating_income"]
    / df["revenue"]
)


# -----------------------------
# Display Results
# -----------------------------

print("\nWalmart Profitability Analysis:\n")

print(
    df[
        [
            "end",
            "revenue",
            "operating_income",
            "operating_margin"
        ]
    ].to_string(index=False)
)


# -----------------------------
# Save Results
# -----------------------------

output_path = (
    "data/processed/"
    "walmart_profitability.csv"
)

df[
    [
        "end",
        "revenue",
        "operating_income",
        "operating_margin"
    ]
].to_csv(
    output_path,
    index=False
)

print(
    f"\nSaved profitability analysis to {output_path}"
)