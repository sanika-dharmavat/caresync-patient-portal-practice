# generate_data.py
# CareSync Analytics Lab - Synthetic Data Generator
# Place this file in: C:\ProjectCareSync\caresync-patient-portal\analytics\
# Run this file FIRST before any other script in the lab.
#
# What this script produces:
#   claims.csv        - 5000 insurance claim records
#   discharges.csv    - 3000 patient discharge records
#
# How to run:
#   Open Command Prompt inside the analytics folder
#   python generate_data.py

import random
import csv
import os
from datetime import datetime, timedelta

random.seed(42)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------
# Helper: random date between two dates
# ---------------------------------------------------------------
def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

# ---------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------
INSURANCE_COMPANIES = [
    "StarHealth",
    "NationalInsurance",
    "BajajAllianz",
    "HDFCErgo",
    "UnitedHealthIndia",
]

REJECTION_REASONS = [
    "Pre-authorization missing",
    "Wrong diagnosis code",
    "Service not covered",
    "Duplicate claim",
    "Late submission",
    "Incomplete documents",
    "Patient details mismatch",
    "Policy lapsed",
]

DEPARTMENTS = [
    "Cardiology",
    "Orthopedics",
    "Neurology",
    "Oncology",
    "General Medicine",
    "Pediatrics",
    "Gynecology",
    "Emergency",
]

DOCTORS = [
    ("DR001", "Dr. Priya Nair",       "Cardiology"),
    ("DR002", "Dr. Suresh Patil",     "Orthopedics"),
    ("DR003", "Dr. Aarti Deshmukh",   "Neurology"),
    ("DR004", "Dr. Rajan Mehta",      "Oncology"),
    ("DR005", "Dr. Sunita Kulkarni",  "General Medicine"),
    ("DR006", "Dr. Kavya Iyer",       "Pediatrics"),
    ("DR007", "Dr. Deepak Sharma",    "Gynecology"),
    ("DR008", "Dr. Anil Joshi",       "Emergency"),
    ("DR009", "Dr. Meera Pillai",     "Cardiology"),
    ("DR010", "Dr. Rohit Verma",      "Orthopedics"),
]

DIAGNOSES = [
    "Hypertension",
    "Diabetes Type 2",
    "Knee Replacement",
    "Stroke Recovery",
    "Lung Cancer - Stage 2",
    "Chest Infection",
    "Appendicitis",
    "Fracture - Femur",
    "Anemia",
    "Dengue Fever",
    "Asthma",
    "Heart Attack",
    "Migraine",
    "Hernia Repair",
    "Cataract Surgery",
]

# ---------------------------------------------------------------
# Rejection probability per insurance company
# (some companies reject more - this creates the WOW finding)
# ---------------------------------------------------------------
REJECTION_RATE = {
    "StarHealth":         0.08,
    "NationalInsurance":  0.31,   # deliberately high
    "BajajAllianz":       0.12,
    "HDFCErgo":           0.09,
    "UnitedHealthIndia":  0.27,   # deliberately high
}

# ---------------------------------------------------------------
# Generate claims.csv
# ---------------------------------------------------------------
start_date = datetime(2024, 1, 1)
end_date   = datetime(2024, 12, 31)

