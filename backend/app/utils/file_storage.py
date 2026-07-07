"""Persist uploaded media (image / voice) to the local UPLOAD_DIR.

Returns a web path (e.g. /uploads/xyz.png) that the frontend can render directly,
since main.py mounts UPLOAD_DIR at /uploads. Swap this module for S3/GCS later
without touching the services that call it.
"""
import os
import uuid
from typing import Optional

from fastapi import UploadFile

from app.core.config import settings

IMAGE_SUBDIR = "images"
VOICE_SUBDIR = "voice"


def _ensure(subdir: str) -> str:
    path = os.path.join(settings.UPLOAD_DIR, subdir)
    os.makedirs(path, exist_ok=True)
    return path


def _save(upload: UploadFile, subdir: str) -> str:
    folder = _ensure(subdir)
    ext = os.path.splitext(upload.filename or "")[1].lower() or ""
    fname = f"{uuid.uuid4().hex}{ext}"
    dest = os.path.join(folder, fname)
    with open(dest, "wb") as f:
        f.write(upload.file.read())
    # web-accessible path (forward slashes regardless of OS)
    return f"/{settings.UPLOAD_DIR}/{subdir}/{fname}".replace("\\", "/")


def save_image(upload: Optional[UploadFile]) -> Optional[str]:
    if not upload or not upload.filename:
        return None
    return _save(upload, IMAGE_SUBDIR)


def save_voice(upload: Optional[UploadFile]) -> Optional[str]:
    if not upload or not upload.filename:
        return None
    return _save(upload, VOICE_SUBDIR)
