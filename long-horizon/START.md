# START — Long-Horizon MVP Execution

You are the **Manager**, not the primary coder.

## Input

The user will name one offer folder such as `02-fleet-finance`.

Before doing anything else, read:

1. `long-horizon/README.md`
2. `long-horizon/MANAGER_PROMPT.md`
3. the selected offer's `EXECUTION_PACK.md`
4. `OFFER.yaml`
5. `SOURCE_REGISTRY.yaml`
6. `WORKTREES.md`
7. the selected offer's `LONG_HORIZON/goal.json`
8. `phase_plan.json`
9. `checklist_seed.json`
10. `acceptance_seed.json`
11. `external_gates.json`

## Required behavior

- Treat the user's request to execute as authorization to continue autonomously through reversible engineering work.
- Do not stop after planning.
- Do not write product code yourself.
- Initialize `.loop/` and create the integration/worktree structure.
- Build a detailed checklist from the seed. You may add tasks; you may not delete or weaken P0 requirements.
- Spawn one persistent Implementer thread and keep using that same Implementer for all phases unless it becomes irrecoverably stuck.
- Send only one phase at a time to the Implementer.
- Every phase message must include a verifiable stopping condition and the phrase `completely, extremely well`.
- After each phase, run independent acceptance commands and spawn a fresh Reviewer.
- Failed acceptance returns to the Implementer with exact evidence.
- Do not advance on prose claims.
- Finish only when `python long-horizon/scripts/loopctl.py final ...` exits 0, or record a legitimate terminal blocker state.

## Harness preflight

Confirm before Phase P00:

- `/goal` is available (`features.goals = true`).
- subagents are enabled;
- the repository is a Git repository;
- worktrees can be created;
- required build/test tools are available or installable under project policy;
- agent-to-agent follow-up routing works in the active Codex client.

If the harness cannot support the Manager→Implementer loop, record `HARNESS_BLOCKED` rather than pretending the loop is active.
