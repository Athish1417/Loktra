from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class DatasetSourceOut(BaseModel):
    """Honest description of the current dataset (sample vs real)."""
    dataset_name: str
    source_name: str
    source_url: Optional[str] = None
    is_official: bool
    imported_at: datetime
    mode: str  # "Sample Data" | "Real Government Dataset Imported"
    constituencies_with_data: int


class DatasetImportResult(BaseModel):
    imported: int
    unmatched: List[str] = []
    mode: str


# --- Phase 4: real government dataset import -------------------------------- #
class PreviewRequest(BaseModel):
    path: str
    source_type: str


class ImportFileRequest(BaseModel):
    path: str
    source_type: str
    is_official: bool = True
    dataset_name: Optional[str] = None
    source_name: Optional[str] = None
    source_department: Optional[str] = None
    source_url: Optional[str] = None
    replace: bool = False


class DatasetSourceLogOut(BaseModel):
    id: int
    dataset_name: str
    source_name: str
    source_department: Optional[str] = None
    source_type: Optional[str] = None
    file_name: str
    file_path: Optional[str] = None
    source_url: Optional[str] = None
    is_official: bool
    record_count: int
    import_status: str
    imported_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DatasetBase(BaseModel):
    population: int = 0
    schools: int = 0
    hospitals: int = 0
    road_score: float = 50.0
    water_score: float = 50.0


class DatasetUpsert(DatasetBase):
    pass


class DatasetOut(DatasetBase):
    id: int
    constituency_id: int
    model_config = ConfigDict(from_attributes=True)
