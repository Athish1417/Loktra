"""Aggregate metadata module.

Import this (via create_all / init_db) when you need Base.metadata to know about
EVERY table. Models themselves import Base from base_class to avoid a cycle.
"""
from app.db.base_class import Base  # noqa: F401

# Register all tables on Base.metadata.
from app.models.user import User  # noqa: E402,F401
from app.models.location import (  # noqa: E402,F401
    State,
    District,
    Constituency,
    Ward,
)
from app.models.complaint import Complaint  # noqa: E402,F401
from app.models.complaint_status import ComplaintStatus  # noqa: E402,F401
from app.models.assignment import Assignment  # noqa: E402,F401
from app.models.department import Department  # noqa: E402,F401
from app.models.dataset import Dataset, DatasetMeta  # noqa: E402,F401
from app.models.gov_dataset import (  # noqa: E402,F401
    DatasetSource,
    ElectionConstituencyRecord,
    LgdLocationRecord,
    NfhsRecord,
    PincodeRecord,
    PopulationRecord,
)
