# Verification phase prompt

Verification is **independent** from research.

## Verdicts per claim
VERIFIED | PARTIALLY_VERIFIED | UNVERIFIED | CONFLICTING | OUTDATED | REJECTED

## High-risk claims require stronger evidence
- fees, mandatory documents, legal requirements, eligibility
- official URLs, payment instructions, deadlines, SLAs

## Outputs
- `data/research/verification/<batch-slug>/claims_verification.json`
- `data/research/verification/<batch-slug>/conflicts_resolution.json`
- `data/research/verification/<batch-slug>/knowledge_gaps.json`

Write `result.json` when complete.
