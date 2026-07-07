"""Super-admin endpoints: manage the location tree and create staff users."""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db.session import get_db
from app.models.location import Constituency, District, State, Ward
from app.models.user import User
from app.schemas.location import (
    ConstituencyCreate,
    ConstituencyOut,
    DistrictCreate,
    DistrictOut,
    StateCreate,
    StateOut,
    WardCreate,
    WardOut,
)
from app.schemas.user import UserCreate, UserOut
from app.services import auth_service, dashboard_service

router = APIRouter(
    prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)]
)


# --- Location tree ---------------------------------------------------------- #
@router.post("/states", response_model=StateOut, status_code=201)
def create_state(payload: StateCreate, db: Session = Depends(get_db)):
    state = State(name=payload.name, code=payload.code)
    db.add(state)
    db.commit()
    db.refresh(state)
    return state


@router.post("/districts", response_model=DistrictOut, status_code=201)
def create_district(payload: DistrictCreate, db: Session = Depends(get_db)):
    district = District(name=payload.name, state_id=payload.state_id)
    db.add(district)
    db.commit()
    db.refresh(district)
    return district


@router.post("/constituencies", response_model=ConstituencyOut, status_code=201)
def create_constituency(
    payload: ConstituencyCreate, db: Session = Depends(get_db)
):
    constituency = Constituency(name=payload.name, district_id=payload.district_id)
    db.add(constituency)
    db.commit()
    db.refresh(constituency)
    return constituency


@router.post("/wards", response_model=WardOut, status_code=201)
def create_ward(payload: WardCreate, db: Session = Depends(get_db)):
    ward = Ward(name=payload.name, constituency_id=payload.constituency_id)
    db.add(ward)
    db.commit()
    db.refresh(ward)
    return ward


# --- Users ------------------------------------------------------------------ #
@router.post("/users", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Create any user (including MP/officer) with an explicit role + constituency."""
    return auth_service.register_user(db, payload, allow_privileged=True)


@router.get("/users", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id).all()


# --- Platform summary ------------------------------------------------------- #
@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    """Platform-wide totals plus state-wise and constituency-wise breakdowns."""
    return dashboard_service.admin_summary(db)
