from __future__ import annotations

import sqlite3
import os
from datetime import datetime
from typing import List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "aidloop.db")


def get_connection() -> sqlite3.Connection:
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    """Create the requirements table if it doesn't exist."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            quantity TEXT NOT NULL,
            raiser_name TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'open',
            fulfiller_name TEXT DEFAULT '',
            proof_path TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fulfilled_at TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def insert_requirement(item_name: str, quantity: str, raiser_name: str = "") -> int:
    """Insert a new open requirement. Returns the inserted row id."""
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO requirements (item_name, quantity, raiser_name, status) VALUES (?, ?, ?, 'open')",
        (item_name.strip(), quantity.strip(), raiser_name.strip()),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


def get_open_requirements() -> List[sqlite3.Row]:
    """Return all requirements with status='open', newest first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM requirements WHERE status='open' ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return rows


def get_requirement_by_id(req_id: int) -> Optional[sqlite3.Row]:
    """Fetch a single requirement by its id."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM requirements WHERE id = ?", (req_id,)
    ).fetchone()
    conn.close()
    return row


def fulfill_requirement(req_id: int, fulfiller_name: str, proof_path: str) -> bool:
    """Mark a requirement as fulfilled. Returns True if successful."""
    conn = get_connection()
    now = datetime.utcnow().isoformat()
    cur = conn.execute(
        "UPDATE requirements SET status='fulfilled', fulfiller_name=?, proof_path=?, fulfilled_at=? WHERE id=? AND status='open'",
        (fulfiller_name.strip(), proof_path, now, req_id),
    )
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated


def get_fulfilled_requirements() -> List[sqlite3.Row]:
    """Return all requirements with status='fulfilled', newest first."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM requirements WHERE status='fulfilled' ORDER BY fulfilled_at DESC"
    ).fetchall()
    conn.close()
    return rows