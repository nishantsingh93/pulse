from datetime import datetime, timezone
from sqlalchemy.orm import Session
from pulse.models import Capability

PROVIDERS = ("x", "youtube", "reddit")
OPERATIONS = ("search", "native_display", "derived_analytics", "sentiment")


def decision(db: Session, workspace_id: str, provider: str, operation: str) -> tuple[bool, str]:
    row = db.get(Capability, (workspace_id, provider, operation))
    if not row:
        return False, "unreviewed"
    if row.decision != "approved":
        return False, row.decision
    expiry = row.expires_at.replace(tzinfo=timezone.utc) if row.expires_at and row.expires_at.tzinfo is None else row.expires_at
    if not row.evidence or not row.approver or not expiry or expiry <= datetime.now(timezone.utc):
        return False, "approval_incomplete_or_expired"
    return True, "approved"
