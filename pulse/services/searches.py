from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from pulse.api.schemas import SearchCreate
from pulse.config import settings
from pulse.models import Membership, Search, SourceRun, Workspace
from pulse.services.policy import decision
from pulse.services.query import parse_query


def create(db: Session, workspace_id: str, membership: Membership, body: SearchCreate):
    end = body.time_range.end if body.time_range else datetime.now(timezone.utc)
    start = body.time_range.start if body.time_range else end - timedelta(days=7)
    cfg = settings()
    estimates = {"x": cfg.x_estimated_cost_cents, "youtube": cfg.youtube_estimated_cost_cents, "reddit": cfg.reddit_estimated_cost_cents}
    warnings = {}
    eligible = []
    for provider in body.platforms:
        allowed, reason = decision(db, workspace_id, provider, "search")
        display, display_reason = decision(db, workspace_id, provider, "native_display")
        if not allowed or not display:
            warnings[provider] = reason if not allowed else display_reason
        elif provider == "x" and start < datetime.now(timezone.utc) - timedelta(days=7, minutes=1):
            warnings[provider] = "history_unsupported"
        elif estimates[provider] <= 0:
            warnings[provider] = "cost_estimate_missing"
        else:
            eligible.append(provider)
    if warnings and not body.allow_partial_sources or not eligible:
        raise HTTPException(422, {"unavailable_sources": warnings})
    workspace = db.execute(select(Workspace).where(Workspace.id == workspace_id).with_for_update()).scalar_one()
    total = sum(estimates[p] for p in eligible)
    if workspace.monthly_limit_cents <= 0 or workspace.spent_cents + workspace.reserved_cents + total > workspace.monthly_limit_cents:
        raise HTTPException(429, "Workspace spend ceiling would be exceeded")
    workspace.reserved_cents += total
    search = Search(workspace_id=workspace_id, created_by=membership.subject, query=body.query, parsed_query=parse_query(body.query), max_items_per_source=body.max_items_per_source, start_at=start, end_at=end, status="pending")
    db.add(search)
    db.flush()
    for provider in body.platforms:
        db.add(SourceRun(workspace_id=workspace_id, search_id=search.id, provider=provider, status="pending" if provider in eligible else "skipped", warning=warnings.get(provider), estimated_cents=estimates[provider] if provider in eligible else 0, provider_query=body.query))
    db.commit()
    return {"search_id": search.id, "status": "pending", "source_warnings": warnings, "status_url": f"/v1/workspaces/{workspace_id}/searches/{search.id}"}
