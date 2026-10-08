
from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from app.main import app, orders

client = TestClient(app)


@pytest.fixture(autouse=True)
def prepare_lab_test(monkeypatch):
    # Disable vulnerable mode during these tests.
    monkeypatch.delenv(
        "ENABLE_VULNERABLE_LAB",
        raising=False
    )

    # Preserve the original order records.
    original = deepcopy(orders)
    orders["ORD-1001"]["refunded"] = False

    yield

    # Restore records after every test.
    orders.clear()
    orders.update(original)


def test_vulnerable_refund_disabled_by_default():
    before = deepcopy(orders)

    response = client.post(
        "/refunds",
        json={
            "order_id": "ORD-1001",
            "customer_id": "CUST-001",
            "amount_cents": 12000
        }
    )

    assert response.status_code == 404
    assert orders == before


def test_order_listing_disabled_by_default():
    response = client.get("/orders")

    assert response.status_code == 404


def test_secure_dispatcher_still_works(monkeypatch):
    monkeypatch.setenv(
        "LAB_TOKEN_CUST_001",
        "test-only-token-001"
    )

    before = deepcopy(orders)

    response = client.post(
        "/lab/secure-agent/evaluate-tool-call",
        headers={
            "Authorization":
            "Bearer test-only-token-001"
        },
        json={
            "order_id": "ORD-1001",
            "amount_cents": 50000
        }
    )

    assert response.status_code == 200

    result = response.json()

    assert result["decision"] == "deny"
    assert result["reason"] == "amount_mismatch"
    assert result["executed"] is False
    assert orders == before
