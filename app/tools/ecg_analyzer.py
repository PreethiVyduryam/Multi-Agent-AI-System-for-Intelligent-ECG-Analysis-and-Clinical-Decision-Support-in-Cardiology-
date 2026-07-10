def analyze_ecg(ecg_data: str) -> str:
    """
    Mock ECG analyzer for Stage 3.

    This simulates an external ECG tool. Later, this can be replaced with:
    - a real ML model
    - a waveform parser
    - an API call
    """

    ecg_text = ecg_data.lower().strip()

    if not ecg_text:
        return "ECG tool result: No ECG data provided."

    if "normal sinus rhythm" in ecg_text:
        return (
            "ECG tool result: Normal sinus rhythm mentioned. "
            "No obvious rhythm abnormality is suggested by the provided ECG description."
        )

    if "irregular" in ecg_text or "atrial fibrillation" in ecg_text or "afib" in ecg_text:
        return (
            "ECG tool result: Possible rhythm irregularity detected from the provided ECG description. "
            "Atrial fibrillation or another arrhythmia may need consideration."
        )

    if "tachycardia" in ecg_text or "fast heart rate" in ecg_text:
        return (
            "ECG tool result: Tachycardia-related wording detected. "
            "The ECG description may suggest an elevated heart rate that could need correlation with symptoms and vitals."
        )

    if "bradycardia" in ecg_text or "slow heart rate" in ecg_text:
        return (
            "ECG tool result: Bradycardia-related wording detected. "
            "The ECG description may suggest a slower heart rate that may need clinical correlation."
        )

    return (
        "ECG tool result: ECG description is present but the mock analyzer could not classify it clearly. "
        "Treat this as inconclusive ECG support information."
    )