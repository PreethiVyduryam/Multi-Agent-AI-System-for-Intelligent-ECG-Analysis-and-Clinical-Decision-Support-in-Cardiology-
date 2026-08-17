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

from app.models.patient import PatientCase, Vitals
from app.rag.retriever import retrieve_evidence
from app.rag.evidence_service import build_evidence_context


# ---------------------------------------------------------
# Case selection
# ---------------------------------------------------------

CASE_ID = sys.argv[1] if len(sys.argv) > 1 else "case_001"


# ---------------------------------------------------------
# Files
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Load patient case
# ---------------------------------------------------------

def load_patient_case() -> tuple[str, PatientCase]:

    with open(
        CASE_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        case = json.load(file)

    patient_information = case[
        "patient_information"
    ]

    vitals_data = patient_information[
        "vital_signs"
    ]

    patient_case = PatientCase(
        symptoms=patient_information[
            "symptoms"
        ],
        patient_state=patient_information[
            "patient_state"
        ],
        medical_history=patient_information[
            "medical_history"
        ],
        vitals=Vitals(
            heart_rate=vitals_data.get(
                "heart_rate"
            ),
            systolic_bp=vitals_data.get(
                "systolic_bp"
            ),
            diastolic_bp=vitals_data.get(
                "diastolic_bp"
            ),
            oxygen_saturation=vitals_data.get(
                "oxygen_saturation"
            ),
        ),
        ecg_data=patient_information.get(
            "ecg"
        ),
    )

    return (
        case["case_id"],
        patient_case,
    )


# ---------------------------------------------------------
# Build retrieval query
# ---------------------------------------------------------

def build_retrieval_query(
    patient_case: PatientCase,
) -> str:

    query_parts = []

    if patient_case.symptoms:
        query_parts.extend(
            patient_case.symptoms
        )

    if patient_case.patient_state:
        query_parts.append(
            patient_case.patient_state
        )

    if patient_case.medical_history:
        query_parts.extend(
            patient_case.medical_history
        )

    if patient_case.ecg_data:
        query_parts.append(
            patient_case.ecg_data
        )

    if patient_case.clinician_question:
        query_parts.append(
            patient_case.clinician_question
        )

    return " ".join(query_parts)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main() -> None:

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    case_id, patient_case = (
        load_patient_case()
    )

    query = build_retrieval_query(
        patient_case
    )

    print(
        "\n========== RAG EVALUATION ==========\n"
    )

    print(f"Case: {case_id}")

    print(
        "\n========== RETRIEVAL QUERY ==========\n"
    )

    print(query)

    # -----------------------------------------------------
    # Retrieve evidence
    # -----------------------------------------------------

    evidence_items = retrieve_evidence(
        query
    )

    print(
        "\n========== RETRIEVED DOCUMENTS ==========\n"
    )

    if not evidence_items:

        print(
            "No relevant evidence retrieved."
        )

    else:

        for index, item in enumerate(
            evidence_items,
            start=1,
        ):

            print(
                f"\n--- Retrieved Document {index} ---"
            )

            print(
                f"Title: {item.get('title')}"
            )

            print(
                f"Organisation: "
                f"{item.get('organisation')}"
            )

            print(
                f"Year: {item.get('year')}"
            )

            print(
                f"Topic: {item.get('topic')}"
            )

            print(
                f"Keywords: {item.get('keywords')}"
            )

            print(
                f"Summary: {item.get('summary')}"
            )

    # -----------------------------------------------------
    # Build evidence context
    # -----------------------------------------------------

    evidence_context = (
        build_evidence_context(
            patient_case
        )
    )

    print(
        "\n========== EVIDENCE CONTEXT "
        "PASSED TO AGENTS ==========\n"
    )

    print(evidence_context)

    # -----------------------------------------------------
    # Save evaluation
    # -----------------------------------------------------

    result_file = (
        RESULTS_DIR
        / f"{case_id}_rag_evaluation.txt"
    )

    with open(
        result_file,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            "========== RAG EVALUATION ==========\n\n"
        )

        file.write(
            f"Case: {case_id}\n\n"
        )

        file.write(
            "========== RETRIEVAL QUERY ==========\n\n"
        )

        file.write(query)

        file.write(
            "\n\n"
        )

        file.write(
            "========== RETRIEVED DOCUMENTS "
            "==========\n\n"
        )

        for index, item in enumerate(
            evidence_items,
            start=1,
        ):

            file.write(
                f"--- Retrieved Document {index} ---\n"
            )

            file.write(
                f"Title: {item.get('title')}\n"
            )

            file.write(
                f"Organisation: "
                f"{item.get('organisation')}\n"
            )

            file.write(
                f"Year: {item.get('year')}\n"
            )

            file.write(
                f"Topic: {item.get('topic')}\n"
            )

            file.write(
                f"Keywords: {item.get('keywords')}\n"
            )

            file.write(
                f"Summary: {item.get('summary')}\n\n"
            )

        file.write(
            "========== EVIDENCE CONTEXT "
            "PASSED TO AGENTS ==========\n\n"
        )

        file.write(
            evidence_context
        )

    print(
        "\nSaved RAG evaluation to:"
    )

    print(result_file)


if __name__ == "__main__":
    main()
