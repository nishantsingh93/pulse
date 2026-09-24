# Pulse — Business Requirements Document

Version: 1.0 | Prepared: 2026-09-23 | Owner: Nishant Singh

Status: implementation baseline; commercial access and launch decisions pending.

Intended project directory: /Users/nishantsingh/Documents/code/pulse

## 1. Purpose and decision rules

Pulse helps people understand what the social internet is discussing, how conversations are changing, and which observed content and creators contribute to those changes. The primary workflow is **search a topic → inspect evidence → understand momentum → ask a follow-up question**.

This document combines business requirements and an implementation baseline for AI coding agents. It incorporates the user's original attached concept and the referenced “Social media integration comparison” conversation. Numerical examples in the original concept were illustrative, not validated API output or market evidence.

“Must” identifies a release requirement; “should” identifies a proposed default; “later” excludes work from MVP. Requirement IDs must be referenced in tickets and tests. Architecture, quality targets, score weights, and pilot limits below are proposed decisions, not measured results or approved commercial commitments.

Provider contracts and applicable law take precedence over feature requirements. Credentials do not establish rights to retain, analyze, export, or transmit content to an AI provider. Unreviewed operations remain disabled. The product owner approves scope; an engineering owner approves architectural decisions; a designated compliance owner approves platform usage before live release.

## 2. Product vision and business goals

Give marketers, agencies, creators, and product researchers a simple way to answer: “What is happening around this topic, where is it accelerating, and what evidence explains the change?” Pulse combines search, source-aware analytics, trend discovery, and an evidence-backed conversational analyst.

The initial business hypothesis is a subscription product for small teams. Candidate entitlements include live searches, tracked topics, refresh frequency, historical windows, seats, and AI analysis allowance. Validate willingness to pay and acquisition costs before committing to prices. No unlimited live-search promise in MVP.

| ID | Goal | Proposed pilot measure |
|---|---|---|
| G-01 | Reduce time to a useful topic assessment | Median under five minutes in moderated tasks, compared with each participant's existing workflow |
| G-02 | Make findings verifiable | Every AI quantitative claim traces to a tool result; post claims trace to accessible evidence |
| G-03 | Establish recurring value | At least five of ten pilot teams complete a useful search in each of three successive weeks |
| G-04 | Establish viable economics | Report provider, AI, and variable infrastructure cost per successful refresh and active workspace |
| G-05 | Demonstrate useful momentum detection | Offline labeled evaluation and prospective pilot review before any predictive claims |

An activated workspace completes a non-demo search and opens evidence or asks a grounded follow-up within seven days of signup. A useful search is explicitly marked useful by a user; completion alone does not establish value. Retention is measured by workspace cohorts, excluding staff and synthetic activity.

## 3. Scope and non-goals

MVP includes workspaces, keyword/phrase/hashtag search, connector interfaces for X, YouTube, and Reddit, approved live integrations, observed activity charts, native engagement metrics, top posts and creators, eligible text sentiment, related terms, saved topics, and read-only conversational analysis. Comparisons, scheduled refresh, and experimental scoring follow a working core slice.

Initial content units are X posts, Reddit submissions, and YouTube videos. Comments and replies are a separate ingestion scope deferred from MVP; provider comment counts remain metrics and do not become ingested mentions. Supported analytical language is initially English.

Later scope includes TikTok, Instagram, Snapchat, alerts, exports, campaign intelligence, creator/content propagation analysis, and creative benchmarking. Prediction requires legally usable history and prospective validation.

Non-goals: exhaustive network coverage, a universal historical archive, private-message ingestion, inferred demographic targeting, cross-platform identity matching, facial recognition, automated outreach, social publishing, ad buying, causal campaign attribution, guaranteed virality predictions, and a universal reach or engagement-rate metric. Audio/video downloading and transcription, native mobile apps, public reseller APIs, and self-service billing are not MVP requirements.

## 4. Personas and use cases

| Persona | Job | Desired outcome |
|---|---|---|
| Brand marketer | Investigate brand/product discussion | Find recurring praise, complaints, and changes |
| Agency strategist | Research topics for clients | Keep client work separate and explain recommendations with sources |
| Creator researcher | Discover developing conversations | Find relevant content opportunities and creators |
| Product researcher | Understand customer language | Inspect themes and examples with sampling limitations |
| Workspace administrator | Manage access and spend | Control membership, connectors, budgets, and retention |

UC-01: Search “AI agents,” select sources and dates, inspect source-specific results and activity, and open original evidence.

UC-02: Ask “What changed yesterday?” Compare equivalent observed windows, identify correlated themes/posts, and distinguish possible explanations from established causes.

UC-03: Inspect creators ranked within a source and period. “Leading” means leading in the observed sample; it does not establish who originated the conversation.

UC-04: Save a topic and revisit it. Refresh under explicit budgets; show when history started and where observations are missing.

UC-05: Compare two topics using the same sources, intervals, and collection method. Explain overlap and coverage differences.

UC-06, later: Compare a campaign to a defined baseline, inspect disclosed sponsorship, and summarize platform-specific performance without claiming incremental sales or inferred organic status.

## 5. User experience

Start with a search box, example topics, available platforms, date range, and visible freshness. Results include Overview, Posts, Creators, and Ask Pulse. Preserve platform attribution and any required separate presentation, including YouTube-specific result rules.

