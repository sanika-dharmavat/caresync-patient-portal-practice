# analyze.py
# CareSync Analytics Lab - Day 10: Working with Data using Pandas
# Place this file in: C:\ProjectCareSync\caresync-patient-portal\analytics\
#
# Run AFTER generate_data.py has been run and claims.csv / discharges.csv exist.
#
# How to run:
#   Open Command Prompt inside the analytics folder
#   python analyze.py
#
# What this script does (step by step):
#   Step 1  - Load the raw data
#   Step 2  - Inspect: understand what we have
#   Step 3  - Clean claims data
#   Step 4  - Clean discharges data
#   Step 5  - Analyze: rejection rates by insurance company
#   Step 6  - Analyze: top rejection reasons
#   Step 7  - Analyze: payment speed (days to payment)
#   Step 8  - Analyze: readmission rates by department
#   Step 9  - Analyze: readmission rates by doctor
#   Step 10 - Save cleaned and summarized files for AWS upload

import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_path(filename):
    return os.path.join(SCRIPT_DIR, filename)

print("=" * 60)
print("CareSync Analytics Lab - Pandas Analysis")
print("=" * 60)

# ---------------------------------------------------------------
# STEP 1: Load raw data
# ---------------------------------------------------------------
print("\nSTEP 1: Loading raw data files")

claims_raw     = pd.read_csv(load_path("claims.csv"))
discharges_raw = pd.read_csv(load_path("discharges.csv"))

print(f"  claims.csv     loaded: {len(claims_raw)} rows, {len(claims_raw.columns)} columns")
print(f"  discharges.csv loaded: {len(discharges_raw)} rows, {len(discharges_raw.columns)} columns")

# ---------------------------------------------------------------
# STEP 2: Inspect - understand what we have
# ---------------------------------------------------------------
print("\nSTEP 2: Inspecting the data")

print("\n  --- claims.csv: first 3 rows ---")
print(claims_raw.head(3).to_string(index=False))

print("\n  --- claims.csv: column types and missing values ---")
inspect_claims = pd.DataFrame({
    "column":   claims_raw.columns,
    "dtype":    claims_raw.dtypes.values,
    "missing":  claims_raw.isnull().sum().values,
})
print(inspect_claims.to_string(index=False))

print("\n  --- discharges.csv: first 3 rows ---")
print(discharges_raw.head(3).to_string(index=False))

print("\n  --- discharges.csv: column types and missing values ---")
inspect_dis = pd.DataFrame({
    "column":   discharges_raw.columns,
    "dtype":    discharges_raw.dtypes.values,
    "missing":  discharges_raw.isnull().sum().values,
})
print(inspect_dis.to_string(index=False))

# ---------------------------------------------------------------
# STEP 3: Clean claims data
# ---------------------------------------------------------------
print("\nSTEP 3: Cleaning claims data")

claims = claims_raw.copy()

# 3a. Fix leading/trailing spaces in text columns
text_cols_claims = ["claim_id", "patient_id", "insurance_company", "status", "rejection_reason"]
for col in text_cols_claims:
    claims[col] = claims[col].astype(str).str.strip()

# 3b. Standardize insurance company names to title case
before_unique = claims["insurance_company"].nunique()
claims["insurance_company"] = claims["insurance_company"].str.title()
after_unique  = claims["insurance_company"].nunique()
print(f"  insurance_company: unique values before={before_unique}, after={after_unique}")

# 3c. Convert bill_amount to numeric. Rows where it cannot convert become NaN.
claims["bill_amount"] = pd.to_numeric(claims["bill_amount"], errors="coerce")
missing_bill = claims["bill_amount"].isnull().sum()
print(f"  bill_amount: {missing_bill} rows have missing/invalid amounts (flagged, not deleted)")

# 3d. Flag bad rows instead of deleting them
claims["data_quality_flag"] = "OK"
claims.loc[claims["bill_amount"].isnull(), "data_quality_flag"] = "Missing bill_amount"

# 3e. Convert date columns to proper datetime type
claims["submit_date"]  = pd.to_datetime(claims["submit_date"],  errors="coerce")
claims["payment_date"] = pd.to_datetime(claims["payment_date"], errors="coerce")

