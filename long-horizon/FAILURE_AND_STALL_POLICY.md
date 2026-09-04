# Failure, Stall, and Escalation Policy

## Retry classes

| Class | Max cycles | Response |
|---|---:|---|
| deterministic implementation/test failure | 4 | corrective goal to same Implementer |
| repeated same-root-cause failure | 2 before tactic change | Explorer + new tactic |
| integration/schema conflict | 3 | integration lane owns resolution |
| transient source/network failure | 5 | bounded exponential backoff; prefer fixture replay |
| external rights/license/contract blocker | 0 bypass attempts | record external blocker; continue fixture-safe work only |
| destructive/irreversible action needing approval | 0 autonomous attempts | stop at prepared reviewable change |

## Stall detector

Default threshold: **20 minutes without a new PASS checklist item**.

A stall is not failure. It is a signal to change tactics. The Implementer should preserve evidence and do one of:

- delegate a focused Explorer;
- isolate a failing test into a smaller reproducer;
- move to another unblocked checklist item in the same phase;
- replace a brittle implementation approach;
- inspect authoritative docs/source fixtures;
- revert a bad experiment and retry from the last green commit.

## Anti-cheating / anti-shortcut rules

The Implementer must not:

- remove requirements;
- mark tasks PASS without evidence;
- weaken or delete failing tests solely to pass gates;
- replace real behavior with hardcoded fixture-specific behavior;
- disable rights/security/tenant checks;
- change acceptance commands after freeze;
- claim source freshness/coverage not supported by evidence.

## Escalation terminal states

### IMPLEMENTATION_COMPLETE_BLOCKED_EXTERNAL

Use when code/evals/replay are complete but production enablement depends on something outside the agent's power, for example written redistribution rights, a provider contract, credentials, government account approval, or an operating license.

### FAILED_REQUIRES_HUMAN

Use only after retry/recovery budget is exhausted or a material product/architecture choice has multiple plausible options with meaningfully different outcomes and no source in the pack resolves it.
