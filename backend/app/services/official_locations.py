"""Phase 5.2 — materialise imported official-dataset locations into the routing tables.

The complaint pipeline routes and scopes by FK ids (State → District → Constituency
→ Ward). Imported official datasets (Census / LGD / NFHS / PIN / Election) carry
location *names*, not ids, so on their own they can't be selected on the submit form
or routed. This module upserts those names into the location tables (case-insensitive,
idempotent) so the existing, already-searchable dropdowns cover wherever official data
was imported — while the seeded demo locations remain as a fallback.

It is additive and safe: run after an import, wrapped by the caller; on any error it
rolls back only its own inserts (the import itself has already been committed).
"""
import logging
import re
from collections import defaultdict

from sqlalchemy.orm import Session

from app.db.india_locations import INDIA_LOCATIONS
from app.models.gov_dataset import (
    ElectionConstituencyRecord,
    LgdLocationRecord,
    NfhsRecord,
    PincodeRecord,
    PopulationRecord,
)
from app.models.location import Constituency, District, State, Ward

logger = logging.getLogger(__name__)

# Cap ward/village creation per sync so a very large village file can't explode the
# location table in a single request. Anything beyond this is skipped (logged).
_WARD_CAP = 5000


def _norm(value) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).lower()


def seed_predefined(db: Session) -> dict:
    """Upsert the predefined all-India state/district master data. Idempotent.

    Each district gets a default constituency (= district name) so it is
    selectable and routable. Existing (seeded/imported) locations are preserved.
    """
    created = {"states": 0, "districts": 0, "constituencies": 0}
    try:
        state_cache = {_norm(s.name): s for s in db.query(State).all()}
        district_cache = {
            (d.state_id, _norm(d.name)): d for d in db.query(District).all()
        }
        # Districts that already have at least one constituency (from the demo seed
        # or a prior run) — we must NOT add a shadow default constituency to those,
        # or citizens could pick a constituency that has no MP/officer attached.
        districts_with_cons = {c.district_id for c in db.query(Constituency).all()}

        for state_name, districts in INDIA_LOCATIONS.items():
            sk = _norm(state_name)
            st = state_cache.get(sk)
            if st is None:
                st = State(name=state_name)
                db.add(st)
                db.flush()
                state_cache[sk] = st
                created["states"] += 1
            for dname in districts:
                dk = (st.id, _norm(dname))
                d = district_cache.get(dk)
                if d is None:
                    d = District(name=dname, state_id=st.id)
                    db.add(d)
                    db.flush()
                    district_cache[dk] = d
                    created["districts"] += 1
                # Only give a district a default constituency when it has none yet.
                if d.id not in districts_with_cons:
                    db.add(Constituency(name=dname, district_id=d.id))
                    districts_with_cons.add(d.id)
                    created["constituencies"] += 1

        db.commit()
        return created
    except Exception:
        db.rollback()
        raise


def sync(db: Session) -> dict:
    """Upsert States/Districts/Constituencies/Wards from imported records. Idempotent."""
    created = {"states": 0, "districts": 0, "constituencies": 0, "wards": 0}
    try:
        state_cache = {_norm(s.name): s for s in db.query(State).all()}
        district_cache = {
            (d.state_id, _norm(d.name)): d for d in db.query(District).all()
        }
        cons_cache = {
            (c.district_id, _norm(c.name)): c for c in db.query(Constituency).all()
        }
        cons_by_district = defaultdict(list)
        for c in cons_cache.values():
            cons_by_district[c.district_id].append(c)
        ward_cache = {
            (w.constituency_id, _norm(w.name)): w for w in db.query(Ward).all()
        }

        def get_state(name):
            k = _norm(name)
            if not k:
                return None
            st = state_cache.get(k)
            if st is None:
                st = State(name=str(name).strip())
                db.add(st)
                db.flush()
                state_cache[k] = st
                created["states"] += 1
            return st

        def get_district(state, name):
            if state is None or not _norm(name):
                return None
            k = (state.id, _norm(name))
            d = district_cache.get(k)
            if d is None:
                d = District(name=str(name).strip(), state_id=state.id)
                db.add(d)
                db.flush()
                district_cache[k] = d
                created["districts"] += 1
            return d

        def get_constituency(district, name):
            if district is None or not _norm(name):
                return None
            k = (district.id, _norm(name))
            c = cons_cache.get(k)
            if c is None:
                c = Constituency(name=str(name).strip(), district_id=district.id)
                db.add(c)
                db.flush()
                cons_cache[k] = c
                cons_by_district[district.id].append(c)
                created["constituencies"] += 1
            return c

        def get_ward(cons, name):
            if cons is None or not _norm(name):
                return None
            k = (cons.id, _norm(name))
            w = ward_cache.get(k)
            if w is None:
                w = Ward(name=str(name).strip(), constituency_id=cons.id)
                db.add(w)
                db.flush()
                ward_cache[k] = w
                created["wards"] += 1
            return w

        def distinct(model, *cols):
            return db.query(*[getattr(model, c) for c in cols]).distinct().all()

        # Constituencies come from election records (state, district, constituency).
        for s, d, c in distinct(
            ElectionConstituencyRecord, "state", "district", "constituency"
        ):
            get_constituency(get_district(get_state(s), d), c)

        # States + districts from every record type that carries them.
        for model in (PopulationRecord, LgdLocationRecord, NfhsRecord, PincodeRecord):
            for s, d in distinct(model, "state", "district"):
                get_district(get_state(s), d)

        # Every imported district needs at least one constituency so it can be
        # selected and routed — default it to the district name where none exists.
        for d in list(district_cache.values()):
            if not cons_by_district.get(d.id):
                get_constituency(d, d.name)

        # Wards/villages from LGD + Census, attached to the district's first
        # constituency (villages aren't tied to a specific constituency in the data).
        for model in (LgdLocationRecord, PopulationRecord):
            if created["wards"] >= _WARD_CAP:
                break
            for s, d, v in distinct(model, "state", "district", "village"):
                if not _norm(v):
                    continue
                district = get_district(get_state(s), d)
                if district is None:
                    continue
                first = cons_by_district.get(district.id)
                cons = first[0] if first else get_constituency(district, district.name)
                get_ward(cons, v)
                if created["wards"] >= _WARD_CAP:
                    logger.warning("official_locations.sync hit ward cap (%s)", _WARD_CAP)
                    break

        db.commit()
        return created
    except Exception:
        db.rollback()
        raise
