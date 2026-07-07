"""Government-dataset import foundation (CSV -> Dataset rows).

This is the structure for loading REAL datasets later (e.g. data.gov.in / Census
India exports). It validates required columns, resolves each row to a seeded
constituency, upserts the metrics, and records dataset-source metadata so the UI
can honestly show the mode. Until a real CSV is imported the app keeps its clearly
labelled sample data.

Expected CSV columns:
  required: state, district, constituency, population, schools_count,
            hospitals_count, road_access_score, water_availability_score
  optional: ward, literacy_rate, health_centres
"""
import csv
import io
from typing import IO, List, Optional

from sqlalchemy.orm import Session

from app.models.dataset import Dataset, DatasetMeta
from app.models.location import Constituency, District, State

REQUIRED_COLUMNS = [
    "state",
    "district",
    "constituency",
    "population",
    "schools_count",
    "hospitals_count",
    "road_access_score",
    "water_availability_score",
]
OPTIONAL_COLUMNS = ["ward", "literacy_rate", "health_centres"]


class DatasetImportError(ValueError):
    """Raised when the CSV is malformed or missing required columns."""


def validate_columns(header: List[str]) -> None:
    present = {(h or "").strip().lower() for h in header}
    missing = [c for c in REQUIRED_COLUMNS if c not in present]
    if missing:
        raise DatasetImportError(
            f"CSV is missing required column(s): {', '.join(missing)}"
        )


def _num(value, cast=float, default=0):
    try:
        return cast(str(value).strip())
    except (TypeError, ValueError):
        return default


def _resolve_constituency(
    db: Session, state: str, district: str, constituency: str
) -> Optional[Constituency]:
    return (
        db.query(Constituency)
        .join(District, Constituency.district_id == District.id)
        .join(State, District.state_id == State.id)
        .filter(
            State.name.ilike(state.strip()),
            District.name.ilike(district.strip()),
            Constituency.name.ilike(constituency.strip()),
        )
        .first()
    )


def import_rows(
    db: Session,
    rows: List[dict],
    *,
    source_name: str,
    dataset_name: str = "Imported Government Dataset",
    source_url: Optional[str] = None,
    is_official: bool = False,
    replace: bool = False,
) -> dict:
    """Upsert Dataset metrics from parsed CSV rows and update source metadata."""
    if replace:
        # Safe replace: clear existing metrics only (constituencies are untouched).
        db.query(Dataset).delete()

    imported, unmatched = 0, []
    for row in rows:
        low = {(k or "").strip().lower(): v for k, v in row.items()}
        cons = _resolve_constituency(
            db, low.get("state", ""), low.get("district", ""),
            low.get("constituency", ""),
        )
        if not cons:
            unmatched.append(
                f"{low.get('constituency')} / {low.get('district')} / {low.get('state')}"
            )
            continue

        ds = (
            db.query(Dataset)
            .filter(Dataset.constituency_id == cons.id)
            .first()
        )
        if not ds:
            ds = Dataset(constituency_id=cons.id)
            db.add(ds)
        ds.population = _num(low.get("population"), int, 0)
        ds.schools = _num(low.get("schools_count"), int, 0)
        ds.hospitals = _num(low.get("hospitals_count"), int, 0)
        ds.road_score = _num(low.get("road_access_score"), float, 50.0)
        ds.water_score = _num(low.get("water_availability_score"), float, 50.0)
        imported += 1

    _set_meta(
        db,
        dataset_name=dataset_name,
        source_name=source_name,
        source_url=source_url,
        is_official=is_official,
    )
    db.commit()
    return {
        "imported": imported,
        "unmatched": unmatched,
        "mode": dataset_mode(is_official),
    }


def import_csv(db: Session, file: IO[bytes], **kwargs) -> dict:
    """Parse an uploaded CSV file object and import its rows."""
    raw = file.read()
    text = raw.decode("utf-8-sig") if isinstance(raw, bytes) else raw
    reader = csv.DictReader(io.StringIO(text))
    validate_columns(reader.fieldnames or [])
    return import_rows(db, list(reader), **kwargs)


# --------------------------------------------------------------------------- #
# Dataset-source metadata
# --------------------------------------------------------------------------- #
def dataset_mode(is_official: bool) -> str:
    return "Real Government Dataset Imported" if is_official else "Sample Data"


def get_meta(db: Session) -> DatasetMeta:
    """Return the single dataset-meta row, creating the sample default if absent."""
    meta = db.query(DatasetMeta).first()
    if not meta:
        meta = DatasetMeta()  # sample defaults, is_official=False
        db.add(meta)
        db.commit()
        db.refresh(meta)
    return meta


def _set_meta(
    db: Session,
    *,
    dataset_name: str,
    source_name: str,
    source_url: Optional[str],
    is_official: bool,
) -> DatasetMeta:
    import datetime

    meta = get_meta(db)
    meta.dataset_name = dataset_name
    meta.source_name = source_name
    meta.source_url = source_url
    meta.is_official = is_official
    meta.imported_at = datetime.datetime.utcnow()
    db.add(meta)
    return meta
