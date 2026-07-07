from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.models.complaint import (
    ComplaintCategory,
    ComplaintStatusEnum,
    UrgencyLevel,
)


class ComplaintCreate(BaseModel):
    """Citizen submission. `category` is an optional hint; the AI may override it."""
    title: str
    description: str
    language: Optional[str] = "en"
    category: Optional[str] = None
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    constituency_id: Optional[int] = None
    ward_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class StatusEvent(BaseModel):
    status: ComplaintStatusEnum
    note: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ComplaintOut(BaseModel):
    id: int
    complaint_code: Optional[str] = None
    title: str
    description: str
    # Enum-typed so Pydantic serialises the human-readable value ("Roads"), not the member.
    category: ComplaintCategory
    original_language: str
    translated_text: Optional[str] = None
    status: ComplaintStatusEnum
    urgency: UrgencyLevel
    priority_score: float
    is_emergency: bool
    ai_summary: Optional[str] = None
    ai_reason: Optional[str] = None
    # Phase 5: dataset provenance for this complaint.
    dataset_mode: Optional[str] = None
    matched_datasets: Optional[List[str]] = None
    duplicate_count: int = 0
    duplicate_group_key: Optional[str] = None
    image_path: Optional[str] = None
    voice_path: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    # Location: ids for routing + resolved names for display.
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    constituency_id: Optional[int] = None
    ward_id: Optional[int] = None
    state_name: Optional[str] = None
    district_name: Optional[str] = None
    constituency_name: Optional[str] = None
    ward_name: Optional[str] = None
    assigned_officer_id: Optional[int] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ComplaintDetail(ComplaintOut):
    timeline: List[StatusEvent] = []


class StatusUpdate(BaseModel):
    status: str  # one of the ComplaintStatusEnum values
    note: Optional[str] = None


class AssignOfficer(BaseModel):
    officer_id: int


class ProgressNote(BaseModel):
    note: str
