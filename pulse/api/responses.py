from datetime import datetime
from typing import Any
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: Any


ERRORS = {code: {"model": ErrorResponse} for code in (400, 401, 403, 404, 409, 422, 429, 500)}


class HealthResponse(BaseModel):
    status: str


class CapabilityState(BaseModel):
    enabled: bool
    reason: str


class SearchAccepted(BaseModel):
    search_id: str
    status: str
    source_warnings: dict[str, str]
    status_url: str


class SourceStatus(BaseModel):
    provider: str
    provider_query: str | None
    status: str
    warning: str | None
    returned_count: int | None
    observed_at: datetime | None


class SearchStatus(BaseModel):
    id: str
    query: str
    parsed_query: dict[str, Any]
    max_items_per_source: int
    start: datetime
    end: datetime
    status: str
    sources: list[SourceStatus]


class ContentItem(BaseModel):
    id: str
    provider: str
    kind: str
    title: str | None
    body: str | None
    url: str
    published_at: datetime
    observed_at: datetime | None


class SearchResults(BaseModel):
    items: list[ContentItem]
    limit: int
    offset: int
    next_offset: int | None
    coverage: str


class SentimentEvidence(BaseModel):
    content_id: str
    provider: str
    url: str
    target: str
    label: str
    lexicon_score_milli: int | None
    text_hash: str
    excerpt: str | None
    abstention_reason: str | None


class SentimentResult(BaseModel):
    estimate: bool
    model_version: str
    counts: dict[str, int]
    classified_count: int
    evidence: list[SentimentEvidence]
    limitation: str


class EvidenceResult(BaseModel):
    id: str
    provider: str
    kind: str
    title: str | None
    body: str | None
    url: str
    published_at: datetime
    fetched_at: datetime


class CategoryResult(BaseModel):
    id: str
    name: str
    terms: list[str]


class TrendItem(BaseModel):
    term: str
    observed_mentions: int
    prior_observed_mentions: int
    growth_percent: float | None
    growth_state: str
    evidence_ids: list[str]


class TrendResult(BaseModel):
    category_id: str
    start: datetime
    end: datetime
    providers: list[str]
    coverage: str
    items: list[TrendItem]
