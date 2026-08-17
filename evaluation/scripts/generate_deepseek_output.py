import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

from app.utils.config import load_env
from app.prompts.deepseek_prompt import build_deepseek_reasoning_prompt
from app.services.deepseek_client import DeepSeekClient


if len(sys.argv) != 2:
    print("Usage: python evaluation/scripts/generate_deepseek_output.py case_003")
    sys.exit(1)

CASE_ID = sys.argv[1]

CASE_FILE = BASE_DIR / "evaluation" / "cases" / f"{CASE_ID}.json"
FLANT5_FILE = BASE_DIR / "evaluation" / "results" / f"{CASE_ID}_flant5_output.txt"
RAG_FILE = BASE_DIR / "evaluation" / "results" / f"{CASE_ID}_rag_evaluation.txt"
OUTPUT_FILE = BASE_DIR / "evaluation" / "results" / f"{CASE_ID}_deepseek_output.txt"


for file_path in [CASE_FILE, FLANT5_FILE, RAG_FILE]:
    if not file_path.exists():
        raise FileNotFoundError(
            f"Required evaluation file not found: {file_path}"
        )


load_env()


with CASE_FILE.open("r", encoding="utf-8") as file:
    case_data = json.load(file)

patient_information = case_data["patient_information"]

flant5_output = FLANT5_FILE.read_text(
    encoding="utf-8"
).strip()

rag_output = RAG_FILE.read_text(
    encoding="utf-8"
).strip()


evidence_marker = "========== EVIDENCE CONTEXT PASSED TO AGENTS =========="

if evidence_marker not in rag_output:
    raise RuntimeError(
        "Could not find the RAG evidence context section."
    )

evidence_context = rag_output.split(
    evidence_marker,
    1,
)[1].strip()


patient_text = json.dumps(
    patient_information,
    indent=2,
)


deepseek_prompt = build_deepseek_reasoning_prompt(
    patient_case=patient_text,
    clinical_summary=flant5_output,
    evidence_context=evidence_context,
)


agent = DeepSeekClient(
    model="deepseek-reasoner"
)


print(
    f"\n========== {CASE_ID.upper()} DEEPSEEK-R1 GENERATION ==========\n"
)

print("Running DeepSeek-R1 using:")
print(f"- {CASE_ID} patient information")
print("- Actual FLAN-T5 output")
print("- Actual RAG evidence")
print()


deepseek_reasoning = agent.generate(
    system_prompt=(
        "You are the DeepSeek-R1 clinical reasoning agent "
        "within a multi-agent cardiology decision-support "
        "system. Use cautious, evidence-informed reasoning. "
        "Do not provide a confirmed diagnosis. "
        "Do not prescribe treatment or medication. "
        "Identify uncertainty and information gaps. "
        "Support clinician review."
    ),
    user_prompt=deepseek_prompt,
)


OUTPUT_FILE.write_text(
    deepseek_reasoning.strip() + "\n",
    encoding="utf-8",
)


print(
    "\n========== DEEPSEEK-R1 OUTPUT ==========\n"
)

print(deepseek_reasoning)

print(
    f"\nDeepSeek-R1 output saved to: {OUTPUT_FILE}"
)
