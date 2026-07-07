"""Pluggable AI provider.

The rest of the app depends ONLY on this interface, never on Gemini directly.
`get_ai_provider()` returns a singleton chosen from config:

    AI_PROVIDER=auto     -> Gemini if GEMINI_API_KEY set, else FallbackProvider
    AI_PROVIDER=gemini   -> GeminiProvider (which itself falls back at runtime on error)
    AI_PROVIDER=fallback -> FallbackProvider (no external calls, no key)

This is why the whole platform runs and demos even with no API key.
"""
from abc import ABC, abstractmethod

from app.schemas.ai import AnalysisResult, RelevanceResult


class AIProvider(ABC):
    name: str = "base"

    @abstractmethod
    def check_relevance(self, text: str) -> RelevanceResult:
        """Governance-relevance gate applied BEFORE a complaint is stored."""

    @abstractmethod
    def analyze(self, text: str) -> AnalysisResult:
        """Category, urgency, summary, reason, emergency flag."""

    @abstractmethod
    def detect_language(self, text: str) -> str:
        """Return an ISO 639-1 code (en, hi, te, ...)."""

    @abstractmethod
    def translate(self, text: str, target: str = "en") -> str:
        """Translate text to `target` language code."""


_provider_singleton: AIProvider | None = None


def get_ai_provider() -> AIProvider:
    global _provider_singleton
    if _provider_singleton is not None:
        return _provider_singleton

    from app.ai.fallback_provider import FallbackProvider
    from app.core.config import settings

    choice = (settings.AI_PROVIDER or "auto").lower()

    if choice in ("gemini", "auto") and settings.GEMINI_API_KEY:
        try:
            from app.ai.gemini_provider import GeminiProvider

            _provider_singleton = GeminiProvider()
        except Exception:
            # SDK missing or client init failed -> degrade gracefully.
            _provider_singleton = FallbackProvider()
    else:
        _provider_singleton = FallbackProvider()

    return _provider_singleton


def reset_provider() -> None:
    """Test hook to force re-selection."""
    global _provider_singleton
    _provider_singleton = None
