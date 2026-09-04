# Parallel Git Worktree Playbook

## 1. Objective

Allow 5–6 coding agents to develop one offer concurrently without file collisions or hidden contract drift.

## 2. Freeze before parallelization

The integration owner creates and merges a **contract freeze commit** containing:

- source registry
- domain entity/event/signal schemas
- REST route names
- CLI command names and output contracts
- database migration ownership
- feature flags / rights gates

Agents may add fields only through an explicit contract PR. They do not opportunistically edit shared contracts from feature branches.

## 3. Standard lanes

| Lane | Branch | Exclusive ownership |
|---|---|---|
| ingest | `feat/<offer>/ingest` | source adapters, raw acquisition, source fixtures |
| domain | `feat/<offer>/domain` | parsers, normalization, entity resolution, events, scores |
| api-cli | `feat/<offer>/api-cli` | FastAPI routes/services, Typer commands, OpenAPI/CLI tests |
| ui | `feat/<offer>/ui` | web routes/components, client data hooks, UX tests |
| qa | `feat/<offer>/qa` | end-to-end fixtures, evals, observability, load/failure tests |
| integration | `int/<offer>` | conflict resolution, dependency bumps, migrations sequencing |

## 4. Path ownership example

```text
feat/fleet/ingest
  offers/fleet/sources/**
  offers/fleet/tests/fixtures/sources/**

feat/fleet/domain
  offers/fleet/domain/**
  offers/fleet/tests/domain/**

feat/fleet/api-cli
  offers/fleet/api/**
  offers/fleet/cli/**

feat/fleet/ui
  apps/web/src/offers/fleet/**

feat/fleet/qa
  offers/fleet/evals/**
  tests/e2e/fleet/**
  offers/fleet/telemetry/**
```

Only the integration lane edits:

- root package lock files
- shared schemas
- shared infrastructure manifests
- root CI
- cross-offer migrations

## 5. Worktree creation

```bash
git switch main
git pull --ff-only

git worktree add ../wt-fleet-ingest -b feat/fleet/ingest main
git worktree add ../wt-fleet-domain -b feat/fleet/domain main
git worktree add ../wt-fleet-api-cli -b feat/fleet/api-cli main
git worktree add ../wt-fleet-ui -b feat/fleet/ui main
git worktree add ../wt-fleet-qa -b feat/fleet/qa main
git worktree add ../wt-fleet-int -b int/fleet main
```

The included helper script creates the same pattern for any slug.

## 6. Integration order

1. contract freeze -> `int/<offer>`
2. ingest + domain independently target frozen fixtures
3. api-cli integrates domain services
4. UI integrates only against OpenAPI/mock fixtures, then live API
5. QA integrates all lanes and runs replay/e2e
6. `int/<offer>` merges to main only after release gate

## 7. Daily agent protocol

Each agent writes `WORKLOG.md` in **its owned subtree only** with:

- commit SHA started from
- assumptions
- files touched
- tests added
- known gaps
- migration/API changes requested

Before pushing:

```bash
git fetch origin
git rebase origin/int/<offer>
pytest <owned tests>
# or pnpm test <owned UI tests>
```

Do not resolve a cross-lane conflict by deleting another lane’s behavior. Escalate to integration owner.

## 8. Acceptance contract

Each lane is mergeable only if:

- its owned tests pass
- no changes outside ownership without explicit approval
- fixtures are deterministic
- network calls are mocked in unit tests
- source rights gate is respected
- `signalctl ... --json` output matches schema for CLI changes
- OpenAPI generation is stable for API changes
- UI has loading/empty/error/partial states

## 9. Cross-offer parallelism

Different offers can run in parallel as long as they do not edit shared platform packages. If a generic improvement is discovered, create a separate `feat/shared/<capability>` PR and merge it first; then rebase all affected offer integration branches.
