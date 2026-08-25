# Master Catalogue Finalization Report

**Catalogue version:** `1.0.0-finalized`  
**Finalized at:** 2026-08-24  
**Phase rule:** No detailed requirements, fees, procedures, or processing times collected.

---

## 1. Executive verdict

The master catalogue has been **verified, normalized, and finalized** for deep research readiness.

| Question | Answer |
|----------|--------|
| Ready for deep requirement research? | **Yes, for CONFIRMED services only** |
| Ready for all 464 entries? | **No** — 10 remain `UNVERIFIED` and must be confirmed first |
| Claims “all Bangladesh government services”? | **No** |
| myGov ID parity complete? | **No** — mapping model exists; **0 verified IDs** |

---

## 2. Count summary

| Metric | Value |
|--------|------:|
| **Original canonical services** (pre-finalization) | **492** |
| **Final canonical services** | **464** |
| Net change | −28 |
| **CONFIRMED** | **454** |
| **UNVERIFIED** | **10** |
| **MERGED** (into another canonical; recorded as redirects) | **15** |
| **DUPLICATE** redirects (incl. prior MVP aliases) | **30** |
| **NOT_A_SERVICE** redirects | **16** |
| **DEPRECATED** | **0** |
| Redirect / relationship entries preserved | **46** |
| Authorities (indexed) | **119** |
| Taxonomy categories | **40** |
| myGov verified mappings | **0** |

Disposition of decisions applied during finalization (uncertain + confirmed cleanups):

| Disposition | Count |
|-------------|------:|
| CONFIRMED (promoted or reconfirmed) | 80 |
| MERGED | 15 |
| NOT_A_SERVICE | 16 |
| UNVERIFIED | 10 |
| DUPLICATE (legacy alias redirects retained) | 30* |

\*Duplicate redirects include prior discovery-phase aliases plus merge targets recorded as `status=DUPLICATE` with `relationship_type=MERGED|DUPLICATE`.

---

## 3. What changed

### 3.1 Verification of uncertain services (90)

Every previous `LIKELY` / `NEEDS_VERIFICATION` entry received an explicit disposition in `data/service_catalogue/finalization_decisions.json`.

**Promoted to CONFIRMED** when credible official evidence supported a real citizen/public-facing service, including for example:

- Online GD — `https://gd.police.gov.bd/`
- Ekpay — `https://ekpay.gov.bd/`
- A-challan treasury payment — `https://www.achallan.gov.bd/`
- Fire e-licence / e-NOC — Fire Service portals
- DIS disability registration — `https://www.dis.gov.bd/`
- Social allowance online application — `https://mis.bhata.gov.bd/online-application`
- Tax/VAT return filing, trademark/patent, Bar/BMDC/BNMC/Pharmacy councils
- Supreme Court certified copy & case tracking; BOESL; cooperative registration

**Left UNVERIFIED** (not forced into CONFIRMED):

1. `agri-seed-certification`
2. `certificates-freedom-fighter-certificate`
3. `dc-armed-forces-property-noc`
4. `education-public-university-admission`
5. `employment-district-employment-exchange`
6. `expatriate-bmet-demand-verification`
7. `judiciary-artha-rin-salish`
8. `judiciary-family-court-services`
9. `land-e-stamp-payment`
10. `religious-waqf-services`

### 3.2 Canonical service rule applied

Removed or merged entries that were **not** distinct user-facing service outcomes:

| Type | Examples | Disposition |
|------|----------|-------------|
| Portals / directories | myGov national portal, MoRA overview, Digital Centre list, Marriage registrar directory, BIDA OSS service list | NOT_A_SERVICE or MERGED |
| Guides / forms / requirements pages | ECC how-to-apply, ECC portal info, EIA guidelines, MOFA attestation form/requirements | NOT_A_SERVICE or MERGED into attestation |
| Agency umbrella labels | Madrasah board “services”, Technical board “services” | NOT_A_SERVICE |
| Internal portals | Legal aid office management | NOT_A_SERVICE |
| Access methods vs outcomes | Hajj registration portal → pre-registration; FF MIS login → FF list | MERGED |

