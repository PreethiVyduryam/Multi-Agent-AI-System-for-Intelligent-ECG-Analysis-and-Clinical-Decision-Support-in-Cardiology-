from app.models.patient import PatientCase
from app.tools.ecg_analyzer import analyze_ecg
from app.tools.literature_search import search_literature


def analyze_ecg_tool(ecg_data: str) -> str:
    """Analyze ECG description text and return a concise cardiology-oriented ECG interpretation.

    Use this when the patient case contains ECG data or an ECG description and you need
    rhythm-related support. Do not use this if no ECG information is available.

    Args:
        ecg_data: ECG description text from the patient case.

    Returns:
        A short ECG interpretation string for decision support.
    """
    print("[TOOL CALL] analyze_ecg_tool")
    print(f"[TOOL ARG] ecg_data={ecg_data}")
    result = analyze_ecg(ecg_data)
    print("[TOOL RESULT]")
    print(result)
    return result


def search_literature_tool(query: str) -> str:
    """Search PubMed literature and return a compact evidence summary.

    Use this when guideline support, review evidence, or research grounding would improve
    the answer. Prefer focused medical search queries rather than conversational sentences.

    Args:
        query: A short, focused medical search query.

    Returns:
        A compact literature result summary with titles and abstract snippets when available.
    """
    print("[TOOL CALL] search_literature_tool")
    print(f"[TOOL ARG] query={query}")
    result = search_literature(query, retmax=8)
    print("[TOOL RESULT]")
    print(result)
    return result


def get_agent_tools(patient_case: PatientCase):
    """
    Return the list of tools the Gemini model can call.

    For now, both tools are always available to the model.
    The model should decide whether they are useful.
    """
    return [analyze_ecg_tool, search_literature_tool]