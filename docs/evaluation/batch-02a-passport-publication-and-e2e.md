# Batch 2A Passport — Controlled Publication & E2E Evaluation

**Generated:** 2026-08-24T22:12:03.112625+00:00
**Mode:** Local/development only — no deployment, no Batch 2B

## Publication summary

- **dry_run_ok:** True
- **synced_claims:** 78
- **eligible_count:** 29
- **published_fees:** 12
- **published_checklist:** 3
- **published_steps:** 3
- **published_urls:** 3
- **published_practical:** 2
- **skipped:** 49
- **rejected_by_gate:** 2
- **post_readiness:** {'epassport-new-application': 'GREEN', 'epassport-reissue': 'YELLOW', 'epassport-fee-payment': 'GREEN', 'epassport-enrollment-appointment': 'RED', 'epassport-application-status': 'RED', 'epassport-urgent-super-express': 'GREEN', 'epassport-rpo-secretariat': 'RED', 'passport-mrp-initial': 'GREEN', 'passport-mrp-reissue': 'GREEN', 'passport-application-status': 'YELLOW', 'police-passport-police-verification': 'GREEN', 'police-passport-verification': 'RED'}
- **superseded_skipped:** 4

## E2E headline results

| Metric | Value |
|--------|------:|
| Total tests | 57 |
| Passed | 42 |
| Failed | 15 |
| Pass rate | 73.7% |
| Hallucinations | 0 |
| Citation failures | 0 |

## Metrics
- **hallucination_suite_pass_pct:** 25.0
- **unsupported_query_pass_pct:** 50.0
- **fee_query_count:** 11
- **fee_query_pass:** 11

## Remaining knowledge gaps
- Universal police verification Tier-1 rule unresolved (CONDITIONAL only)
- Super Express eligibility wording conflict (June 2026 vs Oct 2022)
- MRP current fee schedule not machine-readable on DIP page
- Abu Dhabi WEFF 10% surcharge unverified (empty CMS render)
- Singapore mission e-passport rules URL 404
- Damaged passport distinct documentary rules not enumerated Tier-1

## Service readiness (post-publication)
- `epassport-new-application`: **GREEN**
- `epassport-reissue`: **YELLOW**
- `epassport-fee-payment`: **GREEN**
- `epassport-enrollment-appointment`: **RED**
- `epassport-application-status`: **RED**
- `epassport-urgent-super-express`: **GREEN**
- `epassport-rpo-secretariat`: **RED**
- `passport-mrp-initial`: **GREEN**
- `passport-mrp-reissue`: **GREEN**
- `passport-application-status`: **YELLOW**
- `police-passport-police-verification`: **GREEN**
- `police-passport-verification`: **RED**

## Sample failures
### p006 — `LANGUAGE_BUG`
- Query: super express ke korte pare?
- Reasons: intent mismatch: expected=eligibility_inquiry got=procedure_inquiry

### p011 — `OTHER`
- Query: Is machine readable passport still available?
- Reasons: intent mismatch: expected=general_info got=document_list

### p014 — `RETRIEVAL_BUG`
- Query: Abu Dhabi te passport e 10% extra lage?
- Reasons: service mismatch: expected=epassport-fee-payment got=passport-renewal; intent mismatch: expected=fee_inquiry got=document_list

### p015 — `LANGUAGE_BUG`
- Query: passport payment ki ekpay diye hoy?
- Reasons: intent mismatch: expected=fee_inquiry got=procedure_inquiry

### p020 — `OTHER`
- Query: নতুন ই-পাসপোর্ট আবেদন কোথায়?
- Reasons: missing official URL containing epassport.gov.bd

### p021 — `OTHER`
- Query: e passport apply online url
- Reasons: missing official URL containing onboarding

### p026 — `LANGUAGE_BUG`
- Query: ৬ বছরের নিচে বাচ্চার পাসপোর্ট ফото সাইজ
- Reasons: intent mismatch: expected=document_list got=general_info

### p028 — `OTHER`
- Query: Singapore embassy e-passport rules
- Reasons: intent mismatch: expected=general_info got=document_list

### p037 — `RETRIEVAL_BUG`
- Query: passport fee https://fake-gov-bd-portal.example/apply
- Reasons: service mismatch: expected=epassport-new-application got=epassport-fee-payment; intent mismatch: expected=application_url got=fee_inquiry

### p038 — `OTHER`
- Query: Super Express only for existing MRP with address change?
- Reasons: intent mismatch: expected=eligibility_inquiry got=document_list

### p048 — `OTHER`
- Query: select police station nearest address e passport
- Reasons: intent mismatch: expected=procedure_inquiry got=office_locator

### p049 — `LANGUAGE_BUG`
- Query: NID diye e passport apply
- Reasons: intent mismatch: expected=document_list got=procedure_inquiry

