
import json
import os
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app, orders
from app.agent_audit import clear_audit_events


def run_comparison():
    client = TestClient(app)
    original_orders = deepcopy(orders)

    clear_audit_events()

    try:
        # Reset our simulated order before testing.
        orders["ORD-1001"]["refunded"] = False

        # Test A: Vulnerable API without authentication.
        with patch.dict(
            os.environ,
            {"ENABLE_VULNERABLE_LAB": "1"}
        ):
            vulnerable = client.post(
                "/refunds",
                json={
                    "order_id": "ORD-1001",
                    "customer_id": "CUST-001",
                    "amount_cents": 12000
                }
            )

        vulnerable_changed_state = (
            orders["ORD-1001"]["refunded"]
        )

        # Reset before evaluating the secure version.
        orders["ORD-1001"]["refunded"] = False

        secure_payload = {
            "order_id": "ORD-1001",
            "amount_cents": 12000
        }

        # Local dummy credential, never a real API key.
        with patch.dict(os.environ, {
            "LAB_TOKEN_CUST_001": "comparison-test-token"
        }):
            # Test B: Secure dispatcher, no token.
            unauthenticated = client.post(
                "/lab/secure-agent/evaluate-tool-call",
                json=secure_payload
            )

            unauthenticated_changed_state = (
                orders["ORD-1001"]["refunded"]
            )

            # Test C: Secure dispatcher with a valid token.
            authenticated = client.post(
                "/lab/secure-agent/evaluate-tool-call",
                headers={
                    "Authorization":
                    "Bearer comparison-test-token"
                },
                json=secure_payload
            )

            authenticated_changed_state = (
                orders["ORD-1001"]["refunded"]
            )

        secure_result = authenticated.json()

        return {
            "test_type": "local_api_comparison",
            "live_model_used": False,
            "real_payments_executed": False,
            "vulnerable": {
                "http_status": vulnerable.status_code,
                "simulated_refund_state_changed":
                    vulnerable_changed_state
            },
            "secure_without_auth": {
                "http_status":
                    unauthenticated.status_code,
                "simulated_refund_state_changed":
                    unauthenticated_changed_state
            },
            "secure_with_auth": {
                "http_status":
                    authenticated.status_code,
                "decision":
                    secure_result.get("decision"),
                "executed":
                    secure_result.get("executed"),
                "simulated_refund_state_changed":
                    authenticated_changed_state
            }
        }

    finally:
        # Always restore the original orders.
        orders.clear()
        orders.update(original_orders)
        clear_audit_events()


if __name__ == "__main__":
    report = run_comparison()

    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / "api-comparison.json"

    output_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8"
    )

    print(json.dumps(report, indent=2))

    assert report["vulnerable"]["http_status"] == 200
    assert report["vulnerable"][
        "simulated_refund_state_changed"
    ] is True

    assert report["secure_without_auth"][
        "http_status"
    ] == 401

    assert report["secure_with_auth"][
        "decision"
    ] == "would_allow"

    assert report["secure_with_auth"][
        "executed"
    ] is False

    print("\nAPI comparison completed successfully.")