**Kept distinct** where outcomes differ:

- Birth registration vs birth registration **correction**
- ECC **application** vs ECC **certificate verification** vs ECC **entrepreneur registration**
- MOFA **attestation** vs **e-Apostille**
- Trade licence (canonical) absorbs **renewal** as procedure variant, not a separate outcome

### 3.3 Duplicate / geographic analysis

**Geographic LGI variants were not left as separate canonical services.**

Created / used:

- `local-holding-tax-payment` — DNCC, DSCC, CCC, Pourashava via `geographic_availability`
- `licence-trade-local-government` — DNCC, DSCC, CCC, Municipality, Union Parishad via `geographic_availability`
- `mofa-document-attestation` — absorbs form + requirements pages

Merged into these (aliases + discovery sources preserved):

- `local-dncc-holding-tax`, `local-dscc-holding-tax`, `local-ccc-holding-tax`, `local-pourashava-holding-tax`
- `licence-trade-dncc`, `licence-trade-dscc`, `licence-trade-municipality`, `licence-trade-union-parishad`, `local-ccc-trade-licence`, `business-trade-license-renewal`
- `bida-oss-portal` → `bida-invest-bangladesh-oss`
- `hajj-registration-portal` → `hajj-pre-registration`
- `ff-mis-login` → `ff-mis-freedom-fighter-list`

**No silent deletions.** All removed-from-canonical entries are in `redirects.json` / `duplicates.json` with `canonical_service_id` where applicable.

### 3.4 Status vocabulary normalized

| Old | New |
|-----|-----|
| LIKELY | eliminated from canonical set |
| NEEDS_VERIFICATION | replaced by `UNVERIFIED` |
| CONFIRMED | retained |
| DUPLICATE | redirects only |
| — | `NOT_A_SERVICE` for portals/guides/directories |

Canonical statuses now: **CONFIRMED | UNVERIFIED** only.

---

## 4. Service ID audit

- All `service_id` values remain **slug-based**, unique, and independent of array order.
- IDs were **not** renamed during finalization (stability).
- Merged/removed IDs preserved as redirects with `canonical_service_id`.
- New parent IDs introduced only where needed:
  - `local-holding-tax-payment`
  - `licence-trade-local-government`
  - `mofa-document-attestation`
- UUIDs continue to be deterministic UUID5 of `bd-gov-service:{service_id}` for entries that had them.

---

## 5. Taxonomy audit

File: `data/service_catalogue/categories.json`

Every category has:

- `category_id`
- `name_en`
- `name_bn`
- `description`
- `parent_category` (nullable)

**40 categories** retained (no inflation for count). Notable structure:

- `disability` is a child of `social_protection`
- Separated `permits` vs `licences` vs `registrations`
- Separated `employment` (domestic) vs `expatriate`
- Separated `tax` / `vat` / `customs`
- Separated `judiciary` vs `legal_aid` vs `professional`

Legacy uppercase `category` field retained on entries for compatibility; `category_id` is the stable taxonomy key.

---

## 6. Lifecycle metadata

Normalized fields on every entry:

| Field | Policy |
|-------|--------|
| `status` | Required |
| `discovered_at` | Preserved from discovery; never invented beyond known discovery date |
| `confirmed_at` | Set to `2026-08-24` only when disposition = CONFIRMED in this pass; prior CONFIRMED use `discovered_at` as confirmation proxy |
| `last_checked_at` | Set when reviewed in this finalization |
| `effective_from` / `effective_until` | Left null (no invention) |
| `deprecated_at` | Null (none deprecated this pass) |

---

## 7. myGov relationship

File: `data/service_catalogue/mygov_mapping.json`

**Model:**

```
canonical_service_id  ↔  mygov_service_id
```

