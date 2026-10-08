
from copy import deepcopy

from app.main import orders
from app.security_comparison import run_comparison


def test_vulnerable_api_allows_unauthenticated_refund():
    report = run_comparison()

    assert report["vulnerable"]["http_status"] == 200

    assert report["vulnerable"][
        "simulated_refund_state_changed"
    ] is True


def test_secure_api_rejects_unauthenticated_request():
    report = run_comparison()

    assert report["secure_without_auth"][
        "http_status"
    ] == 401

    assert report["secure_without_auth"][
        "simulated_refund_state_changed"
    ] is False


def test_secure_dispatcher_never_executes():
    original_orders = deepcopy(orders)

    report = run_comparison()

    assert report["secure_with_auth"][
        "decision"
    ] == "would_allow"

    assert report["secure_with_auth"][
        "executed"
    ] is False

    assert report["secure_with_auth"][
        "simulated_refund_state_changed"
    ] is False

    assert orders == original_orders
