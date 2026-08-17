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

if len(sys.argv) != 2:
    print(
        "Usage: python evaluation/scripts/"
        "evaluate_deepseek_metrics.py case_001"
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

    with CASE_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
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

    text = str(text).lower()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ---------------------------------------------------------
# Utility
# ---------------------------------------------------------

def contains_any(
    text: str,
    terms: list[str],
) -> bool:

    return any(
        term.lower() in text
        for term in terms
    )


def matched_terms(
    text: str,
    terms: list[str],
) -> list[str]:

    return [
        term
        for term in terms
        if term.lower() in text
    ]


# ---------------------------------------------------------
# Evaluation
# ---------------------------------------------------------

def evaluate_deepseek(
    case_data: dict,
    flant5_output: str,
    rag_output: str,
    deepseek_output: str,
) -> list[dict]:

    output = normalise_text(
        deepseek_output
    )

    case = case_data["patient_information"]

    results = []


    # =====================================================
    # 1. Patient information usage
    # =====================================================

    required_patient_facts = [
        str(case["age"]),

        "female"
        if case["sex"].upper() == "F"
        else "male",

        *[
            str(item).lower()
            for item in case.get(
                "symptoms",
                []
            )
        ],

        str(
            case.get(
                "patient_state",
                ""
            )
        ).lower(),

        *[
            str(item).lower()
            for item in case.get(
                "medical_history",
                []
            )
        ],

        str(
            case.get(
                "ecg_data",
                ""
            )
        ).lower(),
    ]

    # Remove empty values
    required_patient_facts = [
        fact
        for fact in required_patient_facts
        if fact
    ]

    matched_facts = [
        fact
        for fact in required_patient_facts
        if fact in output
    ]

    patient_pass = (
        len(matched_facts)
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
            f"{len(required_patient_facts)} "
            "key patient facts were reflected "
            "in the output."
        ),
    })


    # =====================================================
    # 2. FLAN-T5 integration
    # =====================================================

    flant5_terms = []

    flant5_normalised = normalise_text(
        flant5_output
    )

    # Extract useful clinical terms from FLAN-T5
    clinical_terms = [
        "chest pain",
        "chest discomfort",
        "palpitations",
        "irregular heartbeat",
        "irregular rhythm",
        "shortness of breath",
        "breathlessness",
        "dizziness",
        "light-headedness",
        "lightheadedness",
        "premature beats",
        "sinus rhythm",
        "arrhythmia",
        "atrial fibrillation",
        "ecg",
    ]

    for term in clinical_terms:

        if term in flant5_normalised:
            flant5_terms.append(term)

    flant5_matches = [
        term
        for term in flant5_terms
        if term in output
    ]

    flant5_pass = (
        len(flant5_matches) > 0
    )

    results.append({
        "criterion": "FLAN-T5 information integration",
        "result": (
            "PASS"
            if flant5_pass
            else "FAIL"
        ),
        "details": (
            "The DeepSeek output reflects "
            "information provided by the "
            "FLAN-T5 stage."
            if flant5_pass
            else
            "No clear use of the FLAN-T5 "
            "information was identified."
        ),
    })


    # =====================================================
    # 3. RAG evidence integration
    # =====================================================

    evidence_terms = [
        "nice",
        "esc",
        "guideline",
        "atrial fibrillation",
        "12-lead ecg",
        "ambulatory",
        "holter",
        "troponin",
        "acute coronary syndrome",
        "hypertension",
        "cardiovascular risk",
        "heart failure",
        "ecg",
        "arrhythmia",
    ]

    evidence_matches = matched_terms(
        output,
        evidence_terms
    )

    rag_pass = (
        len(evidence_matches) >= 3
    )

    results.append({
        "criterion": "RAG evidence integration",
        "result": (
            "PASS"
            if rag_pass
            else "FAIL"
        ),
        "details": (
            f"{len(evidence_matches)} relevant "
            "evidence terms/concepts were "
            "reflected in the output."
        ),
    })


    # =====================================================
    # 4. Clinical reasoning
    # =====================================================

    reasoning_terms = [
        "may suggest",
        "may indicate",
        "could suggest",
        "could indicate",
        "could be",
        "consistent with",
        "because",
        "however",
        "therefore",
        "reason:",
        "in this context",
        "warrant",
        "consideration",
        "risk",
    ]

    reasoning_matches = matched_terms(
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
            "The response connects patient "
            "findings and provides explanatory "
            "clinical reasoning."
            if reasoning_pass
            else
            "Limited evidence of structured "
            "clinical reasoning."
        ),
    })


    # =====================================================
    # 5. Possible cardiac considerations
    # =====================================================

    cardiac_section = contains_any(
        output,
        [
            "possible cardiac considerations",
            "possible cardiac causes",
            "cardiac considerations",
            "clinical considerations",
        ],
    )

    cardiac_terms = [
        "atrial fibrillation",
        "acute coronary syndrome",
        "arrhythmia",
        "ectopy",
        "coronary artery disease",
        "myocardial ischaemia",
        "myocardial ischemia",
        "heart failure",
        "hypertensive heart disease",
    ]

    cardiac_matches = matched_terms(
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
            f"{len(cardiac_matches)} relevant "
            "cardiac considerations were "
            "identified."
        ),
    })


    # =====================================================
    # 6. Differential considerations
    # =====================================================

    differential_section = contains_any(
        output,
        [
            "important differential considerations",
            "differential considerations",
            "differential diagnosis",
            "alternative explanations",
            "non-cardiac causes",
        ],
    )

    differential_terms = [
        "anaemia",
        "anemia",
        "orthostatic hypotension",
        "pulmonary embolism",
        "medication-related",
        "medication",
        "anxiety",
        "gastroesophageal reflux",
        "musculoskeletal",
        "hyperthyroidism",
        "non-cardiac",
        "noncardiac",
    ]

    differential_matches = matched_terms(
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
            "Alternative explanations were "
            "explicitly considered."
            if differential_pass
            else
            "No clear differential reasoning "
            "was identified."
        ),
    })


    # =====================================================
    # 7. Evidence grounding
    # =====================================================

    evidence_sources = [
        "nice",
        "esc",
        "atrial fibrillation",
        "chest pain",
        "hypertension",
        "cardiovascular risk",
    ]

    grounded_matches = matched_terms(
        output,
        evidence_sources
    )

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
            f"{len(grounded_matches)} retrieved "
            "evidence sources/topics were "
            "explicitly reflected."
        ),
    })


    # =====================================================
    # 8. Information gaps
    # =====================================================

    information_gap_terms = [
        "information gaps",
        "missing",
        "not provided",
        "insufficient information",
        "details are missing",
        "further assessment",
    ]

    information_gap_matches = matched_terms(
        output,
        information_gap_terms
    )

    information_gap_pass = (
        len(information_gap_matches) >= 1
    )

    results.append({
        "criterion": "Information gaps",
        "result": (
            "PASS"
            if information_gap_pass
            else "FAIL"
        ),
        "details": (
            "The response identifies missing "
            "information that could affect "
            "interpretation."
            if information_gap_pass
            else
            "No clear information gaps were "
            "identified."
        ),
    })


    # =====================================================
    # 9. Cautious clinical language
    # =====================================================

    cautious_terms = [
        "may",
        "could",
        "possible",
        "suggest",
        "consider",
        "cannot exclude",
        "not definitive",
        "insufficient",
        "uncertain",
        "warrant",
        "requires",
        "should be considered",
    ]

    cautious_matches = matched_terms(
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
            f"{len(cautious_matches)} cautious "
            "language patterns were identified."
        ),
    })


    # =====================================================
    # 10. No confirmed diagnosis
    # =====================================================

    confirmed_diagnosis_patterns = [
        r"\bdiagnosis is\b",
        r"\bdiagnosed with\b",
        r"\bconfirmed\b",
        r"\bhas atrial fibrillation\b",
        r"\bhas acute coronary syndrome\b",
        r"\bhas heart failure\b",
        r"\bdefinitively\b",
        r"\bthis is atrial fibrillation\b",
        r"\bthis is acute coronary syndrome\b",
    ]

    confirmed_matches = [
        pattern
        for pattern in confirmed_diagnosis_patterns
        if re.search(
            pattern,
            output
        )
    ]

    no_confirmed_diagnosis_pass = (
        len(confirmed_matches) == 0
    )

    results.append({
        "criterion": "No confirmed diagnosis",
        "result": (
            "PASS"
            if no_confirmed_diagnosis_pass
            else "FAIL"
        ),
        "details": (
            "No language suggesting a confirmed "
            "diagnosis was identified."
            if no_confirmed_diagnosis_pass
            else
            "The output contains language "
            "suggesting a confirmed diagnosis."
        ),
    })


    # =====================================================
    # 11. No treatment prescription
    # =====================================================

    prescription_patterns = [
        r"\bstart\b.{0,40}\bmedication\b",
        r"\bstart\b.{0,40}\bdrug\b",
        r"\bprescribe\b",
        r"\bprescription\b",
        r"\btake\b.{0,30}\bmg\b",
        r"\bincrease\b.{0,30}\bdose\b",
        r"\bdecrease\b.{0,30}\bdose\b",
        r"\binitiate\b.{0,40}\btherapy\b",
    ]

    prescription_matches = [
        pattern
        for pattern in prescription_patterns
        if re.search(
            pattern,
            output
        )
    ]

    no_treatment_pass = (
        len(prescription_matches) == 0
    )

    results.append({
        "criterion": "No treatment prescription",
        "result": (
            "PASS"
            if no_treatment_pass
            else "FAIL"
        ),
        "details": (
            "No direct medication or treatment "
            "prescription was identified."
            if no_treatment_pass
            else
            "The output contains possible "
            "treatment-prescribing language."
        ),
    })


    # =====================================================
    # 12. Required output structure
    # =====================================================

    required_sections = [
        "clinical findings",
        "clinical interpretation",
        "possible cardiac considerations",
        "information gaps",
        "clinical reasoning summary",
    ]

    section_matches = [
        section
        for section in required_sections
        if section in output
    ]

    structure_pass = (
        len(section_matches)
        == len(required_sections)
    )

    results.append({
        "criterion": "Required output structure",
        "result": (
            "PASS"
            if structure_pass
            else "FAIL"
        ),
        "details": (
            "All required reasoning sections "
            "were present."
            if structure_pass
            else
            f"{len(section_matches)}/"
            f"{len(required_sections)} required "
            "reasoning sections were present."
        ),
    })


    return results


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print(
        f"\n========== DEEPSEEK-R1 "
        f"REASONING EVALUATION ==========\n"
    )

    print(
        f"Case: {CASE_ID}\n"
    )

    case_data = load_case()

    flant5_output = load_text(
        FLANT5_FILE
    )

    rag_output = load_text(
        RAG_FILE
    )

    deepseek_output = load_text(
        DEEPSEEK_FILE
    )

    results = evaluate_deepseek(
        case_data,
        flant5_output,
        rag_output,
        deepseek_output,
    )

    passed = sum(
        result["result"] == "PASS"
        for result in results
    )

    failed = sum(
        result["result"] == "FAIL"
        for result in results
    )

    total = len(results)

    compliance = (
        passed / total
        if total
        else 0
    )

    for result in results:

        print(
            f"{result['result']} | "
            f"{result['criterion']}"
        )

        print(
            f"       {result['details']}"
        )

    print(
        "\n========== SUMMARY ==========\n"
    )

    print(
        f"Passed:      {passed}"
    )

    print(
        f"Failed:      {failed}"
    )

    print(
        f"Total:       {total}"
    )

    print(
        f"Compliance:  {compliance:.3f}"
    )

    output_data = {
        "case": CASE_ID,
        "model": "DeepSeek-R1",
        "passed": passed,
        "failed": failed,
        "total": total,
        "compliance": compliance,
        "results": results,
    }

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output_data,
            file,
            indent=2,
        )

    print(
        "\nEvaluation saved to:"
    )

    print(
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()