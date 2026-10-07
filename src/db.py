"""
db.py - SQLite persistence layer for calculation history
All DB access is centralized here; other modules import these helpers.
"""

import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "calculator.db")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS calculation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expression TEXT NOT NULL,
    result TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def _get_conn() -> sqlite3.Connection:
    """Open a new SQLite connection with row_factory for dict-like rows."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize DB: create tables if they do not exist."""
    with _get_conn() as conn:
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()


def save_history(expression: str, result: str) -> None:
    """Persist one successful calculation record."""
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO calculation_history (expression, result) VALUES (?, ?)",
            (expression, result),
        )
        conn.commit()


def get_all_history() -> list:
    """
    Fetch all history records ordered by id DESC (newest first).
    Returns: [{'id': int, 'expression': str, 'result': str, 'created_at': str}, ...]
    """
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT id, expression, result, created_at FROM calculation_history ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def delete_history_by_id(record_id: int) -> bool:
    """Delete one record by id; returns True if a row was actually removed."""
    with _get_conn() as conn:
        cursor = conn.execute(
            "DELETE FROM calculation_history WHERE id = ?", (record_id,)
        )
        conn.commit()
        return cursor.rowcount > 0


def clear_all_history() -> None:
    """Delete every record in the history table."""
    with _get_conn() as conn:
        conn.execute("DELETE FROM calculation_history")
        conn.commit()