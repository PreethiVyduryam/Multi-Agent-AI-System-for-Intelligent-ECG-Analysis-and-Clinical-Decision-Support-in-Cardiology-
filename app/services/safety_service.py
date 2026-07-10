import re


DISCLAIMER_TEXT = (
    "This is not medical advice and not a confirmed diagnosis. "
    "It is decision-support information for clinical review."
)

CLINICIAN_FOLLOWUP_TEXT = (
    "A licensed clinician should review this information, confirm any diagnosis, "
    "and decide on urgent testing or treatment."
)


def prepend_disclaimer(report: str) -> str:
    if DISCLAIMER_TEXT.lower() in report.lower():
        return report
    return f"{DISCLAIMER_TEXT}\n\n{report}"


def ensure_clinician_followup(report: str) -> str:
    """
    Ensure the report explicitly tells the user that a clinician should review it.

    Important:
    Do NOT treat generic disclaimer language like 'clinical review' as sufficient.
    We only accept explicit clinician-followup wording.
    """
    followup_markers = [
        "licensed clinician",
        "doctor should review",
        "physician should review",
        "consult a doctor",
        "consult a physician",
        "seek medical evaluation",
        "seek urgent medical attention",
        "medical evaluation is recommended",
        "clinician evaluation",
        "clinician review is recommended",
    ]

    lowered = report.lower()
    if any(marker in lowered for marker in followup_markers):
        return report

    return report.rstrip() + f"\n\n{CLINICIAN_FOLLOWUP_TEXT}"


def detect_definitive_language(report: str) -> list[str]:
    risky_patterns = [
        r"\bthis is\b",
        r"\bthe diagnosis is\b",
        r"\bdefinitely\b",
        r"\bconfirmed\b",
        r"\bproves\b",
        r"\bdiagnosed with\b",
    ]

    found = []
    lowered = report.lower()

    for pattern in risky_patterns:
        if re.search(pattern, lowered):
            found.append(pattern)

    return found


def add_safety_warning_if_needed(report: str) -> str:
    risky = detect_definitive_language(report)
    if not risky:
        return report

    warning = (
        "\n\n[SAFETY NOTE] The generated text may contain wording that sounds more definitive "
        "than intended. Treat the report as provisional decision support only."
    )
    return report.rstrip() + warning


def ensure_confidence_section(report: str) -> str:
    """
    Lightweight check: if the report does not mention confidence anywhere,
    append a short safety confidence note.
    """
    if "confidence:" in report.lower():
        return report

    confidence_note = (
        "\n\nConfidence note: This report should be interpreted with low-to-moderate confidence "
        "unless supported by clinician review, formal ECG interpretation, labs, imaging, "
        "and additional history."
    )
    return report.rstrip() + confidence_note


def apply_safety_layer(report: str) -> str:
    report = prepend_disclaimer(report)
    report = ensure_clinician_followup(report)
    report = ensure_confidence_section(report)
    report = add_safety_warning_if_needed(report)
    return report