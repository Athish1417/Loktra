"""MP endpoints: constituency dashboard, complaint list, officer assignment."""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_mp
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.complaint import AssignOfficer, ComplaintDetail, ComplaintOut
from app.schemas.user import UserOut
from app.services import assignment_service, complaint_service, dashboard_service

router = APIRouter(prefix="/mp", tags=["mp"])


@router.get("/dashboard")
def dashboard(mp: User = Depends(require_mp), db: Session = Depends(get_db)):
    """Decision-support analytics scoped to the MP's constituency."""
    return dashboard_service.mp_dashboard(db, mp)


@router.get("/complaints", response_model=List[ComplaintOut])
def constituency_complaints(
    mp: User = Depends(require_mp), db: Session = Depends(get_db)
):
    return complaint_service.list_visible(db, mp)


@router.get("/officers", response_model=List[UserOut])
def constituency_officers(
    mp: User = Depends(require_mp), db: Session = Depends(get_db)
):
    """Officers the MP can assign to (their constituency). Super admin -> all."""
    q = db.query(User).filter(User.role == UserRole.officer)
    if mp.constituency_id:
        q = q.filter(User.constituency_id == mp.constituency_id)
    return q.order_by(User.name).all()


@router.post("/complaints/{complaint_id}/assign", response_model=ComplaintDetail)
def assign(
    complaint_id: int,
    payload: AssignOfficer,
    mp: User = Depends(require_mp),
    db: Session = Depends(get_db),
):
    complaint = complaint_service.get_visible_or_404(db, mp, complaint_id)
    return assignment_service.assign_officer(db, mp, complaint, payload.officer_id)
