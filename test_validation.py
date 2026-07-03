import pytest

from app.models.patient import PatientCase, Vitals
from app.services.assistant import CardiologyAssistant, InputValidationError


class DummyLLM:
    def generate(self, *args, **kwargs):
        return "dummy response"


def build_assistant():
    return CardiologyAssistant(DummyLLM())


def test_validation_passes_for_valid_case():
    assistant = build_assistant()

    patient_case = PatientCase(
        symptoms=["chest pain"],
        patient_state="Intermittent chest discomfort.",
        medical_history=["GERD"],
        vitals=Vitals(
            heart_rate=90,
            systolic_bp=120,
            diastolic_bp=80,
            oxygen_saturation=98,
        ),
    )

    assistant.validate_case(patient_case)


def test_validation_fails_when_symptoms_and_state_missing():
    assistant = build_assistant()

    patient_case = PatientCase(
        symptoms=[],
        patient_state="",
        medical_history=[],
        vitals=Vitals(),
    )

    with pytest.raises(InputValidationError):
        assistant.validate_case(patient_case)


def test_validation_fails_for_invalid_heart_rate():
    assistant = build_assistant()

    patient_case = PatientCase(
        symptoms=["palpitations"],
        patient_state="Fast heartbeat.",
        vitals=Vitals(heart_rate=500),
    )

    with pytest.raises(InputValidationError):
        assistant.validate_case(patient_case)


def test_validation_fails_for_invalid_oxygen_saturation():
    assistant = build_assistant()

    patient_case = PatientCase(
        symptoms=["shortness of breath"],
        patient_state="Feels breathless.",
        vitals=Vitals(oxygen_saturation=20),
    )

    with pytest.raises(InputValidationError):
        assistant.validate_case(patient_case)