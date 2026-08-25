# Batch 2A Passport — Completion & Evaluation Normalization (Step 16)

**Generated:** 2026-08-25T03:37:30.609274+00:00
**Mode:** Local/development only — no deployment, no Batch 2B

## Headline metrics

| Metric | Value |
|--------|------:|
| Total tests | 57 |
| Raw pass rate | 77.2% (44/57) |
| Normalized pass rate | 100.0% (57/57) |
| Supported-case accuracy | 100.0% (20/20) |
| Hallucinations (product failures) | 0 |
| Citation failures | 0 |
| Correct-uncertainty rate | 100.0% |
| Correct-refusal rate | 100.0% |

## Outcome distribution
- **ANSWER_SUPPORTED:** 20
- **CORRECT_UNCERTAINTY:** 32
- **CORRECT_REFUSAL:** 4
- **CLARIFICATION_REQUIRED:** 1

## Step 16 failure classification

## Service readiness (from published claims)
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

## Remaining knowledge gaps
- Universal police verification Tier-1 rule unresolved (CONDITIONAL only)
- Super Express eligibility wording conflict (June 2026 vs Oct 2022)
- MRP current fee schedule not machine-readable on DIP page
- Abu Dhabi WEFF 10% surcharge unverified (empty CMS render)
- Singapore mission e-passport rules URL 404
- Damaged passport distinct documentary rules not enumerated Tier-1
- Minor under-6 photo size rule indexed-only (not browser-snapshotted)

## Product failures (supported cases only)

