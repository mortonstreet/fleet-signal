# Fleet Finance Signals — Technical Execution Pack

**Offer slug:** `fleet-finance`  
**Build stance:** `BUILD_NOW`  
**Commercial target:** $18k–$42k/yr target · modeled sales cycle 4–8 weeks  
**Pack date:** 2026-09-04

## 0. Handoff contract

This document is standalone. A coding agent should be able to implement this offer inside the shared signal-stack architecture without needing to reinterpret the sales offer. When a source/right is marked `CONTRACT_REQUIRED`, `TERMS_REVIEW`, or `BLOCKED`, implementation may build interfaces/fixtures but **must not enable production acquisition or downstream delivery** until the gate changes.

### Product objective

Surface fleets entering refinance, growth or replacement windows by joining state UCC filings to FMCSA carrier records and VIN-level equipment specifications.

### Primary users

- VP Originations
- equipment/fleet finance BDM
- transportation finance sales director
- portfolio/renewal manager

## 1. Product scope and features

### P0 — sellable MVP

- Colorado UCC multi-table ingest
- UCC filing/debtor/secured-party/collateral join
- VIN extraction + validation
- FMCSA carrier entity resolution
- vPIC batch decode cache
- T1 refi/payoff event and score
- lender-book audit
- signal inbox + fleet detail
- CSV/webhook export
- source provenance

### P1 — expansion after P0 proof

- FMCSA historical snapshot deltas for fleet growth
- recall and safety overlays
- additional UCC states behind source-specific rights gate
- competitor lender watchlists
- CRM suppression sync

### P2 — strategic / later

- attribution from subsequent UCC filing naming customer as secured party
- distress SKU
- optional licensed title/NMVTIS data
- customer outcome-driven score calibration

### Non-goals for P0

- No generic dashboard unrelated to the user’s decision workflow.
- No opaque LLM-only scoring.
- No browser-first acquisition where an API/download exists.
- No source/right circumvention.
- No automatic downstream outreach to restricted/consumer contacts unless a separate compliant delivery module is explicitly approved.

## 2. Core domain model

### Canonical entities

- `fleet`
- `carrier`
- `ucc_filing`
- `secured_party`
- `debtor`
- `vehicle`
- `lender`
- `watch`

### Event types

- `UCC_FILED`
- `UCC_CONTINUED`
- `UCC_TERMINATED`
- `LIEN_WINDOW_ENTERED`
- `NEW_AUTHORITY`
- `FLEET_GROWTH`
- `AGING_FLEET`
- `LENDER_SWITCH`

### Signal types

- `refi_opportunity`
- `growth_finance_opportunity`
- `replacement_opportunity`
- `competitive_takeout`
- `portfolio_retention_risk`

### Scoring rules

- T1 timing: months-to-lapse + no continuation + VIN-specific collateral
- growth: power-unit delta + recency
- asset: vehicle class/age/body/GVWR
- contactability + source freshness
- exclude low-confidence UCC↔FMCSA resolutions

**Rule contract:** every score persists `score_version`, feature values, top reason codes, confidence, exclusion reasons and evidence IDs. Hard disqualifiers run before weighted scoring.

## 3. Human UX and workflow

### Golden user workflow

1. Sync CO UCC partitions
2. Join filing↔debtor↔secured party↔collateral
3. Extract VINs and classify blanket collateral
4. Resolve debtor to FMCSA/USDOT
5. Decode VINs in cached 50-VIN vPIC batches
6. Build current lien snapshot
7. Detect month-54+ / no-continuation window
8. Score and match lender territory/watch
9. Generate lender-book leakage audit
10. Record meeting/funded outcome and later attribution


### Required UI surfaces

- Origination signal inbox
- Fleet detail with UCC timeline
- Equipment/VIN table
- Lender/secured-party explorer
- Own-book audit wizard
- Watch builder by state/class/lender
- Source-resolution evidence drawer
- Outcome/funding attribution

### Detail interaction standard

Every signal detail must show:

1. **What changed** — before/after or source event.
2. **Why this signal fired** — reason codes and score features.
3. **Evidence** — source, source record ID/URL, effective time, observed time.
4. **Entity context** — prior events and related entities.
5. **Recommended action/proof asset** — generated from structured fields, editable by human.
6. **Outcome** — offer-specific result state.

### Run UX

Use durable backend stages:

`queued → acquiring → parsing → resolving → diffing → scoring → matching → delivering → completed`

The UI subscribes/polls the run resource; it must not simulate progress client-side.

## 4. Headless CLI / agent workflow

Offer alias: `signalctl fleet`

