import logging
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pulse.api.auth import member, require_admin, require_write
from pulse.api.schemas import CategoryCreate, SearchCreate
from pulse.api.responses import ERRORS, HealthResponse, CapabilityState, SearchAccepted, SearchStatus, SearchResults, SentimentResult, EvidenceResult, CategoryResult, TrendResult
from pulse.api.openapi import openapi_30
from pulse.config import settings
from pulse.db import get_db
from pulse.models import Category, Content, Membership
from pulse.repositories.queries import scoped_search, source_runs, result_page, sentiment_rows
from pulse.services.policy import OPERATIONS, PROVIDERS, decision
from pulse.services.searches import create as create_search_service
from pulse.services.trends import discover as discover_trends

log = logging.getLogger("pulse")
app = FastAPI(title="Pulse API", version="0.1.0", openapi_url="/openapi.json")
app.openapi = lambda: openapi_30(app)
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings().cors_origins.split(",") if x.strip()], allow_methods=["GET", "POST", "DELETE"], allow_headers=["Authorization", "Content-Type"], allow_credentials=False)


@app.middleware("http")
async def secure_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(Exception)
async def unexpected(request: Request, exc: Exception):
    log.exception("Unhandled request error")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": [{"field": ".".join(str(p) for p in error["loc"]), "message": error["msg"]} for error in exc.errors()]})


@app.get("/health/live", response_model=HealthResponse)
def live():
    return {"status": "ok"}


@app.get("/health/ready", response_model=HealthResponse, responses=ERRORS)
def ready(db: Session = Depends(get_db)):
    db.execute(select(1))
    return {"status": "ok"}


@app.get("/v1/workspaces/{workspace_id}/capabilities", response_model=dict[str, dict[str, CapabilityState]], responses=ERRORS)
def capabilities(workspace_id: str, _: Membership = Depends(member), db: Session = Depends(get_db)):
    return {p: {o: {"enabled": decision(db, workspace_id, p, o)[0], "reason": decision(db, workspace_id, p, o)[1]} for o in OPERATIONS} for p in PROVIDERS}


@app.post("/v1/workspaces/{workspace_id}/searches", status_code=202, response_model=SearchAccepted, responses=ERRORS)
def create_search(workspace_id: str, body: SearchCreate, membership: Membership = Depends(member), db: Session = Depends(get_db)):
    require_write(membership)
    return create_search_service(db, workspace_id, membership, body)


@app.get("/v1/workspaces/{workspace_id}/searches/{search_id}", response_model=SearchStatus, responses=ERRORS)
def get_search(workspace_id: str, search_id: str, _: Membership = Depends(member), db: Session = Depends(get_db)):
    row = scoped_search(db, workspace_id, search_id)
    runs = source_runs(db, workspace_id, search_id)
    return {"id": row.id, "query": row.query, "parsed_query": row.parsed_query, "max_items_per_source": row.max_items_per_source, "start": row.start_at, "end": row.end_at, "status": row.status, "sources": [{"provider": r.provider, "provider_query": r.provider_query, "status": r.status, "warning": r.warning, "returned_count": r.returned_count, "observed_at": r.observed_at} for r in runs]}


@app.get("/v1/workspaces/{workspace_id}/searches/{search_id}/results", response_model=SearchResults, responses=ERRORS)
def results(workspace_id: str, search_id: str, limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), _: Membership = Depends(member), db: Session = Depends(get_db)):
    scoped_search(db, workspace_id, search_id)
    enabled = [p for p in PROVIDERS if decision(db, workspace_id, p, "native_display")[0]]
    if settings().app_env == "development":
        enabled.append("synthetic")
    rows = result_page(db, workspace_id, search_id, enabled, limit, offset)
    return {"items": [{"id": c.id, "provider": c.provider, "kind": c.kind, "title": c.title, "body": c.body, "url": c.url, "published_at": c.published_at, "observed_at": r.observed_at} for c, r in rows], "limit": limit, "offset": offset, "next_offset": offset + limit if len(rows) == limit else None, "coverage": "observed_sample"}


@app.get("/v1/workspaces/{workspace_id}/searches/{search_id}/sentiment", response_model=SentimentResult, responses=ERRORS)
def sentiment(workspace_id: str, search_id: str, _: Membership = Depends(member), db: Session = Depends(get_db)):
    scoped_search(db, workspace_id, search_id)
    enabled = [p for p in PROVIDERS if decision(db, workspace_id, p, "sentiment")[0] and decision(db, workspace_id, p, "native_display")[0]]
    if settings().app_env == "development":
        enabled.append("synthetic")
    rows = sentiment_rows(db, workspace_id, search_id, enabled)
    counts = {k: sum(1 for s, _ in rows if s.label == k) for k in ("positive", "negative", "neutral", "unknown")}
    return {"estimate": True, "model_version": "target-vader-0.1", "counts": counts, "classified_count": sum(counts[k] for k in ("positive", "negative", "neutral")), "evidence": [{"content_id": c.id, "provider": c.provider, "url": c.url, "target": s.target, "label": s.label, "lexicon_score_milli": s.score, "text_hash": s.text_hash, "excerpt": s.evidence_text, "abstention_reason": s.abstention_reason} for s, c in rows], "limitation": "Uncalibrated pilot classifier; not approved for external beta"}


@app.get("/v1/workspaces/{workspace_id}/evidence/{content_id}", response_model=EvidenceResult, responses=ERRORS)
def evidence(workspace_id: str, content_id: str, _: Membership = Depends(member), db: Session = Depends(get_db)):
    content = db.get(Content, content_id)
    if not content or content.workspace_id != workspace_id or content.deleted_at or not (content.provider == "synthetic" and settings().app_env == "development") and not decision(db, workspace_id, content.provider, "native_display")[0]:
        raise HTTPException(404, "Evidence not found")
    return {"id": content.id, "provider": content.provider, "kind": content.kind, "title": content.title, "body": content.body, "url": content.url, "published_at": content.published_at, "fetched_at": content.fetched_at}


@app.post("/v1/workspaces/{workspace_id}/categories", status_code=201, response_model=CategoryResult, responses=ERRORS)
def create_category(workspace_id: str, body: CategoryCreate, membership: Membership = Depends(member), db: Session = Depends(get_db)):
    require_admin(membership)
    row = Category(workspace_id=workspace_id, name=body.name, terms=[t.strip() for t in body.terms])
    db.add(row)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409, "Category name already exists") from exc
    return {"id": row.id, "name": row.name, "terms": row.terms}


@app.get("/v1/workspaces/{workspace_id}/categories", response_model=list[CategoryResult], responses=ERRORS)
def categories(workspace_id: str, _: Membership = Depends(member), db: Session = Depends(get_db)):
    return [{"id": c.id, "name": c.name, "terms": c.terms} for c in db.scalars(select(Category).where(Category.workspace_id == workspace_id).order_by(Category.name))]


@app.get("/v1/workspaces/{workspace_id}/categories/{category_id}/trends", response_model=TrendResult, responses=ERRORS)
def category_trends(workspace_id: str, category_id: str, days: int = Query(7, ge=1, le=30), _: Membership = Depends(member), db: Session = Depends(get_db)):
    return discover_trends(db, workspace_id, category_id, days)
