# ============================================================
# FILE: database.py
# ROLE: Database Engineer (DE)
# PURPOSE: All database read/write functions in one place.
# ============================================================

import mysql.connector
from dotenv import load_dotenv
import os

# Load secret values from .env file
load_dotenv()


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Opens a connection to MySQL.
    Reads DB_HOST, DB_USER, DB_PASSWORD, DB_NAME from .env file.
    """
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


# ============================================================
# PATIENT FUNCTIONS
# ============================================================

def get_patient(patient_id):
    """
    Gets one patient by their ID.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM patients WHERE id = %s",
        (patient_id,)
    )

    patient = cursor.fetchone()

    cursor.close()
    conn.close()

    return patient


def get_all_patients():
    """
    Gets all patients.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, name, age, gender
        FROM patients
        ORDER BY id
        """
    )

    patients = cursor.fetchall()

    cursor.close()
    conn.close()

    return patients


# ============================================================
# BED FUNCTIONS
# ============================================================

def find_empty_bed(ward):
    """
    Finds the first empty bed in a given ward.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT bed_id, bed_number, bed_type
        FROM beds
        WHERE ward = %s
        AND is_occupied = 0
        LIMIT 1
        """,
        (ward,)
    )

    bed = cursor.fetchone()

    cursor.close()
    conn.close()

    return bed


def get_on_duty_nurse(ward):
    """
    Finds the nurse currently on duty in a ward.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT nurse_name, shift_start, shift_end
        FROM staff_shifts
        WHERE ward = %s
        AND is_on_duty = 1
        LIMIT 1
        """,
        (ward,)
    )

    nurse = cursor.fetchone()

    cursor.close()
    conn.close()

    return nurse


def assign_bed_to_patient(patient_id, bed_id, nurse_name):
    """
    Assigns a patient to a bed.
    """

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # Step 1: Mark bed as occupied
        cursor.execute(
            """
            UPDATE beds
            SET
                is_occupied = 1,
                patient_id = %s
            WHERE bed_id = %s
            """,
            (patient_id, bed_id)
        )

        # Step 2: Save bed assignment history
        cursor.execute(
            """
            INSERT INTO bed_assignments
            (
                patient_id,
                bed_id,
                nurse_assigned,
                assigned_at,
                assigned_by
            )
            VALUES
            (%s, %s, %s, NOW(), 'ai_agent')
            """,
            (patient_id, bed_id, nurse_name)
        )

        conn.commit()

        return True

    except Exception as e:

        conn.rollback()

        print(f"Database error: {e}")

        return False

    finally:

        cursor.close()
        conn.close()


# ============================================================
# GET PATIENT BED
# ============================================================

def get_patient_bed(patient_id):
    """
    Finds the bed currently assigned to a patient.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            bed_id,
            bed_number,
            ward,
            patient_id
        FROM beds
        WHERE patient_id = %s
        LIMIT 1
        """,
        (patient_id,)
    )

    bed = cursor.fetchone()

    cursor.close()
    conn.close()

    return bed


# ============================================================
# DISCHARGE PATIENT
# ============================================================

def discharge_patient(
    patient_id,
    diagnosis="",
    treatment="",
    medicines="",
    doctor=""
):
    """
    Discharges a patient.

    1. Finds patient's assigned bed.
    2. Gets patient details.
    3. Gets admission date.
    4. Saves discharge summary.
    5. Releases the bed.
    6. Removes patient_id from the bed.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # ----------------------------------------------------
        # STEP 1: Find patient's current bed
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                bed_id,
                bed_number,
                ward
            FROM beds
            WHERE patient_id = %s
            LIMIT 1
            """,
            (patient_id,)
        )

        bed = cursor.fetchone()

        # ----------------------------------------------------
        # STEP 2: Get patient details
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM patients
            WHERE id = %s
            """,
            (patient_id,)
        )

        patient = cursor.fetchone()

        if not patient:

            conn.rollback()

            return {
                "success": False,
                "message": "Patient not found."
            }

        # ----------------------------------------------------
        # STEP 3: Get ward and bed number
        # ----------------------------------------------------

        ward = bed["ward"] if bed else None

        bed_number = (
            bed["bed_number"]
            if bed
            else None
        )

        # ----------------------------------------------------
        # STEP 4: Get admission date
        # ----------------------------------------------------

        admission_date = patient.get("admission_date")

        # If patients table does not contain admission_date,
        # use first bed assignment date.

        if not admission_date:

            cursor.execute(
                """
                SELECT MIN(assigned_at) AS admission_date
                FROM bed_assignments
                WHERE patient_id = %s
                """,
                (patient_id,)
            )

            admission_record = cursor.fetchone()

            if admission_record:

                admission_date = (
                    admission_record.get("admission_date")
                )

        # ----------------------------------------------------
        # STEP 5: Create final summary
        # ----------------------------------------------------

        final_summary = (
            f"Patient {patient.get('name', '')} "
            f"has been discharged successfully."
        )

        # ----------------------------------------------------
        # STEP 6: Save discharge summary
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO discharge_summaries
            (
                patient_id,
                admission_date,
                discharge_date,
                ward,
                bed_number,
                diagnosis,
                treatment,
                medicines,
                doctor,
                status,
                final_summary
            )
            VALUES
            (
                %s,
                %s,
                NOW(),
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                'Discharged',
                %s
            )
            """,
            (
                patient_id,
                admission_date,
                ward,
                bed_number,
                diagnosis,
                treatment,
                medicines,
                doctor,
                final_summary
            )
        )

        # ----------------------------------------------------
        # STEP 7: Release the bed
        # ----------------------------------------------------

        if bed:

            cursor.execute(
                """
                UPDATE beds
                SET
                    is_occupied = 0,
                    patient_id = NULL
                WHERE bed_id = %s
                """,
                (bed["bed_id"],)
            )

        # ----------------------------------------------------
        # STEP 8: Save everything
        # ----------------------------------------------------

        conn.commit()

        return {
            "success": True,
            "message": "Patient discharged and bed released successfully.",
            "patient_id": patient_id,
            "patient_name": patient.get("name"),
            "bed_number": bed_number,
            "ward": ward
        }

    except Exception as e:

        conn.rollback()

        print(f"Discharge database error: {e}")

        return {
            "success": False,
            "message": str(e)
        }

    finally:

        cursor.close()
        conn.close()


# ============================================================
# GET DISCHARGE SUMMARY
# ============================================================

def get_discharge_summary(patient_id):
    """
    Gets the latest discharge summary for a patient.
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                discharge_id,
                patient_id,
                admission_date,
                discharge_date,
                ward,
                bed_number,
                diagnosis,
                treatment,
                medicines,
                doctor,
                status,
                final_summary,
                created_at
            FROM discharge_summaries
            WHERE patient_id = %s
            ORDER BY discharge_id DESC
            LIMIT 1
            """,
            (patient_id,)
        )

        summary = cursor.fetchone()

        return summary

    finally:

        cursor.close()
        conn.close()