# 3f. Convert days_to_payment to numeric
claims["days_to_payment"] = pd.to_numeric(claims["days_to_payment"], errors="coerce")

# 3g. Add month column for trend analysis
claims["submit_month"] = claims["submit_date"].dt.to_period("M").astype(str)

print(f"  Cleaning complete. {claims['data_quality_flag'].value_counts().to_dict()}")

# ---------------------------------------------------------------
# STEP 4: Clean discharges data
# ---------------------------------------------------------------
print("\nSTEP 4: Cleaning discharges data")

discharges = discharges_raw.copy()

# 4a. Strip spaces and standardize department casing
discharges["department"] = discharges["department"].astype(str).str.strip().str.title()
discharges["doctor_name"] = discharges["doctor_name"].astype(str).str.strip()

# 4b. Convert age to numeric
discharges["age"] = pd.to_numeric(discharges["age"], errors="coerce")
missing_age = discharges["age"].isnull().sum()
print(f"  age: {missing_age} rows have missing age (flagged)")

# 4c. Fix impossible length_of_stay values (negative numbers are not real)
bad_los = (discharges["length_of_stay"] < 0).sum()
discharges["length_of_stay"] = discharges["length_of_stay"].where(
    discharges["length_of_stay"] >= 0, other=None
)
print(f"  length_of_stay: {bad_los} impossible values (negative) replaced with blank")

# 4d. Flag bad rows
discharges["data_quality_flag"] = "OK"
discharges.loc[discharges["age"].isnull(), "data_quality_flag"] = "Missing age"
discharges.loc[discharges["length_of_stay"].isnull(), "data_quality_flag"] = "Invalid length_of_stay"

# 4e. Convert dates
discharges["admit_date"]     = pd.to_datetime(discharges["admit_date"],     errors="coerce")
discharges["discharge_date"] = pd.to_datetime(discharges["discharge_date"], errors="coerce")

print(f"  Cleaning complete. {discharges['data_quality_flag'].value_counts().to_dict()}")

# ---------------------------------------------------------------
# STEP 5: Analyze - rejection rates by insurance company
# ---------------------------------------------------------------
print("\nSTEP 5: Rejection rates by insurance company")

# Work only with rows that have a valid bill amount
claims_valid = claims[claims["data_quality_flag"] == "OK"].copy()

rejection_summary = (
    claims_valid
    .groupby("insurance_company")
    .agg(
        total_claims    = ("claim_id",    "count"),
        rejected_claims = ("status",      lambda x: (x == "Rejected").sum()),
        total_billed    = ("bill_amount", "sum"),
        avg_bill        = ("bill_amount", "mean"),
    )
    .reset_index()
)

rejection_summary["rejection_rate_pct"] = (
    rejection_summary["rejected_claims"] / rejection_summary["total_claims"] * 100
).round(1)

rejection_summary["total_billed"]   = rejection_summary["total_billed"].round(0).astype(int)
rejection_summary["avg_bill"]       = rejection_summary["avg_bill"].round(0).astype(int)
rejection_summary = rejection_summary.sort_values("rejection_rate_pct", ascending=False)

print(rejection_summary.to_string(index=False))

# ---------------------------------------------------------------
# STEP 6: Top rejection reasons
# ---------------------------------------------------------------
print("\nSTEP 6: Top rejection reasons")

rejected_claims = claims_valid[claims_valid["status"] == "Rejected"]
reason_counts   = (
    rejected_claims["rejection_reason"]
    .value_counts()
    .reset_index()
)
reason_counts.columns = ["rejection_reason", "count"]
reason_counts["pct_of_all_rejections"] = (
    reason_counts["count"] / len(rejected_claims) * 100
).round(1)

print(reason_counts.to_string(index=False))

# ---------------------------------------------------------------
# STEP 7: Payment speed analysis
# ---------------------------------------------------------------
print("\nSTEP 7: How fast do insurance companies pay?")

approved_claims = claims_valid[claims_valid["status"] == "Approved"].copy()

