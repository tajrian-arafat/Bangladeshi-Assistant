# Batch 3B Research Report — BRTA Vehicle Registration / Ownership / Fitness

**Batch ID:** `BATCH_03B`  
**Slug:** `batch-03b-brta-vehicle`  
**Phase completed:** RESEARCH  
**Researched at:** 2026-08-25  
**Catalogue version:** 1.0.0-finalized (464 canonical services)

---

## Executive summary

Batch 3B covers six CONFIRMED catalogue services in the BRTA vehicle registration domain. Research produced **53 atomic claims** from **12 sources** (11 Tier 1–2). Vehicle-type, usage-class, and procedure-action variants are modeled explicitly — procedures are not flattened into a single generic checklist.

**Fitness certificate** (`brta-fitness-certificate`) is a confirmed catalogue service but assigned to **BATCH_03C**; it is cross-referenced only as a registration/transfer prerequisite. **Lost/damaged registration certificate** has no separate catalogue service ID and is modeled as a sub-procedure under DRC replacement and ownership-transfer conditionals.

**Next automatic transition:** `RESEARCH → VERIFICATION` (orchestrator autonomous loop).

---

## 1. Scope discovery

### In scope (6 services — batch queue)

| Service ID | Name | Subcategory | Official source |
|---|---|---|---|
| `brta-new-vehicle-registration` | New Motor Vehicle Registration | vehicle_registration | BSP vehicleRegistration |
| `brta-ownership-transfer` | Motor Vehicle Ownership Transfer | vehicle_registration | BRTA portal static page |
| `brta-digital-registration-certificate` | Digital Registration Certificate (DRC) | vehicle_registration | BRTA portal static page |
| `brta-vehicle-info-correction` | Vehicle Registration Information Correction | vehicle_registration | BRTA portal static page |
| `brta-retro-reflective-number-plate` | Retro-Reflective Number Plate | vehicle_registration | BRTA portal static page |
| `brta-trustee-board-certificate` | Trustee Board Certificate Download | vehicle_registration | BSP tbc |

### Related CONFIRMED services — out of scope (documented, not duplicated)

| Service ID | Reason |
|---|---|
| `brta-fitness-certificate` | BATCH_03C — prerequisite cross-reference only |
| `brta-fee-calculator` | Cross-cutting fee lookup |
| `brta-bsp-user-registration` | BSP account prerequisite (owner/dealer) |
| `brta-mv-tax-payment`, `brta-tax-token` | BATCH_03C tax services |
| `brta-route-permit` | Commercial-only; BATCH_03C |
| `brta-engine-change`, `brta-color-change`, `brta-tire-size-change` | Modification services; BATCH_03C |
| Lost/damaged RC (no catalogue ID) | Sub-procedure under DRC / transfer conditionals |

### Vehicle variant model

Dimensions captured in `data/research/raw/batch-03b-brta-vehicle/scope.json`:

- **vehicle_type:** motorcycle, private_car, jeep_microbus, bus, truck, auto_rickshaw, trailer, other_commercial
- **usage_class:** private vs commercial
- **origin:** local_assembled, imported, reconditioned
- **procedure_action:** new_registration, ownership_transfer, drc_biometric_issue, registration_info_correction, retro_reflective_plate, trustee_board_certificate_download
- **certificate_state:** valid, lost, damaged, outdated_booklet

---

## 2. Sources

### Tier 1 (BRTA BSP — official portal)

| Source ID | URL | Notes |
|---|---|---|
| `src-bsp-vehicle-registration` | https://bsp.brta.gov.bd/vehicleRegistration/?lan=en | Catalogue official_source; 404 outside BSP hours at fetch |
| `src-bsp-register-owner` | https://bsp.brta.gov.bd/register | Owner/dealer NID-linked registration |
| `src-bsp-fee-calculator` | https://bsp.brta.gov.bd/feeCalculator | Vehicle-type-dependent fees |
| `src-bsp-tbc` | https://bsp.brta.gov.bd/tbc/ | Trustee board certificate download |
| `src-bsp-maintenance-notice` | https://bsp.brta.gov.bd/ | Operating hours 08:00–22:00 BST (Batch 3A cross-ref) |

### Tier 2 (Bangladesh government / catalogue)

| Source ID | URL | Notes |
|---|---|---|
| `src-brta-portal-ownership-transfer` | brta.portal.gov.bd …6922dc6b… | Page title: মালিকানা বদলী; shell snapshot captured |
| `src-brta-portal-drc` | brta.portal.gov.bd …6922dba6… | DRC biometric provision/collection |
| `src-brta-portal-retro-plate` | brta.portal.gov.bd …6922db7a… | Retro-reflective plate + RFID tag |
| `src-brta-portal-info-correction` | brta.portal.gov.bd …6922dc03… | RC information correction |
| `src-brta-portal-fitness-crossref` | brta.portal.gov.bd …6922db91… | Cross-ref only (BATCH_03C) |
| `src-brta-portal-home` | http://brta.portal.gov.bd/ | Portal hub |
| `src-catalogue-transport` | data/service_catalogue/by_category/transport.json | Scope authority |

