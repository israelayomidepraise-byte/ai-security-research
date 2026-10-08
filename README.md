# AI Agent Security Testing Lab

**Prompt Injection | AI Agent Security | API Authorization | Adversarial Testing**

A hands-on AI security research project investigating how AI-assisted customer support systems can introduce security risks when language models are allowed to initiate sensitive backend operations.

The project uses an e-commerce refund workflow to demonstrate insecure API authorization, unsafe AI tool-call proposals, policy enforcement and security testing.

All transactions, customer accounts and order records are simulated.

## Project Overview

AI agents can interact with backend APIs, retrieve information and propose actions. However, their responses and tool calls should never be considered sufficient authorization for sensitive operations.

This laboratory investigates what happens when an AI-assisted refund system receives potentially malicious instructions, including attempts to bypass refund policies or trigger unauthorized transactions.

The project implements vulnerable and protected API workflows so their security behavior can be examined and compared.

## Research Objectives

- Identify weaknesses in AI-assisted refund workflows.
- Demonstrate missing authentication and authorization controls.
- Investigate prompt injection attempts targeting refund tool calls.
- Separate AI-generated proposals from trusted backend decisions.
- Evaluate refund eligibility, customer ownership and amount validation.
- Build reproducible security tests and audit records.
- Compare insecure and protected implementations.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend implementation and security testing |
| FastAPI | REST API development |
| Pydantic | Request validation |
| Pytest | Automated security tests |
| HTTPX | HTTP client and integration testing |
| GitHub Actions | Continuous integration |
| Ollama | Planned live local LLM integration |
| Llama 3.2 | Target model for live adversarial testing |

## System Architecture

The intended secured workflow is:

**Customer Message → AI Agent → Proposed Tool Call → Authenticated Dispatcher → Independent Security Policy → Audit Record**

The backend evaluates refund proposals independently of any instructions contained in a customer message.

The dispatcher currently operates in dry-run mode and does not execute refunds.

## Implemented Components

### 1. Vulnerable Refund API

The original `/refunds` endpoint deliberately demonstrates insecure authentication design.

It accepts a customer identifier supplied in the request without independently authenticating the caller.

This endpoint remains available for controlled, local security experiments.

### 2. Protected Refund Workflow

The `/protected/refunds` endpoint introduces test-token authentication, customer ownership verification, refund eligibility checks, amount validation and duplicate-refund prevention.

The authentication mechanism is designed for this laboratory and is not production-ready.

### 3. Independent Security Policy Engine

The policy engine evaluates refund proposals against business and authorization rules.

Possible decisions include:

- `deny` — The proposed action violates a security or refund rule.
- `would_allow` — The proposal meets the simulated policy requirements.
- `human_review_required` — The proposal exceeds the configured approval threshold.

These evaluations do not execute financial transactions.

### 4. Secure Agent Dispatcher

The `/lab/secure-agent/evaluate-tool-call` endpoint receives refund proposals, associates them with an authenticated test customer, evaluates the security policy and records the decision.

The dispatcher prevents AI-generated tool arguments from establishing customer identity.

### 5. Security Audit System

The audit component records proposal identifiers, timestamps, refund amounts, policy decisions and execution status.

Audit data currently resides in temporary in-memory storage.

### 6. Offline Adversarial Replay

The offline replay engine tests predefined refund proposals against security controls.

Scenarios cover oversized refunds, cross-customer access, ineligible orders, duplicate refunds, high-value transactions and legitimate refund requests.

These deterministic tests evaluate backend behavior. They are not evidence of successful attacks against a live language model.

### 7. Security Evidence Reporting

The reporting component generates structured JSON and Markdown evidence from the offline scenarios.

Reports are available under the `reports/` directory.

## Installation and Local Setup

The following instructions use Windows PowerShell.

**1. Clone the repository**

`git clone https://github.com/israelayomidepraise-byte/ai-security-research.git`

**2. Open the project directory**

`cd ai-security-research`

**3. Create a Python virtual environment**

`py -m venv .venv`

**4. Install dependencies**

`.\.venv\Scripts\python.exe -m pip install -r requirements.txt`

**5. Start the API locally**

`.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000`

**6. Open the API documentation**

http://127.0.0.1:8000/docs

Protected endpoints require locally configured test authentication tokens. Do not place real credentials in source code or commit them to the repository.

## Running Security Tests

Run the complete test suite:

`.\.venv\Scripts\python.exe -m pytest -v`

Run the offline adversarial scenarios:

`.\.venv\Scripts\python.exe -m app.offline_replay`

Generate a security evidence report:

`.\.venv\Scripts\python.exe -m app.reporting`

GitHub Actions also runs automated tests and generates report artifacts following repository updates.

## Security Findings

### Finding 001 — Missing Authentication

The original refund endpoint accepts requests without independently authenticating the requester.

**Status:** Confirmed in local testing.

### Finding 002 — Unsafe AI Tool-Call Risk

AI-generated refund proposals may contain values that violate backend business rules.

**Status:** Mocked tool-call handling and deterministic policy checks implemented. Live model evaluation pending.

### Finding 003 — Incomplete End-to-End Enforcement

The independent policy engine and secure dispatcher demonstrate backend validation. However, the original vulnerable endpoint remains accessible, and live AI-generated proposals are not yet routed through the secured dispatcher.

**Status:** Additional integration and hardening required.

## Current Verification

- Automated Python security tests have passed locally.
- GitHub Actions has successfully completed its initial CI workflow.
- Offline attack replay and evidence reporting have been implemented.
- The authenticated dispatcher has successfully rejected an oversized refund proposal in manual testing.

These results support the specific behaviors tested and should not be interpreted as a complete security certification.

## Current Limitations

The application is a research prototype, not a production payment system.

- No real customer identities or financial transactions are involved.
- The original refund API remains deliberately insecure.
- Test-token authentication is not suitable for production.
- The human approval workflow is represented as a policy decision rather than an operational approval system.
- Audit records are not yet persistent.
- Some AI agent tests use mocked model responses.
- Live Ollama-based prompt injection testing remains pending.
- The laboratory should not be deployed to a public network in its current form.

## Documentation

- [Threat Model](docs/threat-model.md)
- [Refund Prompt Injection Case Study](case-studies/chatbot-refund-prompt-injection.md)
- [Offline Security Report](reports/offline-replay.md)
- [Automated Testing Workflow](.github/workflows/security-tests.yml)

## Development Roadmap

- Integrate live Ollama model responses.
- Route AI-generated tool calls through the secure dispatcher.
- Perform repeatable prompt injection evaluations.
- Compare vulnerable and protected system behavior.
- Improve access controls, logging and approval enforcement.
- Complete security regression testing and publish final evidence.

## Responsible Use

This repository is intended for authorized security research, education and defensive testing.

All experiments should be conducted in controlled environments using simulated transactions and accounts.

The project does not contain real payment integrations.