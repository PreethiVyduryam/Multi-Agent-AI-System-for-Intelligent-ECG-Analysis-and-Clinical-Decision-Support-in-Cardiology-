import json
import re
from pathlib import Path


KNOWLEDGE_BASE_DIR = Path(__file__).parent / "knowledge_base"


# ---------------------------------------------------------
# Generic words that should not influence retrieval
# ---------------------------------------------------------

STOP_WORDS = {
    "and",
    "the",
    "this",
    "that",
    "with",
    "from",
    "into",
    "for",
    "patient",
    "patients",
    "clinical",
    "assessment",
    "management",
    "individual",
    "provide",
    "brief",
    "cardiology",
    "focused",
}


# ---------------------------------------------------------
# Clinical synonym / concept expansion
# ---------------------------------------------------------

CLINICAL_SYNONYMS = {

    "shortness of breath": [
        "breathlessness",
        "dyspnea",
        "dyspnoea",
        "heart failure",
    ],

    "shortness breath": [
        "breathlessness",
        "dyspnea",
        "dyspnoea",
        "heart failure",
    ],

    "dizziness": [
        "lightheadedness",
        "light-headedness",
        "presyncope",
        "arrhythmia",
    ],

    "light-headedness": [
        "dizziness",
        "lightheadedness",
        "presyncope",
        "arrhythmia",
    ],

    "light headedness": [
        "dizziness",
        "lightheadedness",
        "presyncope",
        "arrhythmia",
    ],

    "premature beats": [
        "ectopy",
        "ectopic beats",
        "arrhythmia",
        "palpitations",
    ],

    "premature beat": [
        "ectopy",
        "ectopic beats",
        "arrhythmia",
        "palpitations",
    ],

    "irregular heartbeat": [
        "irregular rhythm",
        "arrhythmia",
        "atrial fibrillation",
        "palpitations",
    ],

    "irregular rhythm": [
        "irregular heartbeat",
        "arrhythmia",
        "atrial fibrillation",
        "palpitations",
    ],

    "palpitation": [
        "palpitations",
        "arrhythmia",
        "irregular heartbeat",
    ],

    "chest discomfort": [
        "chest pain",
        "angina",
        "acute coronary syndrome",
        "myocardial infarction",
    ],

    "chest pain": [
        "chest discomfort",
        "angina",
        "acute coronary syndrome",
        "myocardial infarction",
    ],

    "high blood pressure": [
        "hypertension",
        "blood pressure",
    ],

    "high cholesterol": [
        "hyperlipidaemia",
        "hyperlipidemia",
        "cardiovascular risk",
    ],

    "hyperlipidaemia": [
        "hyperlipidemia",
        "cardiovascular risk",
    ],

    "hyperlipidemia": [
        "hyperlipidaemia",
        "cardiovascular risk",
    ],
}


# ---------------------------------------------------------
# Text normalisation
# ---------------------------------------------------------

