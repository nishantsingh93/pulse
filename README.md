# Pulse API POC

Pulse implements an internal REST API for workspace-scoped topic search, observed category trends and evidence-linked sentiment. The target live sources are X posts, YouTube videos and Reddit submissions. Each source operation stays disabled until a recorded approval and spend configuration allow it. See [BRD.md](BRD.md) and [architecture](docs/architecture.md). Campaign intelligence and predictions are deferred.

## Run locally

Requires Python 3.12+ and `uv`. PostgreSQL 17 is the deployment database; SQLite also works for a single-process local demo. Docker Compose can provide PostgreSQL. Copy `.env.example` to `.env`, set a long random `DEV_TOKEN`, and leave provider credentials empty for the synthetic workflow. For the SQLite demo set `DATABASE_URL=sqlite:///./pulse.db`. For PostgreSQL on the host use `postgresql+psycopg://pulse:pulse@localhost:5432/pulse`; for Compose API/worker services, use host `db` instead of `localhost`.

```sh
# Run this line only for PostgreSQL:
docker compose up -d db
uv sync --extra test
uv run alembic upgrade head
uv run python -m pulse.cli bootstrap --name "Local workspace" --limit-cents 0
uv run uvicorn pulse.api.main:app --reload
```

The bootstrap command prints `workspace_id`. In another terminal, start the worker when testing approved live sources. SQLite supports one local worker; PostgreSQL is required for concurrent workers:

```sh
uv run python -m pulse.worker
```

Export your local IDs and token for the examples:

```sh
export PULSE_WORKSPACE_ID="paste-workspace-id"
export PULSE_TOKEN="paste-DEV_TOKEN-from-.env"
export PULSE_BASE="http://localhost:8000"
```

Seed labeled synthetic examples and copy its printed `synthetic_search_id`:

```sh
uv run python -m pulse.cli seed-synthetic --workspace "$PULSE_WORKSPACE_ID"
export PULSE_SEARCH_ID="paste-synthetic-search-id"
curl -H "Authorization: Bearer $PULSE_TOKEN" "$PULSE_BASE/v1/workspaces/$PULSE_WORKSPACE_ID/searches/$PULSE_SEARCH_ID"
curl -H "Authorization: Bearer $PULSE_TOKEN" "$PULSE_BASE/v1/workspaces/$PULSE_WORKSPACE_ID/searches/$PULSE_SEARCH_ID/results"
curl -H "Authorization: Bearer $PULSE_TOKEN" "$PULSE_BASE/v1/workspaces/$PULSE_WORKSPACE_ID/searches/$PULSE_SEARCH_ID/sentiment"
curl -H "Authorization: Bearer $PULSE_TOKEN" "$PULSE_BASE/v1/workspaces/$PULSE_WORKSPACE_ID/categories"
```

Copy the category ID from the last response:

```sh
export PULSE_CATEGORY_ID="paste-category-id"
curl -H "Authorization: Bearer $PULSE_TOKEN" "$PULSE_BASE/v1/workspaces/$PULSE_WORKSPACE_ID/categories/$PULSE_CATEGORY_ID/trends?days=7"
```

To create another category and inspect an evidence item:

```sh
curl -X POST "$PULSE_BASE/v1/workspaces/$PULSE_WORKSPACE_ID/categories" -H "Authorization: Bearer $PULSE_TOKEN" -H "Content-Type: application/json" -d '{"name":"Products","terms":["AI agents","automation"]}'
export PULSE_CONTENT_ID="paste-id-from-results"
curl -H "Authorization: Bearer $PULSE_TOKEN" "$PULSE_BASE/v1/workspaces/$PULSE_WORKSPACE_ID/evidence/$PULSE_CONTENT_ID"
```

## Live source setup

Set the appropriate provider credential variables in `.env`. In production set `APP_ENV=production` and all three `OIDC_*` variables; the local development token is then rejected. Provision workspace memberships using an operator-controlled process. Configure a workspace monthly spend ceiling and a positive conservative estimate for each provider call. `X_ESTIMATED_COST_CENTS`, `YOUTUBE_ESTIMATED_COST_CENTS`, and `REDDIT_ESTIMATED_COST_CENTS` are reservation estimates, not actual billing records.

An authorized reviewer must verify the specific account agreement and each operation before running the command below. `search` and `native_display` are both needed for a live search. `derived_analytics` is needed for category trends; `sentiment` is needed for text classification. YouTube defaults to native display only. Reddit commercial use requires a separate agreement. The command records a decision; it does not grant provider rights.

```sh
uv run python -m pulse.cli approve --workspace "$PULSE_WORKSPACE_ID" --provider x --operation search --evidence "approval-record-reference" --approver "reviewer-subject" --expires "2026-12-31T00:00:00Z"
uv run python -m pulse.cli approve --workspace "$PULSE_WORKSPACE_ID" --provider x --operation native_display --evidence "approval-record-reference" --approver "reviewer-subject" --expires "2026-12-31T00:00:00Z"
```

Repeat for each provider and operation that has actually been approved. Check the effective state:

```sh
curl -H "Authorization: Bearer $PULSE_TOKEN" "$PULSE_BASE/v1/workspaces/$PULSE_WORKSPACE_ID/capabilities"
```

Submit a search after approvals, credentials, cost estimates and the workspace ceiling are configured:

```sh
curl -X POST "$PULSE_BASE/v1/workspaces/$PULSE_WORKSPACE_ID/searches" -H "Authorization: Bearer $PULSE_TOKEN" -H "Content-Type: application/json" -d '{"query":"AI agents","platforms":["x","youtube","reddit"],"language":"en","allow_partial_sources":true,"max_items_per_source":50}'
```

The response is `202` with a search ID. Poll the search route, then request `/results` and `/sentiment`. Unavailable sources appear as skipped or failed; they are never counted as zero matches. Each live connector currently fetches at most one provider page and labels results as an observed sample. Category trend growth remains unavailable until comparable collection history exists.

## Configuration

| Variable | Purpose |
|---|---|
| `APP_ENV` | `development` enables the local token and synthetic fixtures; use `production` for deployment |
| `DATABASE_URL` | Pooled PostgreSQL connection |
| `CORS_ORIGINS` | Comma-separated allowed browser origins |
| `OIDC_ISSUER`, `OIDC_AUDIENCE`, `OIDC_JWKS_URL` | Production token validation |
| `DEV_TOKEN` | Local development only |
| `X_BEARER_TOKEN`, `YOUTUBE_API_KEY`, `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` | Provider credentials |
| `*_ESTIMATED_COST_CENTS` | Positive reservation per source request |

## Checks and contract

```sh
uv run pytest -q
uv run python -c 'import json; from pathlib import Path; from pulse.api.main import app; Path("docs/api/openapi.json").write_text(json.dumps(app.openapi(), indent=2) + "\n")'
```

The OpenAPI 3.0.3 contract is [docs/api/openapi.json](docs/api/openapi.json). FastAPI also serves `/docs` in development.

Run `uv run python -m pulse.cli purge-expired` daily to remove content fetched more than thirty days ago. A production scheduler and provider-specific retention rules remain release work.

## Release limits

This POC has not passed the BRD's external-beta gates. No X, YouTube or Reddit credentials or commercial entitlements were available for live verification. The classifier has not passed the 300-example holdout evaluation. Provider deletion synchronization, backup tombstone replay, actual-charge reconciliation, multi-page collection, and comparable historical collection are not implemented. Keep live operations disabled until their approvals are recorded, and complete those controls before external beta.
