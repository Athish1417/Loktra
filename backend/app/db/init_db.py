"""Seed the database with a realistic demo dataset.

Run:  python -m app.db.init_db     (from the backend/ directory)

This DROPS and recreates all tables for a clean, deterministic demo, then seeds:
  - a 2-state location tree (Maharashtra, Telangana)
  - per-constituency government datasets (varied infra scores)
  - demo users for every role
  - civic departments
  - sample complaints pushed through the AI + priority pipeline, with some
    advanced through the workflow so MP dashboards are populated.

Complaints are scoped to two constituencies (Goregaon, Serilingampally), each
with its own MP + officer, so role-based visibility is easy to demonstrate.
"""
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.department import Department
from app.models.dataset import Dataset, DatasetMeta
from app.models.location import Constituency, District, State, Ward
from app.models.user import User, UserRole
from app.schemas.complaint import ComplaintCreate
from app.services import assignment_service, complaint_service


def _reset() -> None:
    print("Dropping and recreating all tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _seed_locations(db: Session) -> dict:
    """Build the location tree and return a lookup of key objects."""
    mh = State(name="Maharashtra", code="MH")
    tg = State(name="Telangana", code="TG")
    db.add_all([mh, tg])
    db.flush()

    mumbai = District(name="Mumbai Suburban", state_id=mh.id)
    hyderabad = District(name="Hyderabad", state_id=tg.id)
    db.add_all([mumbai, hyderabad])
    db.flush()

    goregaon = Constituency(name="Goregaon", district_id=mumbai.id)
    andheri = Constituency(name="Andheri West", district_id=mumbai.id)
    serili = Constituency(name="Serilingampally", district_id=hyderabad.id)
    kukatpally = Constituency(name="Kukatpally", district_id=hyderabad.id)
    db.add_all([goregaon, andheri, serili, kukatpally])
    db.flush()

    wards = [
        Ward(name="Aarey Colony", constituency_id=goregaon.id),
        Ward(name="Motilal Nagar", constituency_id=goregaon.id),
        Ward(name="Versova", constituency_id=andheri.id),
        Ward(name="Lokhandwala", constituency_id=andheri.id),
        Ward(name="Gachibowli", constituency_id=serili.id),
        Ward(name="Kondapur", constituency_id=serili.id),
        Ward(name="KPHB", constituency_id=kukatpally.id),
        Ward(name="Moosapet", constituency_id=kukatpally.id),
    ]
    db.add_all(wards)
    db.flush()

    # Datasets (higher score = better existing infrastructure).
    db.add_all([
        Dataset(constituency_id=goregaon.id, population=300_000, schools=40,
                hospitals=6, road_score=45, water_score=38),
        Dataset(constituency_id=andheri.id, population=350_000, schools=55,
                hospitals=9, road_score=60, water_score=65),
        Dataset(constituency_id=serili.id, population=400_000, schools=60,
                hospitals=10, road_score=55, water_score=50),
        Dataset(constituency_id=kukatpally.id, population=380_000, schools=45,
                hospitals=7, road_score=48, water_score=42),
    ])
    db.flush()

    return {
        "mh": mh, "tg": tg, "mumbai": mumbai, "hyderabad": hyderabad,
        "goregaon": goregaon, "andheri": andheri, "serili": serili,
        "kukatpally": kukatpally, "wards": {w.name: w for w in wards},
    }


def _seed_users(db: Session, loc: dict) -> dict:
    def mk(name, email, pwd, role, constituency=None):
        return User(
            name=name, email=email, phone=None,
            hashed_password=hash_password(pwd), role=role,
            constituency_id=constituency.id if constituency else None,
            is_active=True,
        )

    users = {
        "admin": mk("Platform Admin", "admin@loktra.ai", "admin123",
                    UserRole.super_admin),
        "mp_gor": mk("MP Goregaon", "mp@loktra.ai", "mp123456",
                     UserRole.mp, loc["goregaon"]),
        "mp_hyd": mk("MP Serilingampally", "mp.hyd@loktra.ai", "mp123456",
                     UserRole.mp, loc["serili"]),
        "off_gor": mk("Officer Goregaon", "officer@loktra.ai",
                      "officer123", UserRole.officer, loc["goregaon"]),
        "off_hyd": mk("Officer Serilingampally", "officer.hyd@loktra.ai",
                      "officer123", UserRole.officer, loc["serili"]),
        "citizen": mk("Demo Citizen", "citizen@loktra.ai", "citizen123",
                      UserRole.citizen),
    }
    # Give the demo citizen a residential location (Goregaon) so the report form
    # pre-fills a real area that has an MP + officer — complaints route immediately.
    citizen = users["citizen"]
    citizen.home_state_id = loc["mh"].id
    citizen.home_district_id = loc["mumbai"].id
    citizen.home_constituency_id = loc["goregaon"].id
    citizen.home_ward_id = loc["wards"]["Aarey Colony"].id

    db.add_all(list(users.values()))
    db.commit()
    for u in users.values():
        db.refresh(u)
    return users


def _seed_departments(db: Session) -> None:
    departments = [
        ("Public Works Department", "Roads"),
        ("Water Supply Board", "Water Supply"),
        ("Electricity Board", "Electricity"),
        ("Sanitation Department", "Garbage"),
        ("Health Department", "Healthcare"),
        ("Education Department", "Education"),
        ("Municipal Corporation", "Government Services"),
    ]
    db.add_all([Department(name=n, category=c) for n, c in departments])
    db.commit()


def _make(db, citizen, loc, cons_key, ward_name, title, desc):
    c = loc[cons_key]
    ward = loc["wards"][ward_name]
    payload = ComplaintCreate(
        title=title, description=desc, language="en",
        state_id=c.district.state_id, district_id=c.district_id,
        constituency_id=c.id, ward_id=ward.id,
    )
    return complaint_service.create_complaint(db, citizen, payload)


def _advance(db, complaint, officer, mp, steps):
    """steps: any of 'verify', 'assign', 'work_started', 'completed'."""
    for step in steps:
        if step == "verify":
            assignment_service.verify_complaint(db, officer, complaint)
        elif step == "assign":
            assignment_service.assign_officer(db, mp, complaint, officer.id)
        elif step == "work_started":
            assignment_service.update_status(
                db, officer, complaint, "Work Started", "Field work has begun.")
        elif step == "completed":
            assignment_service.update_status(
                db, officer, complaint, "Completed", "Issue resolved and closed.")


def _seed_complaints(db: Session, loc: dict, users: dict) -> int:
    citizen = users["citizen"]
    off_g, mp_g = users["off_gor"], users["mp_gor"]
    off_h, mp_h = users["off_hyd"], users["mp_hyd"]

    # --- Goregaon ---
    c1 = _make(db, citizen, loc, "goregaon", "Aarey Colony",
               "Major water pipeline burst near Aarey Colony",
               "Water gushing out for two days, no supply reaching homes.")
    _advance(db, c1, off_g, mp_g, ["verify", "assign"])

    c2 = _make(db, citizen, loc, "goregaon", "Motilal Nagar",
               "Large potholes on S.V. Road",
               "Multiple deep potholes near the junction causing daily accidents.")
    _advance(db, c2, off_g, mp_g, ["verify"])

    _make(db, citizen, loc, "goregaon", "Motilal Nagar",
          "Street lights not working in Motilal Nagar",
          "The entire lane has been dark for a week, a serious safety concern at night.")

    c4 = _make(db, citizen, loc, "goregaon", "Aarey Colony",
               "Garbage not collected for 5 days",
               "Overflowing bins attracting stray dogs and creating disease risk.")
    _advance(db, c4, off_g, mp_g, ["verify", "assign", "work_started", "completed"])

    c5 = _make(db, citizen, loc, "goregaon", "Aarey Colony",
               "Flooding and wall crack after heavy rain",
               "Waist-deep water logging and a wall has developed a crack; "
               "residents fear the structure may collapse.")
    _advance(db, c5, off_g, mp_g, ["verify", "assign", "work_started"])

    _make(db, citizen, loc, "goregaon", "Motilal Nagar",
          "No power supply since morning",
          "Transformer failure with frequent load shedding across the area.")

    # --- Serilingampally ---
    d1 = _make(db, citizen, loc, "serili", "Gachibowli",
               "Drainage overflow in Gachibowli",
               "Sewage overflowing onto the main road for several days.")
    _advance(db, d1, off_h, mp_h, ["verify", "assign"])

    d2 = _make(db, citizen, loc, "serili", "Kondapur",
               "Shortage of beds at the local PHC",
               "Patients are being turned away; the health centre needs more capacity.")
    _advance(db, d2, off_h, mp_h, ["verify"])

    _make(db, citizen, loc, "serili", "Kondapur",
          "Exposed live wire sparking over footpath",
          "A live wire is hanging and sparking over the footpath near Kondapur, "
          "with a serious risk of electrocution.")

    _make(db, citizen, loc, "serili", "Gachibowli",
          "Poor road condition near IT park",
          "Broken road surface is causing severe traffic jams every morning.")

    return db.query(complaint_service.Complaint).count()


def seed() -> None:
    _reset()
    db = SessionLocal()
    try:
        loc = _seed_locations(db)
        # All-India fallback master data (states + major districts/cities).
        from app.services import official_locations
        official_locations.seed_predefined(db)
        users = _seed_users(db, loc)
        _seed_departments(db)
        # Dataset-source metadata: clearly flagged as sample (is_official=False).
        db.add(DatasetMeta())
        db.commit()
        total = _seed_complaints(db, loc, users)

        print("\n=== Seed complete ===")
        print(f"Complaints created: {total}")
        print("\nLogin credentials (email / password):")
        print("  Super Admin : admin@loktra.ai          / admin123")
        print("  MP/Admin    : mp@loktra.ai             / mp123456")
        print("  Officer     : officer@loktra.ai        / officer123")
        print("  Citizen     : citizen@loktra.ai        / citizen123")
        print("  (demo 2nd constituency: mp.hyd@loktra.ai / mp123456, "
              "officer.hyd@loktra.ai / officer123)")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
