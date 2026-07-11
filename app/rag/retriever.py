import json
from pathlib import Path


KNOWLEDGE_BASE_DIR = Path(__file__).parent / "knowledge_base"


def retrieve_evidence(query: str, top_k: int = 3) -> list[dict]:
    """
    Retrieve relevant evidence from the local knowledge base.
    Searches NICE, ESC, and Research folders.
    """

    query_terms = [term.lower() for term in query.split() if len(term) > 2]
    scored_documents = []

    json_files = KNOWLEDGE_BASE_DIR.rglob("*.json")

    for file_path in json_files:

        with open(file_path, "r", encoding="utf-8") as file:
            document = json.load(file)

        searchable_text = " ".join([
            document.get("title", ""),
            document.get("topic", ""),
            " ".join(document.get("keywords", [])),
            document.get("summary", "")
        ]).lower()

        score = sum(
            1
            for term in query_terms
            if term in searchable_text
        )

        if score > 0:
            scored_documents.append((score, document))

    scored_documents.sort(
        reverse=True,
        key=lambda item: item[0]
    )

    return [
        document
        for _, document in scored_documents[:top_k]
    ]