### Domain commands

```bash
signalctl fleet source sync co-ucc --since 2026-01-01
signalctl fleet source sync fmcsa-census
signalctl fleet ucc join --state CO
signalctl fleet vin decode --pending --batch-size 50
signalctl fleet events detect --type LIEN_WINDOW_ENTERED
signalctl fleet signals list --tier A --state CO
signalctl fleet audit lender --secured-party "Example Bank"
signalctl fleet export --watch <id> --format csv
```

All commands support `--json`, `--non-interactive`, `--dry-run` where mutating/costly, `--idempotency-key`, and explicit limits. Agents should never parse human table output.

### API mapping

| CLI concept | HTTP route |
|---|---|
| source sync | `POST /v1/admin/{offer}/sources/{source_id}/sync` |
| events list | `GET /v1/{offer}/events` |
| signals list | `GET /v1/{offer}/signals` |
| watch create | `POST /v1/{offer}/watches` |
| watch matches | `GET /v1/{offer}/watches/{id}/matches` |
| proof build | `POST /v1/{offer}/proof-assets` |
| export | `POST /v1/{offer}/exports` |
| outcome | `POST /v1/{offer}/outcomes` |
| provenance | `GET /v1/provenance/{record_id}` |

The FastAPI service and CLI call the same Python application-service functions; neither calls the other over HTTP in-process.

## 5. Public APIs / data sources