def normalise_text(text: str) -> str:
    """
    Normalise text for reliable matching.
    """

    text = str(text).lower()

    text = re.sub(
        r"[^a-z0-9\s-]",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ---------------------------------------------------------
# Query expansion
# ---------------------------------------------------------

def expand_query(query: str) -> set[str]:
    """
    Expand the clinical query using related terminology.

    Generic stop words are excluded so that common words
    do not artificially increase retrieval scores.
    """

    query_text = normalise_text(query)

    expanded_terms = {
        term
        for term in query_text.split()
        if len(term) >= 3
        and term not in STOP_WORDS
    }

    for phrase, related_terms in CLINICAL_SYNONYMS.items():

        if phrase in query_text:

            expanded_terms.add(
                normalise_text(phrase)
            )

            for related_term in related_terms:

                expanded_terms.add(
                    normalise_text(related_term)
                )

    return expanded_terms


# ---------------------------------------------------------
# Retrieval
# ---------------------------------------------------------

def retrieve_evidence(
    query: str,
    top_k: int = 3,
) -> list[dict]:
    """
    Retrieve relevant evidence from the local knowledge base.

    Retrieval combines:

    1. Exact clinical keyword matching
    2. Clinical synonym / concept expansion
    3. Topic matching
    4. Title matching
    5. General searchable-text matching
    6. Targeted ECG/rhythm relevance

    Generic words are excluded from scoring.

    The returned documents include retrieval metadata
    for transparency and evaluation.
    """

    query_text = normalise_text(query)

    query_terms = expand_query(query)

    scored_documents = []

    # -----------------------------------------------------
    # Detect ECG / rhythm concepts in the patient query
    # -----------------------------------------------------

    rhythm_terms_present = any(
        phrase in query_text
        for phrase in [
            "premature beats",
            "premature beat",
            "irregular heartbeat",
            "irregular rhythm",
            "palpitations",
            "palpitation",
            "arrhythmia",
        ]
    )

    ecg_present = (
        "ecg" in query_terms
        or "electrocardiogram" in query_text
        or "electrocardiography" in query_text
    )

    # -----------------------------------------------------
    # Search knowledge base
    # -----------------------------------------------------

    for file_path in KNOWLEDGE_BASE_DIR.rglob("*.json"):

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:
            document = json.load(file)

        title = normalise_text(
            document.get("title", "")
        )

        topic = normalise_text(
            document.get("topic", "")
        )

        keywords = [
            normalise_text(keyword)
            for keyword in document.get(
                "keywords",
                [],
            )
        ]

        summary = normalise_text(
            document.get("summary", "")
        )

        searchable_text = " ".join(
            [
                title,
                topic,
                " ".join(keywords),
                summary,
            ]
        )

        score = 0
        matched_terms = []

        # -------------------------------------------------
        # Exact clinical keyword / phrase matching
        # -------------------------------------------------

        for keyword in keywords:

            if not keyword:
                continue

            if keyword in query_text:

                score += 8

                matched_terms.append(
                    keyword
                )

        # -------------------------------------------------
        # Expanded clinical concept matching
        # -------------------------------------------------

        for keyword in keywords:

            if not keyword:
                continue

            if keyword in query_terms:

                score += 6

                matched_terms.append(
                    keyword
                )

        # -------------------------------------------------
        # Topic matching
        # -------------------------------------------------

        for topic_term in topic.split():

            if (
                len(topic_term) >= 3
                and topic_term not in STOP_WORDS
                and topic_term in query_terms
            ):

                score += 4

                matched_terms.append(
                    topic_term
                )

        # -------------------------------------------------
        # Title matching
        # -------------------------------------------------

        for title_term in title.split():

            if (
                len(title_term) >= 3
                and title_term not in STOP_WORDS
                and title_term in query_terms
            ):

                score += 2

                matched_terms.append(
                    title_term
                )

        # -------------------------------------------------
        # General searchable-text matching
        # -------------------------------------------------

        for term in query_terms:

            if (
                len(term) >= 3
                and term in searchable_text
            ):

                score += 1

                matched_terms.append(
                    term
                )

        # -------------------------------------------------
        # Targeted ECG / rhythm relevance
        # -------------------------------------------------

        document_ecg_terms = [
            "ecg",
            "arrhythmia",
            "electrocardiography",
            "atrial fibrillation",
            "palpitations",
            "premature beats",
            "ectopy",
        ]

        document_is_ecg_related = any(
            term in searchable_text
            for term in document_ecg_terms
        )

        if (
            rhythm_terms_present
            and document_is_ecg_related
        ):

            score += 5

            matched_terms.append(
                "rhythm relevance"
            )

        elif (
            ecg_present
            and document_is_ecg_related
        ):

            score += 3

            matched_terms.append(
                "ECG relevance"
            )

        # -------------------------------------------------
        # Remove duplicate matched terms
        # -------------------------------------------------

        matched_terms = sorted(
            set(matched_terms)
        )

        # -------------------------------------------------
        # Keep meaningful matches only
        # -------------------------------------------------

        if score >= 3:

            document_copy = dict(
                document
            )

            document_copy[
                "_retrieval_score"
            ] = score

            document_copy[
                "_matched_terms"
            ] = matched_terms

            scored_documents.append(
                (
                    score,
                    document_copy,
                )
            )

    # -----------------------------------------------------
    # Rank highest relevance first
    # -----------------------------------------------------

    scored_documents.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        document
        for _, document
        in scored_documents[:top_k]
    ]