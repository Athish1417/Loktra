"""Audit record of routing a complaint to a constituency / officer."""
import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False)
    constituency_id = Column(
        Integer, ForeignKey("constituencies.id"), nullable=True
    )
    officer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_at = Column(DateTime, default=datetime.datetime.utcnow)

    complaint = relationship("Complaint", foreign_keys=[complaint_id])
    officer = relationship("User", foreign_keys=[officer_id])
