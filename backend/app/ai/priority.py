"""Priority scoring engine (0-100).

Pure function of AI analysis + the constituency's government dataset. Returns a
transparent breakdown so an MP can see *why* something is prioritised — the core
of the "decision support" pitch.

    score = base(urgency) + emergency_boost + dataset_adjustment   (clamped 0-100)

Dataset scores are 0-100 where higher = better infrastructure, so a LOW relevant
score raises priority (worse existing infra => greater need).
"""
from typing import Optional

from app.models.complaint import ComplaintCategory, UrgencyLevel
from app.models.dataset import Dataset
from app.schemas.ai import AnalysisResult, OfficialContext, PriorityBreakdown
from app.utils.constants import to_category, to_urgency

_URGENCY_BASE = {
    UrgencyLevel.low: 20.0,
    UrgencyLevel.medium: 38.0,
    UrgencyLevel.high: 58.0,
    UrgencyLevel.emergency: 72.0,
}

_EMERGENCY_BOOST = 22.0

# Which dataset score is relevant to which category.
_ROAD_CATEGORIES = {
    ComplaintCategory.roads,
    ComplaintCategory.drainage,
    ComplaintCategory.street_lights,
    ComplaintCategory.public_transport,
}
_WATER_CATEGORIES = {ComplaintCategory.water, ComplaintCategory.garbage}

# NFHS (health/sanitation/nutrition) data informs these categories.
_NFHS_CATEGORIES = {
    ComplaintCategory.healthcare,
    ComplaintCategory.water,
    ComplaintCategory.garbage,
    ComplaintCategory.drainage,
}
_NFHS_MIN_BOOST = 3.0   # any matching NFHS district context
_NFHS_MAX_BOOST = 8.0   # when health indicators strongly support higher urgency
_LGD_BOOST = 2.0        # validated location -> slightly higher confidence


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def compute_priority(
    analysis: AnalysisResult,
    dataset: Optional[Dataset],
    duplicate_count: int = 0,
    population_override: Optional[int] = None,
    official: Optional[OfficialContext] = None,
) -> PriorityBreakdown:
    """Priority 0-100. `population_override` (real Census population, if imported)
    takes precedence over the sample dataset's population; `official` adds bounded
    NFHS/LGD context when imported government datasets cover the location. Everything
    falls back safely to the sample dataset."""
    urgency = to_urgency(analysis.urgency)
    category = to_category(analysis.category)

    base = _URGENCY_BASE.get(urgency, 38.0)
    emergency_boost = _EMERGENCY_BOOST if analysis.is_emergency else 0.0

    adjustment = 0.0
    notes_parts = []

    # Effective population: real (Census) when available, else the sample dataset.
    effective_pop = (
        population_override
        if population_override is not None
        else (dataset.population if dataset else 0)
    )

    if dataset is not None:
        if category in _ROAD_CATEGORIES:
            deficit = (50.0 - dataset.road_score) / 2.5  # up to +20 if score=0
            adjustment += deficit
            notes_parts.append(
                f"road infra score {dataset.road_score:.0f}/100 -> {deficit:+.1f}"
            )
        elif category in _WATER_CATEGORIES:
            deficit = (50.0 - dataset.water_score) / 2.5
            adjustment += deficit
            notes_parts.append(
                f"water infra score {dataset.water_score:.0f}/100 -> {deficit:+.1f}"
            )
        elif category == ComplaintCategory.healthcare:
            per_lakh = _per_lakh(dataset.hospitals, dataset.population)
            deficit = _scarcity_boost(per_lakh, target=3.0)  # want >=3 hospitals/lakh
            adjustment += deficit
            notes_parts.append(
                f"{per_lakh:.1f} hospitals/lakh -> {deficit:+.1f}"
            )
        elif category == ComplaintCategory.education:
            per_lakh = _per_lakh(dataset.schools, dataset.population)
            deficit = _scarcity_boost(per_lakh, target=15.0)  # want >=15 schools/lakh
            adjustment += deficit
            notes_parts.append(
                f"{per_lakh:.1f} schools/lakh -> {deficit:+.1f}"
            )

    # Population boost works from real Census data even without a sample dataset.
    pop_boost = _population_boost(effective_pop)
    if pop_boost:
        adjustment += pop_boost
        src = "real" if population_override is not None else "sample"
        notes_parts.append(f"population {effective_pop:,} ({src}) -> +{pop_boost:.1f}")
    if dataset is None and population_override is None:
        notes_parts.append("no dataset for constituency; base scoring only")

    # Phase 5: imported official datasets refine the score (bounded + explainable).
    if official is not None and official.is_official:
        nfhs_boost = _nfhs_boost(official, category)
        if nfhs_boost:
            adjustment += nfhs_boost
            notes_parts.append(f"NFHS health context -> +{nfhs_boost:.1f}")
        lgd_boost = _lgd_boost(official, category)
        if lgd_boost:
            adjustment += lgd_boost
            notes_parts.append(f"LGD location validated -> +{lgd_boost:.1f}")

    # More corroborating reports of the same issue => higher priority.
    duplicate_boost = min(duplicate_count * 3.0, 12.0)

    score = _clamp(base + emergency_boost + adjustment + duplicate_boost)
    notes = (
        f"base(urgency={urgency.value})={base:.0f}"
        + (f", emergency=+{emergency_boost:.0f}" if emergency_boost else "")
        + (f", dataset[{'; '.join(notes_parts)}]" if notes_parts else "")
        + (f", duplicates(x{duplicate_count})=+{duplicate_boost:.0f}" if duplicate_boost else "")
    )

    return PriorityBreakdown(
        score=round(score, 1),
        base=base,
        emergency_boost=emergency_boost,
        dataset_adjustment=round(adjustment, 1),
        duplicate_boost=round(duplicate_boost, 1),
        notes=notes,
    )


def _nfhs_boost(official: OfficialContext, category: ComplaintCategory) -> float:
    """Health-need boost for health/water/sanitation complaints backed by NFHS data.

    Scales between a presence-only minimum and a maximum by the official health
    indicators' stress signal (0..1). No indicators parseable -> a neutral mid boost.
    """
    if not official.nfhs or category not in _NFHS_CATEGORIES:
        return 0.0
    stress = official.nfhs_stress if official.nfhs_stress is not None else 0.4
    span = _NFHS_MAX_BOOST - _NFHS_MIN_BOOST
    return round(_clamp(_NFHS_MIN_BOOST + stress * span, 0.0, _NFHS_MAX_BOOST), 1)


def _lgd_boost(official: OfficialContext, category: ComplaintCategory) -> float:
    """Small confidence bump when official LGD records validate an infra location."""
    if not official.lgd:
        return 0.0
    if category in _ROAD_CATEGORIES or category in _WATER_CATEGORIES:
        return _LGD_BOOST
    return 0.0


def _population_boost(population: int) -> float:
    """Larger populations mean more people affected -> a small priority bump."""
    if not population:
        return 0.0
    if population >= 400_000:
        return 5.0
    if population >= 250_000:
        return 3.0
    if population >= 100_000:
        return 1.0
    return 0.0


def _per_lakh(count: int, population: int) -> float:
    if not population:
        return 0.0
    return count / (population / 100_000)


def _scarcity_boost(per_lakh: float, target: float, cap: float = 18.0) -> float:
    """More boost the further below target the provision is."""
    if per_lakh >= target:
        return 0.0
    shortfall_ratio = (target - per_lakh) / target
    return round(_clamp(shortfall_ratio * cap, 0.0, cap), 1)
