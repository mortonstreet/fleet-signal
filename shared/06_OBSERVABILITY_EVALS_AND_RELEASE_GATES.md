# Observability, Evals, and Release Gates

## 1. Source telemetry

Per source/run capture:

- fetch latency
- HTTP/status family
- rows/artifacts fetched
- bytes downloaded
- parse success/failure rate
- schema drift count
- entity resolution exact/fuzzy/unresolved rates
- events emitted
- duplicate suppression count
- API/browser cost
- source effective time -> observed time latency

## 2. SLOs

Each offer defines its own freshness target, but shared platform SLOs are:

- 99.5% scheduled-run execution success excluding upstream outages
- 100% raw artifact persistence before parse on production runs
- 0 duplicate event deliveries for the same tenant/watch/event/idempotency key
- provenance available for 100% of delivered source-derived fields
- failed deliveries retry with bounded exponential backoff + dead-letter visibility

## 3. Golden fixtures

Every offer maintains a compact golden corpus with:

- positive events for every P0 event type
- no-change snapshot pairs
- deletion/termination/close cases
- malformed records
- ambiguous entity match
- source schema drift fixture
- time-zone/date edge cases

## 4. Product evals

Measure:

- precision of event detection
- entity resolution accuracy
- scoring stability between versions
- top-K usefulness using customer outcomes
- proof-asset field correctness
- false urgency / stale-event rate

No scoring model ships based only on synthetic data.

## 5. Release gates

A P0 offer is production-ready only when:

1. rights/source gate is green
2. 7 consecutive scheduled runs pass or equivalent replay corpus exists
3. source health endpoint works
4. backfill and incremental paths reconcile
5. idempotent replay emits no new duplicates
6. UI and CLI show identical signal counts for the same filters
7. all proof assets trace to provenance
8. tenant isolation tests pass
9. stop/retry/backoff behavior is exercised
10. runbook exists for source schema change/outage
