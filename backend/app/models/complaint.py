import datetime
import enum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ComplaintCategory(str, enum.Enum):
    roads = "Roads"
    water = "Water Supply"
    electricity = "Electricity"
    drainage = "Drainage"
    garbage = "Garbage"
    healthcare = "Healthcare"
    education = "Education"
    street_lights = "Street Lights"
    public_transport = "Public Transport"
    public_safety = "Public Safety"
    government_services = "Government Services"
    others = "Others"


class ComplaintStatusEnum(str, enum.Enum):
    submitted = "Submitted"
    verified = "Verified"
    assigned = "Assigned"
    work_started = "Work Started"
    completed = "Completed"
    rejected = "Rejected"


class UrgencyLevel(str, enum.Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
    emergency = "Emergency"


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    complaint_code = Column(String, unique=True, index=True, nullable=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    category = Column(Enum(ComplaintCategory), default=ComplaintCategory.others)

    # Multilingual: keep the raw submission AND an English translation.
    original_language = Column(String, default="en")
    original_text = Column(Text, nullable=True)
    translated_text = Column(Text, nullable=True)

    status = Column(
        Enum(ComplaintStatusEnum), default=ComplaintStatusEnum.submitted
    )
    urgency = Column(Enum(UrgencyLevel), default=UrgencyLevel.medium)
    priority_score = Column(Float, default=0.0)  # 0-100
    is_emergency = Column(Boolean, default=False)

    # AI-generated fields
    ai_summary = Column(Text, nullable=True)
    ai_reason = Column(Text, nullable=True)

    # Phase 5: which dataset informed this complaint's priority.
    dataset_mode = Column(String, nullable=True)      # Official Government Dataset | No Official Dataset Match
    matched_datasets = Column(JSON, nullable=True)    # e.g. ["Census", "NFHS"]

    # Duplicate-detection foundation (Phase 3).
    duplicate_count = Column(Integer, default=0)
    duplicate_group_key = Column(String, nullable=True, index=True)

    # Media + geo
    image_path = Column(String, nullable=True)
    voice_path = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # People + location routing
    citizen_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
    constituency_id = Column(
        Integer, ForeignKey("constituencies.id"), nullable=True, index=True
    )
    ward_id = Column(Integer, ForeignKey("wards.id"), nullable=True)
    assigned_officer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # Auto-routing at creation: the MP + officer whose area matches the complaint.
    # Nullable — an unrouted complaint (no matching official) still reaches Admin.
    mp_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    officer_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    # Relationships (explicit FKs because two columns point at users)
    citizen = relationship("User", foreign_keys=[citizen_id])
    assigned_officer = relationship("User", foreign_keys=[assigned_officer_id])
    state = relationship("State", foreign_keys=[state_id])
    district = relationship("District", foreign_keys=[district_id])
    constituency = relationship("Constituency", foreign_keys=[constituency_id])
    ward = relationship("Ward", foreign_keys=[ward_id])
    timeline = relationship(
        "ComplaintStatus",
        back_populates="complaint",
        cascade="all, delete-orphan",
        order_by="ComplaintStatus.created_at",
    )

    # Read-only location names for API responses (dashboards display these).
    @property
    def state_name(self):
        return self.state.name if self.state else None

    @property
    def district_name(self):
        return self.district.name if self.district else None

    @property
    def constituency_name(self):
        return self.constituency.name if self.constituency else None

    @property
    def ward_name(self):
        return self.ward.name if self.ward else None
