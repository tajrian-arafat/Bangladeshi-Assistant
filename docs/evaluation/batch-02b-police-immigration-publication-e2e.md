# Batch 2B — Publication & E2E Evaluation

**Generated:** 2026-08-24T23:13:02.775181+00:00
**Mode:** Local/development only

## E2E headline results

| Metric | Value |
|--------|------:|
| Total tests | 67 |
| Raw pass rate | 74.6% |
| Normalized pass rate | 77.6% |
| Hallucinations (product failures) | 0 |
| Correct uncertainty | 22 |
| Correct refusal | 3 |

## Dry-run validation

- Gate checks A–G: **PASS**

## Critical test cases

- **b001** `Police clearance er fee koto?` → ANSWER_SUPPORTED (pass)
- **b002** `Online PCC fee koto?` → ANSWER_SUPPORTED (pass)
- **b003** `Offline police clearance fee?` → CORRECT_UNCERTAINTY (pass)
- **b004** `Online GD kora jay?` → ANSWER_SUPPORTED (pass)
- **b005** `Shob dhoroner GD online kora jay?` → CORRECT_UNCERTAINTY (pass)
- **b006** `Police passport verification koto din?` → ANSWER_SUPPORTED (pass)
- **b007** `Police clearance pete koto din?` → ANSWER_SUPPORTED (pass)
- **b010** `MRV fee koto?` → CORRECT_UNCERTAINTY (pass)
- **b011** `PCC apply https://fake-police-gov.example/pcc` → CORRECT_REFUSAL (pass)

## Product failures
- **b009**: intent mismatch: expected=application_url got=office_locator
- **b014**: intent mismatch: expected=eligibility_inquiry got=processing_time
- **b018**: service mismatch: expected=police-clearance-certificate got=epassport-new-application; intent mismatch: expected=fee_inquiry got=general_info; online PCC BDT 1500 not shown for online-channel query
- **b022**: intent mismatch: expected=processing_time got=procedure_inquiry
- **b023**: service mismatch: expected=police-general-diary-online got=None; intent mismatch: expected=document_list got=procedure_inquiry
- **b025**: intent mismatch: expected=procedure_inquiry got=document_list
- **b027**: intent mismatch: expected=application_url got=procedure_inquiry
- **b029**: service mismatch: expected=police-passport-verification got=epassport-urgent-super-express
- **b033**: service mismatch: expected=police-passport-verification got=police-clearance-certificate; intent mismatch: expected=general_info got=procedure_inquiry
- **b038**: intent mismatch: expected=general_info got=document_list
- **b046**: service mismatch: expected=migration-visa-application-dip got=None; missing official URL containing dip.gov.bd; missing official URL containing dip.gov.bd
- **b050**: intent mismatch: expected=general_info got=document_list
- **b055**: intent mismatch: expected=general_info got=document_list
- **b059**: service mismatch: expected=police-firearms-license got=driving-licence-renewal
- **b062**: service mismatch: expected=police-general-diary-online got=police-general-diary
