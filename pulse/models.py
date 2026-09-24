import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, ForeignKeyConstraint, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from pulse.db import Base


def now():
    return datetime.now(timezone.utc)


def uid():
    return str(uuid.uuid4())


class Workspace(Base):
    __tablename__ = "workspaces"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(120))
    monthly_limit_cents: Mapped[int] = mapped_column(Integer, default=0)
    spent_cents: Mapped[int] = mapped_column(Integer, default=0)
    reserved_cents: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Membership(Base):
    __tablename__ = "memberships"
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), primary_key=True)
    subject: Mapped[str] = mapped_column(String(255), primary_key=True)
    role: Mapped[str] = mapped_column(String(16))
    __table_args__ = (CheckConstraint("role IN ('owner','admin','analyst','viewer')"),)


class Capability(Base):
    __tablename__ = "capabilities"
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), primary_key=True)
    provider: Mapped[str] = mapped_column(String(16), primary_key=True)
    operation: Mapped[str] = mapped_column(String(32), primary_key=True)
    decision: Mapped[str] = mapped_column(String(16), default="unreviewed")
    evidence: Mapped[str | None] = mapped_column(Text)
    approver: Mapped[str | None] = mapped_column(String(255))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (CheckConstraint("decision IN ('approved','denied','unreviewed')"),)


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    terms: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    __table_args__ = (UniqueConstraint("workspace_id", "name"), Index("ix_categories_workspace", "workspace_id"))


class Search(Base):
    __tablename__ = "searches"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"))
    created_by: Mapped[str] = mapped_column(String(255))
    query: Mapped[str] = mapped_column(String(256))
    parsed_query: Mapped[dict] = mapped_column(JSON)
    max_items_per_source: Mapped[int] = mapped_column(Integer, default=50)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    __table_args__ = (Index("ix_searches_workspace_created", "workspace_id", "created_at"),)


class SourceRun(Base):
    __tablename__ = "source_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"))
    search_id: Mapped[str] = mapped_column(ForeignKey("searches.id", ondelete="CASCADE"))
    provider: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    warning: Mapped[str | None] = mapped_column(Text)
    provider_query: Mapped[str | None] = mapped_column(String(512))
    returned_count: Mapped[int | None] = mapped_column(Integer)
    estimated_cents: Mapped[int] = mapped_column(Integer, default=0)
    leased_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (UniqueConstraint("search_id", "provider"), Index("ix_source_runs_status_lease", "status", "leased_until"))


class Content(Base):
    __tablename__ = "content"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"))
    provider: Mapped[str] = mapped_column(String(16))
    kind: Mapped[str] = mapped_column(String(20))
    external_id: Mapped[str] = mapped_column(String(255))
    creator_id: Mapped[str | None] = mapped_column(String(255))
    title: Mapped[str | None] = mapped_column(Text)
    body: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str] = mapped_column(Text)
    language: Mapped[str | None] = mapped_column(String(16))
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (UniqueConstraint("workspace_id", "provider", "kind", "external_id"), UniqueConstraint("workspace_id", "id"), Index("ix_content_workspace_published", "workspace_id", "published_at"))


class Match(Base):
    __tablename__ = "matches"
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), primary_key=True)
    search_id: Mapped[str] = mapped_column(ForeignKey("searches.id", ondelete="CASCADE"), primary_key=True)
    content_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_run_id: Mapped[str] = mapped_column(ForeignKey("source_runs.id", ondelete="CASCADE"))
    __table_args__ = (ForeignKeyConstraint(["workspace_id", "content_id"], ["content.workspace_id", "content.id"], ondelete="CASCADE"), Index("ix_matches_content", "content_id"))


class Sentiment(Base):
    __tablename__ = "sentiments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"))
    search_id: Mapped[str] = mapped_column(ForeignKey("searches.id", ondelete="CASCADE"))
    content_id: Mapped[str] = mapped_column(ForeignKey("content.id", ondelete="CASCADE"))
    target: Mapped[str] = mapped_column(String(256))
    label: Mapped[str] = mapped_column(String(16))
    score: Mapped[int | None] = mapped_column(Integer)
    text_hash: Mapped[str] = mapped_column(String(64))
    model_version: Mapped[str] = mapped_column(String(64), default="target-vader-0.1")
    abstention_reason: Mapped[str | None] = mapped_column(String(64))
    evidence_text: Mapped[str | None] = mapped_column(Text)
    __table_args__ = (UniqueConstraint("search_id", "content_id"), Index("ix_sentiments_workspace_search", "workspace_id", "search_id"))
