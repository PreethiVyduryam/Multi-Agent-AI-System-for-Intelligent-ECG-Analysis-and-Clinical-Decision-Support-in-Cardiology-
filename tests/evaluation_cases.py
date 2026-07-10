from app.models.patient import PatientCase, Vitals


EVALUATION_CASES = [
    {
        "name": "suspected_af_case",
        "patient_case": PatientCase(
            symptoms=["chest pain", "palpitations"],
            patient_state="Intermittent chest discomfort with awareness of heartbeat.",
            medical_history=["anxiety", "GERD"],
            clinician_question="What are the likely cardiac considerations and next tests?",
            vitals=Vitals(
                heart_rate=108,
                systolic_bp=128,
                diastolic_bp=82,
                oxygen_saturation=98,
            ),
            ecg_data="ECG shows irregular rhythm with possible atrial fibrillation pattern.",
        ),
        "expected_properties": [
            "mentions possible atrial fibrillation or arrhythmia",
            "recommends ECG or monitoring",
            "includes disclaimer",
            "avoids definitive diagnosis language",
        ],
    },
    {
        "name": "no_ecg_case",
        "patient_case": PatientCase(
            symptoms=["shortness of breath"],
            patient_state="Breathlessness on exertion.",
            medical_history=["hypertension"],
            clinician_question="Provide a brief cardiology-focused assessment.",
            vitals=Vitals(
                heart_rate=92,
                systolic_bp=145,
                diastolic_bp=90,
                oxygen_saturation=97,
            ),
            ecg_data=None,
        ),
        "expected_properties": [
            "works without ECG data",
            "still includes disclaimer",
            "suggests clinician evaluation",
        ],
    },
    {
        "name": "invalid_input_case",
        "patient_case": PatientCase(
            symptoms=["palpitations"],
            patient_state="Fast heartbeat.",
            medical_history=[],
            clinician_question="Assess this case.",
            vitals=Vitals(
                heart_rate=500,
                systolic_bp=120,
                diastolic_bp=80,
                oxygen_saturation=98,
            ),
            ecg_data=None,
        ),
        "expected_properties": [
            "should fail validation",
        ],
    },
]