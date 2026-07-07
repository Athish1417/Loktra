"""Importing the models package registers every ORM class on the shared registry,
so SQLAlchemy can always resolve string-based relationships (e.g. relationship("User"))
no matter which module is imported first.
"""
from app.models.user import User, UserRole
from app.models.location import State, District, Constituency, Ward
from app.models.complaint import (
    Complaint,
    ComplaintCategory,
    ComplaintStatusEnum,
    UrgencyLevel,
)
from app.models.complaint_status import ComplaintStatus
from app.models.assignment import Assignment
from app.models.department import Department
from app.models.dataset import Dataset, DatasetMeta
from app.models.gov_dataset import (
    DatasetSource,
    ElectionConstituencyRecord,
    LgdLocationRecord,
    NfhsRecord,
    PincodeRecord,
    PopulationRecord,
)

__all__ = [
    "User",
    "UserRole",
    "State",
    "District",
    "Constituency",
    "Ward",
    "Complaint",
    "ComplaintCategory",
    "ComplaintStatusEnum",
    "UrgencyLevel",
    "ComplaintStatus",
    "Assignment",
    "Department",
    "Dataset",
    "DatasetMeta",
    "DatasetSource",
    "ElectionConstituencyRecord",
    "LgdLocationRecord",
    "NfhsRecord",
    "PincodeRecord",
    "PopulationRecord",
]
