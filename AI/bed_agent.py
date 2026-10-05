# ============================================================
# FILE: bed_agent.py
# ROLE: Data Analyst (DA)
# PURPOSE: AI Agent that assigns hospital beds automatically.
#
# HOW TO RUN: python bed_agent.py
#
# WHAT IT DOES:
#   1. Asks you: which patient? which ward?
#   2. Sends request to Groq AI with available tools.
#   3. AI decides which tool to call.
#   4. Python calls the tool on FastAPI.
#   5. AI sees result, decides next tool.
#   6. Loop until AI says task is done.
# ============================================================
 
import json
import requests      # For calling FastAPI tool endpoints
from groq import Groq
from dotenv import load_dotenv
import os
 
load_dotenv()
 
# ============================================================
# STEP 1: Define the tools for Groq AI
# This is how we tell Groq AI what tools are available.
# Groq uses this list to decide which tool to call.
# ============================================================
 
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_bed",
            "description": "Check if there is an empty bed in a hospital ward.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ward": {
                        "type": "string",
                        "description": "Ward name. Options: General, Emergency, ICU, Pediatric, Maternity"
                    }
                },
                "required": ["ward"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_on_duty_nurse",
            "description": "Get the name of the nurse currently on duty in a ward.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ward": {
                        "type": "string",
                        "description": "Ward name"
                    }
                },
                "required": ["ward"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "assign_bed",
            "description": "Assign a patient to a hospital bed with a nurse.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "integer",
                        "description": "The patient ID number"
                    },
                    "bed_id": {
                        "type": "integer",
                        "description": "The bed ID number"
                    },
                    "nurse_name": {
                        "type": "string",
                        "description": "The name of the nurse who will handle this patient"
                    }
                },
                "required": ["patient_id", "bed_id", "nurse_name"]
            }
        }
    }
]
 
 
# ============================================================
# STEP 2: Function to call a tool on FastAPI
# When AI says "call check_bed", this function does it.
# ============================================================
 
FASTAPI_URL = "http://localhost:8000"   # FastAPI runs here
 
 
def call_tool(tool_name: str, tool_args: dict) -> str:
    """
    Calls one of our FastAPI MCP tool endpoints.
    Returns the result as a JSON string.
    """
    url = f"{FASTAPI_URL}/tools/{tool_name}"
 
    try:
        # POST request sends the arguments to FastAPI
        response = requests.post(url, json=tool_args)
        result = response.json()
        print(f"  [TOOL CALLED] {tool_name}({tool_args})")
        print(f"  [TOOL RESULT] {result}")
        return json.dumps(result)   # Convert dict to string for AI
 
    except Exception as e:
        error_msg = f"Tool call failed: {str(e)}"
        print(f"  [TOOL ERROR] {error_msg}")
        return json.dumps({"error": error_msg})
 
 
# ============================================================
# STEP 3: The Agent Loop
# This is the main logic. It loops until the AI is done.
# ============================================================
 
def run_agent(patient_id: int, ward: str):
    """
    Main agent function.
    Gives Groq AI a task and lets it use tools to complete it.
 
    patient_id: The patient we want to assign
    ward: Which ward they need (General, ICU, etc.)
    """
 
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
 
    # This is the initial task we give the AI
    task_message = f"""
You are a hospital bed assignment agent. Your job:
1. Check if there is an empty bed in the {ward} ward.
2. Find which nurse is on duty in that ward.
3. Assign patient {patient_id} to the empty bed with that nurse.
4. Report what you did.
 
Use the tools available to you. Do not guess. Use real data.
"""
 
    # Start conversation with AI
    messages = [
        {"role": "user", "content": task_message}
    ]
 
    print(f"\n=== AI Agent Starting ===")
    print(f"Task: Assign patient {patient_id} to {ward} ward")
    print(f"=========================\n")
 
    # Agent loop: keep going until AI says it is done
    while True:
        # Send current messages + tools to Groq AI
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            tools=TOOLS,              # Tell AI what tools are available
            tool_choice="auto",       # AI decides when to use a tool
            max_tokens=1000,
        )
 
        ai_message = response.choices[0].message
 
        # Add AI response to conversation history
        messages.append({
            "role": "assistant",
            "content": ai_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                }
                for tc in (ai_message.tool_calls or [])
            ] or None
        })
 
        # Check if AI wants to call a tool
        if ai_message.tool_calls:
            # AI wants to call one or more tools
            for tool_call in ai_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
 
                # Call the actual tool on FastAPI
                tool_result = call_tool(tool_name, tool_args)
 
                # Add tool result to conversation so AI can see it
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })
 
        else:
            # AI did not call any tool. It is done.
            # Print the final message from AI.
            final_answer = ai_message.content
            print(f"\n=== AI Agent Done ===")
            print(f"Result: {final_answer}")
            print(f"=====================\n")
            return final_answer
 
 
# ============================================================
# STEP 4: Run the agent from command line
# ============================================================
 
if __name__ == "__main__":
    print("\n--- Hospital Bed Availability Agent ---")
    print("Make sure FastAPI is running first: uvicorn main:app --reload")
    print("")
 
    # Ask user for input
    patient_id = int(input("Enter patient ID: "))
    ward = input("Enter ward (General / Emergency / ICU / Pediatric / Maternity): ").strip()
 
    # Run the agent
    result = run_agent(patient_id, ward)
 
    print("\nAgent finished. Check MySQL to see the bed_assignments table.")

