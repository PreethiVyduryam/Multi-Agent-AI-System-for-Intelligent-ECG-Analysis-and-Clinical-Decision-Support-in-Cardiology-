from app.services.history_service import build_history_summary


def test_history_summary_handles_no_visits():
    result = build_history_summary([])
    assert "No prior visit history" in result


def test_history_summary_formats_visits_cleanly():
    visits = [
        {
            "visit_timestamp": "2026-04-10 16:05:46",
            "symptoms": '["chest pain", "palpitations"]',
            "patient_state": "Intermittent chest discomfort with awareness of heartbeat.",
            "medical_history": '["anxiety", "GERD"]',
            "ecg_data": "ECG shows irregular rhythm with possible atrial fibrillation pattern.",
        }
    ]

    result = build_history_summary(visits)

    assert "Prior visit history summary:" in result
    assert "Symptoms: chest pain, palpitations" in result
    assert "History: anxiety, GERD" in result
    assert "ECG:" in result