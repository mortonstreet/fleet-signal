# Current Source Corrections — 2026-09-04

The supplied sales/offer specs were treated as product requirements, then source mechanics were re-verified against current official documentation where implementation depends on them.

## 1. Federal contract awards

The original GovCon spec references FPDS-NG as the primary award detector. Public-facing FPDS functionality has now transitioned to SAM.gov; GSA states ezSearch was decommissioned February 24, 2026. The execution pack therefore uses the SAM.gov Contract Awards API as P0 and USAspending as confirmation/history.

Official docs:
- https://sam.gov/fpds
- https://open.gsa.gov/api/contract-awards/
- https://api.usaspending.gov/docs/endpoints

## 2. FDA 510(k) freshness

The offer spec described weekly/openFDA freshness. The current official openFDA 510(k) page states **monthly** update frequency. Device recall and MAUDE/event endpoints are weekly. The product must show per-source effective/observed timestamps and not promise daily/weekly 510(k) clearance alerts from openFDA alone.

Official docs:
- https://open.fda.gov/apis/device/510k/
- https://open.fda.gov/apis/device/recall/
- https://open.fda.gov/apis/device/event/

## 3. NMLS use rights

The original NMLS offer included recruiting and wholesale-BD prospecting. Current official NMLS B2B Access documentation states the subscription is **not available for solicitation or marketing purposes**. Therefore the technical P0 is re-scoped to licensed compliance/verification/counterparty monitoring. Marketing/recruiting modules are disabled unless separate written rights explicitly permit them. Consumer Access is not a scraping workaround.

Official product:
- https://mortgage.nationwidelicensingsystem.org/knowledge/Products/b2b

## 4. ACRIS latency

NYC Open Data ACRIS datasets are deterministic public APIs/backfill sources but are not assumed same-day. Direct ACRIS browser monitoring is a separate P1 source spike gated by automated-access terms and measured source latency. The system must distinguish `effective_at` from `observed_at`.

Reference datasets:
- Master `bnx9-e6tj`
- Legals `8h5j-fqxa`
- Parties `636b-3b5g`
- PLUTO `64uk-42ks`
- HPD Registration Contacts `feu5-w2e2`

## 5. Permit resale

The supplied permit spec itself marks Shovels redistribution/resale rights as unresolved. Shovels provides a current v2 API, but technical access is not the same as downstream resale permission. Production delivery is feature-gated until written rights are obtained.

Docs: https://docs.shovels.ai/

## 6. Freight manifests

The public-record basis under 19 CFR 103.31 does not create an assumed free real-time API. Build the event engine against a provider-neutral manifest contract, then feed it via a lawful FOIA/bulk delivery or a licensed data API. Do not scrape a trade-data vendor UI.

References:
- https://www.ecfr.gov/current/title-19/section-103.31
- https://docs.importyeti.com/
