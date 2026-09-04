# Shared UI System and Workflow Guidance

## 1. Product shape

The UI is a **signal inbox + watch builder + evidence inspector**, not a generic dashboard.

Primary navigation:

1. `Signals` — ranked new opportunities/events
2. `Watches` — saved filters and delivery rules
3. `Entities` — company/person/property/device/etc. records
4. `Proof` — generated sample/audit assets used in sales or decision workflows
5. `Exports / Delivery`
6. `Sources` — health/freshness/coverage (admin/power users)
7. `Settings`

Offer-specific pages are thin projections of these primitives.

## 2. Signal list pattern

Each row/card shows:

- event headline
- score/tier
- effective time and observed time separately
- top 2–3 reason codes
- canonical entity
- money/volume magnitude when relevant
- evidence/source badge
- quick actions: `inspect`, `save`, `suppress`, `export`, `mark outcome`

No opaque “AI score” without reason codes.

## 3. Signal detail drawer/page

Sections:

- **What changed** — before/after diff
- **Why it matters** — deterministic reason codes
- **Evidence** — source links, timestamps, raw record references
- **Entity context** — history and related signals
- **Recommended play** — buyer-specific copy/proof asset, editable
- **Outcome** — contacted, meeting, qualified, funded/placed/etc.

## 4. Watch builder

Use domain filters with a live estimated-result preview. Advanced JSON editor is available but secondary.

State machine:

`draft -> validated -> active -> paused -> archived`

Changes that materially increase source/browser cost display an estimated cost impact before save.

## 5. Run state

All source/analysis operations use a shared visible state:

`queued -> acquiring -> parsing -> resolving -> diffing -> scoring -> matching -> delivering -> completed`

Possible terminal states: `completed`, `partial`, `failed`, `blocked_by_rights`, `cancelled`.

The UI consumes durable backend events; it never infers completion from browser timers.

## 6. Visual design

Keep the implementation lightweight and data-dense:

- neutral palette; no decorative gradients required
- system fonts
- table/list first
- details in drawers/side panels
- keyboard navigation for power users
- responsive but desktop optimized
- empty states explain the next useful action
- source health is visible without leaking low-level diagnostics into normal user flows

The 90s treemap can remain a portfolio/offer chooser, but individual offer products should use conventional information architecture.

## 7. UX telemetry

Capture product events, not raw sensitive content:

- signal_opened
- watch_created/edited/paused
- proof_generated
- export_created
- delivery_configured
- outcome_recorded
- source_health_viewed
- explanation_expanded

Attach `offer`, `signal_type`, `tenant_id_hash`, and latency/cost buckets. Do not log raw emails, private CRM content, or API secrets.
