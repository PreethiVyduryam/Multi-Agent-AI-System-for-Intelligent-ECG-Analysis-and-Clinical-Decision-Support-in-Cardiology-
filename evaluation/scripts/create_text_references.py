from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

REFERENCE_DIR = (
    BASE_DIR
    / "evaluation"
    / "references"
    / "text"
)

REFERENCE_DIR.mkdir(parents=True, exist_ok=True)


REFERENCES = {

"case_001": """
A 52-year-old female presents with chest pain and palpitations. Her medical history includes hypertension and diabetes. Vital signs show a heart rate of 115 bpm, blood pressure of 145/95 mmHg and oxygen saturation of 98%. The reported ECG finding is an irregular heartbeat.

The combination of chest pain, palpitations, tachycardia and an irregular heartbeat warrants consideration of a cardiac rhythm abnormality, including an arrhythmia such as atrial fibrillation. The patient's hypertension and diabetes represent additional cardiovascular risk factors. Acute coronary syndrome or myocardial ischaemia may also require consideration because of the chest pain and associated cardiovascular risk profile.

Further clinical assessment should include formal ECG interpretation and, where clinically appropriate, cardiac rhythm monitoring. Additional investigations may include cardiac biomarkers and assessment of relevant cardiovascular risk factors. The available information is insufficient to establish a confirmed diagnosis, and interpretation should be performed by a qualified healthcare professional.
""",

"case_002": """
A 67-year-old male presents with shortness of breath and dizziness. His medical history includes hypertension and hyperlipidaemia. Vital signs show a heart rate of 88 bpm, blood pressure of 138/84 mmHg and oxygen saturation of 97%. The ECG is described as sinus rhythm with occasional premature beats.

The reported premature beats may represent an intermittent rhythm disturbance and could contribute to the patient's symptoms of dizziness. Arrhythmia should therefore be considered, while the patient's hypertension and hyperlipidaemia also increase cardiovascular risk. Coronary artery disease or other structural cardiac conditions may require consideration depending on the wider clinical assessment.

Further assessment may include ambulatory ECG or Holter monitoring to evaluate the frequency of premature beats and their relationship with symptoms. Echocardiography and appropriate laboratory investigations, including electrolyte and thyroid-function assessment, may also be considered. The available information does not establish a confirmed diagnosis and requires professional clinical interpretation.
""",

"case_003": """
A 59-year-old female presents with exertional chest discomfort, shortness of breath and fatigue. Her medical history includes hypertension and hyperlipidaemia. Vital signs show a heart rate of 96 bpm, blood pressure of 152/92 mmHg and oxygen saturation of 96%. The ECG reports non-specific ST-T wave changes.

The combination of exertional chest discomfort, cardiovascular risk factors and non-specific ECG changes warrants consideration of myocardial ischaemia and coronary artery disease. Acute coronary syndrome may need to be excluded depending on the clinical presentation and additional history. The elevated blood pressure is also clinically relevant and requires further assessment.

Further investigation may include clinical examination, cardiac biomarkers where acute coronary syndrome is suspected, echocardiography and appropriate assessment for inducible ischaemia. Ambulatory ECG monitoring may be considered if an arrhythmia is suspected. The non-specific ECG findings alone cannot establish a diagnosis, and the overall presentation should be assessed by a qualified healthcare professional.
""",

"case_004": """
A 45-year-old male presents with palpitations, dizziness and fatigue. His medical history includes hypertension. Vital signs show a heart rate of 108 bpm, blood pressure of 140/88 mmHg and oxygen saturation of 98%. The ECG reports occasional premature beats.

The patient's palpitations and dizziness in association with premature beats suggest that a cardiac rhythm disturbance should be considered. Arrhythmia, including intermittent atrial fibrillation or another tachyarrhythmia, may require further investigation. Hypertension represents an additional cardiovascular risk factor.

Further assessment may include a formal 12-lead ECG and ambulatory rhythm monitoring, such as Holter monitoring, to determine the frequency and clinical significance of the premature beats. Thyroid-function and electrolyte assessment may also be appropriate when investigating potential causes of rhythm disturbance. The available findings are insufficient to establish a confirmed diagnosis and should be reviewed clinically.
""",

"case_005": """
A 67-year-old female presents with shortness of breath, ankle swelling and fatigue. Her medical history includes hypertension and type 2 diabetes. Vital signs show a heart rate of 88 bpm, blood pressure of 148/90 mmHg and oxygen saturation of 95%. The ECG reports voltage criteria for left ventricular hypertrophy with non-specific repolarisation changes.

The combination of respiratory symptoms, ankle swelling, cardiovascular risk factors and ECG evidence suggestive of left ventricular hypertrophy warrants consideration of structural cardiac disease, including possible heart failure. Coronary artery disease and myocardial ischaemia may also require consideration because of the patient's cardiovascular risk profile. The ECG findings alone are not sufficient to establish a diagnosis.

Further assessment may include echocardiography to evaluate cardiac structure and function, together with appropriate laboratory investigations and cardiovascular assessment. Blood pressure and diabetes should also be considered as relevant contributing risk factors. The presentation requires professional clinical assessment, and the available information should not be interpreted as a confirmed diagnosis.
"""
}


for case_id, text in REFERENCES.items():

    output_file = (
        REFERENCE_DIR
        / f"{case_id}_reference.txt"
    )

    output_file.write_text(
        text.strip() + "\n",
        encoding="utf-8"
    )

    print(f"Created: {output_file}")


print("\nAll five reference reports created successfully.")
