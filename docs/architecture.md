# Pulse API architecture

The POC implements BRD FR-01–06, FR-09, FR-12–13 and a limited category trend view. It uses a modular monolith: FastAPI handles validated requests; a separate worker claims source jobs from PostgreSQL; connector adapters call X, YouTube and Reddit; services enforce policy, budget and sentiment rules; repository code persists normalized records. The database is the durable queue for the pilot load profile. Campaign intelligence, prediction, AI conversation, scheduled refresh and cross-source scores are outside this POC.

```text
Client -> FastAPI -> services -> repositories -> PostgreSQL
                         |                         ^
                         v                         |
                 queued source runs -> worker -> gated connectors
```

`pulse/api` owns HTTP contracts, authentication and error conversion. `pulse/services` owns query grammar, capability decisions, search orchestration, trends and sentiment. `pulse/repositories` owns scoped database queries. `pulse/connectors` owns provider translation and normalization. `migrations` owns schema changes. `tests` contains behavior checks. `docs/api/openapi.json` is an exported contract.

All source operations are denied until an operation-specific approval row has evidence, approver, and a future expiry. The worker checks again before each call. A workspace cost ceiling and per-source estimated cost are required before live calls. Search jobs return partial outcomes; no skipped or failed source is counted as zero activity. Content identity is `(workspace, provider, kind, external_id)`; search membership is a separate unique row, so refreshes do not inflate mentions. Publication and observation timestamps remain separate. YouTube remains native display only unless specific derived-use permissions are recorded. No source is claimed as live verified without credentials and approved entitlements.

The production authentication boundary validates OIDC bearer tokens against an issuer's JWKS, audience and issuer. Development uses a local token and a seeded user. Membership checks precede every workspace query. API processes are stateless. The worker claims rows with `FOR UPDATE SKIP LOCKED`, allowing multiple workers. A timed-out worker lease may be reclaimed; uniqueness constraints make retries idempotent. HTTP calls have timeouts and bounded pagination. Provider errors are stored as sanitized source statuses.

Category trends rank observed distinct items in configured categories. A category is an explicit term set, and the API reports its window, source coverage, observed count, prior count and evidence IDs. Search sentiment is a limited English, target-aware VADER estimate; it abstains for absent target, mixed polarity or weak scores. It records the text hash and model version, and returns cited observed items. The BRD's 300-example quality gate remains required before external beta.

Retention defaults to thirty days for permitted content. The `purge-expired` operator command removes content fetched more than thirty days ago and database dependents; schedule it daily in a deployment. Provider-specific retention, deletion synchronization and backup tombstone replay are not implemented in this POC, so the service must not be released to external beta until those BRD controls are complete.
