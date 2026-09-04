# Data Acquisition Adapter Policy

## 1. Routing order

For every source, choose the **highest** allowed method in this order:

1. Official API
2. Official bulk/download/SFTP/RSS feed
3. Licensed/contracted API or data file
4. Deterministic HTTP/Scrapy against public pages where automated access is allowed
5. Deterministic browser/CDP session for JavaScript-rendered public pages where automated access is allowed
6. Agentic browser extraction only for unstable navigation or semi-structured content that cannot be made deterministic
7. Human/manual acquisition when automation rights or source behavior are unresolved

A lower layer is not a license to bypass restrictions in a higher layer.

## 2. Tool role matrix

| Tool | Use it for | Do not use it for |
|---|---|---|
| `httpx/requests` | JSON APIs, files, RSS, simple HTML | JS-only pages |
| Scrapy | deterministic multi-page crawling, pagination, link following, feed exports | sites whose terms disallow automation; bypassing login/bot controls |
| Obscura | self-hosted/lightweight CDP for permitted JS-heavy public pages | stealth/evasion; CAPTCHA bypass; restricted sites |
| Anchor Browser | managed Playwright/CDP, persistent user-authorized sessions, recordings, reproducible browser tasks | bypassing CAPTCHAs/access controls; bulk crawling when HTTP works |
| Browser Use | bounded agentic navigation and schema-returning tasks where DOM workflows drift | canonical high-volume data ingestion that can be deterministic |
| Hyperbrowser Extract | schema-based extraction from a small set of unstructured pages | replacing an official API/bulk source |

## 3. Browser provider abstraction

Business code calls a provider-neutral interface:

```python
class BrowserProvider(Protocol):
    async def start(self, *, profile: str | None, recording: bool=False) -> BrowserSession: ...
    async def goto(self, session_id: str, url: str) -> None: ...
    async def extract(self, session_id: str, schema: dict, instructions: str | None=None) -> dict: ...
    async def close(self, session_id: str) -> None: ...
```

Adapters live at:

```text
packages/acquisition/browser/
  base.py
  anchor.py
  browser_use.py
  hyperbrowser.py
  obscura.py
```

Offer source adapters depend only on `BrowserProvider`.

## 4. Mandatory source registry fields

Every source must declare:

- owner
- canonical URL
- access type
- auth type
- rate/cadence constraints
- rights status: `open`, `licensed`, `contract_required`, `terms_review`, `blocked`
- `robots_policy` where web crawling is used
- `browser_allowed` boolean
- data classification
- retention policy
- permitted downstream use
- last terms review date
- terms snapshot URI
- kill switch feature flag

## 5. Crawl safety

- Identify the client with a real User-Agent/contact where agencies ask for it.
- Honor documented rate limits and `Retry-After`.
- Default per-domain concurrency to 1–2 until measured.
- Cache immutable pages/files; do not re-fetch identical artifacts.
- Back off on 403/429/5xx rather than changing fingerprints/proxies to evade controls.
- Browser automation must not click through CAPTCHA challenges automatically.
- Proxy geography is for ordinary network locality/reliability, not to circumvent geo restrictions.
- Obscura stealth mode is disabled in this architecture.

## 6. Provenance contract

Every field returned to a user must be traceable to one or more source observations. The UI should show source and as-of time; the API/CLI should return `evidence_ids` and a provenance endpoint.

## 7. Parser fixture discipline

For each source:

```text
offers/<offer>/tests/fixtures/<source>/
  raw/
  expected/
  README.md
```

Each parser PR must include:

- at least 3 realistic fixtures
- one empty/no-result fixture
- one malformed/partial fixture
- checksum of the raw fixture
- schema regression test
- source cadence/rate assumptions

## 8. Current browser tooling references

- Browser Use Cloud API v3 sessions: `https://api.browser-use.com/api/v3/sessions`
- Hyperbrowser SDK Extract: schema-driven `extract.startAndWait(...)`
- Anchor Browser sessions: `POST https://api.anchorbrowser.io/v1/sessions`, CDP URL returned
- Obscura: Playwright/CDP-compatible managed or self-hosted browser; use standard mode + `--obey-robots`
- Scrapy: feed exports support JSON/JSONL/CSV/XML and filesystem/S3/GCS/FTP backends

These providers are optional. Source correctness must not depend on one vendor.
