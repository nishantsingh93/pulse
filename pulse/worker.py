import logging
import time
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, or_, and_
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from langdetect import detect, DetectorFactory, LangDetectException
from pulse.connectors.live import ProviderError, fetch
from pulse.db import Session
from pulse.models import Content, Match, Search, Sentiment, SourceRun, Workspace
from pulse.services.policy import decision
from pulse.services.sentiment import classify

log = logging.getLogger("pulse.worker")
DetectorFactory.seed = 0


def as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def eligible_english(item) -> bool:
    if item.language:
        return item.language == "en"
    text = " ".join(filter(None, (item.title, item.body)))
    if len(text) < 30:
        return False
    try:
        return detect(text) == "en"
    except LangDetectException:
        return False


def insert_for(db, model):
    return sqlite_insert(model) if db.bind.dialect.name == "sqlite" else pg_insert(model)


def claim() -> str | None:
    with Session.begin() as db:
        current = datetime.now(timezone.utc)
        row = db.scalar(select(SourceRun).where(or_(and_(SourceRun.status == "pending", or_(SourceRun.next_retry_at.is_(None), SourceRun.next_retry_at <= current)), and_(SourceRun.status == "running", SourceRun.leased_until < current))).order_by(SourceRun.id).with_for_update(skip_locked=True).limit(1))
        if not row:
            return None
        row.status = "running"
        row.attempts += 1
        row.leased_until = datetime.now(timezone.utc) + timedelta(minutes=2)
        return row.id


def finish(db, run: SourceRun, status: str, warning: str | None = None):
    run.status = status
    run.warning = warning
    run.leased_until = None
    run.next_retry_at = None
    run.observed_at = datetime.now(timezone.utc)
    workspace = db.scalar(select(Workspace).where(Workspace.id == run.workspace_id).with_for_update())
    workspace.reserved_cents -= run.estimated_cents
    if status == "completed":
        # Estimated cost is deliberately reconciled as an estimate until provider billing is imported.
        workspace.spent_cents += run.estimated_cents
    runs = db.scalars(select(SourceRun).where(SourceRun.search_id == run.search_id)).all()
    search = db.get(Search, run.search_id)
    if all(r.status in ("completed", "failed", "skipped") for r in runs):
        search.status = "completed" if all(r.status == "completed" for r in runs) else "partial" if any(r.status == "completed" for r in runs) else "failed"


def process(run_id: str):
    with Session() as db:
        run = db.get(SourceRun, run_id)
        search = db.get(Search, run.search_id)
        if not decision(db, run.workspace_id, run.provider, "search")[0] or not decision(db, run.workspace_id, run.provider, "native_display")[0]:
            with db.begin_nested():
                finish(db, run, "skipped", "approval_revoked")
            db.commit()
            return
        provider = run.provider
        query, start, end, limit = search.query, as_utc(search.start_at), as_utc(search.end_at), search.max_items_per_source
    try:
        items, translated, warnings = fetch(provider, query, start, end, limit)
    except ProviderError as exc:
        with Session.begin() as db:
            run = db.get(SourceRun, run_id)
            if exc.code in ("rate_limited", "provider_http_error") and run.attempts < 3:
                run.status = "pending"
                run.warning = exc.code
                run.leased_until = None
                run.next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=min(max(exc.retry_after or 2 ** run.attempts * 30, 1), 900))
            else:
                finish(db, run, "failed", exc.code)
        return
    except Exception:
        log.error("Provider request failed for source run %s", run_id)
        with Session.begin() as db:
            run = db.get(SourceRun, run_id)
            finish(db, run, "failed", "provider_unavailable")
        return
    with Session.begin() as db:
        run = db.get(SourceRun, run_id)
        search = db.get(Search, run.search_id)
        if not decision(db, run.workspace_id, provider, "search")[0] or not decision(db, run.workspace_id, provider, "native_display")[0]:
            finish(db, run, "skipped", "approval_revoked")
            return
        can_sentiment = decision(db, run.workspace_id, provider, "sentiment")[0]
        for item in items:
            if not as_utc(search.start_at) <= item.published_at < as_utc(search.end_at):
                continue
            values = {"workspace_id": run.workspace_id, "provider": provider, "kind": item.kind, "external_id": item.external_id, "creator_id": item.creator_id, "title": item.title, "body": item.body, "url": item.url, "language": item.language, "published_at": item.published_at}
            db.execute(insert_for(db, Content).values(**values).on_conflict_do_update(index_elements=[Content.workspace_id, Content.provider, Content.kind, Content.external_id], set_={"fetched_at": datetime.now(timezone.utc), "title": item.title, "body": item.body}))
            content = db.scalar(select(Content).where(Content.workspace_id == run.workspace_id, Content.provider == provider, Content.kind == item.kind, Content.external_id == item.external_id))
            if content.deleted_at:
                continue
            db.execute(insert_for(db, Match).values(workspace_id=run.workspace_id, search_id=search.id, content_id=content.id, source_run_id=run.id).on_conflict_do_nothing())
            if can_sentiment and eligible_english(item):
                result = classify(" ".join(filter(None, (item.title, item.body))), search.query)
                db.execute(insert_for(db, Sentiment).values(workspace_id=run.workspace_id, search_id=search.id, content_id=content.id, **result).on_conflict_do_nothing())
        run.provider_query = translated
        run.returned_count = len(items)
        finish(db, run, "completed", "; ".join(warnings) if warnings else None)


def main():
    logging.basicConfig(level=logging.INFO)
    while True:
        run_id = claim()
        if run_id:
            process(run_id)
        else:
            time.sleep(1)


if __name__ == "__main__":
    main()
