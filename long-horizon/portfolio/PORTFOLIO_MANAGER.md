# Portfolio Mode — Running All Signal MVPs

Do **not** put all ten products into one giant `/goal`. Use one Manager→Implementer pair per offer and an optional Portfolio Controller above them.

## Portfolio Controller responsibilities

- choose which offers are active;
- cap simultaneous write-heavy MVPs;
- ensure each offer uses its own `int/<offer>` branch and worktrees;
- serialize shared-contract/root-dependency changes through a `shared-integration` queue;
- collect only phase-level status from each Manager;
- never rewrite an offer's P0 scope;
- pause an offer when an external gate blocks production and allow fixture-backed implementation to continue if safe;
- prefer finishing an MVP before opening too many additional write-heavy MVPs.

## Recommended concurrency

- 2–3 active MVP Manager loops at once on one developer machine/repo.
- Each MVP may use up to five write lanes, but only one writer per lane.
- Additional subagent capacity is best spent on read-only exploration, review, docs/source verification, and test shards.

## Shared-contract queue

The following paths must not be changed independently by offer Managers once offer implementation starts:

- `packages/contracts/**`
- root lockfiles/dependency manifests
- shared migrations
- shared event/source schemas
- shared auth/tenancy/security code
- CI/release infrastructure

An offer that needs a shared change writes `.loop/shared_change_request.json` and pauses only the dependent task. A dedicated shared-integration run reviews and lands the shared change, after which affected offer branches rebase.

## Portfolio completion

Each MVP finishes independently as `COMPLETE`, `IMPLEMENTATION_COMPLETE_BLOCKED_EXTERNAL`, or `FAILED_REQUIRES_HUMAN`. Portfolio status is a summary, not a substitute for per-offer acceptance gates.
