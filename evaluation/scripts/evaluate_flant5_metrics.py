import json
import re
import sys
from pathlib import Path


# ---------------------------------------------------------
# Project path
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))


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

REFERENCE_FILE = (
    BASE_DIR
    / "evaluation"
    / "references"
    / f"{CASE_ID}_flant5.json"
)

RESULTS_DIR = (
    BASE_DIR
    / "evaluation"
    / "results"
)


# ---------------------------------------------------------
# Text normalisation
# ---------------------------------------------------------

def normalise_text(value: str) -> str:
    value = str(value).lower().strip()

    value = value.replace("female", "f")
    value = value.replace("male", "m")

    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[.,;:]+$", "", value)

    return value


# ---------------------------------------------------------
# Load files
# ---------------------------------------------------------

def load_reference() -> dict:
    with open(
        REFERENCE_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def load_prediction() -> str:

    result_file = (
        RESULTS_DIR
        / f"{CASE_ID}_flant5_output.txt"
    )

    if not result_file.exists():
        raise FileNotFoundError(
            f"FLAN-T5 output not found: {result_file}"
        )

    return result_file.read_text(
        encoding="utf-8"
    )


# ---------------------------------------------------------
# Information extraction
# ---------------------------------------------------------

def extract_information_units(
    reference: dict,
    prediction: str,
) -> tuple[set[str], set[str]]:

    expected = reference["expected_information"]

    reference_units = set()

    # -----------------------------------------------------
    # Age
    # -----------------------------------------------------

    reference_units.add(
        f"age:{normalise_text(expected['age'])}"
    )

    # -----------------------------------------------------
    # Sex
    # -----------------------------------------------------

    reference_units.add(
        f"sex:{normalise_text(expected['sex'])}"
    )

    # -----------------------------------------------------
    # Symptoms
    # -----------------------------------------------------

    for symptom in expected["symptoms"]:
        reference_units.add(
            f"symptom:{normalise_text(symptom)}"
        )

    # -----------------------------------------------------
    # Medical history
    # -----------------------------------------------------

    for item in expected["medical_history"]:
        reference_units.add(
            f"history:{normalise_text(item)}"
        )

    # -----------------------------------------------------
    # Vital signs
    # -----------------------------------------------------

    reference_units.add(
        f"heart_rate:{normalise_text(expected['heart_rate'])}"
    )

    reference_units.add(
        f"blood_pressure:{normalise_text(expected['blood_pressure'])}"
    )

    reference_units.add(
        f"oxygen_saturation:"
        f"{normalise_text(expected['oxygen_saturation'])}"
    )

    # -----------------------------------------------------
    # ECG
    # -----------------------------------------------------

    reference_units.add(
        f"ecg:{normalise_text(expected['ecg'])}"
    )

    # -----------------------------------------------------
    # Prediction
    # -----------------------------------------------------

    prediction_normalised = normalise_text(
        prediction
    )

    prediction_units = set()

    # -----------------------------------------------------
    # Age
    # -----------------------------------------------------

    age = str(expected["age"])

    if re.search(
        rf"\b{re.escape(age)}\b",
        prediction_normalised
    ):
        prediction_units.add(
            f"age:{age}"
        )

    # -----------------------------------------------------
    # Sex
    # -----------------------------------------------------

    expected_sex = normalise_text(
        expected["sex"]
    )

    if expected_sex == "f":
        if (
            "female" in prediction_normalised
            or re.search(r"\bf\b", prediction_normalised)
        ):
            prediction_units.add("sex:f")

    elif expected_sex == "m":
        if (
            "male" in prediction_normalised
            or re.search(r"\bm\b", prediction_normalised)
        ):
            prediction_units.add("sex:m")

    # -----------------------------------------------------
    # Symptoms
    # -----------------------------------------------------

    for symptom in expected["symptoms"]:

        symptom_normalised = normalise_text(
            symptom
        )

        if symptom_normalised in prediction_normalised:
            prediction_units.add(
                f"symptom:{symptom_normalised}"
            )

    # -----------------------------------------------------
    # Medical history
    # -----------------------------------------------------

    for item in expected["medical_history"]:

        item_normalised = normalise_text(
            item
        )

        if item_normalised in prediction_normalised:
            prediction_units.add(
                f"history:{item_normalised}"
            )

    # -----------------------------------------------------
    # Vital signs
    # -----------------------------------------------------

    heart_rate = normalise_text(
        expected["heart_rate"]
    )

    if heart_rate in prediction_normalised:
        prediction_units.add(
            f"heart_rate:{heart_rate}"
        )

    blood_pressure = normalise_text(
        expected["blood_pressure"]
    )

    blood_pressure_variants = [
        blood_pressure,
        blood_pressure.replace(
            " mmhg",
            ""
        ),
        blood_pressure.replace(
            "/",
            " / "
        ),
    ]

    if any(
        variant in prediction_normalised
        for variant in blood_pressure_variants
    ):
        prediction_units.add(
            f"blood_pressure:{blood_pressure}"
        )

    oxygen = normalise_text(
        expected["oxygen_saturation"]
    )

    oxygen_variants = [
        oxygen,
        oxygen.replace("%", " %"),
        oxygen.replace("%", ""),
    ]

    if any(
        variant in prediction_normalised
        for variant in oxygen_variants
    ):
        prediction_units.add(
            f"oxygen_saturation:{oxygen}"
        )

    # -----------------------------------------------------
    # ECG
    # -----------------------------------------------------

    ecg_expected = normalise_text(
        expected["ecg"]
    )

    # Exact ECG phrase where possible
    if ecg_expected in prediction_normalised:
        prediction_units.add(
            f"ecg:{ecg_expected}"
        )

    else:

        # Flexible ECG matching for minor wording differences
        ecg_terms = [
            term
            for term in [
                "sinus rhythm",
                "occasional premature beats",
                "premature beats",
                "irregular heartbeat",
                "irregular rhythm",
            ]
            if term in ecg_expected
        ]

        if ecg_terms and all(
            term in prediction_normalised
            for term in ecg_terms
        ):
            prediction_units.add(
                f"ecg:{ecg_expected}"
            )

    return (
        reference_units,
        prediction_units
    )


# ---------------------------------------------------------
# Metrics
# ---------------------------------------------------------

def calculate_metrics(
    reference_units: set[str],
    prediction_units: set[str],
) -> dict:

    true_positives = len(
        reference_units & prediction_units
    )

    false_positives = len(
        prediction_units - reference_units
    )

    false_negatives = len(
        reference_units - prediction_units
    )

    if true_positives + false_positives == 0:
        precision = 0.0
    else:
        precision = (
            true_positives
            / (true_positives + false_positives)
        )

    if true_positives + false_negatives == 0:
        recall = 0.0
    else:
        recall = (
            true_positives
            / (true_positives + false_negatives)
        )

    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = (
            2 * precision * recall
            / (precision + recall)
        )

    return {
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


# ---------------------------------------------------------
# Main evaluation
# ---------------------------------------------------------

def main():

    reference = load_reference()
    prediction = load_prediction()

    reference_units, prediction_units = (
        extract_information_units(
            reference,
            prediction,
        )
    )

    metrics = calculate_metrics(
        reference_units,
        prediction_units,
    )

    matched = (
        reference_units
        & prediction_units
    )

    missing = (
        reference_units
        - prediction_units
    )

    unexpected = (
        prediction_units
        - reference_units
    )

    print(
        f"\n========== FLAN-T5 INFORMATION "
        f"EXTRACTION EVALUATION - {CASE_ID.upper()} ==========\n"
    )

    print("Reference information units:")

    for item in sorted(reference_units):
        print(f"  - {item}")

    print("\nPredicted information units:")

    for item in sorted(prediction_units):
        print(f"  - {item}")

    print("\nMatched:")

    for item in sorted(matched):
        print(f"  + {item}")

    print("\nMissing:")

    for item in sorted(missing):
        print(f"  - {item}")

    print("\nUnexpected:")

    for item in sorted(unexpected):
        print(f"  - {item}")

    print("\n========== METRICS ==========\n")

    print(
        f"True Positives:  {metrics['true_positives']}"
    )

    print(
        f"False Positives: {metrics['false_positives']}"
    )

    print(
        f"False Negatives: {metrics['false_negatives']}"
    )

    print(
        f"Precision:       {metrics['precision']:.3f}"
    )

    print(
        f"Recall:          {metrics['recall']:.3f}"
    )

    print(
        f"F1 Score:        {metrics['f1']:.3f}"
    )

    # -----------------------------------------------------
    # Save metrics
    # -----------------------------------------------------

    output_file = (
        RESULTS_DIR
        / f"{CASE_ID}_flant5_metrics.json"
    )

    result = {
        "case_id": CASE_ID,
        "reference_units": sorted(
            reference_units
        ),
        "prediction_units": sorted(
            prediction_units
        ),
        "matched": sorted(
            matched
        ),
        "missing": sorted(
            missing
        ),
        "unexpected": sorted(
            unexpected
        ),
        "metrics": metrics,
    }

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            result,
            file,
            indent=2
        )

    print(
        f"\nEvaluation saved to:\n{output_file}"
    )


if __name__ == "__main__":
    main()
