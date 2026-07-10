from app.models.patient import PatientCase, PatientProfile, Vitals


def build_demo_profile() -> PatientProfile:
    return PatientProfile(
        patient_id="P002",
        name="Demo Patient",
        age=52,
        sex="F",
    )


def build_demo_case() -> PatientCase:
    return PatientCase(
        symptoms=["chest pain", "palpitations"],
        patient_state="Intermittent chest discomfort with awareness of heartbeat.",
        medical_history=["anxiety", "GERD"],
        clinician_question="Give a brief cardiology-focused assessment.",
        vitals=Vitals(
            heart_rate=108,
            systolic_bp=128,
            diastolic_bp=82,
            oxygen_saturation=98,
        ),
        ecg_data="ECG shows irregular rhythm with possible atrial fibrillation pattern.",
    )