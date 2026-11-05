
import sqlite3
from pathlib import Path
from datetime import datetime

# Project root is the parent of the src folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "investigations.db"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS investigations (
                order_id TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'Under Review',
                confirmed_amount REAL NOT NULL DEFAULT 0,
                evidence_notes TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL
            )
        """)


def save_investigation(
    order_id,
    status,
    confirmed_amount,
    evidence_notes
):
    allowed_statuses = {
        "Under Review",
        "Verified Leakage",
        "False Positive",
        "Resolved"
    }

    if status not in allowed_statuses:
        raise ValueError("Invalid investigation status.")

    if confirmed_amount < 0:
        raise ValueError("Amount cannot be negative.")

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO investigations (
                order_id,
                status,
                confirmed_amount,
                evidence_notes,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(order_id) DO UPDATE SET
                status = excluded.status,
                confirmed_amount = excluded.confirmed_amount,
                evidence_notes = excluded.evidence_notes,
                updated_at = excluded.updated_at
        """, (
            str(order_id),
            status,
            float(confirmed_amount),
            str(evidence_notes),
            datetime.now().isoformat(timespec="seconds")
        ))


def get_investigation(order_id):
    with get_connection() as connection:
        row = connection.execute("""
            SELECT *
            FROM investigations
            WHERE order_id = ?
        """, (str(order_id),)).fetchone()

    return dict(row) if row else None


def get_all_investigations():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT *
            FROM investigations
            ORDER BY updated_at DESC
        """).fetchall()

    return [dict(row) for row in rows]


initialize_database()
