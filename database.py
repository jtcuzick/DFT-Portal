import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).resolve().parent / "dft_requests.db"

VALID_STATUSES = [
    "Submitted",
    "Reviewing",
    "Needs clarification",
    "Queued",
    "Running",
    "Analysis",
    "Complete",
    "Failed",
]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submitted_by TEXT NOT NULL,
                email TEXT,
                project TEXT,
                molecule_name TEXT NOT NULL,
                calculation_type TEXT NOT NULL,
                scientific_question TEXT NOT NULL,
                charge INTEGER,
                multiplicity INTEGER,
                method_preference TEXT,
                basis_set TEXT,
                solvent TEXT,
                status TEXT NOT NULL DEFAULT 'Submitted',
                admin_notes TEXT,
                cluster_job_id TEXT,
                uploaded_file TEXT,
                result_file TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def create_request(
    submitted_by: str,
    email: str,
    project: str,
    molecule_name: str,
    calculation_type: str,
    scientific_question: str,
    charge: int,
    multiplicity: int,
    method_preference: str,
    basis_set: str,
    solvent: str,
    uploaded_file: Optional[str] = None,
):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO requests (
                submitted_by,
                email,
                project,
                molecule_name,
                calculation_type,
                scientific_question,
                charge,
                multiplicity,
                method_preference,
                basis_set,
                solvent,
                uploaded_file
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                submitted_by,
                email,
                project,
                molecule_name,
                calculation_type,
                scientific_question,
                charge,
                multiplicity,
                method_preference,
                basis_set,
                solvent,
                uploaded_file,
            ),
        )
        conn.commit()
        return cursor.lastrowid


def get_all_requests():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM requests
            ORDER BY
                CASE status
                    WHEN 'Submitted' THEN 1
                    WHEN 'Reviewing' THEN 2
                    WHEN 'Needs clarification' THEN 3
                    WHEN 'Queued' THEN 4
                    WHEN 'Running' THEN 5
                    WHEN 'Analysis' THEN 6
                    WHEN 'Failed' THEN 7
                    WHEN 'Complete' THEN 8
                    ELSE 9
                END,
                submitted_at DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def get_request(request_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM requests WHERE id = ?",
            (request_id,),
        ).fetchone()
    return dict(row) if row else None


def update_request(
    request_id: int,
    status: str,
    admin_notes: str,
    cluster_job_id: str,
):
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}")

    with get_connection() as conn:
        conn.execute(
            """
            UPDATE requests
            SET status = ?,
                admin_notes = ?,
                cluster_job_id = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (status, admin_notes, cluster_job_id, request_id),
        )
        conn.commit()


def get_request_counts():
    counts = {status: 0 for status in VALID_STATUSES}

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM requests
            GROUP BY status
            """
        ).fetchall()

    for row in rows:
        counts[row["status"]] = row["count"]

    return counts
