"""Public location lookups that drive the cascading dropdowns + search on the
submit form. Backed by the location tables, which are seeded with demo data AND
kept in sync with every imported official dataset (see official_locations.sync),
so they cover all Indian states/districts/wards that have been imported."""
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.location import Constituency, District, State, Ward
from app.schemas.location import (
    ConstituencyOut,
    DistrictOut,
    StateOut,
    WardOut,
)

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/states", response_model=List[StateOut])
def list_states(db: Session = Depends(get_db)):
    return db.query(State).order_by(State.name).all()


@router.get("/districts", response_model=List[DistrictOut])
def list_districts(
    state_id: Optional[int] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Districts for a state — accepts either state_id or the state name."""
    q = db.query(District)
    if state_id is not None:
        q = q.filter(District.state_id == state_id)
    elif state:
        q = q.join(State).filter(State.name.ilike(state.strip()))
    return q.order_by(District.name).all()


@router.get("/constituencies", response_model=List[ConstituencyOut])
def list_constituencies(district_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Constituency)
        .filter(Constituency.district_id == district_id)
        .order_by(Constituency.name)
        .all()
    )


@router.get("/constituencies-index")
def constituencies_index(db: Session = Depends(get_db)):
    """Flat list of every constituency with its district/state ids, in ONE query.

    Lets the frontend build a constituency lookup with a single request instead of
    walking the whole State→District→Constituency tree (which is slow once many
    locations are seeded/imported).
    """
    rows = (
        db.query(
            Constituency.id,
            Constituency.name,
            Constituency.district_id,
            District.state_id,
        )
        .join(District, Constituency.district_id == District.id)
        .all()
    )
    return [
        {"id": cid, "name": name, "district_id": did, "state_id": sid}
        for cid, name, did, sid in rows
    ]


@router.get("/wards", response_model=List[WardOut])
def list_wards(
    constituency_id: Optional[int] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Wards/villages for a constituency, or for a whole district by name."""
    q = db.query(Ward)
    if constituency_id is not None:
        q = q.filter(Ward.constituency_id == constituency_id)
    elif district:
        dq = db.query(District.id).filter(District.name.ilike(district.strip()))
        if state:
            dq = dq.join(State).filter(State.name.ilike(state.strip()))
        district_ids = [r[0] for r in dq.all()]
        cons_ids = [
            r[0]
            for r in db.query(Constituency.id)
            .filter(Constituency.district_id.in_(district_ids))
            .all()
        ]
        q = q.filter(Ward.constituency_id.in_(cons_ids))
    return q.order_by(Ward.name).all()


@router.get("/search")
def search_locations(q: str, limit: int = 20, db: Session = Depends(get_db)):
    """Case-insensitive partial search across states/districts/cities/wards.

    Returns normalized results, each with the full resolved path (ids + names) so
    the form can jump straight to a location — e.g. searching "visakhapatnam".
    """
    term = f"%{q.strip()}%"
    out: List[dict] = []

    for s in db.query(State).filter(State.name.ilike(term)).limit(limit).all():
        out.append({
            "type": "state", "label": s.name,
            "state_id": s.id, "state": s.name,
            "district_id": None, "district": None,
            "constituency_id": None, "constituency": None,
            "ward_id": None, "ward": None,
        })
    for d in db.query(District).filter(District.name.ilike(term)).limit(limit).all():
        out.append({
            "type": "district", "label": f"{d.name}, {d.state.name}",
            "state_id": d.state_id, "state": d.state.name,
            "district_id": d.id, "district": d.name,
            "constituency_id": None, "constituency": None,
            "ward_id": None, "ward": None,
        })
    for c in db.query(Constituency).filter(Constituency.name.ilike(term)).limit(limit).all():
        out.append({
            "type": "constituency", "label": f"{c.name}, {c.district.name}",
            "state_id": c.district.state_id, "state": c.district.state.name,
            "district_id": c.district_id, "district": c.district.name,
            "constituency_id": c.id, "constituency": c.name,
            "ward_id": None, "ward": None,
        })
    for w in db.query(Ward).filter(Ward.name.ilike(term)).limit(limit).all():
        con = w.constituency
        dis = con.district
        out.append({
            "type": "ward", "label": f"{w.name}, {dis.name}",
            "state_id": dis.state_id, "state": dis.state.name,
            "district_id": dis.id, "district": dis.name,
            "constituency_id": con.id, "constituency": con.name,
            "ward_id": w.id, "ward": w.name,
        })
    return out[:limit]
