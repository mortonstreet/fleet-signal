# Phase Protocol

## Standard phases

| Phase | Purpose | Primary lane |
|---|---|---|
| P00 | Harness preflight, scaffold, contract/acceptance freeze | integration |
| P10 | Source acquisition + immutable raw artifacts + fixtures | ingest |
| P20 | Parse/normalize/entity resolution/snapshot/event domain | domain |
| P30 | Signal rules/scoring/watch matching/proof assets | domain |
| P40 | Application service + API + headless CLI + delivery | api-cli |
| P50 | Human UI/workflow and required error/stale/blocked states | ui |
| P60 | E2E/replay/evals/observability/security/runbooks | qa |
| P70 | Integration hardening, fresh-checkout validation, release gate | integration |

The selected offer's `phase_plan.json` is authoritative if it narrows or expands these mappings without reducing P0 scope.

## Phase lifecycle

`PENDING → DISPATCHED → IMPLEMENTING → CANDIDATE_COMPLETE → GATING → REVIEW → ACCEPTED`

Failure transitions:

`GATING/REVIEW → CORRECTION → IMPLEMENTING`

External dependency:

`IMPLEMENTING/GATING → BLOCKED_EXTERNAL`

## Phase acceptance rule

A phase is accepted only if:

- all required checklist items for the phase are PASS;
- all required acceptance commands for the phase exit 0;
- changed-path ownership is valid;
- reviewer verdict is PASS;
- no unresolved internal blocker is severity 1/2;
- all commits are present and the phase worktree is clean.

## Do not work ahead

Working ahead creates hidden coupling and deprives the Manager of a meaningful checkpoint. A later-phase dependency may be implemented early only when:

1. the current phase cannot pass without it;
2. the dependency is minimal;
3. the change is recorded in `.loop/decisions.md`;
4. path ownership remains valid.
