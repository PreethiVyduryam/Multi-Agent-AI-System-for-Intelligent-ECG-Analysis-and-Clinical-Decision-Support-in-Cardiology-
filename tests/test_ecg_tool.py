from app.tools.ecg_analyzer import analyze_ecg


def test_ecg_tool_detects_normal_sinus_rhythm():
    result = analyze_ecg("ECG: Normal sinus rhythm.")
    assert "Normal sinus rhythm" in result


def test_ecg_tool_detects_possible_arrhythmia():
    result = analyze_ecg("ECG shows irregular rhythm with possible atrial fibrillation.")
    assert "Possible rhythm irregularity" in result or "Atrial fibrillation" in result


def test_ecg_tool_detects_tachycardia():
    result = analyze_ecg("ECG suggests tachycardia with fast heart rate.")
    assert "Tachycardia" in result or "elevated heart rate" in result


def test_ecg_tool_handles_unclear_input():
    result = analyze_ecg("ECG is difficult to interpret.")
    assert "could not classify" in result or "inconclusive" in result.lower()