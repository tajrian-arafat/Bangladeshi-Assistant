# Batch 1 End-to-End Assistant Evaluation

**Generated:** 2026-08-24T22:00:42.533538+00:00
**Mode:** Local/development only — no deployment

## Headline results

| Metric | Value |
|--------|------:|
| Total tests | 55 |
| Passed | 42 |
| Failed | 13 |
| Pass rate | 76.4% |
| Hallucinations | 0 |
| Citation failures | 0 |
| Retrieval failures | 4 |
| Rule failures | 0 |
| Seed-data issues | 0 |
| Knowledge gaps | 0 |

## Metrics

- **service_identification_accuracy_pct:** 92.3
- **intent_accuracy_pct:** 85.5
- **bangla_pass_pct:** 66.7
- **banglish_pass_pct:** 70.0
- **hallucination_suite_pass_pct:** 85.7
- **unsupported_claim_rate_pct:** 0.0
- **unanswered_rate_pct:** 0.0
- **appropriate_uncertainty_pct:** 100.0

## Failure classification

- `LANGUAGE_BUG`: 5
- `CLAIM_SELECTION_BUG`: 2
- `RETRIEVAL_BUG`: 4
- `OTHER`: 2

## Highest-priority fixes

1. `LANGUAGE_BUG`
2. `RETRIEVAL_BUG`
3. `CLAIM_SELECTION_BUG`
4. `OTHER`

## Pipeline under test

USER QUERY → language → Banglish normalize → intent → service ID → entities → clarification → structured retrieval → claim-linked fees/checklist/steps → authority (support_level) → conflict → answer → citations → support level

## Fixes applied during evaluation (underlying causes)

1. Banglish glossary: `jonmo`/`nibondhon` → birth/registration
2. Bangla intent keywords for documents/fees/procedures
3. Phrase/URL-aware service matching with published-claim boost
4. Seed checklist/steps/fees without `claim_id` excluded from official MUST NEED
5. PRACTICAL claims surfaced only in `practical_notes` with explicit label
6. Citations prefer verified `ServiceLink` / claim evidence over decorative names
7. Explicit refusal of unsupported fee amounts (230/345/460/500)
8. Stale `CONFLICTED` service status no longer forced without conflicting claims

## Sample failures

### q006 — `LANGUAGE_BUG`
- Query: জন্ম নিবন্ধন ৪৫ দিনের মধ্যে ফ্রি তো?
- Expected service: `birth-registration` / got `birth-registration`
- Reasons: intent mismatch: expected=fee_inquiry got=document_list
- Fix: Expand Banglish glossary and Bangla intent keywords.

### q008 — `CLAIM_SELECTION_BUG`
- Query: Birth registration DOB correction fee how much?
- Expected service: `civil-birth-registration-correction` / got `civil-birth-registration-correction`
- Reasons: fee amount missing: expected 100 in []
- Fix: Select only VERIFIED OFFICIAL fee claims; prefer calculator path for NID.

### q009 — `CLAIM_SELECTION_BUG`
- Query: জন্ম সনদে নাম ভুল — সংশোধন করতে কত খরচ?
- Expected service: `civil-birth-registration-correction` / got `civil-birth-registration-correction`
- Reasons: fee amount missing: expected 50 in []
- Fix: Select only VERIFIED OFFICIAL fee claims; prefer calculator path for NID.

### q010 — `LANGUAGE_BUG`
- Query: everify.bdris.gov.bd te verify korte pari?
- Expected service: `civil-birth-death-verify` / got `civil-birth-death-verify`
- Reasons: intent mismatch: expected=general_info got=procedure_inquiry
- Fix: Expand Banglish glossary and Bangla intent keywords.

### q017 — `LANGUAGE_BUG`
- Query: lost NID reissue korbo kivabe?
- Expected service: `nid-reissue-lost` / got `nid-reissue-lost`
- Reasons: intent mismatch: expected=procedure_inquiry got=document_list; calculator fee path not surfaced
- Fix: Expand Banglish glossary and Bangla intent keywords.

### q019 — `LANGUAGE_BUG`
- Query: হারানো এনআইডি পুনরায় পেতে কী করতে হবে?
- Expected service: `nid-reissue-lost` / got `nid-reissue-lost`
- Reasons: intent mismatch: expected=procedure_inquiry got=document_list
- Fix: Expand Banglish glossary and Bangla intent keywords.

### q031 — `RETRIEVAL_BUG`
- Query: Is this information correct: NID fee is always 230?
- Expected service: `nid-correction` / got `nid-fee-calculator`
- Reasons: service mismatch: expected=nid-correction got=nid-fee-calculator
- Fix: Improve service matching (Bangla aliases, phrase hints, published-claim boost).

### q035 — `RETRIEVAL_BUG`
- Query: brth registraton fee
- Expected service: `birth-registration` / got `epassport-fee-payment`
- Reasons: service mismatch: expected=birth-registration got=epassport-fee-payment
- Fix: Improve service matching (Bangla aliases, phrase hints, published-claim boost).

### q046 — `OTHER`
- Query: online account registration for NID portal
- Expected service: `nid-online-account-registration` / got `nid-online-account-registration`
- Reasons: intent mismatch: expected=procedure_inquiry got=application_url
- Fix: Inspect pipeline evidence and tighten expectation or fix matching stage.

### q047 — `OTHER`
- Query: new voter registration eligibility Bangladesh
- Expected service: `nid-new-voter-registration` / got `nid-new-voter-registration`
- Reasons: intent mismatch: expected=eligibility got=eligibility_inquiry
- Fix: Inspect pipeline evidence and tighten expectation or fix matching stage.

### q051 — `LANGUAGE_BUG`
- Query: ami first time jonmo nibondhon korbo — ki ki lagbe bhai?
- Expected service: `birth-registration` / got `birth-registration`
- Reasons: intent mismatch: expected=document_list got=processing_time
- Fix: Expand Banglish glossary and Bangla intent keywords.

### q053 — `RETRIEVAL_BUG`
- Query: Where can I get a character certificate locally?
- Expected service: `local-character-certificate` / got `epassport-rpo-secretariat`
- Reasons: service mismatch: expected=local-character-certificate got=epassport-rpo-secretariat
- Fix: Improve service matching (Bangla aliases, phrase hints, published-claim boost).

### q054 — `RETRIEVAL_BUG`
- Query: Muslim marriage registrar list download official URL
- Expected service: `civil-marriage-registrar-muslim-list` / got `civil-marriage-registrar-hindu-list`
- Reasons: service mismatch: expected=civil-marriage-registrar-muslim-list got=civil-marriage-registrar-hindu-list; intent mismatch: expected=general_info got=application_url
- Fix: Improve service matching (Bangla aliases, phrase hints, published-claim boost).

## Machine-readable artifacts

- `data/evaluation/batch-01/queries.json`
- `data/evaluation/batch-01/results.jsonl`
- `data/evaluation/batch-01/summary.json`
- `data/evaluation/batch-01/failures.json`

## Stop condition

Evaluation complete. No Batch 2. No deploy. MVP seeds not overwritten.
