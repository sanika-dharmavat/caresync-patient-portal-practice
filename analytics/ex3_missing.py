# ex3_missing.py
# PANDAS EXERCISE 3: Missing Values
#
# The Problem:
#   Some rows have no bill amount. The cell is empty (None or NaN).
#   NaN stands for "Not a Number". Pandas uses NaN to represent missing data.
#
#   Wrong approach: DELETE the row.
#     If you delete rows with missing amounts, your COUNT of total claims
#     goes down. Your rejection rate calculation becomes wrong.
#     You are hiding a data quality problem instead of reporting it.
#
#   Correct approach: FLAG the row.
#     Keep the row. Add a new column that says "this row has a problem".
#     Now your count stays correct AND you can investigate the missing values later.
#
# How to run:
#   python ex3_missing.py

import pandas as pd  # for working with tables
import numpy as np   # numpy gives us np.nan which means "missing value"

# ---------------------------------------------------------------
# STEP 1: Create a small table with missing values
# ---------------------------------------------------------------

# None means "nothing here" - pandas will convert it to NaN automatically
data = [
    {"claim_id": "C001", "patient_name": "Priya Sharma",   "bill_amount": 15000},
    {"claim_id": "C002", "patient_name": "Sunita Patil",   "bill_amount": None},    # MISSING
    {"claim_id": "C003", "patient_name": "Meena Kulkarni", "bill_amount": 22000},
    {"claim_id": "C004", "patient_name": "Anjali Desai",   "bill_amount": 9500},
    {"claim_id": "C005", "patient_name": "Rekha Joshi",    "bill_amount": None},    # MISSING
    {"claim_id": "C006", "patient_name": "Kavita More",    "bill_amount": 31000},
    {"claim_id": "C007", "patient_name": "Nisha Wagh",     "bill_amount": None},    # MISSING
    {"claim_id": "C008", "patient_name": "Swati Deshpande","bill_amount": 17500},
]

df = pd.DataFrame(data)

# ---------------------------------------------------------------
# STEP 2: See the problem
# ---------------------------------------------------------------

print("=" * 55)
print("STEP 2: Raw data with missing values")
print("=" * 55)
print(df)
# NaN will appear in the bill_amount column for the 3 missing rows

print()
print("STEP 2b: How many values are missing in each column?")
print("-" * 40)
# .isnull()   -> creates a True/False table: True where value is missing
# .sum()      -> counts the Trues (True = 1, False = 0 in Python)
print(df.isnull().sum())
# You will see: bill_amount    3

# ---------------------------------------------------------------
# STEP 3: Show what happens if you try to calculate average
# ---------------------------------------------------------------

print()
print("STEP 3: What happens when you calculate average bill amount?")
print("-" * 40)
# pandas skips NaN values automatically when calculating mean
# This seems helpful but is actually hiding the problem
average = df["bill_amount"].mean()
print(f"Average bill amount = Rs {average:,.0f}")
print("(Pandas skipped the 3 missing rows automatically.)")
print("This average is calculated from only 5 out of 8 rows.")
print("Is that a correct average? No. But pandas did not warn you.")

# ---------------------------------------------------------------
# STEP 4: Wrong approach - what if we deleted the missing rows?
# ---------------------------------------------------------------

print()
print("STEP 4: WRONG approach - deleting missing rows")
print("-" * 40)
# .dropna()          -> removes any row that has at least one missing value
# subset=["bill_amount"] -> only look at the bill_amount column
df_deleted = df.dropna(subset=["bill_amount"])
print(f"Original row count : {len(df)}")
print(f"After deletion     : {len(df_deleted)}")
print("We lost 3 rows. Total claim count is now WRONG.")
print("The missing data problem is now hidden. Very dangerous.")

# ---------------------------------------------------------------
# STEP 5: Correct approach - flag the missing rows
# ---------------------------------------------------------------

print()
print("STEP 5: CORRECT approach - flag missing rows, keep all rows")
print("-" * 40)

# We add a new column called data_quality_flag
# Start by filling it with an empty string for all rows
df["data_quality_flag"] = ""

# df["bill_amount"].isnull()
#   -> this gives True for each row where bill_amount is missing
#
# df.loc[..., "data_quality_flag"] = "Missing bill_amount"
#   -> for the rows where the above is True, set the flag column to this text
#   -> .loc is how pandas selects specific rows and columns to update
df.loc[df["bill_amount"].isnull(), "data_quality_flag"] = "Missing bill_amount"

print(df)
# Now you can see:
#   - All 8 rows are still there (count is correct)
#   - The 3 problem rows have a flag in the data_quality_flag column
#   - The 5 good rows have an empty flag

# ---------------------------------------------------------------
# STEP 6: Use the flag to investigate
# ---------------------------------------------------------------

print()
print("STEP 6: Show only the flagged rows for investigation")
print("-" * 40)
# df["data_quality_flag"] != ""  -> True for rows that have any flag text
flagged = df[df["data_quality_flag"] != ""]
print(f"Total claims     : {len(df)}")
print(f"Flagged claims   : {len(flagged)}")
print(f"Data quality rate: {len(flagged)/len(df)*100:.1f}% of claims have issues")
print()
print("Flagged rows:")
print(flagged[["claim_id", "patient_name", "data_quality_flag"]])

print()
print("KEY LEARNING:")
print("  Never delete rows with missing data. Use a flag column instead.")
print("  Deleting hides the problem. Flagging lets you track and fix it.")
print("  Real data always has missing values. A good analyst expects this.")