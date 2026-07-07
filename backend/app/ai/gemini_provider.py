"""Gemini-backed provider.

The google-genai SDK is imported lazily so the app runs even when it is not
installed. Every call is wrapped: if Gemini errors (network, quota, parse), we
transparently fall back to the rule-based provider, so a live demo never dies.
"""
import json
from typing import Any

from app.ai import prompts
from app.ai.fallback_provider import FallbackProvider
from app.ai.provider import AIProvider
from app.core.config import settings
from app.schemas.ai import AnalysisResult, RelevanceResult


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(self) -> None:
        # Lazy import: raises if SDK absent -> factory catches and uses fallback.
        from google import genai  # type: ignore

        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self._model = settings.GEMINI_MODEL
        self._fallback = FallbackProvider()

    # ------------------------------------------------------------------ #
    # Low-level calls
    # ------------------------------------------------------------------ #
    def _generate(self, prompt: str) -> str:
        resp = self._client.models.generate_content(
            model=self._model, contents=prompt
        )
        return (resp.text or "").strip()

    @staticmethod
    def _extract_json(raw: str) -> dict[str, Any]:
        text = raw.strip().strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("No JSON object in model output")
        return json.loads(text[start : end + 1])

    # ------------------------------------------------------------------ #
    # Interface
    # ------------------------------------------------------------------ #
    def check_relevance(self, text: str) -> RelevanceResult:
        try:
            data = self._extract_json(
                self._generate(
                    prompts.RELEVANCE_PROMPT.format(
                        text=text, categories=prompts.CATEGORY_LIST
                    )
                )
            )
            matched = data.get("matched_category")
            if isinstance(matched, str) and matched.lower() in ("null", "none", ""):
                matched = None
            return RelevanceResult(
                is_relevant=bool(data.get("is_relevant", True)),
                reason=str(data.get("reason", "")),
                matched_category=matched,
            )
        except Exception:
            return self._fallback.check_relevance(text)

    def analyze(self, text: str) -> AnalysisResult:
        try:
            data = self._extract_json(
                self._generate(
                    prompts.ANALYSIS_PROMPT.format(
                        text=text, categories=prompts.CATEGORY_LIST
                    )
                )
            )
            return AnalysisResult(
                category=str(data.get("category", "Others")),
                urgency=str(data.get("urgency", "Medium")),
                summary=str(data.get("summary", "")),
                reason=str(data.get("reason", "")),
                is_emergency=bool(data.get("is_emergency", False)),
            )
        except Exception:
            return self._fallback.analyze(text)

    def detect_language(self, text: str) -> str:
        try:
            code = self._generate(prompts.DETECT_PROMPT.format(text=text))
            code = code.strip().lower()[:2]
            return code or self._fallback.detect_language(text)
        except Exception:
            return self._fallback.detect_language(text)

    def translate(self, text: str, target: str = "en") -> str:
        try:
            from app.utils.constants import LANGUAGES

            target_name = LANGUAGES.get(target, "English")
            out = self._generate(
                prompts.TRANSLATE_PROMPT.format(
                    text=text, target_language=target_name
                )
            )
            return out or text
        except Exception:
            return self._fallback.translate(text, target)
