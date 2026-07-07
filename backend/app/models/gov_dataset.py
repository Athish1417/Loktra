"""Real government-dataset tables (Phase 4).

One `DatasetSource` row is logged per imported file; the normalised rows go into
the per-type record tables. Every metric column is nullable and an `extra` JSON
column captures useful-but-unmapped fields, so messy/partial official files
import safely without crashing.
"""
import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class DatasetSource(Base):
    """Provenance log for one imported official dataset file."""
    __tablename__ = "dataset_sources"

    id = Column(Integer, primary_key=True, index=True)
    dataset_name = Column(String, nullable=False)
    source_name = Column(String, nullable=False)
    source_department = Column(String, nullable=True)  # e.g. Census India, ECI
    source_type = Column(String, index=True)  # census|lgd|pincode|nfhs|election|imports
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    is_official = Column(Boolean, default=True)
    record_count = Column(Integer, default=0)
    import_status = Column(String, default="success")  # success | partial | failed
    imported_at = Column(DateTime, default=datetime.datetime.utcnow)


class PopulationRecord(Base):
    __tablename__ = "population_records"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("dataset_sources.id"), index=True)
    state = Column(String, index=True)
    district = Column(String, index=True)
    subdistrict = Column(String, nullable=True)
    village = Column(String, nullable=True)
    population = Column(Integer, nullable=True)
    households = Column(Integer, nullable=True)
    area = Column(Float, nullable=True)
    extra = Column(JSON, nullable=True)


class LgdLocationRecord(Base):
    __tablename__ = "lgd_location_records"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("dataset_sources.id"), index=True)
    state = Column(String, index=True)
    district = Column(String, index=True)
    subdistrict = Column(String, nullable=True)
    village = Column(String, nullable=True)
    extra = Column(JSON, nullable=True)


class PincodeRecord(Base):
    __tablename__ = "pincode_records"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("dataset_sources.id"), index=True)
    pincode = Column(String, index=True)
    office_name = Column(String, nullable=True)
    district = Column(String, index=True)
    state = Column(String, index=True)
    extra = Column(JSON, nullable=True)


class NfhsRecord(Base):
    __tablename__ = "nfhs_records"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("dataset_sources.id"), index=True)
    level = Column(String, nullable=True)  # "state" | "district"
    state = Column(String, index=True)
    district = Column(String, nullable=True, index=True)
    indicators = Column(JSON, nullable=True)  # flexible: any recognised health metrics


class ElectionConstituencyRecord(Base):
    """Constituency context from ECI summary / result reports (2024, etc.)."""
    __tablename__ = "election_constituency_records"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("dataset_sources.id"), index=True)
    state = Column(String, index=True)
    district = Column(String, nullable=True, index=True)
    constituency = Column(String, nullable=True, index=True)
    extra = Column(JSON, nullable=True)  # electors, votes, winner, party, etc.
