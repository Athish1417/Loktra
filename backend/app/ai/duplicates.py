"""Foundation duplicate-complaint detection (no embeddings, Phase 3).

Heuristic only — deliberately simple and explainable:
complaints in the SAME constituency + SAME category are compared to the incoming
one by keyword overlap (Jaccard) of title+description, boosted when they share a
ward or sit within a short geographic radius. Anything above the threshold is a
"possible duplicate".

Returns a count, the matching complaint ids, and a stable group key so related
reports can be grouped in dashboards later.
"""
import math
import re
from dataclasses import dataclass, field
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.complaint import Complaint
from app.utils.constants import to_category

# Small stopword set so overlap reflects meaningful civic terms, not filler.
_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "at", "for", "is",
    "are", "was", "were", "be", "been", "this", "that", "these", "those", "it",
    "its", "with", "near", "from", "has", "have", "not", "no", "we", "our",
    "my", "there", "here", "since", "very", "please", "day", "days",
}

_PROXIMITY_METRES = 250.0
_DEFAULT_THRESHOLD = 0.35


@dataclass
class DuplicateResult:
    count: int = 0
    ids: List[int] = field(default_factory=list)
    group_key: Optional[str] = None


def _tokens(text: str) -> set:
    words = re.findall(r"[a-z0-9]+", (text or "").lower())
    return {w for w in words if len(w) > 2 and w not in _STOPWORDS}


def _similarity(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _haversine_m(lat1, lon1, lat2, lon2) -> float:
    r = 6_371_000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    h = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlam / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


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
    threshold: float = _DEFAULT_THRESHOLD,
) -> DuplicateResult:
    """Find existing complaints that look like duplicates of the given input."""
    if not constituency_id:
        return DuplicateResult()

    cat = to_category(category)
    q = db.query(Complaint).filter(
        Complaint.constituency_id == constituency_id,
        Complaint.category == cat,
    )
    if exclude_id is not None:
        q = q.filter(Complaint.id != exclude_id)
    candidates = q.all()

    incoming = _tokens(f"{title} {description}")
    matches: List[Complaint] = []
    for c in candidates:
        sim = _similarity(incoming, _tokens(f"{c.title} {c.description}"))
        same_ward = ward_id is not None and c.ward_id == ward_id
        close = (
            latitude is not None
            and longitude is not None
            and c.latitude is not None
            and c.longitude is not None
            and _haversine_m(latitude, longitude, c.latitude, c.longitude)
            <= _PROXIMITY_METRES
        )
        # A strong text match, OR a weaker match reinforced by same ward / proximity.
        if sim >= threshold or (sim >= threshold * 0.6 and (same_ward or close)) or close:
            matches.append(c)

    if not matches:
        return DuplicateResult()

    ids = sorted(c.id for c in matches)
    seed = min(matches, key=lambda c: c.id)
    group_key = seed.duplicate_group_key or f"DUP-{constituency_id}-{cat.name}-{seed.id}"
    return DuplicateResult(count=len(matches), ids=ids, group_key=group_key)
