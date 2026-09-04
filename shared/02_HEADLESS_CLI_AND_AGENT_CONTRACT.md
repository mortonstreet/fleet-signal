# Headless CLI + Agent Contract

## 1. CLI goals

`signalctl` is not a wrapper around the UI. It is a first-class interface over the same application services used by the API.

Requirements:

- deterministic non-interactive operation
- JSON output on stdout with `--json`
- human-readable tables only when attached to a TTY and `--json` is absent
- diagnostics/logs on stderr
- stable exit codes
- `--dry-run` for all mutating/high-cost operations
- idempotency keys
- pagination cursors rather than implicit infinite output
- explicit `--since`, `--until`, `--limit`, `--tenant`
- input from JSON/JSONL/CSV/stdin
- output to stdout or explicit path
- no prompts when `CI=1` or `--non-interactive`

## 2. Command grammar

```text
signalctl offer list
signalctl <offer> source list
signalctl <offer> source sync <source> [--since ... --cursor ... --limit ...]
signalctl <offer> source health [<source>]
signalctl <offer> normalize --run <run-id>
signalctl <offer> events detect --run <run-id>
signalctl <offer> signals score [--event-id ...]
signalctl <offer> signals list [filters]
signalctl <offer> watch create --config watch.json
signalctl <offer> watch run <watch-id>
signalctl <offer> proof build --signal <id>
signalctl <offer> export --watch <id> --format jsonl|csv|parquet
signalctl <offer> outcome record --signal <id> --status ...
signalctl provenance show <evidence-id>
signalctl run inspect <run-id>
signalctl doctor
```

Each offer adds domain aliases, but the generic commands must always work.

## 3. Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 2 | validation / no confident capability match |
| 3 | no data / nothing changed (not an error for scheduled jobs) |
| 4 | rights/feature gate blocked |
| 5 | authentication/credential problem |
| 6 | source rate limited / retryable |
| 7 | source schema drift |
| 8 | partial run |
| 10 | internal failure |

## 4. Machine envelope

Every JSON command returns:

```json
{
  "ok": true,
  "command": "fleet signals list",
  "run_id": "run_...",
  "data": {},
  "next_cursor": null,
  "warnings": [],
  "provenance": [],
  "metrics": {"rows": 0, "cost_usd": 0.0}
}
```

## 5. Agent discovery

Ship:

- generated OpenAPI JSON from FastAPI
- JSON Schemas for all domain inputs/outputs
- `signalctl capabilities --json`
- `signalctl which "natural language capability" --json` backed by a curated command index, never direct arbitrary shell generation
- optional MCP server exposing the same bounded read/write tools

## 6. Cost and approval boundary

Every connector has `estimated_cost` and `cost_class`. Commands that can invoke licensed APIs/browser sessions accept `--max-cost-usd`. Default automation policies reject work that exceeds tenant budget or requires an approval gate.

## 7. Replay

A run manifest records exact source artifacts and versions. Agents can execute:

```bash
signalctl run replay run_123 --offline --json
```

Offline replay must never call the network. This is mandatory for parser/eval reproducibility.
