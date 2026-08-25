# Personalized Requirement Engine — Bangladeshi Assistant

**Version:** 1.0 (design)  
**Date:** 2026-08-24

---

## 1. Purpose

Generate **personalized document checklists and prerequisites** per user context, using only verified claims where marked OFFICIAL, while asking the **minimum necessary questions**.

---

## 2. Requirement Classification

Every requirement item belongs to exactly one class:

| Class | Code | Meaning | Example |
|-------|------|---------|---------|
| Must need | `MUST` | Officially required for this variant | NID for passport renewal |
| Conditional | `CONDITIONAL` | Required only if situation applies | Affidavit if passport lost |
| Recommended | `RECOMMENDED` | Helpful but not officially mandatory | Extra photocopies |
| Not applicable | `N/A` | Explicitly excluded for this variant | — |

Maps to existing `ChecklistItem.item_type` with expanded enum:

```
REQUIRED → MUST
CONDITIONAL → CONDITIONAL
RECOMMENDED → RECOMMENDED
NOT_APPLICABLE → N/A
```

---

## 3. Condition Dimensions

Conditions evaluate against **user context** (clarifications + inferred entities):

| Dimension | Key examples | Notes |
|-----------|--------------|-------|
| Age | `age`, `age_group` | minor/adult/senior |
| Gender | `gender` | Only where legally relevant |
| Applicant role | `student`, `doctor`, `govt_employee`, `private_employee` | |
| Marital status | `marital_status` | where forms differ |
| Application type | `application_type` | first_time, renewal, reissue, replacement |
| Document state | `passport_status`, `document_status` | lost, damaged, expired |
| Business | `business_type`, `tin_type` | individual vs business |
| Vehicle | `vehicle_type`, `licence_class` | BRTA classes |
| Disability | `disability_status` | |
| Geography | `division`, `district`, `upazila`, `city_corporation` | |
| Nationality/status | `nationality`, `visa_status` | |
| Service variant | `passport_type`, `correction_type`, `registration_type` | |

### 3.1 Condition DSL

Extend existing JSON conditions on `ChecklistItem` and `ChecklistCondition`:

```json
{
  "all": [
    {"field": "application_type", "op": "eq", "value": "renewal"},
    {"field": "passport_type", "op": "in", "value": ["e-passport", "mrp"]}
  ],
  "any": [
    {"field": "passport_status", "op": "eq", "value": "lost"},
    {"field": "passport_status", "op": "eq", "value": "damaged"}
  ]
}
```

Operators: `eq`, `neq`, `in`, `not_in`, `gte`, `lte`, `exists`, `missing`.

**Current gap:** `_conditions_match()` only supports flat `all` equality — must upgrade.

---

## 4. Question Selection (Minimal Clarifications)

Goal: resolve maximum CONDITIONAL items with minimum questions.

### 4.1 Algorithm (design)

```
1. Load all checklist items for service variant
2. Split: MUST (always show), CONDITIONAL (need context), RECOMMENDED (optional section)
3. Build dependency graph: which condition fields unlock which items?
4. Compute unknown fields from missing clarification keys
5. Rank questions by information gain (most items unlocked per question)
6. Ask top 1 question per turn (existing orchestrator pattern)
7. Repeat until no critical unknowns OR user skips
8. Emit personalized checklist + N/A exclusions
```

### 4.2 Critical vs optional unknowns

| Unknown blocks | Behavior |
|----------------|----------|
| MUST item applicability | Must ask or show "confirm with office" |
| CONDITIONAL branch | Ask ranked question |
| RECOMMENDED only | Skip question; omit section |

### 4.3 Current orchestrator fixes needed

| Issue | Fix |
|-------|-----|
| Hardcoded slug checks | Drive from condition graph |
| Key mismatch (`passport_type` vs `passport_status`) | Align seed + engine keys |
| No clarification persistence | Store in conversation context |
| Frontend no clarification UI | Collect + resubmit `clarifications` in ChatRequest |

---

## 5. Personalization Outputs

### 5.1 Checklist response

```yaml
checklist:
  must:
    - label, evidence_id, claim_id
  conditional_included:
    - label, reason (which condition matched)
  conditional_excluded:
    - label, reason (condition not met)  # optional debug mode
  recommended:
    - label, evidence_id
  warnings:
    - "Medical certificate rules vary by licence class — verify with BRTA"
```

### 5.2 Prerequisites graph

Services may depend on other services:

```
passport-renewal → requires → nid (active)
driving-licence-renewal → requires → medical-certificate (conditional)
```

Dependency edges stored on service or procedure step; engine walks chain to prepend prerequisites.

---

## 6. Official vs Practical Requirements

| Class | Source | In MUST list? |
|-------|--------|---------------|
| OFFICIAL VERIFIED | Tier 1–2 | Yes |
| OFFICIAL VERIFIED | Tier 3–4 + approval | Yes |
| PRACTICAL | Tier 5–7 | **Separate section only** |

Engine **must not** promote PRACTICAL to MUST without verification event (see VERIFICATION_FRAMEWORK.md).

Example:

> **Official MUST:** NID, current passport  
> **Commonly reported (not official):** Some applicants report extra photocopies — [practical cite]

---

## 7. Localization

Requirement labels returned in user language:

1. Prefer `label_bn` if `language=bn`  
2. Prefer `label_en` if `language=en`  
3. Banglish queries → respond in Banglish or Bengali based on preference  

District-specific overrides:

```
ChecklistItem + district_id / upazila_id override table (future)
```

Fallback: national default + warning "requirements may vary by location".

---

## 8. Integration with Existing ChecklistEngine

Current `ChecklistEngine.build(service, answers)`:

- Loads items sorted by order  
- Filters by flat conditions  

**Target `PersonalizedRequirementEngine`:**

- Wraps/enhances ChecklistEngine  
- Adds question planner  
- Links each item to `claim_id` / `evidence_chunk_id`  
- Returns structured sections by MUST/CONDITIONAL/RECOMMENDED  

Keep backward compatibility during migration.

---

## 9. Example Flow (Passport Renewal)

**User:** "passport renew korte ki ki lagbe?"

1. Match service `passport-renewal`  
2. Unknown: `passport_type`, `application_type`  
3. Ask: "Is this an e-passport or MRP passport?"  
4. User: "e-passport"  
5. Unknown: `application_type`  
6. Ask: "Renewal, reissue, or first-time?"  
7. User: "renewal"  
8. Emit MUST: NID, photos, current/expired passport  
9. Emit CONDITIONAL (not shown): lost passport affidavit — condition not met  
10. All items cite VERIFIED claim IDs  

---

## 10. Data Requirements

Each checklist item needs:

| Field | Required for ACTIVE |
|-------|---------------------|
| `item_type` | Yes |
| `label_bn`, `label_en` | Yes |
| `conditions` | If CONDITIONAL |
| `claim_id` or `evidence_chunk_id` | Yes for OFFICIAL |
| `information_class` | Yes |
| `order` | Yes |

Seed data today lacks evidence links — must be added during curation.

---

## Related Documents

- [KNOWLEDGE_ARCHITECTURE.md](./KNOWLEDGE_ARCHITECTURE.md)
- [VERIFICATION_FRAMEWORK.md](./VERIFICATION_FRAMEWORK.md)
- [KNOWLEDGE_QUALITY_FRAMEWORK.md](./KNOWLEDGE_QUALITY_FRAMEWORK.md)
- [CURRENT_SYSTEM_AUDIT.md](./CURRENT_SYSTEM_AUDIT.md)
