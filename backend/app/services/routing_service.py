"""Auto-route a complaint to the MP + officer whose area matches its location.

Backend is the source of truth for routing (never the frontend). We match the
most specific location first (constituency), then fall back to district, then
state, so a complaint still reaches a relevant official even when no user is bound
to its exact constituency. No match -> None (the complaint still reaches Admin).
"""
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.models.location import Constituency, District
from app.models.user import User, UserRole


def _match(
    db: Session,
    role: UserRole,
    *,
    constituency_id: Optional[int],
    district_id: Optional[int],
    state_id: Optional[int],
) -> Optional[int]:
    base = db.query(User).filter(User.role == role, User.is_active.is_(True))

    if constituency_id:
        u = base.filter(User.constituency_id == constituency_id).first()
        if u:
            return u.id
    if district_id:
        u = (
            base.join(Constituency, User.constituency_id == Constituency.id)
            .filter(Constituency.district_id == district_id)
            .first()
        )
        if u:
            return u.id
    if state_id:
        u = (
            base.join(Constituency, User.constituency_id == Constituency.id)
            .join(District, Constituency.district_id == District.id)
            .filter(District.state_id == state_id)
            .first()
        )
        if u:
            return u.id
    return None


def route_complaint(
    db: Session,
    *,
    state_id: Optional[int],
    district_id: Optional[int],
    constituency_id: Optional[int],
) -> Tuple[Optional[int], Optional[int]]:
    """Return (mp_id, officer_id) for the complaint's location. Never raises."""
    try:
        mp_id = _match(
            db, UserRole.mp,
            constituency_id=constituency_id, district_id=district_id, state_id=state_id,
        )
        officer_id = _match(
            db, UserRole.officer,
            constituency_id=constituency_id, district_id=district_id, state_id=state_id,
        )
        return mp_id, officer_id
    except Exception:  # pragma: no cover - routing must never block submission
        return None, None


def backfill(db: Session) -> int:
    """Route existing complaints that have no mp_id yet (e.g. created before this
    feature). Idempotent + non-fatal — only fills rows still missing a route.
    """
    from app.models.complaint import Complaint

    try:
        rows = db.query(Complaint).filter(Complaint.mp_id.is_(None)).all()
        filled = 0
        for c in rows:
            mp_id, officer_id = route_complaint(
                db,
                state_id=c.state_id,
                district_id=c.district_id,
                constituency_id=c.constituency_id,
            )
            if mp_id or officer_id:
                c.mp_id = mp_id
                c.officer_id = officer_id
                filled += 1
        if filled:
            db.commit()
        return filled
    except Exception:  # pragma: no cover - defensive
        db.rollback()
        return 0
