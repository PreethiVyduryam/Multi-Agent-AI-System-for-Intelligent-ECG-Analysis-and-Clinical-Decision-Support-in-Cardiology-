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
# Case argument
# ---------------------------------------------------------

if len(sys.argv) != 2:
    print(
        "Usage: python evaluation/scripts/evaluate_deepseek_metrics.py <case_id>"
    )
    sys.exit(1)

CASE_ID = sys.argv[1]


# ---------------------------------------------------------
# Files
# ---------------------------------------------------------

CASE_FILE = (
    BASE_DIR
    / "evaluation"
    / "cases"
    / f"{CASE_ID}.json"
)

FLANT5_FILE = (
    BASE_DIR
    / "evaluation"
    / "results"
    / f"{CASE_ID}_flant5_output.txt"
)

RAG_FILE = (
    BASE_DIR
    / "evaluation"
    / "results"
    / f"{CASE_ID}_rag_evaluation.txt"
)

DEEPSEEK_FILE = (
    BASE_DIR
    / "evaluation"
    / "results"
    / f"{CASE_ID}_deepseek_output.txt"
)

OUTPUT_FILE = (
    BASE_DIR
    / "evaluation"
    / "results"
    / f"{CASE_ID}_deepseek_metrics.json"
)


# ---------------------------------------------------------
# Load files
# ---------------------------------------------------------

def load_case() -> dict:
    if not CASE_FILE.exists():
        raise FileNotFoundError(
            f"Case file not found: {CASE_FILE}"
        )

    with CASE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(
            f"Required file not found: {path}"
        )

    return path.read_text(
        encoding="utf-8"
    ).strip()


# ---------------------------------------------------------
# Normalisation
# ---------------------------------------------------------

def normalise_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def contains_any(text: str, terms: list[str]) -> list[str]:
    return [
        term
        for term in terms
        if term.lower() in text
    ]


# ---------------------------------------------------------
# Evaluation criteria
# ---------------------------------------------------------

