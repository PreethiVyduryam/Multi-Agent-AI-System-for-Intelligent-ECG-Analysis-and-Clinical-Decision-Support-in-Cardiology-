from app.db.database import initialize_database
from app.db.patient_repository import (
    upsert_patient,
    save_visit,
    get_patient,
    get_recent_visits,
    get_all_visits,
)
from app.models.patient import PatientProfile, PatientCase, Vitals


def test_database_patient_and_visit_roundtrip(monkeypatch, tmp_path):
    db_file = tmp_path / "test_cardiology_agent.db"
    monkeypatch.setenv("CARDIOLOGY_AGENT_DB_PATH", str(db_file))

    initialize_database()

    profile = PatientProfile(
        patient_id="PTEST001",
        name="Test Patient",
        age=60,
        sex="F",
    )

    patient_case = PatientCase(
        symptoms=["palpitations", "chest pain"],
        patient_state="Intermittent palpitations with chest discomfort.",
        medical_history=["anxiety"],
        clinician_question="What is the next best workup?",
        vitals=Vitals(
            heart_rate=105,
            systolic_bp=130,
            diastolic_bp=85,
            oxygen_saturation=98,
        ),
        ecg_data="ECG shows irregular rhythm.",
    )

    upsert_patient(profile)
    save_visit(profile, patient_case, "Test generated report")

    loaded_patient = get_patient("PTEST001")
    assert loaded_patient is not None
    assert loaded_patient["name"] == "Test Patient"

    recent_visits = get_recent_visits("PTEST001", limit=3)
    assert len(recent_visits) == 1
    assert recent_visits[0]["patient_id"] == "PTEST001"
    assert recent_visits[0]["generated_report"] == "Test generated report"

    all_visits = get_all_visits("PTEST001")
    assert len(all_visits) == 1