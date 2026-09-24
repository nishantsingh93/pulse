from datetime import datetime, timedelta, timezone
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from pulse.api.main import app
from pulse.config import settings
from pulse.db import Base, get_db
from pulse.models import Capability, Category, Content, Membership, Workspace
from pulse.services.policy import decision
from pulse.services.query import matches_text, parse_query
from pulse.services.sentiment import classify


def test_query_grammar():
    ast = parse_query('"AI agents" #research')
    assert matches_text(ast, "AI agents help #research")
    with pytest.raises(HTTPException):
        parse_query("AI OR agents")
    with pytest.raises(HTTPException):
        parse_query('"unclosed')


def test_sentiment_abstains_without_target():
    result = classify("The interface is wonderful.", "AI agents")
    assert result["label"] == "unknown"
    assert result["abstention_reason"] == "target_not_in_text"


def test_policy_denies_missing_and_expired():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        workspace = Workspace(name="A")
        db.add(workspace)
        db.flush()
        assert decision(db, workspace.id, "reddit", "search") == (False, "unreviewed")
        db.add(Capability(workspace_id=workspace.id, provider="reddit", operation="search", decision="approved", approver="reviewer", evidence="agreement", expires_at=datetime.now(timezone.utc)-timedelta(days=1)))
        db.flush()
        assert decision(db, workspace.id, "reddit", "search")[0] is False


def test_workspace_isolation_and_synthetic_trends():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        a, b = Workspace(name="A"), Workspace(name="B")
        db.add_all((a, b))
        db.flush()
        db.add_all((Membership(workspace_id=a.id, subject="local-dev-user", role="owner"), Membership(workspace_id=b.id, subject="other", role="owner")))
        category = Category(workspace_id=a.id, name="Technology", terms=["AI agents"])
        db.add(category)
        db.add(Content(workspace_id=a.id, provider="synthetic", kind="fixture", external_id="one", body="AI agents are useful", url="https://example.invalid/one", published_at=datetime.now(timezone.utc)-timedelta(days=1)))
        db.commit()
        a_id, b_id, cat_id = a.id, b.id, category.id

    def override():
        with Session(engine) as db:
            yield db

    settings.cache_clear()
    config = settings()
    object.__setattr__(config, "dev_token", "test-token")
    object.__setattr__(config, "app_env", "development")
    app.dependency_overrides[get_db] = override
    client = TestClient(app)
    try:
        headers = {"Authorization": "Bearer test-token"}
        assert client.get(f"/v1/workspaces/{b_id}/categories", headers=headers).status_code == 404
        invalid = client.post(f"/v1/workspaces/{a_id}/searches", headers=headers, json={"query": "AI OR agents", "platforms": ["x"]})
        assert invalid.status_code == 400
        response = client.get(f"/v1/workspaces/{a_id}/categories/{cat_id}/trends", headers=headers)
        assert response.status_code == 200
        assert response.json()["items"][0]["observed_mentions"] == 1
        assert response.json()["providers"] == ["synthetic"]
    finally:
        app.dependency_overrides.clear()
        settings.cache_clear()
