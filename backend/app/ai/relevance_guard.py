"""Thin orchestration wrapper: run the governance-relevance gate via the provider."""
from app.ai.provider import get_ai_provider
from app.schemas.ai import RelevanceResult


def guard(text: str) -> RelevanceResult:
    return get_ai_provider().check_relevance(text)
