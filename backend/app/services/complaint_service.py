"""Complaint domain logic.

Two responsibilities that matter most:
  1. create_complaint(): the AI submission pipeline
     language -> relevance guard -> analysis -> priority -> route -> persist.
  2. Visibility: `visible_query()` scopes complaints by role AT THE QUERY LEVEL,
     so out-of-scope complaints never leave the database. An MP for constituency A
     physically cannot receive a complaint from constituency B.
"""
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Query, Session

from app.ai import language, services as ai_services
from app.models.complaint import Complaint, ComplaintStatusEnum
from app.models.complaint_status import ComplaintStatus
from app.models.dataset import Dataset
from app.models.location import Constituency, District, State, Ward
from app.models.user import User, UserRole
from app.services import official_data, routing_service
from app.schemas.complaint import ComplaintCreate
from app.utils.constants import to_category, to_urgency
from app.utils.helpers import make_complaint_code

REJECTION_MESSAGE = (
    "Post Failed. This platform accepts only civic and public governance "
    "related issues."
)


# --------------------------------------------------------------------------- #
# Submission pipeline
# --------------------------------------------------------------------------- #
def create_complaint(
    db: Session,
    citizen: User,
    payload: ComplaintCreate,
    image_path: Optional[str] = None,
    voice_path: Optional[str] = None,
) -> Complaint:
    raw_text = f"{payload.title}. {payload.description}".strip()

    # 1) Language: detect + translate to English for consistent AI processing.
    lang_code, english_text = language.process(raw_text, payload.language)

    # 2) Governance-relevance guard (runs BEFORE anything is stored).
    verdict = ai_services.check_civic_relevance(english_text)
    if not verdict.is_relevant:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": REJECTION_MESSAGE, "reason": verdict.reason},
        )

    # 3) AI analysis: category, urgency, summary, reason, emergency flag.
    analysis = ai_services.analyze_complaint(english_text)

    # Honour an explicit citizen category hint only if AI returned Others.
    category = to_category(analysis.category)
    if payload.category and category.value == "Others":
        category = to_category(payload.category)

    # 4) Duplicate detection (feeds the priority score + is stored on the complaint).
    dup = ai_services.detect_possible_duplicates(
        db,
        category=category.value,
        constituency_id=payload.constituency_id,
        ward_id=payload.ward_id,
        title=payload.title,
        description=payload.description,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )

    # 5) Priority + explainable reason. Look up the imported official datasets that
    #    cover this location; they refine the score and are cited in the reason.
    #    When nothing matches, everything falls back safely to the sample dataset.
    dataset = _dataset_for(db, payload.constituency_id)
    sname, dname, cname, wname = _location_names(db, payload)
    official = official_data.lookup(
        db, state=sname, district=dname, constituency=cname, ward=wname
    )
    real_pop = official.population
    breakdown = ai_services.calculate_priority_score(
        analysis, dataset, duplicate_count=dup.count,
        population_override=real_pop, official=official,
    )
    reason = ai_services.generate_reason(
        analysis, breakdown, dataset, dup.count,
        population=real_pop if real_pop is not None
        else (dataset.population if dataset else None),
        population_is_real=real_pop is not None,
        context_sources=official.matched_labels,
    )
    dataset_mode = (
        "Official Government Dataset" if official.is_official
        else "No Official Dataset Match"
    )

    # Auto-route to the MP + officer whose area matches (backend = source of truth).
    mp_id, officer_id = routing_service.route_complaint(
        db,
        state_id=payload.state_id,
        district_id=payload.district_id,
        constituency_id=payload.constituency_id,
    )

    complaint = Complaint(
        title=payload.title,
        description=payload.description,
        category=category,
        original_language=lang_code,
        original_text=raw_text,
        translated_text=english_text,
        status=ComplaintStatusEnum.submitted,
        urgency=to_urgency(analysis.urgency),
        priority_score=breakdown.score,
        is_emergency=analysis.is_emergency,
        ai_summary=analysis.summary,
        ai_reason=reason,
        dataset_mode=dataset_mode,
        matched_datasets=official.matched_labels,
        duplicate_count=dup.count,
        duplicate_group_key=dup.group_key,
        image_path=image_path,
        voice_path=voice_path,
        latitude=payload.latitude,
        longitude=payload.longitude,
        citizen_id=citizen.id,
        state_id=payload.state_id,
        district_id=payload.district_id,
        constituency_id=payload.constituency_id,
        ward_id=payload.ward_id,
        mp_id=mp_id,
        officer_id=officer_id,
    )
    db.add(complaint)
    db.flush()  # obtain PK to build the tracking code

    complaint.complaint_code = make_complaint_code(complaint.id)
    db.add(
        ComplaintStatus(
            complaint_id=complaint.id,
            status=ComplaintStatusEnum.submitted,
            note="Complaint submitted by citizen.",
            changed_by_id=citizen.id,
        )
    )
    db.commit()
    db.refresh(complaint)
    return complaint


