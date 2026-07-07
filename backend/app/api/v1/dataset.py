"""Government dataset endpoints (view for staff, upsert/import for super admin)."""
import logging
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin, require_staff
from app.db.session import get_db
from app.models.dataset import Dataset
from app.models.user import User
from app.schemas.dataset import (
    DatasetImportResult,
    DatasetOut,
    DatasetSourceLogOut,
    DatasetSourceOut,
    DatasetUpsert,
    ImportFileRequest,
    PreviewRequest,
)
from app.services import (
    dataset_import,
    dataset_service,
    gov_datasets,
    official_locations,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("", response_model=List[DatasetOut])
def list_datasets(
    _: User = Depends(require_staff), db: Session = Depends(get_db)
):
    return dataset_service.list_all(db)


@router.get("/source", response_model=DatasetSourceOut)
def dataset_source(
    _: User = Depends(require_staff), db: Session = Depends(get_db)
):
    """Current dataset mode + source label (Sample vs Official)."""
    meta = dataset_import.get_meta(db)
    official = gov_datasets.has_official_data(db)
    return DatasetSourceOut(
        dataset_name=meta.dataset_name,
        source_name=meta.source_name,
        source_url=meta.source_url,
        is_official=official,
        imported_at=meta.imported_at,
        mode=gov_datasets.current_mode(db),
        constituencies_with_data=db.query(Dataset).count(),
    )


# --- Phase 4: real government dataset files (folder-based) ------------------- #
@router.get("/files")
def list_files(_: User = Depends(require_staff), db: Session = Depends(get_db)):
    """List importable dataset files detected under the datasets/ folders."""
    return {"folders": gov_datasets.SOURCE_TYPES, "files": gov_datasets.scan()}


@router.post("/upload")
def upload_dataset_file(
    file: UploadFile = File(...),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Receive a browser-uploaded CSV/XLS/XLSX into the datasets folder.

    Returns its server path + an auto-detected dataset type; the client then uses
    the existing `/preview` and `/import-file` endpoints on that path.
    """
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in (".csv", ".xlsx", ".xls"):
        raise HTTPException(
            status_code=400, detail="Unsupported file type. Upload CSV, XLS, or XLSX."
        )
    rel = gov_datasets.save_upload(file.file, file.filename or "upload")
    try:
        suggested = gov_datasets.detect_source_type(rel)
    except gov_datasets.DatasetImportError:
        suggested = "imports"
    return {"path": rel, "file_name": os.path.basename(rel), "suggested_type": suggested}


@router.post("/preview")
def preview_file(
    payload: PreviewRequest,
    _: User = Depends(require_staff),
    db: Session = Depends(get_db),
):
    """Preview a dataset file's columns + a few sample rows (with detected fields)."""
    try:
        return gov_datasets.preview(payload.path, payload.source_type)
    except gov_datasets.DatasetImportError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/import-file")
def import_file(
    payload: ImportFileRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Import a detected official dataset file into the database (super admin).

    Skips a file already imported unless `replace=true` (which re-imports it).
    """
    try:
        result = gov_datasets.import_file(
            db,
            rel_path=payload.path,
            source_type=payload.source_type,
            is_official=payload.is_official,
            dataset_name=payload.dataset_name,
            source_name=payload.source_name,
            source_department=payload.source_department,
            source_url=payload.source_url,
            replace=payload.replace,
        )
    except gov_datasets.DatasetImportError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Materialise the imported locations into the routing tables so they become
    # selectable/searchable on the submit form. Never let this fail the import.
    try:
        official_locations.sync(db)
    except Exception:  # pragma: no cover - defensive
        logger.exception("official_locations.sync failed after import (non-fatal)")

    return result


@router.get("/sources", response_model=List[DatasetSourceLogOut])
def imported_sources(
    _: User = Depends(require_staff), db: Session = Depends(get_db)
):
    """Provenance log of imported official datasets (record counts + status)."""
    return gov_datasets.list_sources(db)


@router.delete("/sources/{source_id}")
def delete_source(
    source_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete an imported dataset source and its records (super admin)."""
    if not gov_datasets.delete_source(db, source_id):
        raise HTTPException(status_code=404, detail="Dataset source not found.")
    return {"deleted": source_id, "mode": gov_datasets.current_mode(db)}


@router.post("/import", response_model=DatasetImportResult)
def import_dataset(
    file: UploadFile = File(...),
    source_name: str = Form(...),
    dataset_name: str = Form("Imported Government Dataset"),
    source_url: Optional[str] = Form(None),
    is_official: bool = Form(False),
    replace: bool = Form(False),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Import a real government dataset from a CSV (super admin only).

    Validates required columns, matches rows to constituencies, and records the
    source metadata. Set is_official=true only for a genuine official source.
    """
    try:
        result = dataset_import.import_csv(
            db,
            file.file,
            source_name=source_name,
            dataset_name=dataset_name,
            source_url=source_url,
            is_official=is_official,
            replace=replace,
        )
    except dataset_import.DatasetImportError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return result


@router.get("/{constituency_id}", response_model=DatasetOut)
def get_dataset(
    constituency_id: int,
    _: User = Depends(require_staff),
    db: Session = Depends(get_db),
):
    from fastapi import HTTPException

    ds = dataset_service.get_for_constituency(db, constituency_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return ds


@router.put("/{constituency_id}", response_model=DatasetOut)
def upsert_dataset(
    constituency_id: int,
    payload: DatasetUpsert,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return dataset_service.upsert(db, constituency_id, payload)