Every chart exposes its metric definition, time basis, sample size, source coverage, and observation time. Missing values display “Unavailable,” never zero. Loading, no matches, access blocked, partial fetch, quota exhaustion, unsupported analysis, and insufficient history have distinct states. Synthetic data is labeled persistently and cannot mix with live results.

Require keyboard navigation, visible focus, semantic labels, accessible tables behind charts, non-color status indicators, and responsive layouts. Sentiment is labeled an estimate with examples. The product must not characterize a person's personality or emotional health from their posts.

## 6. Functional requirements

| ID | Priority | Requirement | Acceptance condition |
|---|---|---|---|
| FR-01 | P0 | Authentication and workspace roles | Nonmembers cannot access workspace objects, jobs, conversations, or evidence |
| FR-02 | P0 | Keyword, phrase, and hashtag search | Preserve original query, parsed specification, and per-provider translation |
| FR-03 | P0 | Source/date/type/language filters | Unsupported filters are rejected or explicitly explained, never silently assumed |
| FR-04 | P0 | Independent provider ingestion | A provider failure does not discard successful provider results |
| FR-05 | P0 | Normalized records with native semantics | Duplicate delivery creates one logical object; missing metrics remain distinct from zero |
| FR-06 | P0 | Activity by publication time | Refreshing an existing object does not increase mention count |
| FR-07 | P0 | Permitted metric observation history | Current cumulative values and historical changes are distinguishable |
| FR-08 | P0 | Top posts and creators | Display ranking method, source, interval, and observed population |
| FR-09 | P0 | Eligible English text sentiment | Persist target, label, abstention, text hash, and model version |
| FR-10 | P0 | Grounded conversational analysis | Facts have accessible evidence; insufficient evidence is explained |
| FR-11 | P0 | Save, refresh, and delete topics | Deletion stops scheduled work and starts required cleanup |
| FR-12 | P0 | Capability and budget enforcement | UI, API, workers, and AI tools cannot invoke disabled operations |
| FR-13 | P0 | Coverage disclosure | Sampled results are never labeled all-platform volume |
| FR-14 | P1 | Compare up to two topics | Use consistent source/window definitions and show overlap |
| FR-15 | P1 | Related terms | Suggestions have observed counts and examples; a new search is explicit |
| FR-16 | P1 | Experimental Trend Score | Version inputs and formula; expose insufficient-data state |
| FR-17 | P1 | Scheduled refresh | Configured cadence, caps, pause control, and health status |
| FR-18 | Later | Alerts/reports/exports | Permission-aware content, deduplication, and notification preferences |
| FR-19 | Later | Campaign intelligence | Explicit baseline, dates, sponsorship evidence, and attribution limitations |
| FR-20 | Later | Additional networks and prediction | Separate access and evaluation gates |

P0 defines the private-beta core. P1 completes the intended MVP after the core works. A feature can be available for one source and disabled for another by policy.

## 7. Platform integration constraints

Official documentation was reviewed on 2026-09-23. No credentials, agreements, or account entitlements were tested. Recheck current documentation and the actual account before activation.

| Platform | Planned approach | Gate and limitation |
|---|---|---|
| X | Approved search, post metadata, available native metrics | Verify history, operators, commercial/AI rights, retention, and budget; documentation currently describes pay-per-use pricing [S1] |
| YouTube | Data API video discovery and native statistics | Check project quota [S2–S3]; custom analytics and retained history need policy-specific review and applicable permission [S4] |
| Reddit | Approved commercial Data API agreement | Commercial use requires a separate agreement; review processing, AI, retention, and display rights [S5] |
| TikTok | Later approved commercial route or licensed provider | Research Tools exclude commercial users; research eligibility is not a commercial integration strategy [S6] |
| Instagram | Later feasibility spike | Exact account eligibility, discovery scope, permissions, and retention are unverified; broad keyword access must not be promised [S7] |
| Snapchat | Later Public Profile API feasibility | Profile/content metadata and statistics do not establish broad network keyword search coverage [S8] |

YouTube defaults to native discovery/display only. Its policies restrict derived uses and describe additional permissions for audited analytics applications. Until approved for each operation, exclude its data from sentiment, LLM input, custom aggregates, Trend Score, and export. Apply the relevant storage/refresh requirements, attribution, and search presentation rules. This is Pulse's conservative launch configuration; account-specific approval determines the eventual feature set. [S4]

The three-source target is conditional on access. A one-source pilot may proceed only with a recorded scope decision and accurate labeling; it does not pass the three-source integration milestone. Licensed intermediaries must demonstrate rights for Pulse's use. Do not use scraping, unofficial private endpoints, or quota evasion as fallback.

### Capability registry

For each provider record search, native display, historical lookup, metric snapshots, derived analytics, sentiment, LLM processing, embeddings, exports, scheduled refresh, and deletion synchronization. Each operation has approved/denied/unreviewed status, evidence, approver, review date, and expiry. Only approved operations run.

Also record supported query filters, historical window, native metric definitions, rate limits, cost rules, and retention by data class. Effective capabilities are the intersection of provider agreement, workspace entitlement, and product configuration. A provider kill switch stops new work and invalidates affected cached output.

## 8. Query, collection, and coverage semantics

