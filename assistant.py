from typing import Optional

from app.models.patient import PatientCase
from app.prompts.cardiology_prompt import (
    build_cardiology_system_prompt,
    build_cardiology_user_prompt,
)
from app.services.gemini_client import GeminiChatModel
from app.services.safety_service import apply_safety_layer
from app.tools.agent_tools import get_agent_tools


class InputValidationError(Exception):
    """Raised when the patient case input is invalid."""


class CardiologyAssistant:
    def __init__(self, llm: GeminiChatModel):
        self.llm = llm

    def validate_case(self, patient_case: PatientCase) -> None:
        if not patient_case.symptoms and not patient_case.patient_state.strip():
            raise InputValidationError(
                "At least one symptom or a patient_state description is required."
            )

        hr = patient_case.vitals.heart_rate
        if hr is not None and (hr < 20 or hr > 260):
            raise InputValidationError(
                "heart_rate looks invalid. Please enter a realistic bpm value."
            )

        sbp = patient_case.vitals.systolic_bp
        if sbp is not None and (sbp < 50 or sbp > 300):
            raise InputValidationError(
                "systolic_bp looks invalid. Please enter a realistic value."
            )

        dbp = patient_case.vitals.diastolic_bp
        if dbp is not None and (dbp < 30 or dbp > 200):
            raise InputValidationError(
                "diastolic_bp looks invalid. Please enter a realistic value."
            )

        spo2 = patient_case.vitals.oxygen_saturation
        if spo2 is not None and (spo2 < 40 or spo2 > 100):
            raise InputValidationError(
                "oxygen_saturation looks invalid. Please enter a percentage from 40 to 100."
            )

    def assess_case(self, patient_case: PatientCase, history_summary: Optional[str] = None) -> str:
        self.validate_case(patient_case)

        system_prompt = build_cardiology_system_prompt()
        user_prompt = build_cardiology_user_prompt(
            patient_case=patient_case,
            history_summary=history_summary,
        )

        tools = get_agent_tools(patient_case)

        raw_report = self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            tools=tools,
        )

        safe_report = apply_safety_layer(raw_report)
        return safe_report