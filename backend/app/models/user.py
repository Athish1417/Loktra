import enum

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class UserRole(str, enum.Enum):
    citizen = "citizen"
    officer = "officer"
    mp = "mp"
    super_admin = "super_admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.citizen)

    # Scopes MPs and Officers to a constituency. The "assigned MP" of a
    # constituency is simply the User with role=mp whose constituency_id matches;
    # this avoids a mutual FK between users and constituencies.
    constituency_id = Column(
        Integer, ForeignKey("constituencies.id"), nullable=True
    )

    # Citizen's residential/default location, collected once at registration and
    # pre-filled on the report form (they can still report for another location).
    home_state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
    home_district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
    home_constituency_id = Column(
        Integer, ForeignKey("constituencies.id"), nullable=True
    )
    home_ward_id = Column(Integer, ForeignKey("wards.id"), nullable=True)

    is_active = Column(Boolean, default=True)

    constituency = relationship(
        "Constituency",
        foreign_keys=[constituency_id],
        back_populates="members",
    )