MVP grammar: UTF-8 query of 1–256 characters; whitespace-separated terms imply AND; quoted phrases and hashtags are supported. Defer OR, exclusions, parentheses, and provider-specific syntax. Reject malformed quotes and unsupported operators. Preserve the original query and parsed AST with a version. Explain provider approximations; apply local matching only where permitted, otherwise reject unsupported semantics.

Store UTC and return ISO 8601 timestamps. Intervals are half-open: start inclusive, end exclusive. Default search is the previous seven days. UI time zones do not silently change aggregate definitions. A provider unable to satisfy a requested interval returns a visible limitation; no invented backfill. History begins at legitimate observation or approved backfill.

Capture query parameters, provider ordering, page count, cursor, returned counts, truncation, requested range, observed range, quota status, and cost. Pagination exhaustion does not prove complete network coverage. Changing provider ranking, filters, query, collection caps, or source sets creates a new collection regime.

Proposed pilot limits: 1,000 objects per source per refresh, three concurrent source jobs per workspace, and 20 saved topics. These are product defaults, not claims about provider quotas. Effective limits use the strictest provider, budget, and product constraints. No billable call runs without a configured spend ceiling.

Result revisions bind evidence and aggregates to a stable observed set. Revisions can be invalidated or purged by policy/deletion. Reproducibility does not override deletion obligations. Keep content published time, fetched time, and metric observation time separate.

## 9. Metric definitions

All derived metrics require the relevant source permission. Responses include definition version, population, source, interval, observation time, missingness, and coverage.

| Metric | Definition |
|---|---|
| Observed mentions | Distinct provider+content-type+external-ID objects matching the query and published in the interval; one video/submission is one mention |
| Provider total | Provider-supplied count when exposed, labeled separately from collected objects |
| Growth | 100 × (current − prior) / prior for comparable equal-length windows; prior=0/current>0 returns null and new_activity; both zero returns 0 and no_activity |
| Missing coverage | Null bucket when collection unavailable; zero only when collection ran and returned no eligible objects |
| Native metrics | Views, likes, comments/replies, reposts, quotes, and Reddit score remain separate nullable fields; Reddit score is not likes |
| Engagement total | Explicit source-specific sum only when permitted and semantically valid; no universal cross-source total |
| Engagement rate | Named numerator/denominator for the same population and observation time; null for missing/zero denominator |
| Engagement velocity | Change in a native cumulative metric divided by hours between comparable snapshots; first observation gives no velocity |
| Views | Platform-reported views at observation time; not unique reach and not necessarily views generated during the publication window |
| Unique creators | Distinct provider-specific creator IDs; no cross-platform identity deduplication |
| Creator diversity | Unique observed creators / observed mentions; null for no mentions; not demographic diversity |
| Positive share | Positive / (positive+neutral+negative); show classified population and unknown count |
| Sentiment balance | (positive−negative) / classified count; null when none classified |
| Share of voice | Topic matches / union of matches for the explicit comparison set; disclose overlapping topics, whose shares may sum above 100% |
| Cross-platform spread | Count of eligible comparable sources meeting minimum activity; not proof of causal propagation |
| Top creators | Rank within source by matching object count, then selected native metric, then stable ID; show method |

Default post order uses a versioned text-relevance ranking; source-native metric and publication-time sorts are alternatives. Do not compare views directly with Reddit score. Do not sum cumulative snapshots as period engagement.

Distinct-ID reposts count as observed objects; preserve lineage and offer original-only filtering where supported. Near-duplicate clusters are diagnostics and must not silently remove observations. Negative cumulative metric corrections are flagged and excluded from momentum calculations, not silently converted into growth.

## 10. Experimental Trend Score v0.1

Purpose: rank momentum among monitored topics, not forecast virality or measure the entire internet. Compute only with approved data and comparable collection regimes. Compute source components first; combine only with an explicit source set fixed across the comparison interval.

Daily window: latest complete UTC day versus the preceding seven complete days. Require at least 90% scheduled collection completion in both windows, at least 20 current mentions and five creators per included source, and unchanged query/cap regime. On-demand searches without equivalent collection history are ineligible. Missing collection is never zero activity.

Let clamp01(x)=min(1,max(0,x)):

    G = clamp01(log2((current_daily_mentions+1)/(baseline_daily_mean+1))/3)
    V = clamp01(log2((current_velocity+1)/(baseline_velocity+1))/3)
    D = unique_current_creators/current_mentions
    S = qualifying_sources/eligible_comparable_sources
    R = exp(-hours_since_latest_matching_publication/24)
    score = round(100*(0.40*G+0.20*V+0.15*D+0.15*S+0.10*R))

Current velocity is the median valid per-object hourly change in one configured native metric, using snapshot pairs at most six hours apart and wholly inside the current day. Baseline velocity uses the same method and metric across baseline days. Both require at least 20 valid object deltas. Negative corrections are excluded. For a multi-source score, G, V, D, and R are equal-weight means across the same eligible sources; never sum incompatible raw metrics. A qualifying source for S has at least five current mentions.

If velocity is missing for any included source, return a separate volume_only_v0.1 variant: G=.50, D=.20, S=.15, R=.15. Never silently reweight the full variant. Do not compare variants or differing source sets on one leaderboard. One-source scope is labeled single_source; multi-source scope requires at least two eligible sources. Missing required inputs yield null and a reason.

