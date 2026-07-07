"""Sample Government-Style Dataset per constituency, used in priority scoring.

This is DEMO data only — not imported from official sources (e.g. data.gov.in,
Census India). The schema is kept close to real government indicators so genuine
datasets can be imported later without changing the model.

Scores are 0-100 where HIGHER = better existing infrastructure. Lower scores
push related complaints up the priority list (worse infra -> more urgent need).
"""
import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class DatasetMeta(Base):
    """Single-row metadata describing the CURRENT dataset (sample vs real).

    Lets the UI honestly show "Dataset Mode: Sample Data" and, after a real CSV
    import, "Real Government Dataset Imported" — without ever claiming sample data
    is official.
    """
    __tablename__ = "dataset_meta"

    id = Column(Integer, primary_key=True, index=True)
    dataset_name = Column(String, default="Sample Government-Style Dataset")
    source_name = Column(String, default="Sample (demo) data — not an official source")
    source_url = Column(String, nullable=True)
    is_official = Column(Boolean, default=False)
    imported_at = Column(DateTime, default=datetime.datetime.utcnow)


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    constituency_id = Column(
        Integer, ForeignKey("constituencies.id"), nullable=False, unique=True
    )
    population = Column(Integer, default=0)
    schools = Column(Integer, default=0)
    hospitals = Column(Integer, default=0)
    road_score = Column(Float, default=50.0)
    water_score = Column(Float, default=50.0)

    constituency = relationship("Constituency", back_populates="dataset")
