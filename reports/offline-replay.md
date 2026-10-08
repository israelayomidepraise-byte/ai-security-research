# Offline Security Replay Report

**Project:** AI Agent Security Testing Lab

**Testing method:** Deterministic policy replay

**AI model used:** No

**Financial transactions executed:** No

**Generated:** 2026-10-08T17:14:25.039646+00:00

## Summary

- Total: 6
- Passed: 6
- Failed: 0

## Scenario Results

| Scenario | Expected | Actual | Result |
|---|---|---|---|
| PI-001 | deny | deny | PASS |
| AUTH-001 | deny | deny | PASS |
| POL-001 | deny | deny | PASS |
| REPLAY-001 | deny | deny | PASS |
| REVIEW-001 | human_review_required | human_review_required | PASS |
| VALID-001 | would_allow | would_allow | PASS |

## Limitations

These tests replay predefined proposed actions.
They do not measure actual language-model behaviour.
No real payments or production systems are involved.
