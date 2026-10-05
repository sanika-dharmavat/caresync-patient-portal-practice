# ex4_dates.py
# PANDAS EXERCISE 4: Date Columns Stored as Text
#
# The Problem:
#   Dates that are stored as plain text look fine on screen.
#   But Python does not know they are dates. It just sees words.
#   You cannot sort them correctly, subtract them, or group by month.
#
#   Example of what goes wrong with text dates:
#     Sorting "2024-11-05", "2024-09-20", "2024-10-01" as text
#     gives: "2024-09-20", "2024-10-01", "2024-11-05"  <- looks right
#     But sorting "05-Nov-2024", "20-Sep-2024", "01-Oct-2024" as text
#     gives a wrong result because Python compares letters, not dates.
#
#   Once you convert to a proper date type, you can:
#     - Sort correctly
#     - Calculate how many days between two dates
#     - Group by month or year
#
# How to run:
#   python ex4_dates.py

import pandas as pd

# ---------------------------------------------------------------
# STEP 1: Create a table with dates stored as plain text
# ---------------------------------------------------------------

data = [
    {"claim_id": "C001", "patient_name": "Priya Sharma",   "admission_date": "2024-11-05", "discharge_date": "2024-11-09"},
    {"claim_id": "C002", "patient_name": "Sunita Patil",   "admission_date": "2024-09-20", "discharge_date": "2024-09-25"},
    {"claim_id": "C003", "patient_name": "Meena Kulkarni", "admission_date": "2024-10-01", "discharge_date": "2024-10-04"},
    {"claim_id": "C004", "patient_name": "Anjali Desai",   "admission_date": "2024-12-15", "discharge_date": "2024-12-18"},
    {"claim_id": "C005", "patient_name": "Rekha Joshi",    "admission_date": "2024-08-30", "discharge_date": "2024-09-03"},
    {"claim_id": "C006", "patient_name": "Kavita More",    "admission_date": "2024-11-22", "discharge_date": "2024-11-28"},
]

df = pd.DataFrame(data)

# ---------------------------------------------------------------
# STEP 2: Check what type the columns are right now
# ---------------------------------------------------------------

print("=" * 60)
print("STEP 2: Data types of each column (BEFORE converting)")
print("=" * 60)
# .dtypes shows the data type of every column
# object means "plain text" in pandas
print(df.dtypes)
# You will see: admission_date    object
#               discharge_date    object
# 'object' means Python is treating these dates as plain text, not as dates.

# ---------------------------------------------------------------
# STEP 3: Show what goes wrong with text dates
# ---------------------------------------------------------------

print()
print("STEP 3: What goes wrong when dates are text?")
print("-" * 50)

# Sorting works here because our format is YYYY-MM-DD (year first)
# But try calculating days between dates - that will fail
print("Trying to subtract dates stored as text:")
try:
    # This tries to calculate discharge_date minus admission_date
    # It will fail because you cannot subtract two pieces of text
    df["stay_days"] = df["discharge_date"] - df["admission_date"]
except TypeError as e:
    print(f"  ERROR: {e}")
    print("  Python cannot subtract text. You need real date objects.")

# ---------------------------------------------------------------
# STEP 4: Convert text to proper date using pd.to_datetime()
# ---------------------------------------------------------------

print()
print("STEP 4: Convert text to date using pd.to_datetime()")
print("-" * 50)

# pd.to_datetime()   -> converts text to a proper date type called datetime64
# format="%Y-%m-%d"  -> tells pandas what the text looks like
#                       %Y = 4-digit year, %m = 2-digit month, %d = 2-digit day
#                       So "2024-11-05" means year 2024, month 11, day 05

df["admission_date"] = pd.to_datetime(df["admission_date"], format="%Y-%m-%d")
df["discharge_date"] = pd.to_datetime(df["discharge_date"], format="%Y-%m-%d")

print("Data types AFTER conversion:")
print(df.dtypes)
# Now you will see: admission_date    datetime64[ns]
#                   discharge_date    datetime64[ns]
# datetime64 means pandas knows these are real dates now.

# ---------------------------------------------------------------
# STEP 5: Now calculate days in hospital - this works!
# ---------------------------------------------------------------

print()
print("STEP 5: Calculate length of stay in days")
print("-" * 50)

# Now subtraction works because both columns are real dates
# The result is a "timedelta" (a difference between two times)
# .dt.days converts that timedelta to a simple number
df["length_of_stay"] = (df["discharge_date"] - df["admission_date"]).dt.days

print(df[["claim_id", "patient_name", "admission_date", "discharge_date", "length_of_stay"]])

# ---------------------------------------------------------------
# STEP 6: Group by month
# ---------------------------------------------------------------

print()
print("STEP 6: Count admissions by month")
print("-" * 50)

# .dt.month_name()  -> extracts the month name from a date column
#                      "2024-11-05" becomes "November"
df["admission_month"] = df["admission_date"].dt.month_name()

# Now we can group by month and count
monthly = df.groupby("admission_month").size().rename("admissions")
print(monthly)
# This tells us how many patients were admitted in each month

# ---------------------------------------------------------------
# STEP 7: Sort by date correctly
# ---------------------------------------------------------------

print()
print("STEP 7: Sort by admission date (earliest first)")
print("-" * 50)
# .sort_values() sorts the table by a column
# ascending=True means smallest (earliest) first
df_sorted = df.sort_values("admission_date", ascending=True)
print(df_sorted[["claim_id", "patient_name", "admission_date", "length_of_stay"]])

print()
print("KEY LEARNING:")
print("  Date columns stored as text look fine but break calculations.")
print("  Always convert date columns using pd.to_datetime().")
print("  Once converted, you can subtract, sort, and group by month correctly.")