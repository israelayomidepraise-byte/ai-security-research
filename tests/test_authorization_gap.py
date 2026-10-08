
from fastapi.testclient import TestClient
from app.main import app, orders

client = TestClient(app)



def test_refund_possible_without_authentication(monkeypatch):
    monkeypatch.setenv("ENABLE_VULNERABLE_LAB", "1")

    # This is a deliberately vulnerable lab.
    # No login session or authentication token is provided.

    order = orders["ORD-1001"]
    original_state = order["refunded"]
    order["refunded"] = False

    try:
        response = client.post(
            "/refunds",
            json={
                "order_id": "ORD-1001",
                "customer_id": "CUST-001",
                "amount_cents": 12000
            }
        )

        # A 200 response demonstrates the missing
        # authentication requirement in this lab.
        assert response.status_code == 200
        assert response.json()["status"] == "simulated_refund_approved"

    finally:
        order["refunded"] = original_state
