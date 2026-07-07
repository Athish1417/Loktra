from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=6)
    role: UserRole = UserRole.citizen
    constituency_id: Optional[int] = None
    # Residential/default location (optional at registration).
    home_state_id: Optional[int] = None
    home_district_id: Optional[int] = None
    home_constituency_id: Optional[int] = None
    home_ward_id: Optional[int] = None


class UserOut(UserBase):
    id: int
    role: UserRole
    constituency_id: Optional[int] = None
    home_state_id: Optional[int] = None
    home_district_id: Optional[int] = None
    home_constituency_id: Optional[int] = None
    home_ward_id: Optional[int] = None
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
