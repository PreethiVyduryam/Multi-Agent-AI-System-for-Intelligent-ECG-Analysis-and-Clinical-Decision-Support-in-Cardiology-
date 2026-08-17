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
from app.tools.agent_tools import get_agent_tools
from app.services.safety_service import apply_safety_layer


# ---------------------------------------------------------
# Case selection
# ---------------------------------------------------------

if len(sys.argv) < 2:
    print(
        "Usage: python evaluation/scripts/evaluate_baseline_gemini.py case_001"
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

OUTPUT_DIR = (
    BASE_DIR
    / "evaluation"
    / "results"
    / "baseline"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / f"{CASE_ID}_baseline_gemini_output.txt"
)


# ---------------------------------------------------------
# Validate case
# ---------------------------------------------------------

if not CASE_PATH.exists():
    raise FileNotFoundError(
        f"Case file not found: {CASE_PATH}"
    )


# ---------------------------------------------------------
# Load environment
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
        heart_rate=vitals_data.get("heart_rate"),
        systolic_bp=vitals_data.get("systolic_bp"),
        diastolic_bp=vitals_data.get("diastolic_bp"),
        oxygen_saturation=vitals_data.get("oxygen_saturation"),
    ),
    ecg_data=patient_information.get(
        "ecg",
        patient_information.get("ecg_data"),
    ),
)


# ---------------------------------------------------------
# Baseline system prompt
# ---------------------------------------------------------
#
# IMPORTANT:
# This prompt intentionally excludes:
# - FLAN-T5
# - RAG evidence retrieval
# - DeepSeek-R1
# - enhanced CardiologyAssistant pipeline
#
# The baseline still uses:
# - Gemini 2.5 Flash
# - original ECG/literature tools
# - original safety layer
#
# The report structure is kept comparable with the enhanced
# architecture so that the evaluation does not penalise the
# baseline simply for having a different output format.
# ---------------------------------------------------------

BASELINE_SYSTEM_PROMPT = """
You are the original Gemini-based cardiology decision-support
assistant.

Your task is to provide cautious, structured clinical
decision-support based ONLY on the patient information supplied
in the user prompt and any results returned by the original
cardiology tools.

This is the BASELINE architecture.

The baseline does NOT use:
- FLAN-T5 clinical information extraction
- Retrieval-Augmented Generation (RAG)
- retrieved clinical evidence
- DeepSeek-R1 reasoning
- enhanced multi-agent reasoning

Do not invent patient information.

Do not provide a confirmed diagnosis.

Do not prescribe treatment or medication.

Use cautious language such as:
- possible
- may be considered
- could suggest
- requires further assessment

Always recommend appropriate clinician review.

The final response MUST use exactly this six-section structure:

1. Possible cardiac considerations
2. Recommended next tests or monitoring
3. Immediate safety note
4. Plain-language summary
5. Evidence Summary
6. Safety disclaimer

For Section 5, because this is the baseline architecture,
explicitly state that no external clinical evidence was retrieved
or injected.

Do NOT invent references, guidelines, publications, or evidence
sources.

The absence of retrieved evidence should be clear. The purpose of
this section is to make the output structure comparable with the
enhanced architecture while demonstrating that the baseline does
not perform RAG evidence grounding.

The response is for clinical decision support only and must not
be presented as medical advice or a confirmed diagnosis.
""".strip()


# ---------------------------------------------------------
# Baseline user prompt
# ---------------------------------------------------------

BASELINE_USER_PROMPT = f"""
Assess the following patient case using the original Gemini
cardiology decision-support architecture.

Patient information:

{patient_case}

Important baseline constraints:

- Use only the information provided in the patient case.
- You may use the original ECG/literature tools when appropriate.
- Do not use FLAN-T5.
- Do not use RAG evidence retrieval.
- Do not use DeepSeek-R1.
- Do not invent external evidence or references.
- Do not claim that guidelines or publications support a
  recommendation.
- Do not make a confirmed diagnosis.
- Do not prescribe treatment.
- Identify important information gaps where relevant.
- Include the patient's supplied vital signs when relevant.
- Clearly distinguish reported information from clinical
  considerations.

Required output structure:

1. Possible cardiac considerations
Provide a concise list of possible cardiac considerations and
appropriate cautious language.

2. Recommended next tests or monitoring
List appropriate investigations or monitoring that may help
clarify the presentation.

3. Immediate safety note
Explain whether prompt or urgent clinician assessment may be
appropriate based on the supplied presentation.

4. Plain-language summary
Provide a short, understandable summary of the patient's
presentation and why further clinical assessment may be needed.

5. Evidence Summary
State explicitly that no external clinical evidence was retrieved
or injected because this is the baseline architecture.
Explain briefly that the assessment is based on the supplied
patient information, original Gemini reasoning, and any original
tool results.
Do not provide invented references.

6. Safety disclaimer
State clearly that this is clinical decision-support information,
not medical advice or a confirmed diagnosis, and that a qualified
healthcare professional must make final clinical decisions.
""".strip()


# ---------------------------------------------------------
# Run ORIGINAL baseline components
# ---------------------------------------------------------

print()
print("========== BASELINE GEMINI EVALUATION ==========")
print()
print(f"Case: {CASE_ID}")
print()
print("Architecture:")
print("- Original Gemini 2.5 Flash")
print("- Original ECG/literature tools")
print("- Original safety layer")
print("- No FLAN-T5")
print("- No RAG evidence injection")
print("- No DeepSeek-R1 reasoning")
print("- No enhanced CardiologyAssistant pipeline")
print()


# ---------------------------------------------------------
# Initialise Gemini
# ---------------------------------------------------------

llm = GeminiChatModel(
    model="gemini-2.5-flash"
)


# ---------------------------------------------------------
# Get ORIGINAL baseline tools
# ---------------------------------------------------------

tools = get_agent_tools(patient_case)


# ---------------------------------------------------------
# Generate baseline report
# ---------------------------------------------------------

print("========== GENERATING BASELINE OUTPUT ==========")
print()

raw_report = llm.generate(
    system_prompt=BASELINE_SYSTEM_PROMPT,
    user_prompt=BASELINE_USER_PROMPT,
    tools=tools,
)


# ---------------------------------------------------------
# Apply ORIGINAL safety layer
# ---------------------------------------------------------

baseline_output = apply_safety_layer(
    raw_report
)


# ---------------------------------------------------------
# Save output
# ---------------------------------------------------------

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_PATH.write_text(
    baseline_output.strip() + "\n",
    encoding="utf-8",
)


# ---------------------------------------------------------
# Display output
# ---------------------------------------------------------

print()
print("========== BASELINE GEMINI OUTPUT ==========")
print()
print(baseline_output)
print()
print("============================================")
print()
print("Baseline output saved to:")
print(OUTPUT_PATH)