**Tier 1–2 source count:** 11 of 12 sources (one internal catalogue reference counted as Tier 2).

---

## 3. Claims summary

| Metric | Count |
|---|---|
| Total atomic claims | 53 |
| OFFICIAL | 41 |
| PRACTICAL | 6 |
| DISCOVERY | 6 |
| Claims with structured fee rules | 5 |
| Claims with conditional rules (MUST_NEED / CONDITIONAL / NOT_APPLICABLE) | 28 |

### Per-service claim counts

| Service | Claims | Research status |
|---|---|---|
| brta-new-vehicle-registration | 10 | SUBSTANTIAL |
| brta-ownership-transfer | 11 | SUBSTANTIAL |
| brta-digital-registration-certificate | 9 | SUBSTANTIAL |
| brta-vehicle-info-correction | 8 | SUBSTANTIAL |
| brta-retro-reflective-number-plate | 8 | SUBSTANTIAL |
| brta-trustee-board-certificate | 7 | SUBSTANTIAL |

### High-risk claim areas

- **Fees:** All numeric amounts deferred to BSP fee calculator (`CALCULATOR_DERIVED`); no static fee invented
- **Ownership transfer documents:** TO/TTO forms, original RC, buyer TIN, affidavits — from catalogue notes + portal assignment
- **Fitness prerequisites:** Cross-referenced to BATCH_03C; commercial vs private rules not generalized
- **Lost RC:** Conditional GD/replacement path documented; not promoted to MUST_NEED without portal body extract

---

## 4. Conflicts (3 — unresolved)

1. **Fitness batch assignment** — prerequisite for 03B services but researched in 03C
2. **BSP sub-portal 404 vs catalogue URL** — vehicleRegistration/tbc URLs valid per catalogue but unavailable outside BSP hours
3. **Retro-plate page freshness** — page metadata Nov 2023 vs ownership-transfer page Jun 2026

No conflicts resolved by guessing.

---

## 5. Knowledge gaps (5)

| Gap ID | Priority | Description |
|---|---|---|
| MISSING_BSP_VEHICLE_SUBPORTAL_SNAPSHOT | HIGH | BSP vehicleRegistration/tbc not snapshotted (404 outside hours) |
| MISSING_PORTAL_JS_BODY | HIGH | BRTA portal procedural checklists JS-rendered; shell-only snapshots |
| MISSING_VEHICLE_FEE_MATRIX | MEDIUM | Interactive fee calculator not extracted |
| MISSING_FITNESS_VALIDITY_BY_CLASS | MEDIUM | Deferred to BATCH_03C |
| MISSING_LOST_RC_PROCEDURE_DETAIL | MEDIUM | No standalone catalogue service; GD/reissue details incomplete |

---

## 6. Practical findings (not promoted to OFFICIAL)

- Apply during BSP 08:00–22:00 BST; deep links may 404 outside window
- Use fee calculator + payment verification before circle office visit
- Engine/color/tyre changes are separate modification services (03C)
- Confirm RFID registration after retro-plate installation

---

## 7. Evidence limitations

- BSP Tier-1 sub-portals returned HTTP 404 during research fetch (outside operating window)
- BRTA portal static pages return HTML shell without embedded procedural body (client-side render)
- Fee calculator requires interactive session for vehicle-class matrix
- Batch 3A legacy seed replacement candidate (`driving-licence-renewal`) remains **separate** — not classified as knowledge gap and not auto-approved

---

## 8. Artifacts

```
data/research/raw/batch-03b-brta-vehicle/
├── scope.json
├── services_index.json
├── sources.json
├── claims.json
├── conflicts.json
├── knowledge_gaps.json
├── metadata.json
├── source_snapshots/   (5 BRTA portal shells + BSP hours notice)
└── services/           (6 per-service JSON files)

scripts/generate_batch03b_brta_vehicle_research_artifacts.py
scripts/verify_batch03b_brta_vehicle_claims.py
```

---

## 9. Current phase and next transition

| Field | Value |
|---|---|
| Current phase | RESEARCH — **COMPLETE** |
| Next phase | VERIFICATION (autonomous orchestrator) |
| Orchestrator command | `python3 -m automation.orchestrator.main run` |
| Publication | NOT_STARTED |
| E2E | NOT_STARTED |

---

## 10. Batch 3A legacy seed note

One Batch 3A legacy seed replacement candidate remains **pending human approval**. This is tracked under the seed-replacement workflow and is intentionally **not** part of Batch 3B knowledge gaps or publication gates.
