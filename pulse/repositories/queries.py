from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from pulse.models import Category, Content, Match, Search, Sentiment, SourceRun


def scoped_search(db: Session, workspace_id: str, search_id: str) -> Search:
    row = db.get(Search, search_id)
    if not row or row.workspace_id != workspace_id:
        raise HTTPException(404, "Search not found")
    return row


def source_runs(db: Session, workspace_id: str, search_id: str):
    return db.scalars(select(SourceRun).where(SourceRun.search_id == search_id, SourceRun.workspace_id == workspace_id)).all()


def result_page(db: Session, workspace_id: str, search_id: str, providers: list[str], limit: int, offset: int):
    return db.execute(select(Content, SourceRun).join(Match, Match.content_id == Content.id).join(SourceRun, SourceRun.id == Match.source_run_id).where(Match.workspace_id == workspace_id, Match.search_id == search_id, Content.provider.in_(providers), Content.deleted_at.is_(None)).order_by(Content.published_at.desc(), Content.id).limit(limit).offset(offset)).all()


def sentiment_rows(db: Session, workspace_id: str, search_id: str, providers: list[str]):
    return db.execute(select(Sentiment, Content).join(Content, Content.id == Sentiment.content_id).where(Sentiment.workspace_id == workspace_id, Sentiment.search_id == search_id, Content.provider.in_(providers), Content.deleted_at.is_(None))).all()


def category_content(db: Session, workspace_id: str, providers: list[str], start, end):
    return db.scalars(select(Content).where(Content.workspace_id == workspace_id, Content.provider.in_(providers), Content.deleted_at.is_(None), Content.published_at >= start, Content.published_at < end)).all()
