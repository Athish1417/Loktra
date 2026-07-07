"""MP decision-support dashboard aggregations.

Everything is scoped to the MP's constituency. The recommendations are derived
from the actual open-complaint mix + the constituency dataset, so they read like
genuine governance guidance rather than canned text.
"""
from collections import Counter
from typing import Optional

from sqlalchemy.orm import Session

from app.models.complaint import Complaint, ComplaintStatusEnum, UrgencyLevel
from app.models.dataset import Dataset
from app.models.user import User


def mp_dashboard(db: Session, mp: User) -> dict:
    # Use the same visibility rule as the complaint list (constituency + auto-routed
    # + incomplete-profile fallback) so the dashboard aggregates match what the MP sees.
    from app.services import complaint_service

    cid = mp.constituency_id
    base = complaint_service.visible_query(db, mp)
    complaints = base.all()

    total = len(complaints)
    completed = sum(
        1 for c in complaints if c.status == ComplaintStatusEnum.completed
    )
    emergencies = sum(1 for c in complaints if c.is_emergency)
    high_priority = sum(1 for c in complaints if (c.priority_score or 0) >= 60)
    pending = sum(
        1 for c in complaints if c.status != ComplaintStatusEnum.completed
    )

    category_dist = Counter(c.category.value for c in complaints)
    status_dist = Counter(c.status.value for c in complaints)
    urgency_dist = Counter(c.urgency.value for c in complaints)

    recent = (
        base.order_by(Complaint.created_at.desc()).limit(5).all()
    )

    dataset = (
        db.query(Dataset).filter(Dataset.constituency_id == cid).first()
    )

    return {
        "constituency_id": cid,
        "summary": {
            "total_complaints": total,
            "pending": pending,
            "completed": completed,
            "high_priority": high_priority,
            "emergencies": emergencies,
            "resolution_rate": round((completed / total) * 100, 1) if total else 0.0,
        },
        "category_distribution": dict(category_dist),
        "status_distribution": dict(status_dist),
        "urgency_distribution": dict(urgency_dist),
        "recent_complaints": [
            {
                "id": c.id,
                "code": c.complaint_code,
                "title": c.title,
                "category": c.category.value,
                "urgency": c.urgency.value,
                "priority_score": c.priority_score,
                "status": c.status.value,
                "is_emergency": c.is_emergency,
            }
            for c in recent
        ],
        "recommendations": _recommendations(complaints, dataset),
    }


def admin_summary(db: Session) -> dict:
    """Platform-wide overview for the super admin: totals plus state-wise and
    constituency-wise breakdowns across every complaint."""
    complaints = db.query(Complaint).all()
    total = len(complaints)
    completed = sum(
        1 for c in complaints if c.status == ComplaintStatusEnum.completed
    )

    def _bucket() -> dict:
        return {"total": 0, "completed": 0, "emergencies": 0, "high_priority": 0}

    state_wise: dict[str, dict] = {}
    constituency_wise: dict[str, dict] = {}
    for c in complaints:
        state_name = c.state.name if c.state else "Unassigned"
        cons_name = c.constituency.name if c.constituency else "Unassigned"
        for key, table in ((state_name, state_wise), (cons_name, constituency_wise)):
            b = table.setdefault(key, _bucket())
            b["total"] += 1
            if c.status == ComplaintStatusEnum.completed:
                b["completed"] += 1
            if c.is_emergency:
                b["emergencies"] += 1
            if (c.priority_score or 0) >= 60:
                b["high_priority"] += 1

    return {
        "platform": {
            "total_complaints": total,
            "pending": sum(
                1 for c in complaints
                if c.status != ComplaintStatusEnum.completed
            ),
            "completed": completed,
            "high_priority": sum(
                1 for c in complaints if (c.priority_score or 0) >= 60
            ),
            "emergencies": sum(1 for c in complaints if c.is_emergency),
            "resolution_rate": round((completed / total) * 100, 1) if total else 0.0,
            "total_users": db.query(User).count(),
        },
        "state_wise": [{"state": k, **v} for k, v in state_wise.items()],
        "constituency_wise": [
            {"constituency": k, **v} for k, v in constituency_wise.items()
        ],
    }


def _recommendations(complaints, dataset: Optional[Dataset]) -> list[dict]:
    """Rank action areas by aggregate open-priority pressure, contextualised
    with the constituency dataset."""
    open_ = [c for c in complaints if c.status != ComplaintStatusEnum.completed]
    if not open_:
        return [
            {
                "priority": "info",
                "title": "No pending complaints",
                "detail": "All complaints in your constituency are resolved.",
            }
        ]

    pressure: dict[str, float] = {}
    counts: Counter = Counter()
    for c in open_:
        pressure[c.category.value] = pressure.get(c.category.value, 0.0) + (
            c.priority_score or 0
        )
        counts[c.category.value] += 1

    ranked = sorted(pressure.items(), key=lambda kv: kv[1], reverse=True)

    recs: list[dict] = []
    for category, score in ranked[:3]:
        n = counts[category]
        detail = (
            f"{n} open {category} complaint(s) with combined priority {score:.0f}. "
        )
        if dataset is not None:
            if category in ("Roads", "Drainage", "Street Lights") and dataset.road_score < 50:
                detail += f"Road infrastructure index is low ({dataset.road_score:.0f}/100) — allocate capital works."
            elif category in ("Water Supply", "Garbage") and dataset.water_score < 50:
                detail += f"Water/sanitation index is low ({dataset.water_score:.0f}/100) — prioritise utility upgrades."
            elif category == "Healthcare":
                detail += f"Hospitals: {dataset.hospitals} for population ~{dataset.population:,} — review coverage."
            elif category == "Education":
                detail += f"Schools: {dataset.schools} for population ~{dataset.population:,} — review capacity."
            else:
                detail += "Consider directing departmental resources here."
        recs.append(
            {
                "priority": "high" if score >= 120 else "medium",
                "title": f"Focus on {category}",
                "detail": detail,
            }
        )

    emergencies = [c for c in open_ if c.is_emergency]
    if emergencies:
        recs.insert(
            0,
            {
                "priority": "critical",
                "title": f"{len(emergencies)} active emergency issue(s)",
                "detail": "Emergency-flagged complaints need immediate dispatch of field officers.",
            },
        )
    return recs
