"""Application configuration.

All settings have safe local-dev defaults, so the app boots with no .env file.
Override anything by copying .env.example -> .env.
"""
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- Project ---
    PROJECT_NAME: str = "Loktra"
    API_V1_PREFIX: str = "/api/v1"

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./loktra.db"

    # --- Auth / JWT ---
    JWT_SECRET_KEY: str = "change-me-loktra-dev-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # --- AI ---
    # auto -> Gemini if key present else fallback; gemini -> force; fallback -> force rule-based
    AI_PROVIDER: str = "auto"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # --- Storage ---
    UPLOAD_DIR: str = "uploads"

    # --- Government datasets (real official files live under here) ---
    DATASETS_DIR: str = "datasets"

    # --- CORS (Vite dev server by default) ---
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]


settings = Settings()
