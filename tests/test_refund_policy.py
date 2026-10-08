
import pytest
from fastapi.testclient import TestClient

from app.main import app, orders
from app.refund_policy import evaluate_refund_policy

client = TestClient(app)


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

    original = {
        key: value.copy()
        for key, value in orders.items()
    }
    for order in orders.values():
        order["refunded"] = False

    yield

    orders.clear()
    orders.update(original)


def check(order_id, amount, token="test-only-token-001"):
    return client.post(
        "/lab/policy/evaluate",
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
        "/lab/policy/evaluate",
        json={
            "order_id": "ORD-1001",
            "amount_cents": 12000
        }
    )
    assert response.status_code == 401


def test_valid_refund_would_be_allowed():
    response = check("ORD-1001", 12000)

    assert response.status_code == 200
    assert response.json()["decision"] == "would_allow"
    assert response.json()["executed"] is False
    assert orders["ORD-1001"]["refunded"] is False


def test_wrong_customer_denied():
    response = check(
        "ORD-1001", 12000, "test-only-token-002"
    )
    assert response.json()["decision"] == "deny"
    assert response.json()["reason"] == "order_not_accessible"


def test_unknown_order_denied():
    response = check("ORD-9999", 12000)
    assert response.json()["reason"] == "order_not_accessible"


def test_oversized_refund_denied():
    response = check("ORD-1001", 50000)
    assert response.json()["reason"] == "amount_mismatch"


def test_ineligible_order_denied():
    response = check(
        "ORD-1002", 8000, "test-only-token-002"
    )
    assert response.json()["reason"] == "order_ineligible"


def test_already_refunded_denied():
    orders["ORD-1001"]["refunded"] = True

    response = check("ORD-1001", 12000)
    assert response.json()["reason"] == "already_refunded"


def test_large_refund_requires_human_review():
    sample_orders = {
        "ORD-9001": {
            "customer_id": "CUST-001",
            "total_cents": 50000,
            "eligible": True,
            "refunded": False
        }
    }

    result = evaluate_refund_policy(
        orders=sample_orders,
        authenticated_customer_id="CUST-001",
        order_id="ORD-9001",
        amount_cents=50000
    )

    assert result["decision"] == "human_review_required"
    assert result["executed"] is False
    assert sample_orders["ORD-9001"]["refunded"] is False