Store inputs, source set, weights, formula version, sample sizes, and eligibility decisions. Show components and an “Experimental momentum score” label. Thresholds are hypotheses, requiring review against stable large topics, small bursts, spam, outages, seasonality, and changed caps. This score does not estimate probability of future success.

## 11. Normalized data model

Use UUID internal IDs and string provider IDs. Workspace-owned entities carry workspace_id, timestamps, and lineage. Default to separate workspace storage/caches; shared cross-customer caching requires a later permission and isolation design.

| Entity | Essential fields and constraints |
|---|---|
| Workspace | id, name, timezone, spend limits, retention profile, status |
| Membership | workspace_id, user_id, role; unique pair |
| ProviderConnection | workspace_id, provider, secret reference, capability policy, entitlement version, health |
| CapabilityPolicy | provider/data-class/operation, decision, evidence, expiry, approver |
| Topic | query text/AST/version, filters, schedule, enabled, workspace |
| SearchRun | query or topic, requested interval, creator, status, idempotency key, budget reservation |
| SourceRun | search, provider query/cursor, counts, coverage, warnings, cost, status |
| RawEnvelope | source run, payload reference, schema, received_at, expires_at; optional and permission-controlled |
| Creator | provider/external ID, handle, display name, URL, first/last seen; unique workspace/provider/ID |
| Content | provider/type/external ID, nullable creator, published/fetched times, title/text, URL, language, lineage, deleted_at |
| MetricSnapshot | content, observed_at, metric name, nullable value, unit, source run/schema; unique observation key |
| QueryMatch | query version, content, matched_at, match method; unique query/content |
| ResultRevision | run, revision, content membership, computed_at, coverage, invalidated_at |
| Enrichment | content, target, text hash, label/topic, model/prompt version, confidence, abstention, policy version |
| Aggregate | revision, source, bucket, metric definition, values, sample/coverage metadata |
| TrendScore | topic, window, revision, variant, inputs, nullable score, eligibility reason |
| Conversation/Message | workspace/user, revision, question/answer, evidence, model metadata, usage |
| Evidence | revision, content or aggregate reference, original URL, permission state |
| UsageLedger | workspace/run/provider/model, reserved/actual units, currency, reconciliation state |
| DeletionJob/AuditEvent | scope, reason, deadlines, affected stores, completion evidence; no copied post text |

Missing metric reasons: not_exposed, not_authorized, not_collected, deleted. Preserve actual zero. Allow signed Reddit score; reject invalid negative views. Never infer common identity from equal handles.

Indexes include unique scoped external identity; query/content membership; workspace and publication time; content and observation time; run status; expiry; and full-text index on permitted text. Enforce workspace consistency in foreign keys as well as application checks.

Lifecycle: check rights → reserve budget → fetch → validate → normalize/upsert → record coverage → enrich eligible text → aggregate → publish revision. Metadata refresh and historical metric observations are distinct. When raw storage is prohibited, normalize in memory and discard the payload. All derivatives retain input lineage to support purge and recomputation.

## 12. Proposed architecture

Start with a modular monolith and separate web/API/worker processes. Proposed stack: TypeScript/React web frontend; Python/FastAPI API and analytics; PostgreSQL for operational data and initial full-text search; Redis-backed job queue; optional object storage for permitted temporary payloads. Pin supported dependencies during scaffolding. These are design defaults rather than mandatory library versions.

    Browser → Authenticated API → PostgreSQL
                       ↓              ↑
                Budgeted job queue → Connector workers → Approved providers
                                       ↓
                             Normalize/enrich/aggregate
                       ↓
             Read-only AI orchestration → Typed analytics/evidence tools
                       ↓
             Approved model endpoint with minimized permitted evidence

Use transactions for state/budget reservations and a transactional outbox for queue publication. Jobs are at-least-once with idempotent handlers. Connector interface: capabilities, validate_query, estimate_cost, search_page, fetch_metrics, refresh_or_delete, normalize. Keep provider tokens and cursors out of browser responses and logs.

Honor Retry-After. Default transient retry: exponential backoff with jitter, at most five attempts within 15 minutes; persist next_retry_at for longer waits. Authentication and policy errors stop immediately. Dead-letter records contain identifiers and sanitized errors. Recheck policy before execution and publication.

Defer OpenSearch, streaming infrastructure, a warehouse, and vector search until measured load justifies them. Embeddings require separate rights and deletion controls. Support migrations, staging with synthetic data, feature flags, rollback, and backups.

## 13. Internal API contracts

The API serves Pulse's authenticated application and is not a public resale API. All routes under /v1/workspaces/{workspace_id} verify membership and role. JSON uses snake_case; timestamps are UTC; IDs are strings. Maintain OpenAPI as the shared contract before parallel implementation.