# --------------------------------------------------------------------------- #
# Visibility (RBAC enforced in the query)
# --------------------------------------------------------------------------- #
def visible_query(db: Session, user: User) -> Query:
    q = db.query(Complaint)

    if user.role == UserRole.super_admin:
        return q
    if user.role == UserRole.mp:
        if not user.constituency_id:
            # Incomplete MP profile: don't show an empty dashboard — surface open
            # complaints (the frontend adds a "profile incomplete" helper note).
            return q.filter(Complaint.status != ComplaintStatusEnum.completed)
        # Complaints in the MP's constituency OR auto-routed to this MP.
        return q.filter(
            or_(
                Complaint.constituency_id == user.constituency_id,
                Complaint.mp_id == user.id,
            )
        )
    if user.role == UserRole.officer:
        if not user.constituency_id:
            # Incomplete officer profile: surface open complaints rather than an
            # empty queue (mirrors the MP fallback).
            return q.filter(Complaint.status != ComplaintStatusEnum.completed)
        # Assigned to them, auto-routed to them, or in their constituency.
        return q.filter(
            or_(
                Complaint.assigned_officer_id == user.id,
                Complaint.officer_id == user.id,
                Complaint.constituency_id == user.constituency_id,
            )
        )
    # Citizen: only their own submissions.
    return q.filter(Complaint.citizen_id == user.id)


def list_visible(
    db: Session,
    user: User,
    status_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    emergency_only: bool = False,
    urgency_filter: Optional[str] = None,
    min_priority: Optional[float] = None,
    max_priority: Optional[float] = None,
):
    q = visible_query(db, user)
    if status_filter:
        q = q.filter(Complaint.status == to_status_enum(status_filter))
    if category_filter:
        q = q.filter(Complaint.category == to_category(category_filter))
    if emergency_only:
        q = q.filter(Complaint.is_emergency.is_(True))
    if urgency_filter:
        q = q.filter(Complaint.urgency == to_urgency(urgency_filter))
    if min_priority is not None:
        q = q.filter(Complaint.priority_score >= min_priority)
    if max_priority is not None:
        q = q.filter(Complaint.priority_score <= max_priority)
    return q.order_by(
        Complaint.is_emergency.desc(),
        Complaint.priority_score.desc(),
        Complaint.created_at.desc(),
    ).all()


def get_visible_or_404(db: Session, user: User, complaint_id: int) -> Complaint:
    complaint = (
        visible_query(db, user).filter(Complaint.id == complaint_id).first()
    )
    if not complaint:
        # 404 (not 403) so we don't reveal existence of out-of-scope complaints.
        raise HTTPException(status_code=404, detail="Complaint not found.")
    return complaint


def get_visible_by_code(db: Session, user: User, code: str) -> Complaint:
    complaint = (
        visible_query(db, user)
        .filter(Complaint.complaint_code == code)
        .first()
    )
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found.")
    return complaint


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _dataset_for(db: Session, constituency_id: Optional[int]) -> Optional[Dataset]:
    if not constituency_id:
        return None
    return (
        db.query(Dataset)
        .filter(Dataset.constituency_id == constituency_id)
        .first()
    )


def _location_names(db: Session, payload: ComplaintCreate):
    """Resolve (state, district, constituency, ward) names from the payload ids."""
    sname = (
        db.query(State.name).filter(State.id == payload.state_id).scalar()
        if payload.state_id else None
    )
    dname = (
        db.query(District.name).filter(District.id == payload.district_id).scalar()
        if payload.district_id else None
    )
    cname = (
        db.query(Constituency.name)
        .filter(Constituency.id == payload.constituency_id).scalar()
        if payload.constituency_id else None
    )
    wname = (
        db.query(Ward.name).filter(Ward.id == payload.ward_id).scalar()
        if payload.ward_id else None
    )
    return sname, dname, cname, wname


def to_status_enum(value: str) -> ComplaintStatusEnum:
    from app.utils.constants import to_status

    return to_status(value)
