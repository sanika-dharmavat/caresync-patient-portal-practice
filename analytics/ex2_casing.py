# ex2_casing.py
# PANDAS EXERCISE 2: Inconsistent Casing
#
# The Problem:
#   The same insurance company name is stored in different ways:
#   "NationalInsurance", "nationalinsurance", "NATIONALINSURANCE"
#   Python treats all three as different values.
#   When you group by insurance company, you get 3 separate groups
#   instead of 1. Your totals are wrong.
#
# How to run:
#   python ex2_casing.py

import pandas as pd

# ---------------------------------------------------------------
# STEP 1: Create a small table with the problem
# ---------------------------------------------------------------

data = [
    {"claim_id": "C001", "insurance_company": "NationalInsurance",   "amount": 15000},
    {"claim_id": "C002", "insurance_company": "unitedhealth",         "amount": 22000},
    {"claim_id": "C003", "insurance_company": "NATIONALINSURANCE",   "amount": 18000},
    {"claim_id": "C004", "insurance_company": "UnitedHealth",         "amount": 9000},
    {"claim_id": "C005", "insurance_company": "nationalinsurance",   "amount": 12000},
    {"claim_id": "C006", "insurance_company": "UNITEDHEALTH",         "amount": 31000},
    {"claim_id": "C007", "insurance_company": "NationalInsurance",   "amount": 8000},
]

df = pd.DataFrame(data)

# ---------------------------------------------------------------
# STEP 2: See the problem
# ---------------------------------------------------------------

print("=" * 55)
print("STEP 2: Total amount by insurance company (BEFORE fixing)")
print("=" * 55)

# .groupby() groups all rows that have the same value in a column
# ["amount"]  -> we want to look at the amount column inside each group
# .sum()      -> add up all the amounts in each group
print(df.groupby("insurance_company")["amount"].sum())

# You will see 6 separate groups instead of 2.
# NationalInsurance total is split across 3 rows.
# This is completely wrong for a business report.

# ---------------------------------------------------------------
# STEP 3: Fix using .str.title()
# ---------------------------------------------------------------

print()
print("STEP 3: Fix using .str.title()")
print("-" * 40)

# df["insurance_company"]   -> pick the insurance_company column
# .str                      -> treat each value as text
# .title()                  -> capitalise the First Letter Of Every Word,
#                              make everything else lowercase
#                              "nationalinsurance" -> "Nationalinsurance"
#                              "NATIONALINSURANCE" -> "Nationalinsurance"
#                              "NationalInsurance" -> "Nationalinsurance"
# All three become the same. Problem solved.
df["insurance_company"] = df["insurance_company"].str.title()

print("Values after .str.title():")
print(df["insurance_company"].tolist())

# ---------------------------------------------------------------
# STEP 4: Count again after fixing
# ---------------------------------------------------------------

print()
print("STEP 4: Total amount by insurance company (AFTER fixing)")
print("-" * 40)
print(df.groupby("insurance_company")["amount"].sum())
# Now you see exactly 2 groups with correct totals

# ---------------------------------------------------------------
# STEP 5: Also show the count of claims per company
# ---------------------------------------------------------------

print()
print("STEP 5: Number of claims per company (AFTER fixing)")
print("-" * 40)
# .size() counts how many rows are in each group
print(df.groupby("insurance_company").size().rename("claim_count"))

print()
print("KEY LEARNING:")
print("  Always run .str.title() on name columns before grouping.")
print("  One company stored in 3 different ways = 3 wrong totals.")
print("  .str.title() makes them all the same so grouping works correctly.")