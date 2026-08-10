from app.utils.config import load_env
from app.services.deepseek_client import DeepSeekClient
from app.prompts.deepseek_prompt import build_deepseek_reasoning_prompt


load_env()

patient_case = """
Patient ID: P200
Name: Jane Doe
Age: 52
Sex: F

Symptoms:
Chest pain and palpitations.

Medical history:
Hypertension, diabetes and previous heart-related issues.

Vital signs:
Heart rate: 115 bpm
Blood pressure: 145/95 mmHg

ECG:
Irregular heartbeat reported.
"""

clinical_summary = """
Chief Complaint:
- Chest pain

Symptoms:
- Chest pain
- Palpitations

Vital Signs:
- Heart rate: 115 bpm
- Blood pressure: 145/95 mmHg

Risk Factors:
- Hypertension
- Diabetes

Medical History:
- Previous heart-related issues

ECG Findings:
- Irregular heartbeat

Patient Information:
- 52-year-old female
"""

evidence_context = """
NICE: Atrial fibrillation: diagnosis and management (2021)
Relevant evidence indicates that suspected atrial fibrillation
should be assessed using ECG-based rhythm confirmation.

NICE: Chest pain of recent onset: assessment and diagnosis (2016)
Relevant evidence supports clinical assessment and ECG evaluation
for patients presenting with chest pain.

ESC Guidelines for Acute Coronary Syndromes (2023)
Relevant evidence supports prompt assessment of patients with
symptoms potentially suggestive of acute coronary syndromes.
"""

prompt = build_deepseek_reasoning_prompt(
    patient_case=patient_case,
    clinical_summary=clinical_summary,
    evidence_context=evidence_context,
)

agent = DeepSeekClient()

result = agent.generate(
    system_prompt=(
        "You are a cautious clinical reasoning agent within a "
        "multi-agent cardiology decision-support system."
    ),
    user_prompt=prompt,
)

print("\n========== DEEPSEEK-R1 REASONING ==========\n")
print(result)
