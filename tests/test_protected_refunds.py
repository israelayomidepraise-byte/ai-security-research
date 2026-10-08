
import pytest
from fastapi.testclient import TestClient
from app.main import app, orders

client = TestClient(app)


@pytest.fixture(autouse=True)
def prepare_test(monkeypatch):
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


def test_no_authentication_rejected():
    response = client.post(
        "/protected/refunds",
        json={
            "order_id": "ORD-1001",
            "amount_cents": 12000
        }
    )

    assert response.status_code == 401


def test_other_customers_order_rejected():
    response = client.post(
        "/protected/refunds",
        headers={
            "Authorization": "Bearer test-only-token-002"
        },
        json={
            "order_id": "ORD-1001",
            "amount_cents": 12000
        }
    )

    assert response.status_code == 403


def test_oversized_refund_rejected():
    response = client.post(
        "/protected/refunds",
        headers={
            "Authorization": "Bearer test-only-token-001"
        },
        json={
            "order_id": "ORD-1001",
            "amount_cents": 50000
        }
    )

    assert response.status_code == 400


def test_authorized_refund_approved():
    response = client.post(
        "/protected/refunds",
        headers={
            "Authorization": "Bearer test-only-token-001"
        },
        json={
            "order_id": "ORD-1001",
            "amount_cents": 12000
        }
    )

    assert response.status_code == 200
    assert orders["ORD-1001"]["refunded"] is True
