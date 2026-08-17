from typing import Optional

from app.models.patient import PatientCase
from app.prompts.cardiology_prompt import (
    build_cardiology_system_prompt,
    build_cardiology_user_prompt,
)
from app.prompts.deepseek_prompt import build_deepseek_reasoning_prompt
from app.rag.evidence_service import build_evidence_context
from app.services.deepseek_client import DeepSeekClient
from app.services.flant5_client import FlanT5Client
from app.services.gemini_client import GeminiChatModel
from app.services.safety_service import apply_safety_layer
from app.tools.agent_tools import get_agent_tools


class InputValidationError(Exception):
    """Raised when the patient case input is invalid."""


class CardiologyAssistant:
    def __init__(self, llm: GeminiChatModel):
        self.llm = llm
        self.flant5 = FlanT5Client()
        self.deepseek = DeepSeekClient()

    def validate_case(self, patient_case: PatientCase) -> None:
        """Validate the structured patient input before processing."""

        if (
            not patient_case.symptoms
            and not patient_case.patient_state.strip()
        ):
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
        Run the multi-agent cardiology decision-support pipeline.

        Pipeline:
        1. FLAN-T5 clinical information extraction
        2. RAG evidence retrieval
        3. DeepSeek-R1 clinical reasoning
        4. Gemini cardiology decision-support generation
        5. Existing safety layer
        """

        self.validate_case(patient_case)

        # ---------------------------------------------------------
        # 1. FLAN-T5: Clinical Information Extraction
        # ---------------------------------------------------------
        clinical_summary = self.flant5.extract_clinical_information(
            str(patient_case)
        )

        # ---------------------------------------------------------
        # 2. RAG: Retrieve relevant clinical evidence
        # ---------------------------------------------------------
        evidence_context = build_evidence_context(patient_case)

        # ---------------------------------------------------------
        # 3. DeepSeek-R1: Clinical Reasoning
        # ---------------------------------------------------------
        deepseek_prompt = build_deepseek_reasoning_prompt(
            patient_case=str(patient_case),
            clinical_summary=clinical_summary,
            evidence_context=evidence_context,
        )

        deepseek_reasoning = self.deepseek.generate(
            system_prompt=(
                "You are the clinical reasoning agent within a "
                "multi-agent cardiology decision-support system. "
                "Use cautious, evidence-informed reasoning. "
                "Do not provide a confirmed diagnosis or prescribe treatment."
            ),
            user_prompt=deepseek_prompt,
        )

        # ---------------------------------------------------------
        # 4. Gemini: Cardiology Decision-Support Generation
        # ---------------------------------------------------------
        system_prompt = build_cardiology_system_prompt()

        base_user_prompt = build_cardiology_user_prompt(
            patient_case=patient_case,
            history_summary=history_summary,
            clinical_summary=clinical_summary,
        )

        user_prompt = f"""
{base_user_prompt}

==============================
Retrieved Clinical Evidence
==============================

{evidence_context}

==============================
DeepSeek-R1 Clinical Reasoning
==============================

{deepseek_reasoning}

==============================
Additional Instructions
==============================

- Use the retrieved evidence to support the clinical-reasoning process.
- Use the DeepSeek-R1 reasoning as an additional reasoning input.
- Relate the final response to the patient symptoms, vital signs, ECG
  information, medical history, FLAN-T5 clinical information extraction
  summary, DeepSeek-R1 reasoning, and retrieved evidence.
- Do not present any consideration as a confirmed diagnosis.
- Do not blindly repeat DeepSeek-R1 conclusions.
- Critically interpret the DeepSeek-R1 reasoning against the available
  patient information and retrieved evidence.
- Do not invent references.
- Do not claim that a source states something that is not contained in
  the retrieved evidence.
- If the evidence is limited or not directly relevant, state this clearly.
- Ensure that clinician review is recommended.
- Keep the response cautious, structured, and suitable for clinical
  decision-support.
- Include an evidence-informed reasoning section in the final report.
""".strip()

        # ---------------------------------------------------------
        # 5. Available Cardiology Tools
        # ---------------------------------------------------------
        tools = get_agent_tools(patient_case)

        # ---------------------------------------------------------
        # 6. Gemini: Generate Final Decision-Support Report
        # ---------------------------------------------------------
        raw_report = self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            tools=tools,
        )

        # ---------------------------------------------------------
        # 7. Existing Safety Layer
        # ---------------------------------------------------------
        safe_report = apply_safety_layer(raw_report)

        return safe_report