# ============================================================
# FILE: mcp_tools.py
# ROLE: Data Analyst (DA)
# PURPOSE: Functions that work as MCP tools.
#          FastAPI will expose these as HTTP endpoints.
#          The AI agent calls these to do real database actions.
# ============================================================
 
from database import find_empty_bed, get_on_duty_nurse, assign_bed_to_patient
 
 
def tool_check_bed(ward: str) -> dict:
    """
    MCP Tool 1: Check if an empty bed exists in a ward.
 
    Input: ward name (example: "General")
    Output: dict with bed info, or message if no bed found.
 
    The AI agent calls this to find an empty bed.
    """
    bed = find_empty_bed(ward)
 
    if bed is None:
        # No empty bed in this ward
        return {
            "status": "no_bed",
            "message": f"No empty beds available in {ward} ward right now."
        }
 
    # Found a bed! Return its details.
    return {
        "status": "found",
        "bed_id": bed["bed_id"],
        "bed_number": bed["bed_number"],
        "bed_type": bed["bed_type"],
        "ward": ward
    }
 
 
def tool_get_on_duty_nurse(ward: str) -> dict:
    """
    MCP Tool 2: Get the nurse currently on duty in a ward.
 
    Input: ward name
    Output: dict with nurse name and shift times, or message if none.
 
    The AI agent calls this to know who will receive the patient.
    """
    nurse = get_on_duty_nurse(ward)
 
    if nurse is None:
        return {
            "status": "no_nurse",
            "message": f"No nurse currently on duty in {ward} ward."
        }
 
    return {
        "status": "found",
        "nurse_name": nurse["nurse_name"],
        "shift_start": str(nurse["shift_start"]),
        "shift_end": str(nurse["shift_end"]),
        "ward": ward
    }
 
 
def tool_assign_bed(patient_id: int, bed_id: int, nurse_name: str) -> dict:
    """
    MCP Tool 3: Assign a patient to a bed.
 
    Input: patient_id, bed_id, nurse_name
    Output: success or failure message.
 
    This writes to the database:
    - Marks the bed as occupied.
    - Records the assignment in bed_assignments table.
    - Sets assigned_by = "ai_agent" so we know AI did this.
    """
    success = assign_bed_to_patient(patient_id, bed_id, nurse_name)
 
    if success:
        return {
            "status": "assigned",
            "message": f"Patient {patient_id} assigned to bed {bed_id}.",
            "nurse_assigned": nurse_name,
            "assigned_by": "ai_agent"
        }
    else:
        return {
            "status": "error",
            "message": "Database error. Could not assign bed."
        }

