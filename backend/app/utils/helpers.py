"""Small stateless helpers."""
from datetime import datetime


def make_complaint_code(complaint_id: int) -> str:
    """Human-friendly, unique tracking id derived from the DB primary key.

    e.g. LOK-2026-000123
    """
    year = datetime.utcnow().year
    return f"LOK-{year}-{complaint_id:06d}"