| Method/path below workspace | Contract |
|---|---|
| GET /capabilities | Effective provider operations, disabled reasons, limits, freshness |
| POST /searches | Validate, reserve cost, enqueue; 202 with search_id and status URL |
| GET /searches/{id} | Overall/source status, warnings, latest revision |
| POST /searches/{id}/cancel | Stop future pages and release unused reservation; 202 |
| GET /searches/{id}/results | revision/cursor/limit parameters; stable page and next cursor |
| GET /searches/{id}/metrics | revision/bucket parameters; typed permitted aggregates |
| GET /searches/{id}/creators | revision/platform parameters; source-specific ranking |
| POST/GET /topics | Create/list saved topics; create returns 201 |
| PATCH/DELETE /topics/{id} | Versioned changes; delete returns 202 and cleanup ID |
| POST /conversations | Bind to search and revision; 201 |
| POST /conversations/{id}/messages | Submit question; 202 with analysis job ID |
| GET /analysis-jobs/{id} | Pending status or answer, claims, evidence, limitations, usage |
| GET /evidence/{id} | Revalidate permissions/deletion before returning attributable evidence |
| POST /deletion-requests | Authorized scoped request; 202 with job ID |
| GET /deletion-requests/{id} | Per-store progress and completion |

Example search request, using synthetic identifiers and dates:

~~~json
{
  "query": "AI agents",
  "platforms": ["x", "youtube", "reddit"],
  "time_range": {"start": "2026-09-16T00:00:00Z", "end": "2026-09-23T00:00:00Z"},
  "language": "en",
  "allow_partial_sources": true,
  "max_items_per_source": 1000
}
~~~

If allow_partial_sources=false, reject unavailable sources before spending. If true, report each skipped source and reason. With no eligible sources, return 422 without provider calls. Unsupported language filtering requires permitted local filtering or rejection.

~~~json
{
  "search_id": "sr_example",
  "status": "partial",
  "revision": "rev_example_1",
  "sources": [
    {"platform": "x", "status": "succeeded", "coverage": "sampled", "collected_count": 412},
    {"platform": "youtube", "status": "succeeded", "coverage": "sampled", "collected_count": 38, "analysis_enabled": false},
    {"platform": "reddit", "status": "blocked", "reason": "commercial_access_not_approved"}
  ],
  "warnings": ["Observed results do not represent all platform activity."]
}
~~~

Job transitions: queued → running → succeeded/partial/failed/cancelled. Source jobs may additionally be blocked. Partial means at least one source succeeded and another was incomplete, blocked, or failed. If none succeeds, the search fails. Running revisions are provisional. Terminal revisions are stable except policy/deletion invalidation.

Job-creating POSTs require Idempotency-Key scoped to workspace+route+body hash for 24 hours. Same key/body returns the original resource; changed body returns 409. Signed cursors bind workspace, query, revision, filters, and sort. Default page size 25; maximum 100. Invalidated revisions return 410. Concurrent topic updates require a version/ETag precondition.

~~~json
{
  "error": {
    "code": "BUDGET_EXCEEDED",
    "message": "This workspace has reached its configured search budget.",
    "retryable": false,
    "request_id": "req_example",
    "details": {"scope": "workspace"}
  }
}
~~~

Status mapping: 400 malformed input; 401 unauthenticated; 403 role denial; 404 absent/nonmember object; 409 version/idempotency conflict; 410 invalid revision; 422 unsupported capability; 429 local rate/budget limit; 503 unavailable service. Provider failures after acceptance appear in source status. Schemas must explicitly allow null and declare metric units.

## 14. AI analyst behavior

The runtime analyst is read-only. Allowed typed tools: get_capabilities, get_metrics, compare_windows, list_posts, list_creators, get_evidence, get_trend_components. Each executes with authenticated workspace and pinned revision. No arbitrary SQL, shell, credentials, or unrestricted URL fetching. A new paid search requires a separate explicit user action.

Flow: identify scope → inspect permissions/coverage → obtain deterministic aggregates → retrieve bounded permitted evidence → draft claims → validate numbers/citations → return answer and limitations. Counts and percentages come from analytics tools, not model arithmetic. Defaults: eight tool calls, 40 evidence objects, 30-second timeout, and configured per-answer token/cost limits, enforced outside the model.

Answer schema: answer, claims with fact/inference kind, evidence_ids, metric_refs, limitations, revision, as_of. Every factual number must match a typed aggregate; every post claim must resolve to permitted evidence. On validation failure, retry once within budget; then return deterministic metrics with “Analysis unavailable.”

For “why,” distinguish correlation and plausible explanation from causation. For “who started it,” use “earliest observed in this dataset” unless stronger evidence exists. Unsupported demographic, location, private-content, or predictive questions must state what is unavailable. Show contradictory evidence when present. Unknown sentiment is not neutral.

Treat social content as untrusted quoted data. Instructions, code, or URLs in content must never change tool scope, budgets, or system behavior. Do not automatically follow links in posts. Test injection attempts to expose secrets, access other workspaces, change limits, or invoke unauthorized tools.

No training or fine-tuning on provider content by default. Model processing, retention, residency, training use, and subprocessors require source-compatible approval. Minimize evidence and traces; source deletion applies to stored prompts and answers. Customer queries can reveal strategy and remain workspace-confidential.

### Sentiment and related topics

Analyze permitted English text only. Labels: positive, neutral, negative, unknown. Unknown covers low confidence, unresolved mixed polarity, unsupported language, insufficient context, or no text. Target is the queried topic; abstain if target sentiment cannot be established. Store target, text hash, model/prompt version, and abstention reason.

Use at least 300 legally usable holdout examples balanced across eligible sources and labels. Proposed target: macro-F1 ≥0.75 on supported classes; separately report abstention, coverage, confusion matrix, and per-source performance. Calibrate confidence thresholds on holdout data; a model's self-reported confidence alone is insufficient. Related terms start with deterministic co-occurrence and supporting examples; semantic clustering is later.

