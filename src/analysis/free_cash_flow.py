import pandas as pd


# Load operating cash flow
ocf_df = pd.read_csv(
    "data/processed/walmart_operating_cash_flow.csv"
)

ocf_df["end"] = pd.to_datetime(ocf_df["end"])


# Load capital expenditures
capex_df = pd.read_csv(
    "data/processed/walmart_capex.csv"
)

capex_df["end"] = pd.to_datetime(capex_df["end"])


# Combine the two datasets
df = pd.merge(
    ocf_df,
    capex_df,
    on=["start", "end"],
    how="inner"
)


# Calculate Free Cash Flow
df["free_cash_flow"] = (
    df["operating_cash_flow"]
    - df["capital_expenditures"]
)


# Calculate FCF margin
df["fcf_margin"] = (
    df["free_cash_flow"]
    / df["operating_cash_flow"]
)


# Display results
print("\nWalmart Free Cash Flow Analysis:\n")

print(
    df[
        [
            "end",
            "operating_cash_flow",
            "capital_expenditures",
            "free_cash_flow",
            "fcf_margin"
        ]
    ].to_string(index=False)
)


# Save results
output_path = "data/processed/walmart_free_cash_flow.csv"

df[
    [
        "end",
        "operating_cash_flow",
        "capital_expenditures",
        "free_cash_flow",
        "fcf_margin"
    ]
].to_csv(
    output_path,
    index=False
)

print(
    f"\nSaved FCF analysis to {output_path}"
)