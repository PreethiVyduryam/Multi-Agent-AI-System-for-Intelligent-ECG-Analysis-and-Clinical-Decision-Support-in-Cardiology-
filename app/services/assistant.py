from typing import Optional

from app.models.patient import PatientCase
from app.prompts.cardiology_prompt import (
    build_cardiology_system_prompt,
    build_cardiology_user_prompt,
)
from app.rag.evidence_service import build_evidence_context
from app.services.gemini_client import GeminiChatModel
from app.services.safety_service import apply_safety_layer
from app.tools.agent_tools import get_agent_tools


class InputValidationError(Exception):
    """Raised when the patient case input is invalid."""


class CardiologyAssistant:
    def __init__(self, llm: GeminiChatModel):
        self.llm = llm

    def validate_case(self, patient_case: PatientCase) -> None:
        """Validate the structured patient input before processing."""

        if not patient_case.symptoms and not patient_case.patient_state.strip():
            raise InputValidationError(
                "At least one symptom or a patient_state description is required."
            )

        heart_rate = patient_case.vitals.heart_rate
        if heart_rate is not None and not 20 <= heart_rate <= 260:
            raise InputValidationError(
                "heart_rate looks invalid. Please enter a realistic bpm value."
            )

        systolic_bp = patient_case.vitals.systolic_bp
        if systolic_bp is not None and not 50 <= systolic_bp <= 300:
            raise InputValidationError(
                "systolic_bp looks invalid. Please enter a realistic value."
            )

        diastolic_bp = patient_case.vitals.diastolic_bp
        if diastolic_bp is not None and not 30 <= diastolic_bp <= 200:
            raise InputValidationError(
                "diastolic_bp looks invalid. Please enter a realistic value."
            )

        oxygen_saturation = patient_case.vitals.oxygen_saturation
        if oxygen_saturation is not None and not 40 <= oxygen_saturation <= 100:
            raise InputValidationError(
                "oxygen_saturation looks invalid. "
                "Please enter a percentage from 40 to 100."
            )

    def assess_case(
        self,
        patient_case: PatientCase,
        history_summary: Optional[str] = None,
    ) -> str:
        """
        Validate the case, retrieve local clinical evidence, generate a
        cardiology decision-support report, and apply the safety layer.
        """

        self.validate_case(patient_case)

        system_prompt = build_cardiology_system_prompt()

        base_user_prompt = build_cardiology_user_prompt(
            patient_case=patient_case,
            history_summary=history_summary,
        )

        evidence_context = build_evidence_context(patient_case)

        user_prompt = f"""
{base_user_prompt}

==============================
Retrieved Clinical Evidence
==============================

{evidence_context}

Additional instructions:

- Use the retrieved evidence to support the clinical-reasoning process.
- Relate recommendations to the patient symptoms, vital signs, ECG report,
  medical history, and retrieved evidence.
- Do not present any consideration as a confirmed diagnosis.
- Do not invent references or claim that a source states something that is
  not contained in the retrieved evidence.
- If the evidence is limited or not directly relevant, state this clearly.
- Ensure that clinician review is recommended.
- Include an evidence-informed reasoning section in the final report.
""".strip()

        tools = get_agent_tools(patient_case)

        raw_report = self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            tools=tools,
        )

        safe_report = apply_safety_layer(raw_report)

        return safe_report