
# AI Agent Security Lab — Threat Model

## 1. System Overview

This project examines security risks in an AI-assisted
e-commerce refund workflow.

The lab uses simulated customer accounts, orders and
refund transactions. No real payments are processed.

The project currently includes:

- A deliberately vulnerable refund API.
- A protected refund API with test-token authentication.
- An independent refund policy evaluator.
- An AI agent integration using Ollama's local API.
- A refund proposal audit recorder.
- Offline attack replay scenarios.
- Automated tests and GitHub Actions CI.

Live AI model evaluation is pending.

## 2. Assets Requiring Protection

1. Customer identities and account ownership.
2. Order records and refund eligibility.
3. Refund amounts and transaction states.
4. Authentication credentials.
5. AI agent tool-call permissions.
6. Security audit records.

## 3. Trust Boundaries

### Boundary A: Customer to API

Customer-supplied information is untrusted.

Order identifiers and claimed customer identities must
not establish authentication.

### Boundary B: Customer to AI Agent

Customer messages may contain instructions attempting
to override the agent's intended behaviour.

User messages must not be treated as system instructions.

### Boundary C: AI Agent to Backend

AI-generated tool calls are untrusted proposals.

The backend must independently validate every action.

### Boundary D: Backend to Transaction State

Refund approval must depend on verified identity,
order ownership, eligibility, amount limits and
required approvals.

## 4. Identified Threats

| ID | Threat | Impact | Priority |
|---|---|---|---|
| T01 | Unauthenticated refund requests | Unauthorized simulated refunds | High |
| T02 | Prompt injection influencing refund tool calls | Agent proposes prohibited actions | High |
| T03 | Cross-customer order access | Unauthorized account activity | High |
| T04 | Oversized refund requests | Financial policy violation | High |
| T05 | Repeated refund requests | Duplicate transaction risk | High |
| T06 | Exposed API credentials | Unauthorized API access | High |
| T07 | Missing human approval enforcement | High-value refund bypass | High |
| T08 | Unrestricted audit proposal submissions | Log flooding or resource exhaustion | Medium |

Priorities are preliminary qualitative lab assessments,
not findings from a production penetration test.

## 5. Current Security Findings

### Finding 001 — Missing Authentication

The original POST /refunds endpoint accepts
caller-supplied customer identifiers without
authenticating the requester.

A local test demonstrated that a correctly formed
refund request could be approved without credentials.

Status: Confirmed in the simulated lab.

### Finding 002 — Untrusted AI Tool Arguments

The AI integration can generate proposed refund
amounts and order identifiers.

These proposals are recorded through the audit
workflow without executing transactions.

Status: Mocked tool-call behaviour tested.
Live model behaviour not yet evaluated.

### Finding 003 — Incomplete Policy Enforcement

The independent policy evaluator checks customer
ownership, eligibility, amount matching, previous
refund status and an approval threshold.

However, creating this policy evaluator does not
automatically enforce it across all refund endpoints.

Status: Integration and enforcement work remaining.

## 6. Security Controls

Currently implemented:

- Refund amount validation.
- Basic test-token authentication on protected routes.
- Customer ownership checks.
- Duplicate refund checks.
- Independent policy evaluation.
- Dry-run refund proposal logging.
- Automated regression tests.
- Offline security scenario replay.

Planned improvements:

- Enforce one shared policy across protected execution.
- Introduce explicit approval state and workflow.
- Harden audit endpoint access.
- Validate AI tool calls against authenticated sessions.
- Improve logging and error handling.
- Conduct live prompt injection evaluations.
- Add negative and adversarial regression tests.

## 7. Known Limitations

The original refund endpoint remains intentionally
vulnerable for controlled security demonstrations.

The authentication implementation uses static
environment-configured test tokens and is not
production-ready.

Audit records are stored temporarily in memory.

The independent policy evaluator is not yet enforced
by every refund execution path.

Some tests use mocked language-model responses.
Those tests do not establish real-world model
robustness against prompt injection.

The system is intended for local testing only.
It must not be deployed publicly in its current form.

## 8. Security Objective

Demonstrate that even when an AI model proposes
an unsafe refund action, trusted backend controls
can independently reject or require approval
for that action.

A successful final evaluation must distinguish:

1. Whether the AI attempted an unsafe tool call.
2. Whether the backend accepted that call.
3. Whether any simulated transaction state changed.
4. Whether the same attack succeeds after remediation.
