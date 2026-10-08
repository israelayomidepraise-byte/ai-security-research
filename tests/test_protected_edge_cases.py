
import pytest
from fastapi.testclient import TestClient
from app.main import app, orders

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_tests(monkeypatch):
    monkeypatch.setenv(
        "LAB_TOKEN_CUST_001", "test-only-token-001"
    )
    monkeypatch.setenv(
        "LAB_TOKEN_CUST_002", "test-only-token-002"
    )

    for order in orders.values():
        order["refunded"] = False

    yield

    for order in orders.values():
        order["refunded"] = False


def request_refund(order_id, amount, token):
    return client.post(
        "/protected/refunds",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "order_id": order_id,
            "amount_cents": amount
        }
    )


def test_nonexistent_order():
    response = request_refund(
        "ORD-9999", 12000, "test-only-token-001"
    )
    assert response.status_code == 404


def test_ineligible_order():
    response = request_refund(
        "ORD-1002", 8000, "test-only-token-002"
    )
    assert response.status_code == 403


def test_invalid_authentication_token():
    response = request_refund(
        "ORD-1001", 12000, "invalid-token"
    )
    assert response.status_code == 401


def test_zero_refund_amount():
    response = request_refund(
        "ORD-1001", 0, "test-only-token-001"
    )
    assert response.status_code == 422


def test_refund_replay():
    first = request_refund(
        "ORD-1001", 12000, "test-only-token-001"
    )
    second = request_refund(
        "ORD-1001", 12000, "test-only-token-001"
    )

    assert first.status_code == 200
    assert second.status_code == 409