**Findings:**

- myGov.bd is an **access / orchestration layer** listing ministries, sectors, and service applications.
- Public sector pages do **not** currently expose a stable, scrape-verified machine-readable service ID catalogue in this pass.
- Public messaging cites large integrated-service counts; **that count is not equal to unique underlying government services**.
- **Verified mappings stored: 0**
- Each canonical entry has `mygov_service_ids: []` until a verified ID is known.

Do not use myGov entry counts as catalogue completeness.

---

## 8. Local government model

File: `data/service_catalogue/local_government_model.json`

**Principle:** One canonical service + `geographic_availability[]`, not one service per district/LGI.

**Tiers:** Division → District → City Corporation → Municipality → Upazila → Union → Ward

**Availability values:** AVAILABLE | UNAVAILABLE | PROCEDURE_DIFFERS | OFFICE_DIFFERS | URL_DIFFERS | FEE_DIFFERS

**Currently populated on:**

- `local-holding-tax-payment`
- `licence-trade-local-government`

**Still incomplete:** 64-district DC matrices, remaining city corporations, pourashava-level URL/fee variance — model is ready; data is sample-seeded only.

---

## 9. Major remaining gaps

1. **myGov ID mapping** — unresolved for all services  
2. **UNVERIFIED 10** — must not be deep-researched yet  
3. **SSPS programme names (≈147)** — programme inventory ≠ always distinct application services; may need programme↔application linking later  
4. **Subordinate courts** — only high-level judiciary entries  
5. **Non-Dhaka/Chattogram city corporations** — geo model ready, instances sparse  
6. **Bangla names** — some entries still English-first  
7. **Lifecycle journey tags** — many services still untagged  

---

## 10. Catalogue quality assessment

| Criterion | Assessment |
|-----------|------------|
| Uncertain-status debt | Cleared from LIKELY/NEEDS_VERIFICATION; 10 honest UNVERIFIED remain |
| Portal/guide pollution | Materially reduced |
| Geographic duplication | Holding tax & trade licence normalized |
| Alias preservation | Yes (redirects + parent aliases) |
| ID stability | Yes |
| Taxonomy | Normalized with `categories.json` |
| Evidence honesty | CONFIRMED only with credible sources; no forced confirmation |
| Requirements readiness | **Ready for CONFIRMED subset** |

**Quality grade for discovery inventory:** suitable as the master inventory baseline for the next phase (deep research on selected CONFIRMED services).

---

## 11. Deliverable files

| Path | Role |
|------|------|
| `data/service_catalogue/services.json` | Final canonical catalogue (`1.0.0-finalized`) |
| `data/service_catalogue/final/services.json` | Snapshot copy |
| `data/service_catalogue/redirects.json` | MERGED / DUPLICATE / NOT_A_SERVICE records |
| `data/service_catalogue/duplicates.json` | DUPLICATE subset (compat) |
| `data/service_catalogue/categories.json` | Taxonomy |
| `data/service_catalogue/authorities.json` | Authority index |
| `data/service_catalogue/mygov_mapping.json` | myGov mapping model |
| `data/service_catalogue/local_government_model.json` | LGI geo model |
| `data/service_catalogue/finalization_decisions.json` | Full decision log |
| `data/service_catalogue/metadata.json` | Aggregate metrics |
| `data/service_catalogue/schema.json` | Updated JSON Schema |
| `data/service_catalogue/by_category/*.json` | Per-category splits |
| `scripts/finalize_service_catalogue.py` | Reproducible finalization |

Rebuild:

```bash
python3 scripts/finalize_service_catalogue.py
```

---

## 12. Stop condition

**STOPPING HERE as requested.**

This phase did **not** begin detailed service research (documents, fees, procedures, processing times).

**Next phase (when authorized):** Select a prioritized CONFIRMED subset and research requirements — excluding the 10 UNVERIFIED entries until confirmed.
