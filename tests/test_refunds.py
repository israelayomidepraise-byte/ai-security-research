
import pytest
from fastapi.testclient import TestClient
from app.main import app, orders

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_test_orders():
    # Keep each test independent.
    for order in orders.values():
        order["refunded"] = False

    yield

    for order in orders.values():
        order["refunded"] = False


def test_oversized_refund_rejected():
    response = client.post("/refunds", json={
        "order_id": "ORD-1001",
        "customer_id": "CUST-001",
        "amount_cents": 50000
    })

    assert response.status_code == 400


def test_wrong_customer_id_rejected():
    response = client.post("/refunds", json={
        "order_id": "ORD-1001",
        "customer_id": "CUST-002",
        "amount_cents": 12000
    })

    assert response.status_code == 403


def test_ineligible_order_rejected():
    response = client.post("/refunds", json={
        "order_id": "ORD-1002",
        "customer_id": "CUST-002",
        "amount_cents": 8000
    })

    assert response.status_code == 403


def test_valid_refund_approved():
    response = client.post("/refunds", json={
        "order_id": "ORD-1001",
        "customer_id": "CUST-001",
        "amount_cents": 12000
    })

    assert response.status_code == 200
    assert response.json()["status"] == "simulated_refund_approved"


def test_duplicate_refund_rejected():
    payload = {
        "order_id": "ORD-1001",
        "customer_id": "CUST-001",
        "amount_cents": 12000
    }

    first = client.post("/refunds", json=payload)
    second = client.post("/refunds", json=payload)

    assert first.status_code == 200
    assert second.status_code == 409