## 15. Privacy, compliance, and security

Before external beta, establish jurisdiction, lawful basis, privacy notices, subject-request process, contracts, and processor terms. This BRD specifies controls and does not determine that a particular legal regime or proposed use is satisfied.

Retention is per provider and data class: originals, native observations, derivatives, prompts, caches, and backups. Proposed defaults where permitted: raw envelopes 24 hours; content/snapshots and conversations 30 days; sanitized operational logs 30 days; content-free security audit events 90 days. Stricter obligations win. Longer history requires approval. Derivatives do not automatically outlive source content.

Deletion immediately suppresses evidence and cached answers, then purges or recomputes relational data, queue payloads, object storage, indexes, optional embeddings, aggregates, and AI traces. Target active-store completion within 24 hours; shorter obligations override. Backups expire within 30 days where allowed; restore must replay tombstones before serving traffic. Replayed jobs must not resurrect deleted records. Record a content-free deletion receipt by store.

Use managed authentication, TLS, secure HTTP-only cookies, applicable CSRF protection, encryption at rest, secrets management, and least-privilege service identities. Owner/admin manages members, connectors, budgets, and deletion. Analyst searches/saves/asks. Viewer reads existing authorized results only. Tenant checks apply to jobs, caches, tools, and evidence as well as HTTP endpoints.

Bound query complexity and input lengths, parameterize SQL, sanitize rendered content, block executable markup, and allowlist outbound provider hosts to reduce SSRF. Audit permission/configuration/budget changes, deletions, and exports without logging content or tokens. Run dependency/secret scanning and object-authorization tests before beta. No protected-trait inference or creator contact enrichment in MVP.

## 16. Observability, reliability, and economics

Proposed beta load profile: 20 concurrent active users, 100,000 retained permitted content objects per workspace, and configured refresh caps. Validate these targets under a documented test environment.

| Measure | Target |
|---|---|
| Internal API availability | 99.5% monthly; report provider availability separately |
| Cached results | p95 under two seconds, excluding client network |
| Search acceptance | p95 under one second to validate/queue |
| Fresh source results | First available source within 15 seconds p95 under normal provider response; at 60 seconds show explicit ongoing/partial state |
| AI answer | p95 under 30 seconds or bounded fallback |
| Tracked topic freshness | Proposed hourly refresh where permitted/affordable; display actual lag |
| Recovery | Proposed RPO ≤24 hours and RTO ≤4 hours, verified by restore exercise |

Trace request, workspace, search, source run, job, and analysis IDs. Measure queue age, fetch success/timeouts/429s, new/duplicate objects, null metric rates, collection coverage, snapshot lag, sentiment abstention, citation failures, token usage, budget reservations, actual charges, and deletion deadlines. Redact content and secrets.

Alert operators on sustained backlog, provider failure spikes, expired approvals, deletion deadline risk, and budget reconciliation discrepancies. Warn at 80% of configured spend; pause at the limit. Document runbooks and responsible owners. End users should see source health without repeated notifications for unchanged outages.

Cost per refresh = provider charges + model charges + attributed variable infrastructure. Cost per useful search uses explicit usefulness feedback and is null when there are no useful searches. Reserve budget atomically before work, reconcile afterward, and release unused reservations. Bound concurrent reservations. Report billing uncertainty rather than implying the local ledger perfectly predicts provider charges.

## 17. MVP phases and exit gates

| Phase | Deliverable | Exit gate |
|---|---|---|
| 0 — Feasibility | Rights matrix, actual entitlements/prices, budgets, query/metric definitions | Every operation classified; blocked sources have synthetic fixtures; no unreviewed spend |
| 1 — Foundation | Auth, schema, jobs, synthetic search UI, first approved connector | Search → evidence works; isolation, retry, budget, and deletion tests pass |
| 2 — Initial sources | X, native YouTube discovery, Reddit under agreement | Three permitted connectors pass live tests, or owner records reduced pilot scope |
| 3 — Analytics | Eligible history, rankings, sentiment, related terms, score flag | Metric golden tests and quality review pass; denied operations stay disabled |
| 4 — Private beta | Grounded AI, telemetry, restore, pilot onboarding | Citation, injection, deletion, load, and user-task review pass |
| 5 — Complete MVP | Comparisons, approved scheduled refresh, validated score | All P1 requirements pass within agreed cost limits |
| 6 — Expansion | Campaign features, reports/alerts, later platforms | Independent rights review and customer demand per feature |
| 7 — Prediction research | Creative benchmarks and forecast experiments | Legally usable history, held-out/prospective evaluation, calibrated uncertainty |

Phases express dependencies, not calendar promises. External approvals may determine the timeline. Synthetic development can proceed while access is pending but cannot count as live integration acceptance.

## 18. Acceptance criteria and testing

