
import httpx
import pytest

from fastapi.testclient import TestClient
from app.main import app, orders
from app.agent_audit import (
    clear_audit_events,
    get_audit_events
)
import app.local_agent as local_agent

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_lab():
    clear_audit_events()
    original = orders["ORD-1001"]["refunded"]
    orders["ORD-1001"]["refunded"] = False

    yield

    orders["ORD-1001"]["refunded"] = original
    clear_audit_events()


def mock_ollama(monkeypatch, message):
    def fake_post(url, json, timeout):
        return httpx.Response(
            200,
            json={"message": message},
            request=httpx.Request("POST", url)
        )

    monkeypatch.setattr(
        local_agent.httpx, "post", fake_post
    )


def test_normal_message_without_refund(monkeypatch):
    mock_ollama(monkeypatch, {
        "content": "Hello! How can I help?",
        "tool_calls": []
    })

    response = client.post(
        "/lab/agent/chat",
        json={"message": "Hello"}
    )

    assert response.status_code == 200
    assert response.json()["refund_proposals"] == []
    assert len(get_audit_events()) == 0


def test_refund_proposal_is_not_executed(monkeypatch):
    mock_ollama(monkeypatch, {
        "content": "",
        "tool_calls": [{
            "function": {
                "name": "propose_refund",
                "arguments": {
                    "order_id": "ORD-1001",
                    "amount_cents": 50000
                }
            }
        }]
    })

    response = client.post(
        "/lab/agent/chat",
        json={"message": "Please refund my order"}
    )

    assert response.status_code == 200
    assert response.json()["executed"] is False
    assert len(response.json()["refund_proposals"]) == 1
    assert len(get_audit_events()) == 1
    assert orders["ORD-1001"]["refunded"] is False


def test_invalid_tool_arguments_rejected(monkeypatch):
    mock_ollama(monkeypatch, {
        "content": "",
        "tool_calls": [{
            "function": {
                "name": "propose_refund",
                "arguments": {
                    "order_id": "ORD-1001",
                    "amount_cents": -500
                }
            }
        }]
    })

    response = client.post(
        "/lab/agent/chat",
        json={"message": "Refund request"}
    )

    assert response.status_code == 200
    assert response.json()["rejected_proposals"] == 1
    assert len(get_audit_events()) == 0


def test_ollama_unavailable(monkeypatch):
    def unavailable(*args, **kwargs):
        raise httpx.ConnectError(
            "Simulated connection failure"
        )

    monkeypatch.setattr(
        local_agent.httpx, "post", unavailable
    )

    response = client.post(
        "/lab/agent/chat",
        json={"message": "Hello"}
    )

    assert response.status_code == 503
    assert len(get_audit_events()) == 0
