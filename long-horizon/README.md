# Signal Stack Long-Horizon Manager Loop

**Date:** 2026-09-04  
**Purpose:** Execute any Signal Stack MVP as a long-running Codex build using a persistent **Manager → Implementer** loop with phase goals, subagents, worktrees, durable progress state, and executable acceptance gates.

## The operating model

This pack adapts the Manager Loop described by Matt Shumer on 2026-09-04:

1. A **Manager** owns the full goal, creates/maintains the checklist, and divides the build into phases.
2. The Manager spawns one persistent **Implementer** in a separate agent thread.
3. The Manager stays in `/goal` mode and sends the Implementer one phase at a time in `/goal` mode.
4. Each phase prompt uses the wording **"complete this phase completely, extremely well"** and has a verifiable stopping condition.
5. The Implementer keeps a visible HTML checklist/progress surface and uses bounded specialist subagents/worktrees.
6. The Manager independently verifies the phase before allowing the next phase to start.

This pack adds controls that are necessary for software delivery but are not specified in the original post: immutable phase contracts, acceptance IDs, independent reviewer verdicts, retry/escalation rules, path ownership, external-blocker semantics, evidence logs, and a final readiness gate.

### Primary sources

- Matt Shumer Manager Loop post: https://x.com/mattshumer_/status/2095723177389232540
- Codex `/goal` documentation: https://learn.chatgpt.com/use-cases/follow-goals
- Codex subagents: https://learn.chatgpt.com/docs/agent-configuration/subagents
- Codex worktrees: https://learn.chatgpt.com/docs/environments/git-worktrees

## One-command mental model

You should be able to open the target repository, ensure this pack is present, start a fresh Manager Codex thread, and issue:

```text
/goal Read long-horizon/START.md and execute offer 02-fleet-finance as the Manager. Do not stop until the final readiness gate passes or a legitimate external blocker is recorded.
```

The Manager must then create one persistent Implementer thread and run the phases itself. You should not manually shepherd phase transitions.

## Roles

### Manager — persistent control plane

The Manager:

- owns the full MVP goal and stopping condition;
- reads the offer execution pack before any delegation;
- initializes durable state under `.loop/`;
- expands the seed checklist without reducing P0 scope;
- freezes phase boundaries and acceptance commands;
- spawns **one persistent Implementer thread**;
- sends one phase `/goal` at a time;
- waits for Implementer completion;
- independently runs acceptance commands and reviewer checks;
- sends correction goals when the phase fails;
- merges accepted phase commits into the integration branch;
- never writes product code;
- declares completion only when `loopctl final` exits 0.

### Implementer — persistent execution plane

The Implementer:

- works only on the phase currently assigned by the Manager;
- can spawn specialist subagents whenever parallelism helps;
- uses worktrees and exclusive path ownership for write-heavy work;
- updates the checklist/progress HTML as work lands;
- commits at meaningful checkpoints;
- runs tests before returning control;
- reports evidence, commit SHA, changed paths, failures, and blockers;
- never weakens acceptance criteria to make a phase pass.

### Reviewer — fresh, independent critic

A new Reviewer is spawned for each phase acceptance attempt. It is read-only and does not see the Implementer's rationale. It reviews the actual diff, tests, evidence, and acceptance contract and returns one of:

- `PASS`
- `FAIL`
- `BLOCKED_EXTERNAL`

The Reviewer never fixes code. Failed review goes back to the Implementer.

## Why the two-agent loop is the default

Long runs suffer from context pollution and stalled local optimization. The Manager retains requirements/decisions while the Implementer absorbs build logs and code minutiae. Codex's own subagent guidance recommends keeping noisy work off the main thread and warns that parallel write-heavy workflows create conflicts, so this pack uses **high parallelism for reading/testing and bounded parallelism for writers**.

## Default concurrency

The included `.codex/config.toml.example` uses 12 spawned threads per session. Increase only after the repo is stable.

- Write-heavy work: at most **one writer per exclusive lane** (`ingest`, `domain`, `api-cli`, `ui`, `qa`).
- Read-heavy exploration/test shards: 8–16 concurrent agents is reasonable.
- Very high concurrency (including 96, as described in Shumer's experiment) is an optional stress profile, not the default. High thread counts amplify token cost, rate limits, disk/worktree pressure, and coordination failures.

## Durable state

Every run lives under `.loop/`:

```text
.loop/
  run_state.json
  checklist.json
  acceptance_results.json
  blockers.json
  decisions.md
  events.jsonl
  evidence/
  progress.html
```

Nothing critical exists only in chat context.

## Completion states

`COMPLETE` is allowed only when all required acceptance gates pass.

Other legitimate terminal states:

- `IMPLEMENTATION_COMPLETE_BLOCKED_EXTERNAL` — code/replay/evals are complete, but a rights, credential, provider-contract, license, or other external production gate is unresolved.
- `FAILED_REQUIRES_HUMAN` — retry/escalation budget was exhausted on an internal engineering problem or a material product decision cannot be inferred safely.

The loop must never bypass a rights or security gate merely to satisfy "keep going until done."

## Pack layout

```text
long-horizon/
  START.md
  MANAGER_PROMPT.md
  IMPLEMENTER_PROMPT.md
  REVIEWER_PROMPT.md
  PHASE_PROTOCOL.md
  FAILURE_AND_STALL_POLICY.md
  codex/
    config.toml.example
    config.96-read-heavy.example.toml
    agents/*.toml
  scripts/
    loopctl.py
    verify_owned_paths.py
    bootstrap_worktrees.sh
  schemas/*.schema.json
  portfolio/
    PORTFOLIO_MANAGER.md
    portfolio.json

offers/<offer>/LONG_HORIZON/
  LAUNCH.md
  goal.json
  phase_plan.json
  checklist_seed.json
  acceptance_seed.json
  external_gates.json
```

## Recommended flow

1. Run `python long-horizon/scripts/loopctl.py verify-plan --offer-dir offers/<offer>/LONG_HORIZON`.
2. Start Manager with the exact prompt in `offers/<offer>/LONG_HORIZON/LAUNCH.md`.
3. Manager initializes `.loop/` with `loopctl init`.
4. Manager performs Phase `P00`, runs `loopctl compile-acceptance`, reviews/adjusts the concrete commands, and freezes `.loop/acceptance.lock.json`.
5. Manager verifies required external gates with `loopctl external` and hashes the lock and does not let the Implementer edit it.
6. Manager spawns one Implementer.
7. For each phase, Manager sends the phase `/goal`, waits, then gates and reviews.
8. After all phases, run `loopctl final` and full offline replay.
9. Promote `int/<offer>` only when the final gate is green.

## The key anti-drift rule

The Manager may reorder tasks inside an existing phase and the Implementer may change tactics. Neither may silently remove P0 requirements, weaken acceptance, change rights gates, or substitute a smaller product. Any scope change requires a recorded decision in `.loop/decisions.md` and an explicit change to the frozen contract before implementation continues.
