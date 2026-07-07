from typing import List, Optional

from pydantic import BaseModel


class OfficialContext(BaseModel):
    """Phase 5 — which imported official datasets cover a complaint's location.

    A plain data object (no DB access) so the pure priority engine can score from
    it. All-False / all-None means nothing matched, i.e. safe sample fallback.
    """
    census: bool = False
    lgd: bool = False
    nfhs: bool = False
    election: bool = False
    population: Optional[int] = None      # real Census population for the district
    households: Optional[int] = None
    nfhs_stress: Optional[float] = None   # 0..1 health-need signal, None if unknown

    @property
    def is_official(self) -> bool:
        return any([self.census, self.lgd, self.nfhs, self.election])

    @property
    def matched_labels(self) -> List[str]:
        pairs = [(self.census, "Census"), (self.lgd, "LGD"),
                 (self.nfhs, "NFHS"), (self.election, "Election")]
        return [label for flag, label in pairs if flag]


class RelevanceResult(BaseModel):
    is_relevant: bool
    reason: str
    matched_category: Optional[str] = None


class AnalysisResult(BaseModel):
    category: str
    urgency: str
    summary: str
    reason: str
    is_emergency: bool = False
    emergency_keyword: Optional[str] = None


class PriorityBreakdown(BaseModel):
    """Transparent, explainable priority — great for the 'decision support' story."""
    score: float
    base: float
    emergency_boost: float
    dataset_adjustment: float
    duplicate_boost: float = 0.0
    notes: str


class LanguageResult(BaseModel):
    language: str
    translated_text: str
