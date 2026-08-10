from app.services.flant5_client import FlanT5Client

agent = FlanT5Client()

patient_case = """
65-year-old male.

Chest pain for 2 hours.

Pain radiates to left arm.

History of hypertension and diabetes.

Heart rate: 115 bpm

Blood pressure: 145/95 mmHg

ECG shows ST elevation in leads II, III and aVF.
"""

result = agent.extract_clinical_information(patient_case)

print("\n========== FLAN-T5 OUTPUT ==========\n")
print(result)
