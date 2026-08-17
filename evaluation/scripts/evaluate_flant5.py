import json
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))


from app.models.patient import PatientCase, Vitals
from app.services.flant5_client import FlanT5Client


# ---------------------------------------------------------
# Case selection
# ---------------------------------------------------------

CASE_ID = sys.argv[1] if len(sys.argv) > 1 else "case_001"


CASE_FILE = (
    BASE_DIR
    / "evaluation"
    / "cases"
    / f"{CASE_ID}.json"
)

RESULTS_DIR = (
    BASE_DIR
    / "evaluation"
    / "results"
)


def load_patient_case() -> tuple[str, PatientCase, dict]:

    with open(
        CASE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        case = json.load(file)

    patient_information = (
        case["patient_information"]
    )

    vitals_data = (
        patient_information["vital_signs"]
    )

    patient_case = PatientCase(
        symptoms=patient_information["symptoms"],
        patient_state=patient_information["patient_state"],
        medical_history=patient_information["medical_history"],
        vitals=Vitals(
            heart_rate=vitals_data.get("heart_rate"),
            systolic_bp=vitals_data.get("systolic_bp"),
            diastolic_bp=vitals_data.get("diastolic_bp"),
            oxygen_saturation=vitals_data.get(
                "oxygen_saturation"
            ),
        ),
        ecg_data=patient_information.get("ecg"),
    )

    return (
        case["case_id"],
        patient_case,
        patient_information
    )


def build_clinical_text(
    patient_information: dict
) -> str:

    symptoms = ", ".join(
        patient_information.get(
            "symptoms",
            []
        )
    )

    medical_history = ", ".join(
        patient_information.get(
            "medical_history",
            []
        )
    )

    vitals = patient_information.get(
        "vital_signs",
        {}
    )

    age = patient_information.get(
        "age",
        "Not provided"
    )

    sex = patient_information.get(
        "sex",
        "Not provided"
    )

    patient_state = patient_information.get(
        "patient_state",
        "Not provided."
    )

    ecg = patient_information.get(
        "ecg",
        "Not provided."
    )

    heart_rate = vitals.get(
        "heart_rate",
        "Not provided"
    )

    systolic_bp = vitals.get(
        "systolic_bp",
        "Not provided"
    )

    diastolic_bp = vitals.get(
        "diastolic_bp",
        "Not provided"
    )

    oxygen_saturation = vitals.get(
        "oxygen_saturation",
        "Not provided"
    )

    return f"""
A {age}-year-old {sex} patient reports {symptoms}.

Patient state:
{patient_state}

Medical history:
{medical_history}

Vital signs:
Heart rate: {heart_rate} bpm
Blood pressure: {systolic_bp}/{diastolic_bp} mmHg
Oxygen saturation: {oxygen_saturation}%

ECG information:
{ecg}
""".strip()


def main() -> None:

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    case_id, patient_case, patient_information_data = (
        load_patient_case()
    )

    patient_information = build_clinical_text(
        patient_information_data
    )

    print(
        "\n========== FLAN-T5 EVALUATION ==========\n"
    )

    print(
        f"Case: {case_id}"
    )

    print(
        "\n========== INPUT TO FLAN-T5 ==========\n"
    )

    print(patient_information)

    agent = FlanT5Client()

    output = agent.extract_clinical_information(
        patient_information
    )

    print(
        "\n========== FLAN-T5 OUTPUT ==========\n"
    )

    print(output)

    result_file = (
        RESULTS_DIR
        / f"{case_id}_flant5_output.txt"
    )

    with open(
        result_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(output)

    print(
        "\nSaved output to:"
    )

    print(result_file)


if __name__ == "__main__":
    main()
