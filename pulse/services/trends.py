from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from pulse.config import settings
from pulse.models import Category
from pulse.repositories.queries import category_content
from pulse.services.policy import PROVIDERS, decision


def as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def discover(db: Session, workspace_id: str, category_id: str, days: int):
    category = db.get(Category, category_id)
    if not category or category.workspace_id != workspace_id:
        raise HTTPException(404, "Category not found")
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    previous = start - timedelta(days=days)
    permitted = [p for p in PROVIDERS if decision(db, workspace_id, p, "derived_analytics")[0] and decision(db, workspace_id, p, "native_display")[0]]
    if settings().app_env == "development":
        permitted.append("synthetic")
    if not permitted:
        raise HTTPException(422, "No provider is approved for derived analytics")
    rows = category_content(db, workspace_id, permitted, previous, end)
    result = []
    for term in category.terms:
        matching = [c for c in rows if term.casefold() in ((c.title or "") + " " + (c.body or "")).casefold()]
        current = [c for c in matching if as_utc(c.published_at) >= start]
        prior = [c for c in matching if as_utc(c.published_at) < start]
        result.append({"term": term, "observed_mentions": len(current), "prior_observed_mentions": len(prior), "growth_percent": None, "growth_state": "insufficient_comparable_collection", "evidence_ids": [c.id for c in sorted(current, key=lambda c: c.published_at, reverse=True)[:5]]})
    result.sort(key=lambda r: r["observed_mentions"], reverse=True)
    return {"category_id": category.id, "start": start, "end": end, "providers": permitted, "coverage": "retained_observed_sample_only", "items": result}
