from app.rag.retriever import retrieve_evidence


def build_evidence_context(patient_case) -> str:
    """Build a retrieval query from the patient case and return evidence context."""
    query_parts: list[str] = []

    if patient_case.symptoms:
        query_parts.extend(patient_case.symptoms)

    if patient_case.patient_state:
        query_parts.append(patient_case.patient_state)

    if patient_case.medical_history:
        query_parts.extend(patient_case.medical_history)

    if patient_case.ecg_data:
        query_parts.append(patient_case.ecg_data)

    if patient_case.clinician_question:
        query_parts.append(patient_case.clinician_question)

    query = " ".join(query_parts)
    evidence_items = retrieve_evidence(query)

    if not evidence_items:
        return "No specific local evidence was retrieved for this case."

    return "\n\n".join(
        f"Retrieved Evidence {index + 1}:\n{item}"
        for index, item in enumerate(evidence_items)
    )
