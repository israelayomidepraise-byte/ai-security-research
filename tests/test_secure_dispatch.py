
from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from app.main import app, orders
from app.agent_audit import (
    get_audit_events,
    clear_audit_events
)

client = TestClient(app)

URL = "/lab/secure-agent/evaluate-tool-call"


@pytest.fixture(autouse=True)
def setup_test(monkeypatch):
    monkeypatch.setenv(
        "LAB_TOKEN_CUST_001",
        "test-only-token-001"
    )
    monkeypatch.setenv(
        "LAB_TOKEN_CUST_002",
        "test-only-token-002"
    )

    original = deepcopy(orders)
    clear_audit_events()

    yield

    orders.clear()
    orders.update(original)
    clear_audit_events()


def submit(order_id, amount, token="test-only-token-001"):
    return client.post(
        URL,
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "order_id": order_id,
            "amount_cents": amount
        }
    )


def test_authentication_required():
    response = client.post(
        URL,
        json={
            "order_id": "ORD-1001",
            "amount_cents": 12000
        }
    )

    assert response.status_code == 401
    assert get_audit_events() == []


def test_invalid_token_rejected():
    response = submit(
        "ORD-1001", 12000, "invalid-token"
    )

    assert response.status_code == 401


def test_cross_customer_refund_denied():
    response = submit(
        "ORD-1001", 12000, "test-only-token-002"
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "deny"
    assert response.json()["reason"] == "order_not_accessible"
    assert response.json()["executed"] is False


def test_oversized_refund_denied_and_audited():
    before = deepcopy(orders)

    response = submit("ORD-1001", 50000)

    assert response.status_code == 200
    assert response.json()["decision"] == "deny"
    assert response.json()["reason"] == "amount_mismatch"
    assert response.json()["executed"] is False
    assert orders == before

    events = get_audit_events()

    assert len(events) == 1
    assert events[0]["decision"] == "deny"
    assert events[0]["executed"] is False


def test_valid_refund_is_dry_run_only():
    before = deepcopy(orders)

    response = submit("ORD-1001", 12000)

    assert response.status_code == 200
    assert response.json()["decision"] == "would_allow"
    assert response.json()["executed"] is False
    assert orders == before


def test_model_cannot_supply_customer_identity():
    response = client.post(
        URL,
        headers={
            "Authorization": "Bearer test-only-token-002"
        },
        json={
            "order_id": "ORD-1001",
            "amount_cents": 12000,
            "customer_id": "CUST-001"
        }
    )

    assert response.status_code == 422
    assert get_audit_events() == []


def test_high_value_refund_requires_review():
    orders["ORD-9001"] = {
        "customer_id": "CUST-001",
        "total_cents": 50000,
        "eligible": True,
        "refunded": False
    }

    response = submit("ORD-9001", 50000)

    assert response.status_code == 200
    assert response.json()["decision"] == "human_review_required"
    assert response.json()["executed"] is False
    assert orders["ORD-9001"]["refunded"] is False