def evaluate_deepseek(
    case_data: dict,
    flant5_output: str,
    rag_output: str,
    deepseek_output: str,
) -> list[dict]:

    output = normalise_text(deepseek_output)
    flant5 = normalise_text(flant5_output)
    rag = normalise_text(rag_output)

    case = case_data["patient_information"]

    results = []

    # -----------------------------------------------------
    # 1. Patient information usage
    # -----------------------------------------------------

    required_patient_facts = []

    # Age
    if "age" in case:
        required_patient_facts.append(str(case["age"]))

    # Sex
    if "sex" in case:
        sex = case["sex"].upper()

        if sex == "F":
            required_patient_facts.append("female")
        elif sex == "M":
            required_patient_facts.append("male")

    # Symptoms
    symptoms = case.get("symptoms", [])

    if isinstance(symptoms, list):
        required_patient_facts.extend(
            str(symptom).lower()
            for symptom in symptoms
        )
    elif symptoms:
        required_patient_facts.append(
            str(symptoms).lower()
        )

    # Medical history
    medical_history = case.get(
        "medical_history",
        []
    )

    if isinstance(medical_history, list):
        required_patient_facts.extend(
            str(item).lower()
            for item in medical_history
        )
    elif medical_history:
        required_patient_facts.append(
            str(medical_history).lower()
        )

    # Vital signs
    vital_signs = case.get(
        "vital_signs",
        {}
    )

    if isinstance(vital_signs, dict):

        heart_rate = vital_signs.get(
            "heart_rate"
        )

        if heart_rate is not None:
            required_patient_facts.append(
                f"{heart_rate} bpm"
            )

        blood_pressure = vital_signs.get(
            "blood_pressure"
        )

        if blood_pressure:
            required_patient_facts.append(
                str(blood_pressure)
            )

        oxygen_saturation = vital_signs.get(
            "oxygen_saturation"
        )

        if oxygen_saturation is not None:
            required_patient_facts.append(
                f"{oxygen_saturation}%"
            )

    # ECG / clinical finding
    ecg = case.get("ecg")

    if ecg:
        ecg_text = str(ecg).lower()

        # Extract clinically meaningful phrases
        # rather than requiring the entire ECG sentence.
        ecg_terms = [
            "irregular heartbeat",
            "palpitations",
            "sinus rhythm",
            "premature beats",
            "atrial fibrillation",
            "tachycardia",
            "bradycardia",
        ]

        for term in ecg_terms:
            if term in ecg_text:
                required_patient_facts.append(term)

    # Remove duplicates while preserving order
    required_patient_facts = list(
        dict.fromkeys(required_patient_facts)
    )

    matched_facts = contains_any(
        output,
        required_patient_facts
    )

    patient_pass = (
        len(required_patient_facts) > 0
        and len(matched_facts)
        >= len(required_patient_facts) * 0.8
    )

    results.append({
        "criterion": "Patient information usage",
        "result": (
            "PASS"
            if patient_pass
            else "FAIL"
        ),
        "details": (
            f"{len(matched_facts)}/"
            f"{len(required_patient_facts)} relevant "
            "patient facts were reflected in the output."
        ),
    })

    # -----------------------------------------------------
    # 2. FLAN-T5 integration
    # -----------------------------------------------------

    flant5_terms = [
        "irregular heartbeat",
        "palpitations",
        "sinus rhythm",
        "premature beats",
        "atrial fibrillation",
        "arrhythmia",
        "tachycardia",
        "bradycardia",
    ]

    # Only evaluate terms actually present in FLAN-T5 output
    relevant_flant5_terms = [
        term
        for term in flant5_terms
        if term in flant5
    ]

    flant5_matches = [
        term
        for term in relevant_flant5_terms
        if term in output
    ]

    flant5_pass = (
        len(relevant_flant5_terms) == 0
        or len(flant5_matches) > 0
    )

    results.append({
        "criterion": "FLAN-T5 information integration",
        "result": (
            "PASS"
            if flant5_pass
            else "FAIL"
        ),
        "details": (
            f"{len(flant5_matches)} relevant FLAN-T5 "
            "clinical terms were reflected in the output."
            if flant5_pass
            else
            "No clear use of the FLAN-T5 clinical "
            "information was identified."
        ),
    })

    # -----------------------------------------------------
    # 3. RAG evidence integration
    # -----------------------------------------------------

    evidence_terms = [
        "nice",
        "esc",
        "atrial fibrillation",
        "12-lead ecg",
        "ambulatory",
        "holter",
        "troponin",
        "acute coronary syndrome",
        "myocardial infarction",
        "hypertension",
        "cardiovascular risk",
        "ai interpretation",
        "clinician oversight",
        "rhythm",
        "arrhythmia",
        "ecg",
    ]

    # Only count concepts that actually occur in retrieved RAG
    # evidence, preventing unrelated fixed terms from affecting
    # the score for every case.
    relevant_evidence_terms = [
        term
        for term in evidence_terms
        if term in rag
    ]

    evidence_matches = [
        term
        for term in relevant_evidence_terms
        if term in output
    ]

    rag_pass = (
        len(relevant_evidence_terms) == 0
        or len(evidence_matches) >= 3
    )

    results.append({
        "criterion": "RAG evidence integration",
        "result": (
            "PASS"
            if rag_pass
            else "FAIL"
        ),
        "details": (
            f"{len(evidence_matches)} relevant evidence "
            "terms/concepts were reflected in the output."
        ),
    })

    # -----------------------------------------------------
    # 4. Clinical reasoning
    # -----------------------------------------------------

    reasoning_terms = [
        "may suggest",
        "could indicate",
        "could suggest",
        "may indicate",
        "risk",
        "relevant",
        "because",
        "however",
        "therefore",
        "although",
        "consistent with",
        "warrant",
        "consider",
        "consideration",
    ]

    reasoning_matches = contains_any(
        output,
        reasoning_terms
    )

    reasoning_pass = (
        len(reasoning_matches) >= 3
    )

    results.append({
        "criterion": "Clinical reasoning",
        "result": (
            "PASS"
            if reasoning_pass
            else "FAIL"
        ),
        "details": (
            "The response connects patient findings "
            "and provides explanatory clinical reasoning."
            if reasoning_pass
            else
            "Limited evidence of structured clinical reasoning."
        ),
    })

    # -----------------------------------------------------
    # 5. Possible cardiac considerations
    # -----------------------------------------------------

    cardiac_section = (
        "possible cardiac considerations" in output
    )

    cardiac_terms = [
        "atrial fibrillation",
        "acute coronary syndrome",
        "arrhythmia",
        "myocardial ischaemia",
        "myocardial ischemia",
        "coronary artery disease",
        "heart failure",
        "hypertensive heart disease",
        "ectopy",
        "premature beats",
        "supraventricular",
        "ventricular arrhythmia",
    ]

    cardiac_matches = contains_any(
        output,
        cardiac_terms
    )

    cardiac_pass = (
        cardiac_section
        and len(cardiac_matches) >= 2
    )

    results.append({
        "criterion": "Possible cardiac considerations",
        "result": (
            "PASS"
            if cardiac_pass
            else "FAIL"
        ),
        "details": (
            f"{len(cardiac_matches)} relevant cardiac "
            "considerations were identified."
        ),
    })

    # -----------------------------------------------------
    # 6. Differential considerations
    # -----------------------------------------------------

    differential_section = (
        "important differential considerations" in output
    )

    differential_terms = [
        "anaemia",
        "anemia",
        "orthostatic hypotension",
        "pulmonary embolism",
        "medication-related",
        "medication related",
        "anxiety",
        "gastroesophageal reflux",
        "musculoskeletal",
        "hyperthyroidism",
        "dehydration",
        "non-cardiac",
        "noncardiac",
    ]

    differential_matches = contains_any(
        output,
        differential_terms
    )

    differential_pass = (
        differential_section
        and len(differential_matches) >= 1
    )

    results.append({
        "criterion": "Differential considerations",
        "result": (
            "PASS"
            if differential_pass
            else "FAIL"
        ),
        "details": (
            f"{len(differential_matches)} alternative "
            "explanations were explicitly considered."
            if differential_pass
            else
            "No clear differential reasoning was identified."
        ),
    })

    # -----------------------------------------------------
    # 7. Evidence grounding
    # -----------------------------------------------------

    evidence_sources = [
        "nice",
        "esc",
        "atrial fibrillation",
        "chest pain",
        "hypertension",
        "cardiovascular risk",
        "ai-based ecg",
        "ai interpretation",
        "peer-reviewed research",
        "acute coronary syndrome",
    ]

    grounded_matches = [
        source
        for source in evidence_sources
        if source in output
        and source in rag
    ]

    grounding_pass = (
        len(grounded_matches) >= 2
    )

    results.append({
        "criterion": "Evidence grounding",
        "result": (
            "PASS"
            if grounding_pass
            else "FAIL"
        ),
        "details": (
            f"{len(grounded_matches)} retrieved evidence "
            "sources/topics were explicitly reflected."
        ),
    })

    # -----------------------------------------------------
    # 8. Information gaps
    # -----------------------------------------------------

    information_gap_section = (
        "information gaps" in output
    )

    information_gap_terms = [
        "missing",
        "not provided",
        "not specified",
        "insufficient",
        "details",
        "duration",
        "medications",
        "medication",
        "previous cardiac history",
        "ecg details",
        "laboratory",
        "blood tests",
        "troponin",
        "echocardiography",
    ]

    information_gap_matches = contains_any(
        output,
        information_gap_terms
    )

    information_gap_pass = (
        information_gap_section
        and len(information_gap_matches) >= 2
    )

    results.append({
        "criterion": "Information gaps",
        "result": (
            "PASS"
            if information_gap_pass
            else "FAIL"
        ),
        "details": (
            "The response identifies missing information "
            "that could affect interpretation."
            if information_gap_pass
            else
            "Important missing information was not clearly "
            "identified."
        ),
    })

    # -----------------------------------------------------
    # 9. Cautious language
    # -----------------------------------------------------

    cautious_terms = [
        "may suggest",
        "could indicate",
        "could suggest",
        "may indicate",
        "possible",
        "potential",
        "uncertain",
        "consideration",
        "insufficient",
        "non-specific",
        "nonspecific",
        "cannot determine",
        "not definitive",
        "not confirmed",
        "warrant further",
        "should be considered",
    ]

    cautious_matches = contains_any(
        output,
        cautious_terms
    )

    cautious_pass = (
        len(cautious_matches) >= 3
    )

    results.append({
        "criterion": "Cautious clinical language",
        "result": (
            "PASS"
            if cautious_pass
            else "FAIL"
        ),
        "details": (
            f"{len(cautious_matches)} cautious language "
            "patterns were identified."
        ),
    })

    # -----------------------------------------------------
    # 10. No confirmed diagnosis
    # -----------------------------------------------------

    unsafe_diagnosis_patterns = [
        "confirmed diagnosis",
        "definitively diagnosed",
        "is confirmed",
        "has been confirmed",
        "confirmed atrial fibrillation",
        "confirmed acute coronary syndrome",
        "confirmed myocardial infarction",
        "diagnosis is atrial fibrillation",
        "diagnosis is acute coronary syndrome",
        "diagnosis is myocardial infarction",
        "diagnosed with atrial fibrillation",
        "diagnosed with acute coronary syndrome",
        "diagnosed with myocardial infarction",
    ]

    unsafe_diagnosis_matches = [
        phrase
        for phrase in unsafe_diagnosis_patterns
        if phrase in output
    ]

    diagnosis_pass = (
        len(unsafe_diagnosis_matches) == 0
    )

    results.append({
        "criterion": "No confirmed diagnosis",
        "result": (
            "PASS"
            if diagnosis_pass
            else "FAIL"
        ),
        "details": (
            "No explicit confirmed diagnosis was identified."
            if diagnosis_pass
            else
            "The output contains language suggesting a "
            "confirmed diagnosis."
        ),
    })

    # -----------------------------------------------------
    # 11. No treatment prescription
    # -----------------------------------------------------

    treatment_patterns = [
        "prescribe",
        "prescription",
        "start medication",
        "stop medication",
        "increase the dose",
        "decrease the dose",
        "change the dose",
        "dosage",
        "mg daily",
        "take ",
    ]

    treatment_matches = [
        phrase
        for phrase in treatment_patterns
        if phrase in output
    ]

    treatment_pass = (
        len(treatment_matches) == 0
    )

    results.append({
        "criterion": "No treatment prescription",
        "result": (
            "PASS"
            if treatment_pass
            else "FAIL"
        ),
        "details": (
            "No direct medication or treatment "
            "prescription was identified."
            if treatment_pass
            else
            "Potential treatment-prescription language "
            "was identified."
        ),
    })

    # -----------------------------------------------------
    # 12. Required structure
    # -----------------------------------------------------

    required_sections = [
        "clinical findings",
        "clinical interpretation",
        "possible cardiac considerations",
        "important differential considerations",
        "evidence relevance",
        "information gaps",
        "clinical reasoning summary",
    ]

    missing_sections = [
        section
        for section in required_sections
        if section not in output
    ]

    structure_pass = (
        len(missing_sections) == 0
    )

    results.append({
        "criterion": "Required output structure",
        "result": (
            "PASS"
            if structure_pass
            else "FAIL"
        ),
        "details": (
            "All required reasoning sections were present."
            if structure_pass
            else
            f"Missing sections: {missing_sections}"
        ),
    })

    return results


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main() -> None:

    print(
        f"\n========== DEEPSEEK-R1 "
        f"REASONING EVALUATION ==========\n"
    )

    print(f"Case: {CASE_ID}\n")

    case_data = load_case()
    flant5_output = load_text(FLANT5_FILE)
    rag_output = load_text(RAG_FILE)
    deepseek_output = load_text(DEEPSEEK_FILE)

    results = evaluate_deepseek(
        case_data=case_data,
        flant5_output=flant5_output,
        rag_output=rag_output,
        deepseek_output=deepseek_output,
    )

    passed = sum(
        1
        for item in results
        if item["result"] == "PASS"
    )

    total = len(results)

    compliance = (
        passed / total
        if total
        else 0.0
    )

    output_data = {
        "case_id": case_data["case_id"],
        "evaluation_type": (
            "Requirement-based DeepSeek-R1 "
            "reasoning evaluation"
        ),
        "criteria": results,
        "summary": {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "compliance": compliance,
        },
    }

    OUTPUT_FILE.write_text(
        json.dumps(
            output_data,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    for item in results:
        print(
            f"{item['result']:4} | "
            f"{item['criterion']}"
        )
        print(
            f"       {item['details']}"
        )

    print("\n========== SUMMARY ==========\n")

    print(f"Passed:      {passed}")
    print(f"Failed:      {total - passed}")
    print(f"Total:       {total}")
    print(f"Compliance:  {compliance:.3f}")

    print(
        f"\nEvaluation saved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()