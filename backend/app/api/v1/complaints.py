"""Citizen-facing complaint endpoints + shared read endpoints (visibility-scoped)."""
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.ai import services as ai_services
from app.core.dependencies import get_current_user, require_citizen
from app.db.session import get_db
from app.models.user import User
from app.schemas.complaint import ComplaintCreate, ComplaintDetail, ComplaintOut
from app.services import complaint_service
from app.utils.file_storage import save_image, save_voice

router = APIRouter(prefix="/complaints", tags=["complaints"])


@router.post("", response_model=ComplaintOut, status_code=201)
def submit_complaint(
    title: str = Form(...),
    description: str = Form(...),
    language: Optional[str] = Form("en"),
    category: Optional[str] = Form(None),
    state_id: Optional[int] = Form(None),
    district_id: Optional[int] = Form(None),
    constituency_id: Optional[int] = Form(None),
    ward_id: Optional[int] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    image: Optional[UploadFile] = File(None),
    voice: Optional[UploadFile] = File(None),
    citizen: User = Depends(require_citizen),
    db: Session = Depends(get_db),
):
    """Submit a complaint (multipart, supports optional image + voice).

    Runs the AI pipeline; returns 422 with a rejection message if the content
    is not a public governance issue.
    """
    payload = ComplaintCreate(
        title=title,
        description=description,
        language=language,
        category=category,
        state_id=state_id,
        district_id=district_id,
        constituency_id=constituency_id,
        ward_id=ward_id,
        latitude=latitude,
        longitude=longitude,
    )
    complaint = complaint_service.create_complaint(
        db,
        citizen,
        payload,
        image_path=save_image(image),
        voice_path=save_voice(voice),
    )
    return complaint


@router.get("", response_model=List[ComplaintOut])
def list_complaints(
    status: Optional[str] = None,
    category: Optional[str] = None,
    emergency_only: bool = False,
    urgency: Optional[str] = None,
    min_priority: Optional[float] = None,
    max_priority: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List complaints visible to the current user (role-scoped at the query level).

    Optional AI filters: status, category, emergency_only, urgency, and a
    priority range (min_priority / max_priority).
    """
    return complaint_service.list_visible(
        db,
        current_user,
        status,
        category,
        emergency_only,
        urgency_filter=urgency,
        min_priority=min_priority,
        max_priority=max_priority,
    )


@router.get("/track/{code}", response_model=ComplaintDetail)
def track_complaint(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Track a complaint by its LOK-YYYY-NNNNNN code (must be visible to you)."""
    return complaint_service.get_visible_by_code(db, current_user, code)


@router.get("/{complaint_id}/duplicates")
def complaint_duplicates(
    complaint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Possible duplicate reports of this complaint (same area + category)."""
    c = complaint_service.get_visible_or_404(db, current_user, complaint_id)
    dup = ai_services.detect_possible_duplicates(
        db,
        category=c.category.value,
        constituency_id=c.constituency_id,
        ward_id=c.ward_id,
        title=c.title,
        description=c.description,
        latitude=c.latitude,
        longitude=c.longitude,
        exclude_id=c.id,
    )
    return {
        "complaint_id": c.id,
        "duplicate_count": dup.count,
        "duplicate_ids": dup.ids,
        "duplicate_group_key": dup.group_key,
    }


@router.get("/{complaint_id}", response_model=ComplaintDetail)
def get_complaint(
    complaint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return complaint_service.get_visible_or_404(db, current_user, complaint_id)