| ID | Scenario | Expected result / requirements |
|---|---|---|
| AC-01 | B requests A's search/job/evidence/conversation | No data leakage; FR-01, FR-10 |
| AC-02 | Provider page delivered twice | One logical content object and one observation per dedup key; FR-05–07 |
| AC-03 | X succeeds, Reddit blocked, YouTube native-only | Partial state and correct capability enforcement; FR-04, FR-12 |
| AC-04 | Missing views versus actual zero | Different stored/displayed states; FR-05 |
| AC-05 | Prior zero and current positive | Null growth with new_activity label; FR-06 |
| AC-06 | Missing baseline collection | Missing bucket, suppressed incomparable growth/score; FR-13, FR-16 |
| AC-07 | Likes snapshots 10 then 15 | Delta 5, never 25; FR-07 |
| AC-08 | Sarcasm or unclear target | Supported correct label or abstention; quality report records errors; FR-09 |
| AC-09 | Post instructs model to expose secrets | No permission change, leak, or unauthorized tool call; FR-10 |
| AC-10 | Model invents a quantitative claim | Validation rejects it; bounded retry/fallback; FR-10 |
| AC-11 | Requested history exceeds entitlement | Visible unsupported range, no invented backfill; FR-03 |
| AC-12 | Deletion races ingestion | Immediate suppression and no resurrection; FR-11–12 |
| AC-13 | Concurrent jobs exceed combined budget | Atomic reservations prevent overspend; FR-12 |
| AC-14 | Approval revoked after answer caching | Affected output invalidated and cleaned up; FR-12 |
| AC-15 | Query/source/cap regime changes | New regime; no equivalent-history claim; FR-13, FR-16 |
| AC-16 | User asks who originated a topic | Earliest-observed qualification or insufficient evidence; FR-10 |
| AC-17 | Two topics overlap | Union denominator and overlap disclosure; FR-14 |
| AC-18 | No prior metric snapshot | Native value available, velocity unavailable; FR-07, FR-16 |
| AC-19 | Source lacks sentiment/LLM permission | No enrichment, transmission, or derived result; FR-09–12 |
| AC-20 | Backup restored after a deletion | Tombstones replay before serving; deleted content absent; FR-11 |

Testing layers: unit tests for metrics and policy rules; golden connector fixtures; mocked contracts for pagination/429s/deletion; database tests for isolation/idempotency/budgets; UI end-to-end tests for primary and degraded flows; capped approved live smoke tests; at least 50 representative/adversarial AI questions.

AI release thresholds: all citations resolve and are authorized; all displayed numeric claims match tool outputs; zero cross-workspace leakage in the evaluation suite; at least 90% human-rated supported factual claims. These finite tests are release evidence, not universal future guarantees. Review at least ten spike/stable-topic cases before enabling scores.

Definition of done: linked requirement, permission enforcement, relevant passing checks, documented schema/config changes, accessible UI states when applicable, sanitized telemetry, and no unreviewed provider spend. Release requires access, deletion, cost, quality, and operational signoff.

## 19. Prioritized implementation backlog

| Ticket | Priority | Deliverable | Dependencies | Acceptance |
|---|---|---|---|---|
| PULSE-001 | P0 | Rights matrix and budget/capability configuration | None | Phase 0; AC-19 |
| PULSE-002 | P0 | OpenAPI, query/metric schemas, synthetic fixtures | 001 | FR-02–03; AC-04–05 |
| PULSE-003 | P0 | Web/API/worker scaffold, CI, configuration | 002 | Reproducible synthetic workflow |
| PULSE-004 | P0 | Auth, roles, workspace isolation | 003 | AC-01 |
| PULSE-005 | P0 | Schema, migrations, lineage, TTL, tombstones | 002–004 | AC-02, AC-12 |
| PULSE-006 | P0 | Queue/outbox, retries, reservations | 004–005 | AC-02, AC-13 |
| PULSE-007 | P0 | X connector and entitlement checks | 001,005–006 | Capped live test; AC-11 |
| PULSE-008 | P0 | YouTube native discovery/display | 001,005–006 | AC-03, AC-19 |
| PULSE-009 | P0 | Reddit connector with commercial gate | 001,005–006 | Agreement-linked activation |
| PULSE-010 | P0 | Search/results/coverage/evidence UI | 002,004,006 | UC-01; AC-03–04 |
| PULSE-011 | P0 | Permitted activity/native snapshot analytics | 005–010 | AC-05–07, AC-18 |
| PULSE-012 | P0 | Rankings and saved topics | 010–011 | FR-08, FR-11 |
| PULSE-013 | P0 | Sentiment and holdout evaluation | 001,005,011 | Quality target; AC-08, AC-19 |
| PULSE-014 | P0 | AI tools, validators, evaluation | 010–013 | AC-09–10, AC-16 |
| PULSE-015 | P0 | Deletion propagation and restore checks | 005–014 | AC-12, AC-14, AC-20 |
| PULSE-016 | P0 | Cost/operations dashboard and load checks | 006–015 | Section 16 targets |
| PULSE-017 | P1 | Comparison and related terms | 011–014 | AC-17; FR-14–15 |
| PULSE-018 | P1 | Experimental score and component UI | 011,013,016 | AC-06, AC-15, AC-18 |
| PULSE-019 | P1 | Scheduled refresh and pause controls | 006,012,016 | FR-17 and budget checks |
| PULSE-020 | Later | Campaign/alerts/reports/platform expansion specs | Complete MVP | Separate approved requirements |

Recommended first build: PULSE-002 through PULSE-006 using synthetic fixtures, followed by the first approved live connector. Foundation development can use deny-by-default capability decisions while contracts are pending. Budget approval is required before paid integration testing.

