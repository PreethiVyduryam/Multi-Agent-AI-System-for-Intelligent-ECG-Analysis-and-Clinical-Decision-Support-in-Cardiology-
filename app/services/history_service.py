import json
from typing import List


def _safe_load_json_list(value: str) -> list:
    try:
        data = json.loads(value)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _shorten_text(text: str, max_len: int = 100) -> str:
    if not text:
        return ""
    text = " ".join(text.split())
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def build_history_summary(recent_visits: List[dict]) -> str:
    if not recent_visits:
        return "No prior visit history is available for this patient."

    lines = ["Prior visit history summary:"]

    # Oldest first for readability
    for visit in reversed(recent_visits):
        symptoms = _safe_load_json_list(visit.get("symptoms", "[]"))
        medical_history = _safe_load_json_list(visit.get("medical_history", "[]"))

        visit_time = visit.get("visit_timestamp", "Unknown date")
        patient_state = _shorten_text(visit.get("patient_state", ""), max_len=80)
        ecg_data = _shorten_text(visit.get("ecg_data", ""), max_len=80)

        symptom_text = ", ".join(symptoms[:3]) if symptoms else "No symptoms recorded"
        history_text = ", ".join(medical_history[:3]) if medical_history else "No medical history recorded"

        summary_parts = [
            f"Visit on {visit_time}",
            f"Symptoms: {symptom_text}",
        ]

        if patient_state:
            summary_parts.append(f"State: {patient_state}")

        if history_text:
            summary_parts.append(f"History: {history_text}")

        if ecg_data:
            summary_parts.append(f"ECG: {ecg_data}")

        lines.append("- " + ". ".join(summary_parts) + ".")

    return "\n".join(lines)