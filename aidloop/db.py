from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import List, TypedDict, Optional

import streamlit as st
from supabase import create_client, Client


# ── Typed dicts for type hints ────────────────────────────────────────
class Requirement(TypedDict):
    id: int
    item_name: str
    quantity: str
    raiser_name: str
    status: str
    fulfiller_name: str
    proof_path: str
    raiser_proof_path: str
    created_at: str
    fulfilled_at: str | None


# ── Supabase client (lazy init) ───────────────────────────────────────
_SUPABASE: Optional[Client] = None


def _get_client() -> Client:
    """Return a cached Supabase client.

    Credentials are resolved in this order:
    1. ``st.secrets["supabase_url"]`` / ``st.secrets["supabase_key"]``
       (works locally via ``.streamlit/secrets.toml`` and on Streamlit
       Cloud via the dashboard Secrets editor).
    2. ``SUPABASE_URL`` / ``SUPABASE_KEY`` environment variables
       (useful for CI or other hosting).
    """
    global _SUPABASE
    if _SUPABASE is None:
        # Try st.secrets first (local dev + Streamlit Cloud dashboard)
        try:
            url = st.secrets["supabase_url"]
            key = st.secrets["supabase_key"]
        except KeyError:
            # Fall back to environment variables
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_KEY")

        if not url or not key:
            raise RuntimeError(
                "Supabase credentials not found. "
                "Set them via Streamlit secrets (secrets.toml or dashboard) "
                "or via SUPABASE_URL / SUPABASE_KEY environment variables."
            )

        _SUPABASE = create_client(url, key)
    return _SUPABASE


# ── Public helpers ────────────────────────────────────────────────────

def _row_to_dict(row) -> dict:
    """Convert a Supabase response row to a plain dict."""
    return dict(row)


def init_db() -> None:
    """No-op — the table is created manually in Supabase via SQL editor."""
    pass


def insert_requirement(item_name: str, quantity: str, raiser_name: str = "", raiser_proof_path: str = "") -> int:
    """Insert a new open requirement. Returns the inserted row id."""
    client = _get_client()
    data = {
        "item_name": item_name.strip(),
        "quantity": quantity.strip(),
        "raiser_name": raiser_name.strip(),
        "raiser_proof_path": raiser_proof_path,
        "status": "open",
    }
    result = client.table("requirements").insert(data).execute()
    return result.data[0]["id"]


def get_open_requirements() -> List[dict]:
    """Return all requirements with status='open', newest first."""
    client = _get_client()
    result = (
        client.table("requirements")
        .select("*")
        .eq("status", "open")
        .order("created_at", desc=True)
        .execute()
    )
    return [_row_to_dict(r) for r in result.data]


def get_requirement_by_id(req_id: int) -> Optional[dict]:
    """Fetch a single requirement by its id."""
    client = _get_client()
    result = (
        client.table("requirements")
        .select("*")
        .eq("id", req_id)
        .limit(1)
        .execute()
    )
    if result.data:
        return _row_to_dict(result.data[0])
    return None


def fulfill_requirement(
    req_id: int, fulfiller_name: str, proof_path: str
) -> bool:
    """Mark a requirement as fulfilled. Returns True if successful."""
    client = _get_client()
    now = datetime.now(timezone.utc).isoformat()
    result = (
        client.table("requirements")
        .update({
            "status": "fulfilled",
            "fulfiller_name": fulfiller_name.strip(),
            "proof_path": proof_path,
            "fulfilled_at": now,
        })
        .eq("id", req_id)
        .eq("status", "open")
        .execute()
    )
    return len(result.data) > 0


def get_fulfilled_requirements() -> List[dict]:
    """Return all requirements with status='fulfilled', newest first."""
    client = _get_client()
    result = (
        client.table("requirements")
        .select("*")
        .eq("status", "fulfilled")
        .order("fulfilled_at", desc=True)
        .execute()
    )
    return [_row_to_dict(r) for r in result.data]