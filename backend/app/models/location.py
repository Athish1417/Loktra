"""Normalised location hierarchy that drives complaint routing and visibility.

State -> District -> Constituency -> Ward
The Constituency is the routing unit: complaints are scoped to it, and only that
constituency's MP + officers can see them.
"""
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    code = Column(String, nullable=True)

    districts = relationship(
        "District", back_populates="state", cascade="all, delete-orphan"
    )


class District(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)

    state = relationship("State", back_populates="districts")
    constituencies = relationship(
        "Constituency", back_populates="district", cascade="all, delete-orphan"
    )


class Constituency(Base):
    __tablename__ = "constituencies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)

    district = relationship("District", back_populates="constituencies")
    wards = relationship(
        "Ward", back_populates="constituency", cascade="all, delete-orphan"
    )
    # Users (MP + officers) attached to this constituency.
    members = relationship(
        "User",
        foreign_keys="User.constituency_id",
        back_populates="constituency",
    )
    dataset = relationship(
        "Dataset",
        back_populates="constituency",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Ward(Base):
    __tablename__ = "wards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    constituency_id = Column(
        Integer, ForeignKey("constituencies.id"), nullable=False
    )

    constituency = relationship("Constituency", back_populates="wards")
