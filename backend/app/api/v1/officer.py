"""Officer endpoints: verify complaints and update work progress."""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_officer
from app.db.session import get_db
from app.models.user import User
from app.schemas.complaint import (
    ComplaintDetail,
    ComplaintOut,
    ProgressNote,
    StatusUpdate,
)
from app.services import assignment_service, complaint_service

router = APIRouter(prefix="/officer", tags=["officer"])


@router.get("/complaints", response_model=List[ComplaintOut])
def my_queue(
    officer: User = Depends(require_officer), db: Session = Depends(get_db)
):
    """Complaints in the officer's constituency or assigned to them."""
    return complaint_service.list_visible(db, officer)


@router.post("/complaints/{complaint_id}/verify", response_model=ComplaintDetail)
def verify(
    complaint_id: int,
    officer: User = Depends(require_officer),
    db: Session = Depends(get_db),
):
    complaint = complaint_service.get_visible_or_404(db, officer, complaint_id)
    return assignment_service.verify_complaint(db, officer, complaint)


@router.post("/complaints/{complaint_id}/status", response_model=ComplaintDetail)
def update_status(
    complaint_id: int,
    payload: StatusUpdate,
    officer: User = Depends(require_officer),
    db: Session = Depends(get_db),
):
    complaint = complaint_service.get_visible_or_404(db, officer, complaint_id)
    return assignment_service.update_status(
        db, officer, complaint, payload.status, payload.note
    )


@router.post("/complaints/{complaint_id}/note", response_model=ComplaintDetail)
def add_note(
    complaint_id: int,
    payload: ProgressNote,
    officer: User = Depends(require_officer),
    db: Session = Depends(get_db),
):
    """Add a progress note without changing the complaint's status."""
    complaint = complaint_service.get_visible_or_404(db, officer, complaint_id)
    return assignment_service.add_note(db, officer, complaint, payload.note)
