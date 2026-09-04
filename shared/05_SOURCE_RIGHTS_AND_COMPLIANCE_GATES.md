# Source Rights and Compliance Gates

This is an engineering gate, not a legal opinion. The system must be able to disable a source or delivery use instantly.

## Gate states

- `OPEN_CONFIRMED` — official public/open API or bulk data with intended reuse consistent with product use.
- `PUBLIC_TERMS_REVIEWED` — public website automation reviewed and allowed for the specific method/cadence.
- `LICENSED` — contract grants required API/download/downstream rights.
- `CONTRACT_REQUIRED` — architecture can be built, production acquisition disabled until contract executed.
- `BLOCKED` — source/use is not permitted for the intended product.

## Mandatory feature flags

```text
SOURCE_<SOURCE_ID>_ENABLED
OFFER_<OFFER>_DELIVERY_ENABLED
OFFER_<OFFER>_MARKETING_USE_ENABLED
OFFER_<OFFER>_PERSON_DATA_ENABLED
```

## Known high-priority gates in this pack

### NMLS
NMLS B2B Access is designed for SAFE Act-related uses such as license verification/fraud prevention and the official product page states it is not available for solicitation or marketing. Therefore marketing/recruiting lead modules remain disabled unless a separate written agreement authorizes that use. Do not scrape Consumer Access as a workaround.

### Permit / Shovels
The uploaded offer spec already marks downstream resale/redistribution rights as unresolved. Use the API only for evaluation/internal scoring until written downstream rights are confirmed.

### CRE listings
Do not assume scraping rights for Crexi, LoopNet or another listing site. Use licensed feeds, user-authorized exports, broker-owned public pages where terms permit, or a thin listing signal after review.

### Freight manifest
19 CFR 103.31 permits publication of specified vessel manifest information, but a public real-time bulk CBP API was not identified. Production acquisition should use a lawful FOIA/data agreement/licensed API, not extraction from a competitor UI.

### Recruiting people data
Public job postings are different from candidate identity/contact data. Candidate records should come from customer ATS/CRM, consented/public sources whose terms allow reuse, or a licensed enrichment provider. Do not automate restricted professional-network pages.

## Personal/contact data

- prefer business contact data and customer-owned records
- maintain source + purpose metadata
- tenant-level suppression and DNC lists are first-class
- keep public-source facts separate from inferred/third-party contact fields
- configurable retention/deletion policies
