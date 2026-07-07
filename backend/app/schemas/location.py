from typing import Optional

from pydantic import BaseModel, ConfigDict


class _Named(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class StateOut(_Named):
    code: Optional[str] = None


class DistrictOut(_Named):
    pass


class ConstituencyOut(_Named):
    pass


class WardOut(_Named):
    pass


# --- create payloads (super admin) ---
class StateCreate(BaseModel):
    name: str
    code: Optional[str] = None


class DistrictCreate(BaseModel):
    name: str
    state_id: int


class ConstituencyCreate(BaseModel):
    name: str
    district_id: int


class WardCreate(BaseModel):
    name: str
    constituency_id: int
