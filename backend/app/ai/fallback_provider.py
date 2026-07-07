"""Deterministic, offline AI provider.

Implements the same interface as Gemini using keyword banks + Unicode script
detection. No API key, no network — so demos never break.
"""
from app.ai.provider import AIProvider
from app.schemas.ai import AnalysisResult, RelevanceResult
from app.utils.constants import (
    BLOCKED_KEYWORDS,
    CATEGORY_KEYWORDS,
    EMERGENCY_KEYWORDS,
    GOVERNANCE_KEYWORDS,
    IRRELEVANT_PATTERNS,
    SCRIPT_RANGES,
)
from app.models.complaint import ComplaintCategory


class FallbackProvider(AIProvider):
    name = "fallback"

    # ------------------------------------------------------------------ #
    # Relevance guard
    # ------------------------------------------------------------------ #
    def check_relevance(self, text: str) -> RelevanceResult:
        """Hard governance-relevance gate — layered rules, reject by default.

        A submission is accepted only when there is a genuine civic signal
        (a category keyword, an emergency keyword, or governance context) AND no
        overriding off-topic signal. Everything else is rejected before it is
        ever saved.
        """
        low = (text or "").lower()

        # Layer 1 — explicit non-civic INTENT (entertainment / sports / shopping /
        # gaming / general questions). Hard reject regardless of stray keywords.
        if any(p.search(low) for p in IRRELEVANT_PATTERNS):
            return RelevanceResult(
                is_relevant=False,
                reason="Recognised as a non-civic request (entertainment, sports, "
                "shopping or general query), not a public-governance issue.",
                matched_category=None,
            )

        # Layer 2 — gather civic vs off-topic signals.
        category_hit = self._best_category(low)
        emergency_hit = any(k in low for k in EMERGENCY_KEYWORDS)
        governance_hit = any(k in low for k in GOVERNANCE_KEYWORDS)
        blocked_hit = next((k for k in BLOCKED_KEYWORDS if k in low), None)

        strong_civic = category_hit is not None or emergency_hit
        any_civic = strong_civic or governance_hit

        # Layer 3 — an off-topic term with no strong civic keyword -> reject.
        if blocked_hit and not strong_civic:
            return RelevanceResult(
                is_relevant=False,
                reason=f"Matched off-topic term '{blocked_hit}' with no civic context.",
                matched_category=None,
            )

        # Layer 4 — no civic OR governance signal at all -> reject.
        # (Removes the old permissive "treat as Others" acceptance.)
        if not any_civic:
            return RelevanceResult(
                is_relevant=False,
                reason="No civic or public-governance content detected.",
                matched_category=None,
            )

        # Accept: a real civic issue (categorised, or governance context -> Others).
        matched = (
            category_hit.value if category_hit else ComplaintCategory.others.value
        )
        return RelevanceResult(
            is_relevant=True,
            reason=f"Recognised as a {matched} civic issue.",
            matched_category=matched,
        )

    # ------------------------------------------------------------------ #
    # Analysis
    # ------------------------------------------------------------------ #
    def analyze(self, text: str) -> AnalysisResult:
        low = (text or "").lower()

        category = self._best_category(low) or ComplaintCategory.others
        emergency_hit = next((k for k in EMERGENCY_KEYWORDS if k in low), None)
        is_emergency = emergency_hit is not None

        if is_emergency:
            urgency = "Emergency"
        elif category in (
            ComplaintCategory.healthcare,
            ComplaintCategory.water,
            ComplaintCategory.public_safety,
            ComplaintCategory.electricity,
        ):
            urgency = "High"
        else:
            urgency = "Medium"

        summary = self._summarize(text)
        if is_emergency:
            reason = (
                f"Emergency indicator '{emergency_hit}' detected; "
                f"classified as {category.value} with {urgency} urgency."
            )
        else:
            reason = (
                f"Keyword analysis maps this to {category.value}; "
                f"urgency set to {urgency}."
            )

        return AnalysisResult(
            category=category.value,
            urgency=urgency,
            summary=summary,
            reason=reason,
            is_emergency=is_emergency,
            emergency_keyword=emergency_hit,
        )

    # ------------------------------------------------------------------ #
    # Language
    # ------------------------------------------------------------------ #
    def detect_language(self, text: str) -> str:
        for ch in text or "":
            code_point = ord(ch)
            for start, end, lang in SCRIPT_RANGES:
                if start <= code_point <= end:
                    return lang
        return "en"

    def translate(self, text: str, target: str = "en") -> str:
        # Offline: cannot truly translate. Return text unchanged; real translation
        # requires Gemini or a translation API (see language.py).
        return text

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _best_category(low_text: str):
        """Return the category with the most keyword hits, or None."""
        best, best_score = None, 0
        for category, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in low_text)
            if score > best_score:
                best, best_score = category, score
        return best

    @staticmethod
    def _summarize(text: str, max_words: int = 28) -> str:
        words = (text or "").split()
        if len(words) <= max_words:
            return text.strip()
        return " ".join(words[:max_words]).rstrip(".,") + "..."
