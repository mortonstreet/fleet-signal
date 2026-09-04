# Shared Signal Platform Architecture

## 1. Target repository shape

```text
signal-stack/
  apps/
    web/                    # Next.js / React TypeScript UI
    api/                    # FastAPI HTTP + OpenAPI
    worker/                 # Python ingestion/diff/scoring/delivery workers
  packages/
    contracts/              # Pydantic models + generated TypeScript types
    acquisition/            # HTTP/bulk/browser provider abstractions
    connectors/             # reusable source helpers (Socrata, SFTP, openFDA, SAM, etc.)
    entities/               # normalization/entity-resolution primitives
    events/                 # snapshot/diff/event ledger primitives
    scoring/                # deterministic feature + score framework
    delivery/               # webhook/email/CSV/object-store exports
    cli/                    # Typer CLI: signalctl
    telemetry/              # OpenTelemetry + Sentry/PostHog wrappers
  offers/
    recruiting/
    fleet/
    fda510k/
    fl_tax_lien/
    acris/
    cre/
    freight/
    govcon/
    permits/
    nmls/
  migrations/
  infra/
  tests/
```

## 2. Runtime stack

| Concern | Default | Why |
|---|---|---|
| Web | Next.js App Router + TypeScript | Fast iteration, server rendering, Vercel deploy |
| API | FastAPI + Pydantic v2 | Typed OpenAPI, Python-native data workflows |
| CLI | Typer + Pydantic | Same use cases as API, easy JSON/non-interactive mode |
| Worker | Python async workers + Redis queue/locks | Reuse parsers; bounded retries; low ops burden |
| Transaction DB | Supabase Postgres | tenant config, users, source config, watches, entity canonical keys, entitlements |
| Event/history DB | ClickHouse | append-heavy observations, events, scores, delivery/outcome analytics |
| Raw lake | Cloudflare R2 / S3 | immutable HTML/JSON/CSV/ZIP/PDF artifacts and replayability |
| Cache/queue | Upstash Redis / Redis | locks, rate limits, cursors, small job payloads |
| Local analytics | DuckDB + Parquet + Polars | backfills, source QA, reproducible local tests |
| Auth | Clerk | tenant membership / RBAC; API service tokens separately scoped |
| Billing | Stripe | entitlements and usage limits |
| Observability | Sentry + OpenTelemetry + PostHog | errors/traces + product events |
| Deploy | Vercel web; Railway API/workers | matches existing operating model |

Do not put high-volume event history in Postgres unless the offer is tiny. Do not put customer configuration in ClickHouse.

## 3. Canonical lifecycle

### 3.1 Ingest

`SourceAdapter.fetch()` returns an immutable `RawArtifact` reference:

- `source_id`
- `source_native_cursor`
- `fetched_at`
- `effective_at` / source publication time if known
- `http_etag` / `last_modified` if available
- `content_sha256`
- `storage_uri`
- `terms_snapshot_id`
- `parser_version`

### 3.2 Parse and normalize

`SourceParser.parse(raw_artifact)` emits source records. Never mutate the artifact. A re-parser can replay old artifacts under a new version.

### 3.3 Resolve

Resolve source identities to canonical entities with evidence:

- exact IDs first (UEI, USDOT, K-number, BBL, NMLS ID, license number)
- deterministic normalized name/address second
- fuzzy matching only as a candidate generator
- LLM-assisted resolution never auto-merges without a confidence policy

### 3.4 Diff

Compare snapshots using domain-specific stable keys. Emit immutable events with `before`, `after`, and evidence IDs.

### 3.5 Score

Scores are functions of explicit features. Persist:

- feature values
- feature version
- score rule version
- top reason codes
- confidence
- eligibility/exclusion reasons

### 3.6 Match and deliver

A signal is customer-independent. A watchlist match is customer-specific. Keep these distinct so one source event can serve many tenants cheaply.

## 4. Multi-tenant boundaries

- `tenant_id` is required on watchlist, delivery, outcome, CRM sync and user-created object tables.
- Public source records and canonical public entities are global, not duplicated per tenant.
- Customer suppressions, private CRM/ATS imports and outcomes live in tenant-scoped tables.
- Never leak tenant-private enrichment into a global entity without explicit policy.

## 5. Suggested tables

### Postgres

`tenants`, `memberships`, `api_tokens`, `offer_entitlements`, `source_configs`, `source_rights`, `watches`, `watch_filters`, `delivery_channels`, `suppressions`, `crm_connections`, `private_entities`, `outcomes`, `feature_flags`, `audit_log`.

### ClickHouse

`source_observations`, `entity_observations`, `events`, `signal_features`, `signals`, `watch_matches`, `deliveries`, `delivery_attempts`, `outcome_facts`, `pipeline_metrics`.

### R2

```text
raw/{source_id}/{yyyy}/{mm}/{dd}/{artifact_id}.{ext}
exports/{tenant_id}/{offer}/{export_id}.{csv|jsonl|parquet}
proof/{tenant_id}/{offer}/{proof_id}.{html|json|pdf}
replay/{run_id}/manifest.json
```

## 6. Shared service interfaces

```python
class SourceAdapter(Protocol):
    async def fetch(self, cursor: str | None, limit: int | None) -> FetchBatch: ...
    async def health(self) -> SourceHealth: ...

class Parser(Protocol):
    def parse(self, artifact: RawArtifact) -> Iterable[SourceRecord]: ...

class Resolver(Protocol):
    async def resolve(self, record: SourceRecord) -> ResolutionResult: ...

class EventDetector(Protocol):
    def diff(self, previous: Snapshot | None, current: Snapshot) -> list[Event]: ...

class SignalRule(Protocol):
    def evaluate(self, event: Event, context: SignalContext) -> SignalDecision: ...
```

## 7. Idempotency

Every mutating command/API call accepts an `idempotency_key`. Derive ingest job idempotency from:

`sha256(source_id + partition + cursor/window + parser_version)`.

Event uniqueness is based on:

`sha256(offer + event_type + canonical_entity_id + effective_at + stable_event_payload)`.

## 8. API boundary

Shared routes:

- `GET /v1/offers`
- `GET /v1/{offer}/entities`
- `GET /v1/{offer}/events`
- `GET /v1/{offer}/signals`
- `POST /v1/{offer}/watches`
- `GET /v1/{offer}/watches/{id}/matches`
- `POST /v1/{offer}/exports`
- `POST /v1/{offer}/proof-assets`
- `POST /v1/{offer}/outcomes`
- `GET /v1/provenance/{record_id}`
- admin: `POST /v1/admin/{offer}/sources/{source_id}/sync`
- admin: `GET /v1/admin/runs/{run_id}`

Offer-specific routes are allowed only where the domain truly adds behavior; do not proliferate CRUD endpoints for UI convenience.

## 9. Deployment topology

```text
Vercel Web
    |
    v
Railway FastAPI ---- Supabase Postgres
    |                       |
    |                       +-- tenant config / watches / auth mappings
    |
    +---- Redis <---- Railway Workers ---- public APIs / bulk / browser providers
    |                          |
    |                          +---- R2 raw artifacts
    |
    +---- ClickHouse <---------+---- events / signals / analytics
```

Use separate worker queues per source family (`http`, `bulk`, `browser`, `enrichment`, `delivery`) so a degraded browser source cannot starve deterministic API ingestion.