payment_speed = (
    approved_claims
    .groupby("insurance_company")
    .agg(
        avg_days_to_payment = ("days_to_payment", "mean"),
        median_days         = ("days_to_payment", "median"),
        pct_paid_within_30  = ("days_to_payment", lambda x: (x <= 30).mean() * 100),
    )
    .reset_index()
)
payment_speed["avg_days_to_payment"] = payment_speed["avg_days_to_payment"].round(1)
payment_speed["median_days"]         = payment_speed["median_days"].round(1)
payment_speed["pct_paid_within_30"]  = payment_speed["pct_paid_within_30"].round(1)
payment_speed = payment_speed.sort_values("avg_days_to_payment")

print(payment_speed.to_string(index=False))

# ---------------------------------------------------------------
# STEP 8: Readmission rates by department
# ---------------------------------------------------------------
print("\nSTEP 8: Readmission rates by department (within 30 days)")

dis_valid = discharges[discharges["data_quality_flag"] == "OK"].copy()

readmit_dept = (
    dis_valid
    .groupby("department")
    .agg(
        total_discharges    = ("discharge_id", "count"),
        readmissions        = ("readmitted_within_30_days", lambda x: (x == "Yes").sum()),
        avg_length_of_stay  = ("length_of_stay", "mean"),
    )
    .reset_index()
)

readmit_dept["readmission_rate_pct"] = (
    readmit_dept["readmissions"] / readmit_dept["total_discharges"] * 100
).round(1)

readmit_dept["avg_length_of_stay"] = readmit_dept["avg_length_of_stay"].round(1)
readmit_dept = readmit_dept.sort_values("readmission_rate_pct", ascending=False)

print(readmit_dept.to_string(index=False))

# ---------------------------------------------------------------
# STEP 9: Readmission rates by doctor
# ---------------------------------------------------------------
print("\nSTEP 9: Readmission rates by doctor")

readmit_doctor = (
    dis_valid
    .groupby(["doctor_id", "doctor_name", "department"])
    .agg(
        total_patients  = ("discharge_id", "count"),
        readmissions    = ("readmitted_within_30_days", lambda x: (x == "Yes").sum()),
    )
    .reset_index()
)

readmit_doctor["readmission_rate_pct"] = (
    readmit_doctor["readmissions"] / readmit_doctor["total_patients"] * 100
).round(1)

readmit_doctor = readmit_doctor.sort_values("readmission_rate_pct", ascending=False)
print(readmit_doctor.to_string(index=False))

# ---------------------------------------------------------------
# STEP 10: Save cleaned and summarized files
# ---------------------------------------------------------------
print("\nSTEP 10: Saving output files")

# Cleaned datasets (for AWS S3 upload)
claims_clean_path = load_path("claims_cleaned.csv")
dis_clean_path    = load_path("discharges_cleaned.csv")
claims_valid.to_csv(claims_clean_path, index=False)
dis_valid.to_csv(dis_clean_path, index=False)
print(f"  claims_cleaned.csv    saved ({len(claims_valid)} rows)")
print(f"  discharges_cleaned.csv saved ({len(dis_valid)} rows)")

# Summary files (for reference)
rej_path = load_path("summary_rejection_by_insurer.csv")
rea_path = load_path("summary_readmission_by_dept.csv")
rejection_summary.to_csv(rej_path, index=False)
readmit_dept.to_csv(rea_path, index=False)
print(f"  summary_rejection_by_insurer.csv saved")
print(f"  summary_readmission_by_dept.csv  saved")

print()
print("=" * 60)
print("ANALYSIS COMPLETE")
print()
print("KEY FINDINGS:")
top_rejecter = rejection_summary.iloc[0]
top_dept     = readmit_dept.iloc[0]
print(f"  Highest rejection rate: {top_rejecter['insurance_company']} "
      f"at {top_rejecter['rejection_rate_pct']}%")
print(f"  Highest readmission dept: {top_dept['department']} "
      f"at {top_dept['readmission_rate_pct']}%")
print()
print("Next step: Upload claims_cleaned.csv and discharges_cleaned.csv to AWS S3")
print("=" * 60)
