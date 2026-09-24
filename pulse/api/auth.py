import secrets
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pulse.config import settings
from pulse.db import get_db
from pulse.models import Membership


bearer = HTTPBearer(auto_error=False)


def subject(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(401, "Bearer token required")
    token = credentials.credentials
    cfg = settings()
    if cfg.app_env == "development" and cfg.dev_token and secrets.compare_digest(token, cfg.dev_token):
        return "local-dev-user"
    if not (cfg.oidc_issuer and cfg.oidc_audience and cfg.oidc_jwks_url):
        raise HTTPException(401, "OIDC authentication is not configured")
    try:
        key = jwt.PyJWKClient(cfg.oidc_jwks_url).get_signing_key_from_jwt(token)
        claims = jwt.decode(token, key.key, algorithms=["RS256", "ES256"], audience=cfg.oidc_audience, issuer=cfg.oidc_issuer)
        return claims["sub"]
    except (jwt.PyJWTError, KeyError) as exc:
        raise HTTPException(401, "Invalid token") from exc


def member(workspace_id: str, user: str = Depends(subject), db: Session = Depends(get_db)) -> Membership:
    membership = db.get(Membership, (workspace_id, user))
    if not membership:
        raise HTTPException(404, "Workspace not found")
    return membership


def require_write(membership: Membership):
    if membership.role == "viewer":
        raise HTTPException(403, "Write access required")


def require_admin(membership: Membership):
    if membership.role not in ("owner", "admin"):
        raise HTTPException(403, "Admin access required")
