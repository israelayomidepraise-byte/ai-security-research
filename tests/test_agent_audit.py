
import pytest
from fastapi.testclient import TestClient

from app.main import app, orders
from app.agent_audit import (
    get_audit_events,
    clear_audit_events
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_audit():
    clear_audit_events()
    original = {
        key: order["refunded"]
        for key, order in orders.items()
    }

    yield

    for key, state in original.items():
        orders[key]["refunded"] = state

    clear_audit_events()


def test_refund_proposal_recorded():
    orders["ORD-1001"]["refunded"] = False

    response = client.post(
        "/lab/agent/propose-refund",
        json={
            "order_id": "ORD-1001",
            "amount_cents": 50000
        }
    )

    assert response.status_code == 200
    assert response.json()["executed"] is False
    assert response.json()["decision"] == "proposal_only"

    assert len(get_audit_events()) == 1
    assert orders["ORD-1001"]["refunded"] is False


def test_invalid_amount_rejected():
    response = client.post(
        "/lab/agent/propose-refund",
        json={
            "order_id": "ORD-1001",
            "amount_cents": -500
        }
    )

    assert response.status_code == 422
    assert len(get_audit_events()) == 0


def test_unexpected_fields_rejected():
    response = client.post(
        "/lab/agent/propose-refund",
        json={
            "order_id": "ORD-1001",
            "amount_cents": 50000,
            "secret_token": "do-not-record"
        }
    )

    assert response.status_code == 422
    assert len(get_audit_events()) == 0
