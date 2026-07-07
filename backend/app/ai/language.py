"""Language handling: detect + translate to English.

Architecture note: today this delegates to the AI provider (Gemini translates;
the offline fallback returns text unchanged). To plug in Google Cloud Translation
or Azure Translator later, implement it here — nothing else needs to change.
"""
from typing import Optional, Tuple

from app.ai.provider import get_ai_provider


def process(text: str, declared_language: Optional[str] = None) -> Tuple[str, str]:
    """Return (language_code, english_text).

    If the caller declares a language we trust it; otherwise we auto-detect.
    """
    provider = get_ai_provider()
    language = (declared_language or "").strip().lower() or provider.detect_language(text)

    if language == "en":
        return "en", text

    english = provider.translate(text, target="en")
    return language, english
