"""Verification, officer assignment, and status progression.

Every mutation is authorised against the actor's scope and appends to the
complaint timeline, giving a full audit trail.
"""
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.assignment import Assignment
from app.models.complaint import Complaint, ComplaintStatusEnum
from app.models.complaint_status import ComplaintStatus
from app.models.user import User, UserRole
from app.utils.constants import to_status


def _can_act(actor: User, complaint: Complaint) -> bool:
    if actor.role == UserRole.super_admin:
        return True
    if actor.role == UserRole.mp:
        return complaint.constituency_id == actor.constituency_id
    if actor.role == UserRole.officer:
        return (
            complaint.assigned_officer_id == actor.id
            or complaint.constituency_id == actor.constituency_id
        )
    return False


def _authorize(actor: User, complaint: Complaint) -> None:
    if not _can_act(actor, complaint):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorised to act on this complaint.",
        )


def _log(db: Session, complaint: Complaint, new_status: ComplaintStatusEnum,
         note: Optional[str], actor: User) -> None:
    complaint.status = new_status
    db.add(
        ComplaintStatus(
            complaint_id=complaint.id,
            status=new_status,
            note=note,
            changed_by_id=actor.id,
        )
    )


def verify_complaint(db: Session, actor: User, complaint: Complaint) -> Complaint:
    _authorize(actor, complaint)
    _log(db, complaint, ComplaintStatusEnum.verified,
         "Complaint verified as genuine.", actor)
    db.commit()
    db.refresh(complaint)
    return complaint


def add_note(db: Session, actor: User, complaint: Complaint, note: str) -> Complaint:
    """Append a progress note to the timeline without changing the status."""
    _authorize(actor, complaint)
    db.add(
        ComplaintStatus(
            complaint_id=complaint.id,
            status=complaint.status,
            note=note,
            changed_by_id=actor.id,
        )
    )
    db.commit()
    db.refresh(complaint)
    return complaint


def update_status(
    db: Session, actor: User, complaint: Complaint, new_status: str,
    note: Optional[str] = None,
) -> Complaint:
    _authorize(actor, complaint)
    try:
        target = to_status(new_status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status '{new_status}'.")
    _log(db, complaint, target, note, actor)
    db.commit()
    db.refresh(complaint)
    return complaint


def assign_officer(
    db: Session, actor: User, complaint: Complaint, officer_id: int
) -> Complaint:
    """MP (or super admin) assigns an officer within the same constituency."""
    _authorize(actor, complaint)

    officer = db.query(User).filter(User.id == officer_id).first()
    if not officer or officer.role != UserRole.officer:
        raise HTTPException(status_code=404, detail="Officer not found.")
    if officer.constituency_id != complaint.constituency_id:
        raise HTTPException(
            status_code=400,
            detail="Officer must belong to the complaint's constituency.",
        )

    complaint.assigned_officer_id = officer.id
    db.add(
        Assignment(
            complaint_id=complaint.id,
            constituency_id=complaint.constituency_id,
            officer_id=officer.id,
            assigned_by_id=actor.id,
        )
    )
    _log(db, complaint, ComplaintStatusEnum.assigned,
         f"Assigned to officer {officer.name}.", actor)
    db.commit()
    db.refresh(complaint)
    return complaint
