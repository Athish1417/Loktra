"""Thin orchestration wrapper: run complaint analysis via the provider."""
from app.ai.provider import get_ai_provider
from app.schemas.ai import AnalysisResult


def analyze(text: str) -> AnalysisResult:
    return get_ai_provider().analyze(text)
