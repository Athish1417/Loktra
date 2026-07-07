"""CRUD for the per-constituency government dataset used in priority scoring."""
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.models.location import Constituency
from app.schemas.dataset import DatasetUpsert


def get_for_constituency(db: Session, constituency_id: int) -> Optional[Dataset]:
    return (
        db.query(Dataset)
        .filter(Dataset.constituency_id == constituency_id)
        .first()
    )


def list_all(db: Session) -> List[Dataset]:
    return db.query(Dataset).all()


def upsert(db: Session, constituency_id: int, payload: DatasetUpsert) -> Dataset:
    constituency = (
        db.query(Constituency).filter(Constituency.id == constituency_id).first()
    )
    if not constituency:
        raise HTTPException(status_code=404, detail="Constituency not found.")

    dataset = get_for_constituency(db, constituency_id)
    if dataset is None:
        dataset = Dataset(constituency_id=constituency_id)
        db.add(dataset)

    dataset.population = payload.population
    dataset.schools = payload.schools
    dataset.hospitals = payload.hospitals
    dataset.road_score = payload.road_score
    dataset.water_score = payload.water_score

    db.commit()
    db.refresh(dataset)
    return dataset
