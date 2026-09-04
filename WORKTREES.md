# Fleet Finance Signals — Parallel Worktree Instructions

## Contract-freeze branch

```bash
git worktree add ../wt-fleet-int -b int/fleet main
```

Freeze and commit first:

- `offers/fleet/contracts/**`
- `offers/fleet/source_registry.yaml`
- `offers/fleet/domain/event_types.py`
- `offers/fleet/domain/signal_types.py`
- REST route names
- CLI command names

## Parallel lanes

```bash
git worktree add ../wt-fleet-ingest -b feat/fleet/ingest int/fleet
git worktree add ../wt-fleet-domain -b feat/fleet/domain int/fleet
git worktree add ../wt-fleet-api-cli -b feat/fleet/api-cli int/fleet
git worktree add ../wt-fleet-ui -b feat/fleet/ui int/fleet
git worktree add ../wt-fleet-qa -b feat/fleet/qa int/fleet
```

## Exclusive ownership

| Lane | May edit |
|---|---|
| ingest | `offers/fleet/sources/**`, source fixtures |
| domain | `offers/fleet/domain/**`, domain tests |
| api-cli | `offers/fleet/api/**`, `offers/fleet/cli/**` |
| ui | `apps/web/src/offers/fleet/**` |
| qa | `offers/fleet/evals/**`, `tests/e2e/fleet/**`, offer telemetry |
| integration | contracts, migrations, root deps, CI, cross-lane conflict resolution |

## Agent assignment prompts

### ingest agent
Implement only source acquisition + raw artifact persistence + fixtures. Do not implement scoring/UI/API. Respect source rights from `SOURCE_REGISTRY.yaml`. Return normalized parser inputs and source health metrics.

### domain agent
Implement parsers, entity resolution, snapshots, P0 event detectors, score features/reason codes against frozen fixtures. No network calls.

### api-cli agent
Expose frozen application services through FastAPI and `signalctl`. JSON output is canonical. Do not duplicate domain logic.

### UI agent
Build required screens against generated OpenAPI types and fixture-backed mocks. Never infer source freshness or score behavior client-side.

### QA agent
Build replay corpus, end-to-end tests, source schema-drift tests, telemetry assertions, rate/cost failure cases and release checklist.

## Rebase discipline

Before every merge request:

```bash
git fetch origin
git rebase origin/int/fleet
```

Integration owner merges lanes into `int/fleet` one at a time, runs offline replay, then merges the integration branch to main.
