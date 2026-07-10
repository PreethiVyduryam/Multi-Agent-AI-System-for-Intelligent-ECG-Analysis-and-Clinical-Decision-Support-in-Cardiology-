import os
import sqlite3


def get_db_path() -> str:
    return os.getenv("CARDIOLOGY_AGENT_DB_PATH", "cardiology_agent.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            patient_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            sex TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS visits (
            visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            visit_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            symptoms TEXT,
            patient_state TEXT,
            medical_history TEXT,
            clinician_question TEXT,
            vitals_json TEXT,
            ecg_data TEXT,
            generated_report TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(patient_id)
        )
        """
    )

    conn.commit()
    conn.close()