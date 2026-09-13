import json
import pandas as pd

# -----------------------------
# Load Revenue
# -----------------------------

revenue_df = pd.read_csv("data/processed/walmart_revenue.csv")
revenue_df["end"] = pd.to_datetime(revenue_df["end"])
revenue_df = revenue_df.rename(columns={"val": "revenue"})


# -----------------------------
# Load Accounts Receivable
# -----------------------------

ar_df = pd.read_csv("data/processed/walmart_accounts_receivable.csv")
ar_df["end"] = pd.to_datetime(ar_df["end"])
ar_df = ar_df.rename(columns={"val": "accounts_receivable"})


# -----------------------------
# Load Inventory
# -----------------------------

inventory_df = pd.read_csv("data/processed/walmart_inventory.csv")
inventory_df["end"] = pd.to_datetime(inventory_df["end"])
inventory_df = inventory_df.rename(columns={"val": "inventory"})


# -----------------------------
# Load Accounts Payable
# -----------------------------

ap_df = pd.read_csv("data/processed/walmart_accounts_payable.csv")
ap_df["end"] = pd.to_datetime(ap_df["end"])
ap_df = ap_df.rename(columns={"val": "accounts_payable"})


# -----------------------------
# Load Cost of Revenue
# -----------------------------

with open("data/raw/walmart_companyfacts.json", "r") as file:
    data = json.load(file)

cost_records = data["facts"]["us-gaap"]["CostOfRevenue"]["units"]["USD"]

cost_df = pd.DataFrame(cost_records)

# Keep annual 10-K filings
cost_df = cost_df[cost_df["form"] == "10-K"].copy()

# Keep records with start and end dates
cost_df = cost_df[
    cost_df["start"].notna() & cost_df["end"].notna()
].copy()

# Convert dates
cost_df["start"] = pd.to_datetime(cost_df["start"])
cost_df["end"] = pd.to_datetime(cost_df["end"])

# Keep approximately annual periods
cost_df["days"] = (
    cost_df["end"] - cost_df["start"]
).dt.days

cost_df = cost_df[
    (cost_df["days"] >= 300) &
    (cost_df["days"] <= 400)
].copy()

# Remove duplicate reporting periods
cost_df = cost_df.drop_duplicates(subset=["start", "end"])

# Keep only the columns we need
cost_df = cost_df[["end", "val"]]

cost_df = cost_df.rename(
    columns={"val": "cost_of_revenue"}
)


# -----------------------------
# Merge the Data
# -----------------------------

df = pd.merge(
    revenue_df,
    ar_df,
    on="end",
    how="inner"
)

df = pd.merge(
    df,
    inventory_df,
    on="end",
    how="inner"
)

df = pd.merge(
    df,
    ap_df,
    on="end",
    how="inner"
)

df = pd.merge(
    df,
    cost_df,
    on="end",
    how="inner"
)

df = df.sort_values("end")


# -----------------------------
# Calculate DSO
# -----------------------------

df["average_ar"] = (
    df["accounts_receivable"]
    + df["accounts_receivable"].shift(1)
) / 2

df["dso"] = (
    df["average_ar"]
    / df["revenue"]
    * 365
)


# -----------------------------
# Calculate DIO
# -----------------------------

df["average_inventory"] = (
    df["inventory"]
    + df["inventory"].shift(1)
) / 2

df["dio"] = (
    df["average_inventory"]
    / df["cost_of_revenue"]
    * 365
)


# -----------------------------
# Calculate DPO
# -----------------------------

df["average_ap"] = (
    df["accounts_payable"]
    + df["accounts_payable"].shift(1)
) / 2

df["dpo"] = (
    df["average_ap"]
    / df["cost_of_revenue"]
    * 365
)


# -----------------------------
# Calculate Cash Conversion Cycle
# -----------------------------

df["ccc"] = (
    df["dso"]
    + df["dio"]
    - df["dpo"]
)


# -----------------------------
# Display Results
# -----------------------------

print("\nWalmart Working Capital Analysis:\n")

print(
    df[
        [
            "end",
            "revenue",
            "dso",
            "dio",
            "dpo",
            "ccc"
        ]
    ].to_string(index=False)
)

# -----------------------------
# Save Working Capital Analysis
# -----------------------------

output_path = "data/processed/walmart_working_capital.csv"

df[
    [
        "end",
        "revenue",
        "accounts_receivable",
        "inventory",
        "accounts_payable",
        "cost_of_revenue",
        "dso",
        "dio",
        "dpo",
        "ccc"
    ]
].to_csv(output_path, index=False)

print(f"\nSaved working capital analysis to {output_path}")