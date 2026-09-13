import json
import pandas as pd

file_path = "data/raw/walmart_companyfacts.json"

with open(file_path, "r") as file:
    data = json.load(file)

revenue = data["facts"]["us-gaap"][
    "RevenueFromContractWithCustomerExcludingAssessedTax"
]

records = revenue["units"]["USD"]

df = pd.DataFrame(records)

# Keep only annual 10-K filings
df = df[df["form"] == "10-K"].copy()

# Keep only records that represent a full fiscal year
df = df[df["start"].notna() & df["end"].notna()].copy()

# Calculate the length of each reporting period
df["start"] = pd.to_datetime(df["start"])
df["end"] = pd.to_datetime(df["end"])

df["days"] = (df["end"] - df["start"]).dt.days

# Walmart's fiscal year is approximately 365 days
df = df[(df["days"] >= 300) & (df["days"] <= 400)].copy()

# Remove duplicate reporting periods
df = df.drop_duplicates(subset=["start", "end"])

# Sort chronologically
df = df.sort_values("end")

# Keep the columns we need
df = df[["start", "end", "val"]]

print("\nClean Walmart Revenue Data:\n")
print(df.to_string(index=False))

df["revenue_growth"] = df["val"].pct_change()

print("\nRevenue Growth:\n")
print(df[["end", "val", "revenue_growth"]].to_string(index=False))

output_path = "data/processed/walmart_revenue.csv"

df.to_csv(output_path, index=False)

print(f"\nSaved cleaned data to {output_path}")

# -----------------------------
# Accounts Receivable
# -----------------------------

ar_records = data["facts"]["us-gaap"]["AccountsReceivableNet"]["units"]["USD"]

ar_df = pd.DataFrame(ar_records)

# Keep annual 10-K filings
ar_df = ar_df[ar_df["form"] == "10-K"].copy()

# Convert date
ar_df["end"] = pd.to_datetime(ar_df["end"])

# Keep only the date and value
ar_df = ar_df[["end", "val"]]

# Remove duplicate dates
ar_df = ar_df.drop_duplicates(subset=["end"])

# Sort chronologically
ar_df = ar_df.sort_values("end")

print("\nClean Walmart Accounts Receivable Data:\n")
print(ar_df.to_string(index=False))

# Save the cleaned data
output_path = "data/processed/walmart_accounts_receivable.csv"

ar_df.to_csv(output_path, index=False)

print(f"\nSaved Accounts Receivable data to {output_path}")

# -----------------------------
# Inventory
# -----------------------------

inventory_records = data["facts"]["us-gaap"]["InventoryNet"]["units"]["USD"]

inventory_df = pd.DataFrame(inventory_records)

# Keep annual 10-K filings
inventory_df = inventory_df[inventory_df["form"] == "10-K"].copy()

# Convert date
inventory_df["end"] = pd.to_datetime(inventory_df["end"])

# Keep only the date and value
inventory_df = inventory_df[["end", "val"]]

# Remove duplicate dates
inventory_df = inventory_df.drop_duplicates(subset=["end"])

# Sort chronologically
inventory_df = inventory_df.sort_values("end")

print("\nClean Walmart Inventory Data:\n")
print(inventory_df.to_string(index=False))

# Save the cleaned data
output_path = "data/processed/walmart_inventory.csv"

inventory_df.to_csv(output_path, index=False)

print(f"\nSaved Inventory data to {output_path}")

# -----------------------------
# Accounts Payable
# -----------------------------

ap_records = data["facts"]["us-gaap"]["AccountsPayableCurrent"]["units"]["USD"]

ap_df = pd.DataFrame(ap_records)

# Keep annual 10-K filings
ap_df = ap_df[ap_df["form"] == "10-K"].copy()

# Convert date
ap_df["end"] = pd.to_datetime(ap_df["end"])

# Keep only the date and value
ap_df = ap_df[["end", "val"]]

# Remove duplicate dates
ap_df = ap_df.drop_duplicates(subset=["end"])

# Sort chronologically
ap_df = ap_df.sort_values("end")

print("\nClean Walmart Accounts Payable Data:\n")
print(ap_df.to_string(index=False))

# Save the cleaned data
output_path = "data/processed/walmart_accounts_payable.csv"

ap_df.to_csv(output_path, index=False)

