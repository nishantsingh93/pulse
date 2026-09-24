import argparse
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, delete
from pulse.db import Session
from pulse.models import Capability, Category, Content, Match, Membership, Search, Sentiment, SourceRun, Workspace
from pulse.services.query import parse_query
from pulse.services.sentiment import classify
from pulse.config import settings


def main():
    parser = argparse.ArgumentParser(description="Pulse operator commands")
    sub = parser.add_subparsers(dest="command", required=True)
    bootstrap = sub.add_parser("bootstrap")
    bootstrap.add_argument("--name", required=True)
    bootstrap.add_argument("--subject", default="local-dev-user")
    bootstrap.add_argument("--limit-cents", type=int, default=0)
    approval = sub.add_parser("approve")
    approval.add_argument("--workspace", required=True)
    approval.add_argument("--provider", required=True, choices=["x", "youtube", "reddit"])
    approval.add_argument("--operation", required=True, choices=["search", "native_display", "derived_analytics", "sentiment"])
    approval.add_argument("--evidence", required=True)
    approval.add_argument("--approver", required=True)
    approval.add_argument("--expires", required=True, help="ISO 8601 timestamp with UTC offset")
    fixture = sub.add_parser("seed-synthetic")
    fixture.add_argument("--workspace", required=True)
    fixture.add_argument("--subject", default="local-dev-user")
    sub.add_parser("purge-expired")
    args = parser.parse_args()
    with Session.begin() as db:
        if args.command == "bootstrap":
            if args.limit_cents < 0:
                parser.error("Limit cannot be negative")
            workspace = Workspace(name=args.name, monthly_limit_cents=args.limit_cents)
            db.add(workspace)
            db.flush()
            db.add(Membership(workspace_id=workspace.id, subject=args.subject, role="owner"))
            print(f"workspace_id={workspace.id}")
        elif args.command == "approve":
            expires = datetime.fromisoformat(args.expires.replace("Z", "+00:00"))
            if expires.tzinfo is None or expires <= datetime.now(timezone.utc):
                parser.error("Expiry must be a future time with UTC offset")
            if not db.get(Workspace, args.workspace):
                parser.error("Workspace does not exist")
            row = db.get(Capability, (args.workspace, args.provider, args.operation))
            if not row:
                row = Capability(workspace_id=args.workspace, provider=args.provider, operation=args.operation)
                db.add(row)
            row.decision, row.evidence, row.approver, row.expires_at = "approved", args.evidence, args.approver, expires
            print("approval_recorded")
        elif args.command == "seed-synthetic":
            if settings().app_env != "development":
                parser.error("Synthetic fixtures are development-only")
            if not db.get(Membership, (args.workspace, args.subject)):
                parser.error("Membership does not exist")
            end = datetime.now(timezone.utc)
            search = Search(workspace_id=args.workspace, created_by=args.subject, query="AI agents", parsed_query=parse_query("AI agents"), max_items_per_source=50, start_at=end-timedelta(days=7), end_at=end, status="completed")
            db.add(search)
            db.flush()
            run = SourceRun(workspace_id=args.workspace, search_id=search.id, provider="synthetic", status="completed", returned_count=2, observed_at=end, warning="Synthetic fixture; never live data")
            db.add(run)
            db.flush()
            for i, body in enumerate(("AI agents are useful for research workflows.", "AI agents are unreliable for important decisions.")):
                content = Content(workspace_id=args.workspace, provider="synthetic", kind="fixture", external_id=f"{search.id}-{i}", creator_id=f"fixture-{i}", title=None, body=body, url=f"https://example.invalid/fixture/{search.id}/{i}", language="en", published_at=end-timedelta(days=i+1))
                db.add(content)
                db.flush()
                db.add(Match(workspace_id=args.workspace, search_id=search.id, content_id=content.id, source_run_id=run.id))
                db.add(Sentiment(workspace_id=args.workspace, search_id=search.id, content_id=content.id, **classify(body, "AI agents")))
            if not db.scalar(select(Category).where(Category.workspace_id == args.workspace, Category.name == "Technology")):
                db.add(Category(workspace_id=args.workspace, name="Technology", terms=["AI agents", "automation"]))
            print(f"synthetic_search_id={search.id}")
        elif args.command == "purge-expired":
            cutoff = datetime.now(timezone.utc) - timedelta(days=30)
            count = db.execute(delete(Content).where(Content.fetched_at < cutoff)).rowcount
            print(f"purged_content={count}")


if __name__ == "__main__":
    main()
