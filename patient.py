from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Vitals:
    heart_rate: Optional[int] = None
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    oxygen_saturation: Optional[int] = None


@dataclass
class PatientProfile:
    patient_id: str
    name: str
    age: Optional[int] = None
    sex: Optional[str] = None


@dataclass
class PatientCase:
    symptoms: List[str] = field(default_factory=list)
    patient_state: str = ""
    medical_history: List[str] = field(default_factory=list)
    clinician_question: str = "Provide a brief cardiology-focused assessment."
    vitals: Vitals = field(default_factory=Vitals)
    ecg_data: Optional[str] = None