| Source | Access | Cadence | Rights | Acquisition | Priority |
|---|---|---|---|---|---|
| [Colorado UCC Filing Information](https://data.colorado.gov/d/wffy-3uut) | Socrata open data | source-dependent | `OPEN_CONFIRMED` | `socrata` | P0 |
| [Colorado Secured Party Information](https://data.colorado.gov/d/ap62-sav4) | Socrata open data | source-dependent | `OPEN_CONFIRMED` | `socrata` | P0 |
| [Colorado UCC Collateral Information](https://data.colorado.gov/d/4am6-w6u4) | Socrata open data | source-dependent | `OPEN_CONFIRMED` | `socrata` | P0 |
| [Colorado UCC Debtor Information](https://data.colorado.gov/d/8upq-58vz) | Socrata open data | source-dependent | `OPEN_CONFIRMED` | `socrata` | P0 |
| [FMCSA Company Census File](https://data.transportation.gov/d/az4n-8mr2) | Socrata public dataset | daily-ish; source dataset updated frequently | `OPEN_CONFIRMED` | `socrata` | P0 |
| [NHTSA vPIC Vehicle API](https://vpic.nhtsa.dot.gov/api/) | public API | on demand | `OPEN_CONFIRMED` | `httpx` | P0 |
| [NHTSA Recalls API](https://api.nhtsa.gov/recalls/recallsByVehicle) | public API | on demand | `OPEN_CONFIRMED` | `httpx` | P1 |
| [Florida Secured Transaction Registry](https://floridaucc.com/) | public search / separate download product | unknown | `CONTRACT_REQUIRED` | `manual_or_licensed_download` | P1 |
| [NMVTIS title data](provider-specific) | licensed provider | on demand | `CONTRACT_REQUIRED` | `provider_api` | P2 |

See `SOURCE_REGISTRY.yaml` for machine-readable access/auth/right details.

## 6. Acquisition implementation

No browser required for P0. Use Socrata API/export for Colorado and FMCSA; httpx for vPIC/NHTSA. Add state-specific adapters only after access and downstream-use rights are documented.

### Required connector structure

```text
offers/fleet/sources/
  registry.py
  <source_id>/
    adapter.py
    parser.py
    schemas.py
    fixtures/
    README.md
```

Each adapter implements `fetch(cursor, window, limit)`, `health()`, and returns immutable artifact references. Parsers receive bytes/artifact references—not live browser objects.

### Browser routing when allowed

1. Prefer deterministic Playwright/CDP extraction with Anchor or standard Obscura for JS rendering.
2. Use Hyperbrowser Extract when the page is semi-structured and a JSON schema can bound the output.
3. Use Browser Use only where navigation is genuinely non-deterministic or selectors drift too often.
4. Convert successful agentic/browser runs into deterministic fixtures/selectors when feasible.
5. Never use proxy/stealth/CAPTCHA capabilities to evade source controls.

## 7. Infrastructure and data model

FMCSA and multi-table UCC snapshots belong in ClickHouse/Parquet; canonical fleets/lenders/watch config in Postgres; raw Socrata pages and state exports in R2. VIN decode cache can be ClickHouse or Postgres keyed by VIN+decoder_version.

### Minimum physical tables

#### Postgres

- `fleet_source_config`
- `fleet_canonical_entity`
- `fleet_entity_identifier`
- `fleet_watch`
- `fleet_watch_filter`
- `fleet_suppressions`
- `fleet_outcomes`

#### ClickHouse

- `fleet_source_observations`
- `fleet_entity_observations`
- `fleet_events`
- `fleet_signal_features`
- `fleet_signals`
- `fleet_watch_matches`

#### R2

```text
raw/fleet/{source_id}/{yyyy}/{mm}/{dd}/...
exports/{tenant_id}/fleet/...
proof/{tenant_id}/fleet/...
```

### Data correctness invariants

- Raw artifact stored before parser success is marked.
- Stable source-native IDs are never rewritten.
- Entity merge is reversible/auditable.
- Events are immutable; corrections emit a new event/version.
- `effective_at` and `observed_at` are distinct.
- Watch matching does not mutate global signals.
- Delivery is idempotent by tenant+watch+signal+channel.

## 8. Proof asset

**P0 proof:** Lender Leakage Audit: count own liens entering a refinance/lapse window plus 3–10 competitor-financed fleets with timing, fleet growth and equipment evidence.

Proof assets are generated from structured, source-linked fields and stored as HTML/JSON first. PDF is optional rendering, not the canonical evidence format.

## 9. UI build guidance

### Recommended component tree

```text
fleet/
  SignalInbox
    SignalFilters
    SignalRow
    SignalReasonCodes
  SignalDetail
    ChangePanel
    EvidencePanel
    EntityContext
    RecommendedAction
    OutcomeForm
  WatchBuilder
  EntityDetail
  ProofPreview
  SourceHealthPanel
```

### UI state requirements

For every data surface implement:

- loading
- empty/no-signal
- partial source coverage
- stale source
- source blocked by rights
- backend failure/retry
- no permission

Do not hide source staleness behind a generic success state.

## 10. Scheduled jobs

Default job graph:

```text
source_sync
  -> persist_artifact
  -> parse
  -> resolve_entities
  -> build_snapshot
  -> detect_events
  -> compute_signal_features
  -> score
  -> match_watches
  -> deliver
  -> metrics/outcome-ready
```

Each node retries independently with bounded exponential backoff. Browser jobs run in a separate queue with lower concurrency and explicit dollar/session budgets.

## 11. Tests and evals

### Unit

- parser fixture tests per source
- normalization tests
- exact-ID and ambiguous entity resolution
- every P0 event positive + no-change case
- score feature/reason-code snapshot tests
- rights gate tests

### Integration

- backfill vs incremental reconciliation
- duplicate source artifact replay
- failed source resume from cursor
- signal count parity API vs CLI
- watch idempotency
- export provenance completeness

### E2E

Golden scenario: acquire fixture → parse → resolve → event → signal → watch match → proof → outcome. Network is mocked/replayed in CI.

### Offer-specific blockers to test

- UCC source schemas and availability vary materially by state
- entity resolution between debtor legal names and FMCSA carriers
- blanket liens may lack VINs

## 12. Security / rights / privacy

- Source adapters enforce `rights_status` at runtime.
- Secrets are references, never persisted in raw artifacts/logs.
- Tenant-private data is not used to enrich global public entities unless explicitly configured.
- Browser recordings are off by default and never retain credentials longer than necessary.
- All exports are tenant-scoped and auditable.
- Contact/person data fields carry source/purpose metadata independently from company/event facts.

## 13. Parallel Git worktree plan

This offer uses five feature lanes plus integration. See `WORKTREES.md` for exact commands and path ownership. Freeze `OFFER.yaml`, `SOURCE_REGISTRY.yaml`, event names, API routes and CLI command names on `int/fleet` before opening parallel work.

### Merge order

1. ingest fixtures/adapters
2. domain parsers/events/scores
3. API + CLI
4. UI against frozen OpenAPI/mocks
5. QA/evals/telemetry
6. integration replay and release gate

## 14. Definition of done — P0

- [ ] rights gate green for every enabled production source
- [ ] all P0 source adapters have golden fixtures and health checks
- [ ] incremental sync is idempotent and resumable
- [ ] all P0 event types covered by tests
- [ ] signal scores expose reason codes/evidence
- [ ] CLI and API parity tests pass
- [ ] UI handles stale/partial/blocked states
- [ ] proof asset generated from a replay fixture
- [ ] delivery dedupe verified
- [ ] outcome recording works
- [ ] source outage/schema-drift runbook exists
- [ ] integration branch passes full replay without network access
