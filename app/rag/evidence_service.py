from app.rag.retriever import retrieve_evidence


def build_evidence_context(patient_case) -> str:
    """
    Build a retrieval query from the patient case and
    return formatted evidence for downstream agents.
    """

    query_parts = []

    if patient_case.symptoms:
        query_parts.extend(
            patient_case.symptoms
        )

    if patient_case.patient_state:
        query_parts.append(
            patient_case.patient_state
        )

    if patient_case.medical_history:
        query_parts.extend(
            patient_case.medical_history
        )

    if patient_case.ecg_data:
        query_parts.append(
            patient_case.ecg_data
        )

    if patient_case.clinician_question:
        query_parts.append(
            patient_case.clinician_question
        )

    query = " ".join(query_parts)

    evidence_items = retrieve_evidence(
        query,
        top_k=3,
    )

    if not evidence_items:
        return (
            "No relevant evidence was retrieved "
            "from the local knowledge base."
        )

    formatted_items = []

    for item in evidence_items:

        matched_terms = item.get(
            "_matched_terms",
            [],
        )

        retrieval_score = item.get(
            "_retrieval_score",
            0,
        )

        formatted_items.append(
            f"""
Title: {item.get('title', 'Unknown')}

Organisation: {item.get('organisation', 'Unknown')}

Year: {item.get('year', 'Unknown')}

Topic: {item.get('topic', 'Unknown')}

Retrieval Score:
{retrieval_score}

Matched Clinical Terms:
{", ".join(matched_terms) if matched_terms else "None"}

Summary:
{item.get('summary', 'No summary available.')}
""".strip()
        )

    return (
        "\n\n"
        "----------------------------------------"
        "\n\n"
    ).join(
        formatted_items
    )
