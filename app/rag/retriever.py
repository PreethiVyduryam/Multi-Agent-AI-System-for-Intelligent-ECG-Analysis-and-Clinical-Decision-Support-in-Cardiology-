from pathlib import Path


KNOWLEDGE_BASE_DIR = Path(__file__).parent / "knowledge_base"


def retrieve_evidence(query: str, top_k: int = 3) -> list[str]:
    """Retrieve relevant local evidence snippets using simple keyword scoring."""
    query_terms = [term.lower() for term in query.split() if len(term) > 2]
    scored_documents: list[tuple[int, str]] = []

    for file_path in KNOWLEDGE_BASE_DIR.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")
        lower_text = text.lower()

        score = sum(1 for term in query_terms if term in lower_text)

        if score > 0:
            scored_documents.append((score, text))

    scored_documents.sort(reverse=True, key=lambda item: item[0])

    return [document for _, document in scored_documents[:top_k]]
