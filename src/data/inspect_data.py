import json
import pandas as pd

file_path = "data/raw/walmart_companyfacts.json"

with open(file_path, "r") as file:
    data = json.load(file)

ap = data["facts"]["us-gaap"]["AccountsPayableCurrent"]

print("\nAccounts Payable label:")
print(ap["label"])

print("\nAccounts Payable description:")
print(ap["description"])

print("\nAvailable units:")
print(ap["units"].keys())

records = ap["units"]["USD"]

df = pd.DataFrame(records)

print("\nFirst 20 Accounts Payable records:")
print(df.head(20).to_string(index=False))

# Search for operating income tags

tags = data["facts"]["us-gaap"].keys()

operating_tags = [
    tag for tag in tags
    if "OperatingIncome" in tag
]

print("\nOperating Income Tags:\n")
print(operating_tags)

# Inspect Operating Income

operating_records = data["facts"]["us-gaap"]["OperatingIncomeLoss"]["units"]["USD"]

operating_df = pd.DataFrame(operating_records)

print("\nOperating Income label:")
print(
    data["facts"]["us-gaap"]["OperatingIncomeLoss"]["label"]
)

print("\nOperating Income description:")
print(
    data["facts"]["us-gaap"]["OperatingIncomeLoss"]["description"]
)

print("\nAvailable units:")
print(
    data["facts"]["us-gaap"]["OperatingIncomeLoss"]["units"].keys()
)

print("\nFirst 20 Operating Income records:")
print(operating_df.head(20).to_string(index=False))

# Search for Operating Cash Flow tags

tags = data["facts"]["us-gaap"].keys()

cash_flow_tags = [
    tag for tag in tags
    if "OperatingCashFlow" in tag
    or "NetCashProvidedByUsedInOperatingActivities" in tag
]

print("\nOperating Cash Flow Tags:\n")
print(cash_flow_tags)


# Search for Capital Expenditure tags

capex_tags = [
    tag for tag in tags
    if "PaymentsToAcquirePropertyPlantAndEquipment" in tag
    or "CapitalExpenditures" in tag
]

print("\nCapital Expenditure Tags:\n")
print(capex_tags)

# Inspect Operating Cash Flow

ocf_records = data["facts"]["us-gaap"][
    "NetCashProvidedByUsedInOperatingActivities"
]["units"]["USD"]

ocf_df = pd.DataFrame(ocf_records)

print("\nOperating Cash Flow label:")
print(
    data["facts"]["us-gaap"][
        "NetCashProvidedByUsedInOperatingActivities"
    ]["label"]
)

print("\nOperating Cash Flow description:")
print(
    data["facts"]["us-gaap"][
        "NetCashProvidedByUsedInOperatingActivities"
    ]["description"]
)

print("\nAvailable units:")
print(
    data["facts"]["us-gaap"][
        "NetCashProvidedByUsedInOperatingActivities"
    ]["units"].keys()
)

print("\nFirst 20 Operating Cash Flow records:")
print(ocf_df.head(20).to_string(index=False))


# Inspect Capital Expenditures

capex_records = data["facts"]["us-gaap"][
    "PaymentsToAcquirePropertyPlantAndEquipment"
]["units"]["USD"]

capex_df = pd.DataFrame(capex_records)

print("\nCapital Expenditures label:")
print(
    data["facts"]["us-gaap"][
        "PaymentsToAcquirePropertyPlantAndEquipment"
    ]["label"]
)

print("\nCapital Expenditures description:")
print(
    data["facts"]["us-gaap"][
        "PaymentsToAcquirePropertyPlantAndEquipment"
    ]["description"]
)

print("\nAvailable units:")
print(
    data["facts"]["us-gaap"][
        "PaymentsToAcquirePropertyPlantAndEquipment"
    ]["units"].keys()
)

print("\nFirst 20 Capital Expenditure records:")
print(capex_df.head(20).to_string(index=False))