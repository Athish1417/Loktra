"""Clean, testable AI service functions — the Phase 3 intelligence layer facade.

Routes and tests call these well-named functions instead of poking the provider
directly. Everything runs through the pluggable AI provider, so it degrades to the
deterministic rule-based fallback whenever Gemini is unavailable.

Exposed functions (per spec):
  check_civic_relevance, detect_category, detect_urgency, detect_emergency,
  calculate_priority_score, generate_summary, generate_reason,
  detect_possible_duplicates, analyze_complaint
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.ai import duplicates as _duplicates
from app.ai.priority import compute_priority
from app.ai.provider import get_ai_provider
from app.models.dataset import Dataset
from app.schemas.ai import (
    AnalysisResult,
    OfficialContext,
    PriorityBreakdown,
    RelevanceResult,
)

DuplicateResult = _duplicates.DuplicateResult


# --------------------------------------------------------------------------- #
# Relevance + analysis
# --------------------------------------------------------------------------- #
def check_civic_relevance(text: str) -> RelevanceResult:
    """Governance-relevance gate. is_relevant=False => reject the submission."""
    return get_ai_provider().check_relevance(text)


def analyze_complaint(text: str) -> AnalysisResult:
    """Full analysis: category, urgency, summary, reason, emergency flag."""
    return get_ai_provider().analyze(text)


def detect_category(text: str) -> str:
    return analyze_complaint(text).category


def detect_urgency(text: str) -> str:
    return analyze_complaint(text).urgency


def detect_emergency(text: str) -> bool:
    return analyze_complaint(text).is_emergency


def generate_summary(text: str) -> str:
    return analyze_complaint(text).summary


# --------------------------------------------------------------------------- #
# Priority + explanation
# --------------------------------------------------------------------------- #
def calculate_priority_score(
    analysis: AnalysisResult,
    dataset: Optional[Dataset],
    duplicate_count: int = 0,
    population_override: Optional[int] = None,
    official: Optional[OfficialContext] = None,
) -> PriorityBreakdown:
    return compute_priority(
        analysis, dataset,
        duplicate_count=duplicate_count,
        population_override=population_override,
        official=official,
    )


def generate_reason(
    analysis: AnalysisResult,
    breakdown: PriorityBreakdown,
    dataset: Optional[Dataset] = None,
    duplicate_count: int = 0,
    population: Optional[int] = None,
    population_is_real: bool = False,
    context_sources: Optional[List[str]] = None,
) -> str:
    """Human-readable, bullet-style explanation stored on the complaint."""
    bullets = []

    if analysis.is_emergency:
        if analysis.emergency_keyword:
            bullets.append(f"Emergency keyword detected: {analysis.emergency_keyword}")
        else:
            bullets.append("Emergency situation detected")
        bullets.append("Public safety risk is high")

    bullets.append(f"Category assessed as {analysis.category}")
    bullets.append(f"Urgency assessed as {analysis.urgency}")

    pop = population if population is not None else (dataset.population if dataset else 0)
    if pop:
        level = "high" if pop >= 300_000 else "moderate" if pop >= 150_000 else "modest"
        src = " from official Census data" if population_is_real else ""
        bullets.append(f"Area population is {level} ({pop:,}){src}")

    if dataset is not None:
        if dataset.road_score < 50 or dataset.water_score < 50:
            bullets.append("Existing infrastructure index is low in this area")
        if dataset.hospitals or dataset.schools:
            bullets.append(
                f"Local access: {dataset.hospitals} hospital(s), {dataset.schools} school(s)"
            )

    if duplicate_count:
        bullets.append(
            f"{duplicate_count} similar report(s) found in the same area"
        )

    if context_sources:
        bullets.append(
            f"Priority enhanced using imported {', '.join(context_sources)} "
            "dataset context."
        )

    bullets.append(f"Priority score: {breakdown.score:.0f}")
    return "\n".join(f"- {b}" for b in bullets)


# --------------------------------------------------------------------------- #
# Duplicate detection
# --------------------------------------------------------------------------- #
def detect_possible_duplicates(
    db: Session,
    *,
    category: str,
    constituency_id: Optional[int],
    ward_id: Optional[int] = None,
    title: str = "",
    description: str = "",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    exclude_id: Optional[int] = None,
) -> DuplicateResult:
    return _duplicates.detect_possible_duplicates(
        db,
        category=category,
        constituency_id=constituency_id,
        ward_id=ward_id,
        title=title,
        description=description,
        latitude=latitude,
        longitude=longitude,
        exclude_id=exclude_id,
    )
