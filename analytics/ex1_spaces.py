# ex1_spaces.py
# PANDAS EXERCISE 1: Leading and Trailing Spaces
#
# The Problem:
#   A space before or after a word makes it look the same to human eyes,
#   but Python sees them as completely different values.
#   "Rejected" and " Rejected" are NOT equal.
#   This breaks grouping, counting, and filtering.
#
# How to run:
#   python ex1_spaces.py

import pandas as pd  # pandas is the main library we use to work with tables of data

# ---------------------------------------------------------------
# STEP 1: Create a small table with the problem
# ---------------------------------------------------------------

# We create a list of dictionaries. Each dictionary is one row.
# Notice the spaces in some status values below. Hard to see, but they are there.
data = [
    {"patient_name": "Priya Sharma",   "status": "Approved"},    # correct
    {"patient_name": "Sunita Patil",   "status": " Rejected"},   # space at the START
    {"patient_name": "Meena Kulkarni", "status": "Approved "},   # space at the END
    {"patient_name": "Anjali Desai",   "status": " Approved "},  # spaces on BOTH sides
    {"patient_name": "Rekha Joshi",    "status": "Rejected"},    # correct
    {"patient_name": "Kavita More",    "status": "Rejected"},    # correct
]

# pd.DataFrame() turns our list of rows into a table
df = pd.DataFrame(data)

# ---------------------------------------------------------------
# STEP 2: See what the data looks like RIGHT NOW (before fixing)
# ---------------------------------------------------------------

print("=" * 55)
print("STEP 2: Raw data - what we loaded")
print("=" * 55)
print(df)
# Output will show the table. The spaces are invisible here, which is the danger.

print()
print("STEP 2b: Count by status (BEFORE fixing)")
print("-" * 40)
# .value_counts() counts how many times each unique value appears
# Because of spaces, 'Approved', ' Rejected', 'Approved ', ' Approved '
# are all treated as DIFFERENT values
print(df["status"].value_counts())
# You will see Approved appear THREE times as separate entries - that is wrong!

# ---------------------------------------------------------------
# STEP 3: Show the problem clearly
# ---------------------------------------------------------------

print()
print("STEP 3: Prove the spaces are really there")
print("-" * 40)
# repr() shows us the exact characters including spaces
for val in df["status"]:
    print(repr(val))
# Now you can see the spaces with your own eyes

# ---------------------------------------------------------------
# STEP 4: Fix it using .str.strip()
# ---------------------------------------------------------------

print()
print("STEP 4: Fix using .str.strip()")
print("-" * 40)

# df["status"]        -> this picks the 'status' column
# .str                -> this tells pandas: treat each value as a piece of text
# .strip()            -> this removes spaces from the LEFT and RIGHT of the text
# We save the result back into the same column, replacing the old values
df["status"] = df["status"].str.strip()

print("Fixed! Here is what .str.strip() did to each value:")
for val in df["status"]:
    print(repr(val))
# Now every value is clean. No extra spaces.

# ---------------------------------------------------------------
# STEP 5: Count again after fixing
# ---------------------------------------------------------------

print()
print("STEP 5: Count by status (AFTER fixing)")
print("-" * 40)
print(df["status"].value_counts())
# Now you see: Approved = 4, Rejected = 2  (correct!)

# ---------------------------------------------------------------
# STEP 6: Filter - find all Rejected claims
# ---------------------------------------------------------------

print()
print("STEP 6: Filter - show only Rejected claims")
print("-" * 40)
# df["status"] == "Rejected"  -> this checks each row: is the status exactly "Rejected"?
# df[...]                     -> this keeps only the rows where the check is True
rejected = df[df["status"] == "Rejected"]
print(rejected)
# Before the fix, this would have returned only 2 rows and missed the one with " Rejected"
# After the fix, it correctly returns all Rejected rows

print()
print("KEY LEARNING:")
print("  Always run .str.strip() on text columns before you group or filter.")
print("  A space you cannot see will silently break your report.")