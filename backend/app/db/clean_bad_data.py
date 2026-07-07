"""Safely remove previously-accepted irrelevant demo complaints.

The old civic-relevance guard was too permissive and let non-civic content
through (e.g. "Who won yesterday's cricket match?"). This utility finds those
by explicit off-topic markers — it does NOT re-judge borderline complaints — so
genuine civic complaints are never deleted.

Usage (from the backend/ directory):

    python -m app.db.clean_bad_data                 # dry run: list what would go
    python -m app.db.clean_bad_data --apply         # delete the matches
    python -m app.db.clean_bad_data --code LOK-2026-000018 --apply   # target one
"""
import argparse
import re
from typing import List, Optional

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.assignment import Assignment
from app.models.complaint import Complaint

# Explicit off-topic markers used ONLY to identify junk test complaints.
# Matched on WORD BOUNDARIES so short tokens never hit real words
# (e.g. "ipl" must not match "multiple").
IRRELEVANT_MARKERS = [
    "cricket", "movie", "film", "song", "joke", "celebrity", "virat kohli",
    "free fire", "pubg", "bgmi", "dating", "netflix", "web series", "ipl",
    "football match", "who won", "best phone", "shopping spree",
]
_MARKER_RE = re.compile(
    r"\b(" + "|".join(re.escape(m) for m in IRRELEVANT_MARKERS) + r")\b"
)


def find_irrelevant(db: Session) -> List[Complaint]:
    hits = []
    for c in db.query(Complaint).all():
        text = f"{c.title} {c.description} {c.original_text or ''}".lower()
        if _MARKER_RE.search(text):
            hits.append(c)
    return hits


def clean(
    db: Session, *, codes: Optional[List[str]] = None, apply: bool = False
) -> List[Complaint]:
    if codes:
        targets = (
            db.query(Complaint).filter(Complaint.complaint_code.in_(codes)).all()
        )
    else:
        targets = find_irrelevant(db)

    if not targets:
        print("No irrelevant complaints found.")
        return []

    verb = "DELETING" if apply else "WOULD DELETE"
    for c in targets:
        print(f"  {verb}: {c.complaint_code} [{c.category.value}] {c.title!r}")

    if apply:
        ids = [c.id for c in targets]
        # Assignment has no cascade; remove its rows first.
        db.query(Assignment).filter(Assignment.complaint_id.in_(ids)).delete(
            synchronize_session=False
        )
        for c in targets:
            db.delete(c)  # status-history rows cascade via the timeline relationship
        db.commit()
        print(f"Deleted {len(targets)} complaint(s).")
    else:
        print(f"\n{len(targets)} match(es). Re-run with --apply to delete.")
    return targets


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove irrelevant demo complaints.")
    parser.add_argument("--apply", action="store_true", help="actually delete (default: dry run)")
    parser.add_argument("--code", action="append", dest="codes",
                        help="target a specific complaint_code (repeatable)")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        clean(db, codes=args.codes, apply=args.apply)
    finally:
        db.close()


if __name__ == "__main__":
    main()
