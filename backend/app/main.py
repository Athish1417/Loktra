"""FastAPI application factory for Loktra AI."""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base  # noqa: F401  (imports all models -> full metadata)
from app.db.session import engine


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="AI-powered constituency intelligence & civic grievance platform.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create tables on boot (seed via `python -m app.db.init_db`).
    Base.metadata.create_all(bind=engine)

    # Guarantee the demo login accounts exist with the correct roles on every boot.
    # Done here (not only on the ASGI startup event) so it runs under any server
    # setup. Never blocks boot.
    try:
        from app.db.session import SessionLocal
        from app.services import auth_service

        _db = SessionLocal()
        try:
            auth_service.ensure_demo_users(_db)
        finally:
            _db.close()
    except Exception:  # pragma: no cover - never block boot
        pass

    # Serve uploaded media.
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    app.mount(
        "/uploads",
        StaticFiles(directory=settings.UPLOAD_DIR),
        name="uploads",
    )

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.on_event("startup")
    def _sync_official_locations():
        """Backfill locations from any already-imported official datasets on boot,
        so imported states/districts/wards are selectable even if they were imported
        before this hook existed. Idempotent + non-fatal."""
        from app.db.session import SessionLocal
        from app.services import official_locations

        db = SessionLocal()
        try:
            from app.services import auth_service, routing_service

            auth_service.ensure_demo_users(db)      # demo logins on a fresh deploy
            official_locations.seed_predefined(db)  # all-India fallback master data
            official_locations.sync(db)             # imported official locations on top
            routing_service.backfill(db)            # route any complaints missing mp_id
        except Exception:  # pragma: no cover - defensive
            pass
        finally:
            db.close()

    @app.get("/", tags=["meta"])
    def root():
        from app.ai.provider import get_ai_provider

        return {
            "name": settings.PROJECT_NAME,
            "status": "ok",
            "ai_provider": get_ai_provider().name,
            "docs": "/docs",
        }

    @app.get("/health", tags=["meta"])
    def health():
        return {"status": "healthy"}

    return app


app = create_app()
