"""Phase 5 — official government dataset lookup for AI prioritisation.

Given a complaint's resolved location, finds which imported official datasets
(Census / LGD / NFHS / Election) cover it and packages them into an
``OfficialContext`` the priority engine can score from. Reuses the Phase 4
importer's tables (``app.models.gov_dataset``) and the existing ``gov_datasets``
helpers — the importer itself is untouched.

Every lookup is read-only and defensive: on any missing field, empty dataset or
unexpected error it reports "not matched", so the caller falls back to the sample
dataset and complaint submission never crashes.
"""
import logging
import re
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.gov_dataset import (
    ElectionConstituencyRecord,
    LgdLocationRecord,
    NfhsRecord,
    PincodeRecord,
    PopulationRecord,
)
from app.schemas.ai import OfficialContext
from app.services import gov_datasets

logger = logging.getLogger(__name__)

# NFHS factsheet indicator-name patterns -> stress direction.
#   +1: a HIGHER value means more need   (e.g. anaemia / stunting prevalence)
#   -1: a LOWER value means more need    (e.g. % households with improved sanitation)
# Matched on the normalised indicator NAME, never on a district, so it is reusable
# across any NFHS district/state factsheet without hardcoding places.
_NFHS_STRESS_PATTERNS = [
    ("anaemi", 1), ("anemia", 1), ("stunted", 1), ("wasted", 1),
    ("underweight", 1), ("diarrhoea", 1), ("diarrhea", 1),
    ("improvedsanitation", -1), ("improveddrinkingwater", -1),
    ("drinkingwater", -1), ("cleanfuel", -1),
    ("institutionalbirth", -1), ("institutionaldeliver", -1), ("antenatal", -1),
]


def _clean(name: Optional[str]) -> Optional[str]:
    if isinstance(name, str) and name.strip():
        return name.strip()
    return None


def _norm(text) -> str:
    return re.sub(r"[^a-z0-9]", "", str(text or "").lower())


def _to_num(value) -> Optional[float]:
    try:
        return float(str(value).replace(",", "").replace("%", "").strip())
    except (TypeError, ValueError):
        return None


def lookup(
    db: Session,
    *,
    state: Optional[str] = None,
    district: Optional[str] = None,
    constituency: Optional[str] = None,
    village: Optional[str] = None,
    ward: Optional[str] = None,
    pincode: Optional[str] = None,
) -> OfficialContext:
    """Resolve every official dataset matching this location. Never raises."""
    try:
        return _lookup(
            db,
            state=_clean(state),
            district=_clean(district),
            constituency=_clean(constituency),
            village=_clean(village),
            ward=_clean(ward),
            pincode=_clean(pincode),
        )
    except Exception:  # official data must never break complaint submission
        logger.exception("official_data.lookup failed; falling back to sample data")
        return OfficialContext()


def _lookup(db, *, state, district, constituency, village, ward, pincode):
    ctx = OfficialContext()

    # --- Census: real district population + households --------------------- #
    ctx.population = gov_datasets.real_population_for(db, state, district)
    if district:
        rows = _census_rows(db, state, district)
        if rows:
            ctx.census = True
            households = sum(r.households for r in rows if r.households)
            ctx.households = households or None

    # --- LGD: village / panchayat / administrative-hierarchy validation ---- #
    if district:
        ctx.lgd = _lgd_match(db, state, district, place=village or ward, pincode=pincode)

    # --- NFHS: district (else state) health/sanitation/nutrition context --- #
    if district or state:
        indicators = _nfhs_indicators(db, state, district)
        if indicators is not None:
            ctx.nfhs = True
            ctx.nfhs_stress = _nfhs_stress(indicators)

    # --- Election: constituency context ------------------------------------ #
    if constituency:
        ctx.election = (
            db.query(ElectionConstituencyRecord.id)
            .filter(ElectionConstituencyRecord.constituency.ilike(constituency))
            .first()
            is not None
        )

    return ctx


# --------------------------------------------------------------------------- #
# Per-dataset lookups (each returns safely on missing data)
# --------------------------------------------------------------------------- #
def _census_rows(db, state, district) -> List[PopulationRecord]:
    q = db.query(PopulationRecord).filter(PopulationRecord.district.ilike(district))
    if state:
        q = q.filter(PopulationRecord.state.ilike(state))
    return q.all()


def _lgd_match(db, state, district, place=None, pincode=None) -> bool:
    base = db.query(LgdLocationRecord.id).filter(
        LgdLocationRecord.district.ilike(district)
    )
    if state:
        base = base.filter(LgdLocationRecord.state.ilike(state))
    # Prefer an exact village/panchayat validation when we know the place name.
    if place and base.filter(LgdLocationRecord.village.ilike(place)).first() is not None:
        return True
    # Otherwise a district-level LGD row still validates the admin hierarchy.
    if base.first() is not None:
        return True
    # A matching PIN-code post office also confirms the location exists.
    if pincode:
        pin = db.query(PincodeRecord.id).filter(PincodeRecord.pincode == pincode)
        if state:
            pin = pin.filter(PincodeRecord.state.ilike(state))
        return pin.first() is not None
    return False


def _nfhs_indicators(db, state, district) -> Optional[dict]:
    row = None
    if district:
        q = db.query(NfhsRecord).filter(NfhsRecord.district.ilike(district))
        if state:
            q = q.filter(NfhsRecord.state.ilike(state))
        row = q.first()
    if row is None and state:
        row = (
            db.query(NfhsRecord)
            .filter(NfhsRecord.state.ilike(state), NfhsRecord.district.is_(None))
            .first()
        )
    if row is None:
        return None
    return row.indicators if isinstance(row.indicators, dict) else {}


def _nfhs_stress(indicators: dict) -> Optional[float]:
    """Aggregate a 0..1 "health need" signal from recognised NFHS indicators.

    Returns None when no known indicator is present/parseable, so the scorer can
    fall back to a neutral presence-only boost.
    """
    scores = []
    for name, value in indicators.items():
        num = _to_num(value)
        if num is None:
            continue
        key = _norm(name)
        for pattern, direction in _NFHS_STRESS_PATTERNS:
            if pattern in key:
                frac = num / 100.0 if direction > 0 else (100.0 - num) / 100.0
                scores.append(max(0.0, min(1.0, frac)))
                break
    if not scores:
        return None
    return round(sum(scores) / len(scores), 3)
