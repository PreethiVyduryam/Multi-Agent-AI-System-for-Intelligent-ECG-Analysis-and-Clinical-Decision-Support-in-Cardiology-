import os

from app.utils.config import load_env
from app.data.demo_case import build_demo_case, build_demo_profile
from app.services.gemini_client import GeminiChatModel
from app.services.assistant import CardiologyAssistant, InputValidationError
from app.db.database import initialize_database
from app.db.patient_repository import upsert_patient, save_visit, get_recent_visits
from app.services.history_service import build_history_summary


def main() -> None:
    load_env()
    initialize_database()

    patient_profile = build_demo_profile()
    patient_case = build_demo_case()

    upsert_patient(patient_profile)

    recent_visits = get_recent_visits(patient_profile.patient_id, limit=3)
    history_summary = build_history_summary(recent_visits)

    print("\n[DEBUG] Loaded patient history summary:")
    print(history_summary)
    print()

    llm = GeminiChatModel(model="gemini-2.5-flash")
    assistant = CardiologyAssistant(llm)

    try:
        report = assistant.assess_case(patient_case, history_summary=history_summary)
    except InputValidationError as e:
        print(f"Input validation error: {e}")
        return
    except Exception as e:
        print(f"Application error: {e}")
        return

    print("\n--- Structured Cardiology Support Report ---")
    print(report)
    print("-------------------------------------------")

    save_visit(patient_profile, patient_case, report)

    os.makedirs("Results", exist_ok=True)
    output_path = os.path.join("Results", "stage1_2_report.txt")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Saved report to {output_path}")


if __name__ == "__main__":
    main()