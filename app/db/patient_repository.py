import json
from dataclasses import asdict
from typing import List, Optional

from app.db.database import get_connection
from app.models.patient import PatientProfile, PatientCase


def upsert_patient(profile: PatientProfile) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO patients (patient_id, name, age, sex)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(patient_id) DO UPDATE SET
            name = excluded.name,
            age = excluded.age,
            sex = excluded.sex
        """,
        (profile.patient_id, profile.name, profile.age, profile.sex),
    )

    conn.commit()
    conn.close()


def save_visit(profile: PatientProfile, patient_case: PatientCase, generated_report: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    vitals_json = json.dumps(asdict(patient_case.vitals))
    symptoms_json = json.dumps(patient_case.symptoms)
    medical_history_json = json.dumps(patient_case.medical_history)

    cursor.execute(
        """
        INSERT INTO visits (
            patient_id,
            symptoms,
            patient_state,
            medical_history,
            clinician_question,
            vitals_json,
            ecg_data,
            generated_report
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            profile.patient_id,
            symptoms_json,
            patient_case.patient_state,
            medical_history_json,
            patient_case.clinician_question,
            vitals_json,
            patient_case.ecg_data,
            generated_report,
        ),
    )

    conn.commit()
    conn.close()


def get_recent_visits(patient_id: str, limit: int = 3) -> List[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM visits
        WHERE patient_id = ?
        ORDER BY visit_timestamp DESC, visit_id DESC
        LIMIT ?
        """,
        (patient_id, limit),
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_all_visits(patient_id: str) -> List[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM visits
        WHERE patient_id = ?
        ORDER BY visit_timestamp DESC, visit_id DESC
        """,
        (patient_id,),
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_patient(patient_id: str) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM patients
        WHERE patient_id = ?
        """,
        (patient_id,),
    )

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None