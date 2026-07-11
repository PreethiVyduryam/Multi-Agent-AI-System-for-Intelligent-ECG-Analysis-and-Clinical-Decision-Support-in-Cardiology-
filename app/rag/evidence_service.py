from app.rag.retriever import retrieve_evidence


def build_evidence_context(patient_case) -> str:
    """Build a retrieval query from the patient case and return formatted evidence."""

    query_parts = []

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
        return "No relevant evidence was retrieved."

    formatted_items = []

    for item in evidence_items:

        formatted_items.append(
            f"""
Title: {item['title']}

Organisation: {item['organisation']}

Year: {item['year']}

Topic: {item['topic']}

Summary:
{item['summary']}
"""
        )

    return "\n\n----------------------------------------\n\n".join(formatted_items)