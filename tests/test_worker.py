from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session, sessionmaker
from pulse.connectors.live import Item
from pulse.db import Base
from pulse.models import Capability, Content, Match, Search, Sentiment, SourceRun, Workspace
from pulse.services.query import parse_query
import pulse.worker as worker


def test_worker_ingests_duplicate_once_and_records_sentiment(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'worker.db'}")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(worker, "Session", session_factory)
    end = datetime.now(timezone.utc) - timedelta(minutes=1)
    with Session(engine) as db:
        workspace = Workspace(name="Test", monthly_limit_cents=100, reserved_cents=1)
        db.add(workspace)
        db.flush()
        for operation in ("search", "native_display", "sentiment"):
            db.add(Capability(workspace_id=workspace.id, provider="x", operation=operation, decision="approved", evidence="test grant", approver="test", expires_at=end+timedelta(days=1)))
        search = Search(workspace_id=workspace.id, created_by="test", query="AI agents", parsed_query=parse_query("AI agents"), start_at=end-timedelta(days=1), end_at=end, max_items_per_source=10, status="pending")
        db.add(search)
        db.flush()
        run = SourceRun(workspace_id=workspace.id, search_id=search.id, provider="x", estimated_cents=1, status="pending")
        db.add(run)
        db.commit()
        run_id = run.id
        workspace_id = workspace.id
    item = Item("x", "post", "123", "creator", None, "AI agents are excellent for research.", "https://x.com/i/web/status/123", "en", end-timedelta(hours=1))
    monkeypatch.setattr(worker, "fetch", lambda provider, query, start, end, limit: ([item, item], query, []))
    assert worker.claim() == run_id
    worker.process(run_id)
    with Session(engine) as db:
        assert db.scalar(select(func.count()).select_from(Content)) == 1
        assert db.scalar(select(func.count()).select_from(Match)) == 1
        assert db.scalar(select(func.count()).select_from(Sentiment)) == 1
        assert db.get(Workspace, workspace_id).reserved_cents == 0
        assert db.get(SourceRun, run_id).status == "completed"