print(f"\nSaved Accounts Payable data to {output_path}")

# -----------------------------
# Operating Income
# -----------------------------

operating_records = data["facts"]["us-gaap"]["OperatingIncomeLoss"]["units"]["USD"]

operating_df = pd.DataFrame(operating_records)

# Keep annual 10-K filings
operating_df = operating_df[operating_df["form"] == "10-K"].copy()

# Keep records with start and end dates
operating_df = operating_df[
    operating_df["start"].notna() &
    operating_df["end"].notna()
].copy()

# Convert dates
operating_df["start"] = pd.to_datetime(operating_df["start"])
operating_df["end"] = pd.to_datetime(operating_df["end"])

# Calculate length of reporting period
operating_df["days"] = (
    operating_df["end"] - operating_df["start"]
).dt.days

# Keep approximately annual periods
operating_df = operating_df[
    (operating_df["days"] >= 300) &
    (operating_df["days"] <= 400)
].copy()

# Keep only the date and value
operating_df = operating_df[["start", "end", "val"]]

# Remove duplicate reporting periods
operating_df = operating_df.drop_duplicates(
    subset=["start", "end"]
)

# Sort chronologically
operating_df = operating_df.sort_values("end")

print("\nClean Walmart Operating Income Data:\n")
print(operating_df.to_string(index=False))

# Save the cleaned data
output_path = "data/processed/walmart_operating_income.csv"

operating_df.to_csv(output_path, index=False)

print(f"\nSaved Operating Income data to {output_path}")

# ---------------------------------------------------------
# Operating Cash Flow
# ---------------------------------------------------------

ocf_records = data["facts"]["us-gaap"][
    "NetCashProvidedByUsedInOperatingActivities"
]["units"]["USD"]

ocf_df = pd.DataFrame(ocf_records)

ocf_df = ocf_df[ocf_df["form"] == "10-K"].copy()
ocf_df = ocf_df[
    ocf_df["start"].notna() & ocf_df["end"].notna()
].copy()

ocf_df["start"] = pd.to_datetime(ocf_df["start"])
ocf_df["end"] = pd.to_datetime(ocf_df["end"])

ocf_df["days"] = (
    ocf_df["end"] - ocf_df["start"]
).dt.days

# Keep records representing approximately one full fiscal year
ocf_df = ocf_df[
    (ocf_df["days"] >= 300) &
    (ocf_df["days"] <= 400)
].copy()

ocf_df = ocf_df.drop_duplicates(
    subset=["start", "end"]
)

ocf_df = ocf_df[["start", "end", "val"]]

ocf_df = ocf_df.rename(
    columns={"val": "operating_cash_flow"}
)

ocf_output = "data/processed/walmart_operating_cash_flow.csv"

ocf_df.to_csv(
    ocf_output,
    index=False
)

print("\nOperating Cash Flow:")
print(ocf_df.to_string(index=False))

print(
    f"\nSaved operating cash flow to {ocf_output}"
)


# ---------------------------------------------------------
# Capital Expenditures
# ---------------------------------------------------------

capex_records = data["facts"]["us-gaap"][
    "PaymentsToAcquirePropertyPlantAndEquipment"
]["units"]["USD"]

capex_df = pd.DataFrame(capex_records)

capex_df = capex_df[capex_df["form"] == "10-K"].copy()
capex_df = capex_df[
    capex_df["start"].notna() & capex_df["end"].notna()
].copy()

capex_df["start"] = pd.to_datetime(capex_df["start"])
capex_df["end"] = pd.to_datetime(capex_df["end"])

capex_df["days"] = (
    capex_df["end"] - capex_df["start"]
).dt.days

# Keep records representing approximately one full fiscal year
capex_df = capex_df[
    (capex_df["days"] >= 300) &
    (capex_df["days"] <= 400)
].copy()

capex_df = capex_df.drop_duplicates(
    subset=["start", "end"]
)

capex_df = capex_df[["start", "end", "val"]]

capex_df = capex_df.rename(
    columns={"val": "capital_expenditures"}
)

capex_output = "data/processed/walmart_capex.csv"

capex_df.to_csv(
    capex_output,
    index=False
)

print("\nCapital Expenditures:")
print(capex_df.to_string(index=False))

print(
    f"\nSaved capital expenditures to {capex_output}"
)