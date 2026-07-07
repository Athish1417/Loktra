"""Aggregate all v1 routers under a single APIRouter."""
from fastapi import APIRouter

from app.api.v1 import admin, auth, complaints, dataset, locations, mp, officer

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(locations.router)
api_router.include_router(complaints.router)
api_router.include_router(officer.router)
api_router.include_router(mp.router)
api_router.include_router(admin.router)
api_router.include_router(dataset.router)
