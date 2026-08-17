import json
import sys
from pathlib import Path

# ---------------------------------------------------------
# Project path
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))


# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from app.utils.config import load_env
from app.models.patient import PatientCase, Vitals
from app.services.gemini_client import GeminiChatModel
from app.prompts.cardiology_prompt import (
    build_cardiology_system_prompt,
)
from app.tools.agent_tools import get_agent_tools
from app.services.safety_service import apply_safety_layer


# ---------------------------------------------------------
# Case selection
# ---------------------------------------------------------

if len(sys.argv) < 2:
    print(
        "Usage: python evaluation/scripts/evaluate_gemini.py case_001"
    )
    sys.exit(1)

CASE_ID = sys.argv[1]


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

CASE_PATH = (
    BASE_DIR
    / "evaluation"
    / "cases"
    / f"{CASE_ID}.json"
)

FLANT5_OUTPUT_PATH = (
    BASE_DIR
    / "evaluation"
    / "results"
    / f"{CASE_ID}_flant5_output.txt"
)

RAG_OUTPUT_PATH = (
    BASE_DIR
    / "evaluation"
    / "results"
    / f"{CASE_ID}_rag_evaluation.txt"
)

DEEPSEEK_OUTPUT_PATH = (
    BASE_DIR
    / "evaluation"
    / "results"
    / f"{CASE_ID}_deepseek_output.txt"
)

OUTPUT_PATH = (
    BASE_DIR
    / "evaluation"
    / "results"
    / f"{CASE_ID}_gemini_output.txt"
)


# ---------------------------------------------------------
# Validate required files
# ---------------------------------------------------------

required_files = [
    CASE_PATH,
    FLANT5_OUTPUT_PATH,
    RAG_OUTPUT_PATH,
    DEEPSEEK_OUTPUT_PATH,
]

for file_path in required_files:
    if not file_path.exists():
        raise FileNotFoundError(
            f"Required evaluation file not found: {file_path}"
        )


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_env()


# ---------------------------------------------------------
# Load patient case
# ---------------------------------------------------------

with CASE_PATH.open("r", encoding="utf-8") as file:
    case_data = json.load(file)

patient_information = case_data["patient_information"]


# ---------------------------------------------------------
# Build PatientCase
# ---------------------------------------------------------

vitals_data = patient_information.get(
    "vital_signs",
    patient_information.get("vitals", {}),
)

patient_case = PatientCase(
    symptoms=patient_information.get(
        "symptoms",
        [],
    ),
    patient_state=patient_information.get(
        "patient_state",
        "",
    ),
    medical_history=patient_information.get(
        "medical_history",
        [],
    ),
    clinician_question=patient_information.get(
        "clinician_question",
        "Provide a brief cardiology-focused assessment.",
    ),
    vitals=Vitals(
        heart_rate=vitals_data.get(
            "heart_rate"
        ),
        systolic_bp=vitals_data.get(
            "systolic_bp"
        ),
        diastolic_bp=vitals_data.get(
            "diastolic_bp"
        ),
        oxygen_saturation=vitals_data.get(
            "oxygen_saturation"
        ),
    ),
    ecg_data=patient_information.get(
        "ecg",
        patient_information.get(
            "ecg_data"
        ),
    ),
)


# ---------------------------------------------------------
# Load previous-agent outputs
# ---------------------------------------------------------

clinical_summary = (
    FLANT5_OUTPUT_PATH
    .read_text(encoding="utf-8")
    .strip()
)

rag_text = (
    RAG_OUTPUT_PATH
    .read_text(encoding="utf-8")
    .strip()
)

deepseek_reasoning = (
    DEEPSEEK_OUTPUT_PATH
    .read_text(encoding="utf-8")
    .strip()
)


# ---------------------------------------------------------
# Extract RAG evidence context
# ---------------------------------------------------------

evidence_marker = (
    "========== EVIDENCE CONTEXT PASSED TO AGENTS =========="
)

if evidence_marker not in rag_text:
    raise RuntimeError(
        "Could not find the RAG evidence context section."
    )

evidence_context = rag_text.split(
    evidence_marker,
    1,
)[1].strip()


# ---------------------------------------------------------
# Build controlled Gemini prompt
# ---------------------------------------------------------

system_prompt = build_cardiology_system_prompt()

user_prompt = f"""
Evaluate the following {CASE_ID} as a cardiology
decision-support system.

IMPORTANT:
- Use ONLY the patient information provided below.
- Do not invent patient history, symptoms, diagnoses,
  medications, test results, or other clinical facts.
- Treat FLAN-T5 as an information-extraction input,
  not as ground truth.
- Use the retrieved RAG evidence only as supporting
  evidence.
- Use DeepSeek-R1 as an additional reasoning input,
  not as ground truth.
- Critically check all previous-agent information
  against the actual patient case.
- Do not present a confirmed diagnosis.
- Do not prescribe medication.
- Clearly identify uncertainty and information gaps.
- Recommend clinician review.

==============================
{CASE_ID.upper()} — PATIENT INFORMATION
==============================

{json.dumps(patient_information, indent=2)}

==============================
FLAN-T5 OUTPUT
==============================

{clinical_summary}

==============================
RAG EVIDENCE
==============================

{evidence_context}

==============================
DEEPSEEK-R1 REASONING
==============================

{deepseek_reasoning}

==============================
TASK
==============================

Produce a cautious cardiology decision-support report.

The report should contain:

1. Possible cardiac considerations
2. Recommended next tests or monitoring
3. Immediate safety note
4. Plain-language summary
5. Evidence Summary
6. Safety disclaimer

When discussing patient-specific information, ensure
that every factual claim can be traced back to the patient
case or explicitly supplied supporting agent output.

If information is missing, say that it is missing.

Do not fill gaps with assumptions.
""".strip()


# ---------------------------------------------------------
# Create Gemini agent
# ---------------------------------------------------------

agent = GeminiChatModel(
    model="gemini-2.5-flash"
)


# ---------------------------------------------------------
# Run Gemini
# ---------------------------------------------------------

print(
    f"\n========== {CASE_ID.upper()} GEMINI EVALUATION ==========\n"
)

print("Running Gemini using:")
print(f"- {CASE_ID} patient information")
print("- Actual FLAN-T5 output")
print("- Actual RAG evidence")
print("- Actual DeepSeek-R1 output")
print()

tools = get_agent_tools(patient_case)

raw_report = agent.generate(
    system_prompt=system_prompt,
    user_prompt=user_prompt,
    tools=tools,
)


# ---------------------------------------------------------
# Apply existing safety layer
# ---------------------------------------------------------

safe_report = apply_safety_layer(
    raw_report
)


# ---------------------------------------------------------
# Save output
# ---------------------------------------------------------

OUTPUT_PATH.write_text(
    safe_report + "\n",
    encoding="utf-8",
)


# ---------------------------------------------------------
# Display result
# ---------------------------------------------------------

print(
    f"========== {CASE_ID.upper()} GEMINI FINAL REPORT ==========\n"
)

print(safe_report)

print(
    f"\nGemini output saved to: {OUTPUT_PATH}"
)