claims = []
for i in range(1, 5001):
    claim_id      = f"CLM{i:05d}"
    patient_id    = f"PT{random.randint(1, 2000):05d}"
    doctor        = random.choice(DOCTORS)
    insurance     = random.choice(INSURANCE_COMPANIES)
    bill_amount   = round(random.uniform(5000, 150000), 2)
    submit_date   = random_date(start_date, end_date)

    # Decide if rejected based on company-specific rate
    is_rejected = random.random() < REJECTION_RATE[insurance]

    if is_rejected:
        status           = "Rejected"
        rejection_reason = random.choice(REJECTION_REASONS)
        paid_amount      = 0.0
        payment_date     = ""
        days_to_payment  = ""
    else:
        status           = "Approved"
        rejection_reason = ""
        paid_amount      = round(bill_amount * random.uniform(0.75, 1.0), 2)
        payment_days     = random.randint(7, 120)
        payment_date     = (submit_date + timedelta(days=payment_days)).strftime("%Y-%m-%d")
        days_to_payment  = payment_days

    # Introduce deliberate data quality issues (for Pandas cleaning exercise)
    if random.random() < 0.03:
        insurance = insurance.lower()          # inconsistent casing
    if random.random() < 0.02:
        bill_amount = ""                       # missing value
    if random.random() < 0.015:
        status = " " + status                 # leading space

    claims.append({
        "claim_id":        claim_id,
        "patient_id":      patient_id,
        "doctor_id":       doctor[0],
        "doctor_name":     doctor[1],
        "department":      doctor[2],
        "insurance_company": insurance,
        "bill_amount":     bill_amount,
        "paid_amount":     paid_amount,
        "submit_date":     submit_date.strftime("%Y-%m-%d"),
        "payment_date":    payment_date,
        "days_to_payment": days_to_payment,
        "status":          status,
        "rejection_reason": rejection_reason,
    })

claims_path = os.path.join(OUTPUT_DIR, "claims.csv")
with open(claims_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=claims[0].keys())
    writer.writeheader()
    writer.writerows(claims)

print(f"claims.csv written  -> {claims_path}  ({len(claims)} rows)")

# ---------------------------------------------------------------
# Generate discharges.csv
# ---------------------------------------------------------------

# Readmission probability per department
# (Cardiology and Emergency have high readmission - WOW finding)
READMIT_RATE = {
    "Cardiology":       0.28,   # high - deliberate
    "Orthopedics":      0.07,
    "Neurology":        0.14,
    "Oncology":         0.11,
    "General Medicine": 0.09,
    "Pediatrics":       0.06,
    "Gynecology":       0.05,
    "Emergency":        0.33,   # highest - deliberate
}

discharges = []
for i in range(1, 3001):
    discharge_id   = f"DC{i:05d}"
    patient_id     = f"PT{random.randint(1, 2000):05d}"
    doctor         = random.choice(DOCTORS)
    department     = doctor[2]
    diagnosis      = random.choice(DIAGNOSES)
    admit_date     = random_date(start_date, datetime(2024, 11, 30))
    los_days       = random.randint(1, 21)            # length of stay
    discharge_date = admit_date + timedelta(days=los_days)
    age            = random.randint(18, 85)

    is_readmitted = random.random() < READMIT_RATE[department]

    if is_readmitted:
        readmit_days = random.randint(3, 29)
        readmit_date = (discharge_date + timedelta(days=readmit_days)).strftime("%Y-%m-%d")
    else:
        readmit_days = ""
        readmit_date = ""

    # Introduce deliberate data quality issues
    if random.random() < 0.025:
        department = department.upper()               # casing issue
    if random.random() < 0.02:
        age = ""                                      # missing value
    if random.random() < 0.01:
        los_days = -1                                 # impossible value

    discharges.append({
        "discharge_id":    discharge_id,
        "patient_id":      patient_id,
        "doctor_id":       doctor[0],
        "doctor_name":     doctor[1],
        "department":      department,
        "diagnosis":       diagnosis,
        "age":             age,
        "admit_date":      admit_date.strftime("%Y-%m-%d"),
        "discharge_date":  discharge_date.strftime("%Y-%m-%d"),
        "length_of_stay":  los_days,
        "readmitted_within_30_days": "Yes" if is_readmitted else "No",
        "readmission_date": readmit_date,
        "days_to_readmission": readmit_days,
    })

discharges_path = os.path.join(OUTPUT_DIR, "discharges.csv")
with open(discharges_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=discharges[0].keys())
    writer.writeheader()
    writer.writerows(discharges)

print(f"discharges.csv written -> {discharges_path}  ({len(discharges)} rows)")
print()
print("Data generation complete. Upload both CSV files to your AWS S3 bucket.")