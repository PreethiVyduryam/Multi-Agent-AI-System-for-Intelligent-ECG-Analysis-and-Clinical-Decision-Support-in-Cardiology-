from flask import Blueprint, render_template, request, redirect, url_for

from app.db.database import initialize_database
from app.db.patient_repository import (
    upsert_patient,
    save_visit,
    get_recent_visits,
    get_all_visits,
    get_patient,
)
from app.models.patient import PatientProfile, PatientCase, Vitals
from app.services.assistant import CardiologyAssistant, InputValidationError
from app.services.gemini_client import GeminiChatModel
from app.services.history_service import build_history_summary
from app.utils.config import DEMO_PREFILL
from app.web.demo_data import get_demo_form_data


web_bp = Blueprint("web", __name__)


def _parse_int(value: str):
    value = (value or "").strip()
    if not value:
        return None
    return int(value)


@web_bp.route("/", methods=["GET"])
def index():
    form_data = get_demo_form_data() if DEMO_PREFILL else {}
    return render_template("index.html", form_data=form_data)


@web_bp.route("/submit", methods=["POST"])
def submit_case():
    initialize_database()

    patient_id = request.form.get("patient_id", "").strip()
    name = request.form.get("name", "").strip()
    age = _parse_int(request.form.get("age", ""))
    sex = request.form.get("sex", "").strip() or None

    symptoms_raw = request.form.get("symptoms", "").strip()
    symptoms = [s.strip() for s in symptoms_raw.split(",") if s.strip()]

    patient_state = request.form.get("patient_state", "").strip()

    medical_history_raw = request.form.get("medical_history", "").strip()
    medical_history = [m.strip() for m in medical_history_raw.split(",") if m.strip()]

    clinician_question = request.form.get("clinician_question", "").strip() or (
        "Provide a brief cardiology-focused assessment."
    )

    ecg_data = request.form.get("ecg_data", "").strip() or None

    vitals = Vitals(
        heart_rate=_parse_int(request.form.get("heart_rate", "")),
        systolic_bp=_parse_int(request.form.get("systolic_bp", "")),
        diastolic_bp=_parse_int(request.form.get("diastolic_bp", "")),
        oxygen_saturation=_parse_int(request.form.get("oxygen_saturation", "")),
    )

    profile = PatientProfile(
        patient_id=patient_id,
        name=name,
        age=age,
        sex=sex,
    )

    patient_case = PatientCase(
        symptoms=symptoms,
        patient_state=patient_state,
        medical_history=medical_history,
        clinician_question=clinician_question,
        vitals=vitals,
        ecg_data=ecg_data,
    )

    upsert_patient(profile)

    recent_visits = get_recent_visits(profile.patient_id, limit=3)
    history_summary = build_history_summary(recent_visits)

    llm = GeminiChatModel(model="gemini-2.5-flash")
    assistant = CardiologyAssistant(llm)

    try:
        report = assistant.assess_case(patient_case, history_summary=history_summary)
    except InputValidationError as e:
        return render_template(
            "report.html",
            error=f"Input validation error: {e}",
            report=None,
            patient=profile,
        )
    except Exception as e:
        return render_template(
            "report.html",
            error=f"Application error: {e}",
            report=None,
            patient=profile,
        )

    save_visit(profile, patient_case, report)

    return render_template(
        "report.html",
        error=None,
        report=report,
        patient=profile,
    )


@web_bp.route("/history/<patient_id>", methods=["GET"])
def history(patient_id: str):
    initialize_database()

    patient = get_patient(patient_id)
    visits = get_all_visits(patient_id)

    return render_template(
        "history.html",
        patient=patient,
        visits=visits,
    )