## 20. Risks and mitigations

| Risk | Impact | Mitigation / owner |
|---|---|---|
| Commercial access unavailable | Three-source target delayed | Recorded narrower pilot; product owner |
| Derived/AI uses restricted | Analytics unavailable on a source | Runtime capability gates and native display; compliance |
| API cost exceeds subscription value | Unsustainable economics | Metering, reservations, refresh caps; product/engineering |
| Sampling changes | False growth | Collection-regime versions and score suppression; data owner |
| Cold start / limited retained history | Weak baseline | Honest history start and insufficient-data state; product |
| Spam/amplification | Misleading momentum | Duplicate and participation diagnostics; data owner |
| AI fabrication/injection | Trust/security failure | Typed tools and validation; AI engineering |
| Sentiment bias/error | Misleading interpretation | Supported scope, abstention, holdout review; data owner |
| Deletion leaves derivatives | Privacy/contract failure | Lineage and purge/restore controls; security/engineering |
| Weak demand | Low adoption | Pilot task research and willingness-to-pay validation; product |

## 21. Open questions

| Question | Implementation default | Owner / deadline |
|---|---|---|
| Which segment leads the pilot? | Small brand/agency research teams | Product before onboarding |
| Monthly provider/AI budget? | No live spend until ceiling configured | Product before live testing |
| Which agreements already exist? | None assumed | Product/compliance, Phase 0 |
| Which sources permit custom analytics/AI? | Disabled until approved per operation | Compliance, Phase 0 |
| Hosting region and jurisdictions? | Configurable; decide before external beta | Product/compliance |
| Required/allowed retained history? | Conservative per-source TTL, no long-history promise | Compliance before ingestion |
| English-only acceptable? | English analysis initially | Product before pilot |
| Reduced-source pilot acceptable? | Requires recorded scope decision | Product after feasibility |
| Should replies/comments be included? | Excluded initially | Product after cost/quality review |
| Pricing and tiers? | Manual pilot entitlements, billing later | Product after validation |
| Is Pulse branding/domain available? | Working project name | Product before public launch |
| Optimal score weights? | Experimental v0.1 only | Data/product after evaluation |

Nonblocking defaults let agents build immediately. Rights, spend limits, and beta privacy decisions must remain explicit gates and cannot be replaced with invented approvals.

## 22. Recommended repository and document structure

~~~text
pulse/
  BRD.md
  README.md
  AGENTS.md
  .env.example
  apps/
    web/
    api/
    worker/
  packages/
    contracts/
    analytics/
    connectors/
      x/
      youtube/
      reddit/
    ai/
  db/migrations/
  tests/
    unit/
    integration/
    contracts/
    e2e/
    evaluations/
    fixtures/synthetic/
  docs/
    decisions/
    product/user-flows.md
    product/backlog.md
    integrations/rights-matrix.md
    integrations/provider-capabilities.md
    data/metric-dictionary.md
    data/retention-and-deletion.md
    api/openapi.yaml
    ai/behavior-and-evaluation.md
    security/threat-model.md
    operations/runbooks.md
    operations/cost-model.md
  infra/
  scripts/
~~~

README explains synthetic local startup, configuration, and checks. AGENTS.md records ownership, test commands, secret handling, rights enforcement, and completion expectations. The environment example contains placeholders only. Architecture decision records explain refinements; the backlog and rights matrix track actual status without silently rewriting baseline requirements.

Coding-agent workflow: read BRD and applicable AGENTS.md; claim a dependency-ready ticket; inspect contracts; implement a complete small slice; run relevant acceptance checks; document assumptions/migrations; report results and unresolved gates. Parallelize frontend against agreed fixtures and connectors against stable interfaces. Assign one owner for shared schema changes. Agents cannot approve commercial rights, raise budgets, or label synthetic output as live verification.

## 23. Official source register

Reviewed on 2026-09-23 for feasibility. Revalidate effective terms and account-specific agreements before activation. This register does not establish that access was granted.

- **S1:** [X API pricing](https://docs.x.com/x-api/getting-started/pricing) — pricing model and spend controls; actual console rates drive configuration.
- **S2:** [YouTube Data API overview](https://developers.google.com/youtube/v3/getting-started) — setup and quota context.
- **S3:** [YouTube search.list](https://developers.google.com/youtube/v3/docs/search/list) — discovery parameters and endpoint quota information.
- **S4:** [YouTube developer policies](https://developers.google.com/youtube/terms/developer-policies) — presentation, derived-use, storage, and permission constraints.
- **S5:** [Reddit Data API terms](https://redditinc.com/policies/data-api-terms) — commercial agreement requirement and data-use conditions.
- **S6:** [TikTok Research Tools FAQ](https://developers.tiktok.com/docs/en/research-api-faq) — commercial users are not eligible for Research Tools.
- **S7:** [Instagram hashtag-search documentation](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-facebook-login/hashtag-search) — page could not be retrieved during preparation; capabilities remain unverified.
- **S8:** [Snap Public Profile API](https://developers.snap.com/marketing-api/Public-Profile-API/Introduction) — public-profile integration scope.

The user's original concept is the source of the product direction. Prior conversational claims that integrations would be easy are not access guarantees. Implementation success requires both technical functionality and permission for the specific use.
