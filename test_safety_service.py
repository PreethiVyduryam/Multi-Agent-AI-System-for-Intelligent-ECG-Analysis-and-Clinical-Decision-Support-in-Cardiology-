from app.services.safety_service import (
    DISCLAIMER_TEXT,
    CLINICIAN_FOLLOWUP_TEXT,
    prepend_disclaimer,
    ensure_clinician_followup,
    ensure_confidence_section,
    detect_definitive_language,
    add_safety_warning_if_needed,
    apply_safety_layer,
)


def test_prepend_disclaimer_adds_text():
    report = "1. Possible cardiac considerations\n- Possible AF"
    result = prepend_disclaimer(report)
    assert DISCLAIMER_TEXT in result


def test_ensure_clinician_followup_adds_note():
    report = "1. Possible cardiac considerations\n- Possible AF"
    result = ensure_clinician_followup(report)
    assert CLINICIAN_FOLLOWUP_TEXT in result


def test_ensure_confidence_section_adds_note_when_missing():
    report = "1. Possible cardiac considerations\n- Possible AF"
    result = ensure_confidence_section(report)
    assert "Confidence note:" in result


def test_detect_definitive_language_finds_risky_phrases():
    report = "This is atrial fibrillation. The diagnosis is confirmed."
    risky = detect_definitive_language(report)
    assert len(risky) > 0


def test_add_safety_warning_if_needed_appends_warning():
    report = "This is atrial fibrillation."
    result = add_safety_warning_if_needed(report)
    assert "[SAFETY NOTE]" in result


def test_apply_safety_layer_adds_required_safety_elements():
    report = "1. Possible cardiac considerations\n- Possible AF"
    result = apply_safety_layer(report)

    assert DISCLAIMER_TEXT in result
    assert "Confidence note:" in result
    assert (
        CLINICIAN_FOLLOWUP_TEXT in result
        or "licensed clinician" in result.lower()
        or "medical evaluation" in result.lower()
    )