
from copy import deepcopy

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app, orders
from app.agent_audit import (
    clear_audit_events,
    get_audit_events
)
import app.secure_agent_chat as secure_chat

client = TestClient(app)
URL = "/lab/secure-agent/chat"

AUTH = {
    "Authorization": "Bearer test-only-token-001"
}


@pytest.fixture(autouse=True)
def reset_lab(monkeypatch):
    monkeypatch.setenv(
        "LAB_TOKEN_CUST_001", "test-only-token-001"
    )
    monkeypatch.setenv(
        "LAB_TOKEN_CUST_002", "test-only-token-002"
    )

    original = deepcopy(orders)
    clear_audit_events()

    yield

    orders.clear()
    orders.update(original)
    clear_audit_events()


def mock_model(monkeypatch, message):
    def fake_post(url, json, timeout):
        return httpx.Response(
            200,
            json={"message": message},
            request=httpx.Request("POST", url)
        )

    monkeypatch.setattr(
        secure_chat.httpx, "post", fake_post
    )


def tool_message(arguments, name="propose_refund"):
    return {
        "content": "",
        "tool_calls": [{
            "function": {
                "name": name,
                "arguments": arguments
            }
        }]
    }


def submit(message="Please process my refund", headers=None):
    return client.post(
        URL,
        headers=AUTH if headers is None else headers,
        json={"message": message}
    )


def test_unauthenticated_request_rejected(monkeypatch):
    def must_not_call_model(*args, **kwargs):
        raise AssertionError("Model must not be contacted")

    monkeypatch.setattr(
        secure_chat.httpx, "post", must_not_call_model
    )

    response = submit(headers={})

    assert response.status_code == 401


def test_normal_conversation(monkeypatch):
    mock_model(monkeypatch, {
        "content": "How can I help you?",
        "tool_calls": []
    })

    response = submit("Hello")

    assert response.status_code == 200
    assert response.json()["policy_decisions"] == []
    assert get_audit_events() == []


def test_oversized_refund_denied(monkeypatch):
    mock_model(monkeypatch, tool_message({
        "order_id": "ORD-1001",
        "amount_cents": 50000
    }))

    before = deepcopy(orders)
    response = submit()

    result = response.json()["policy_decisions"][0]

    assert result["decision"] == "deny"
    assert result["reason"] == "amount_mismatch"
    assert result["executed"] is False
    assert orders == before
    assert len(get_audit_events()) == 1


def test_valid_refund_remains_dry_run(monkeypatch):
    mock_model(monkeypatch, tool_message({
        "order_id": "ORD-1001",
        "amount_cents": 12000
    }))

    response = submit()

    result = response.json()["policy_decisions"][0]

    assert result["decision"] == "would_allow"
    assert result["executed"] is False
    assert orders["ORD-1001"]["refunded"] is False


def test_cross_customer_refund_denied(monkeypatch):
    mock_model(monkeypatch, tool_message({
        "order_id": "ORD-1001",
        "amount_cents": 12000
    }))

    response = submit(headers={
        "Authorization": "Bearer test-only-token-002"
    })

    result = response.json()["policy_decisions"][0]

    assert result["decision"] == "deny"
    assert result["reason"] == "order_not_accessible"


def test_model_cannot_impersonate_customer(monkeypatch):
    mock_model(monkeypatch, tool_message({
        "order_id": "ORD-1001",
        "amount_cents": 12000,
        "customer_id": "CUST-001"
    }))

    response = submit()

    assert response.json()["rejected_tool_calls"] == 1
    assert response.json()["policy_decisions"] == []
    assert get_audit_events() == []


def test_unknown_tool_rejected(monkeypatch):
    mock_model(monkeypatch, tool_message(
        {"command": "refund"},
        name="execute_payment"
    ))

    response = submit()

    assert response.json()["rejected_tool_calls"] == 1
    assert response.json()["executed"] is False


def test_model_unavailable(monkeypatch):
    def offline(*args, **kwargs):
        raise httpx.ConnectError("Model unavailable")

    monkeypatch.setattr(
        secure_chat.httpx, "post", offline
    )

    response = submit()

    assert response.status_code == 503
    assert get_audit_events() == []
