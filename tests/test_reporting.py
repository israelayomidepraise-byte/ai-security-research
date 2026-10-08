
from copy import deepcopy

from app.main import orders
from app.reporting import build_report, save_report


def test_report_summary():
    report = build_report(deepcopy(orders))

    assert report["summary"]["total"] == 6
    assert report["summary"]["passed"] == 6
    assert report["summary"]["failed"] == 0
    assert report["model_used"] is False
    assert report["transactions_executed"] is False


def test_report_files_created(tmp_path):
    report = build_report(deepcopy(orders))

    json_path, markdown_path = save_report(
        report,
        directory=tmp_path
    )

    assert json_path.exists()
    assert markdown_path.exists()

    content = markdown_path.read_text(
        encoding="utf-8"
    )

    assert "Offline Security Replay Report" in content
    assert "AI model used:** No" in content


def test_report_detects_failed_scenario():
    broken_scenario = {
        "id": "FAIL-TEST",
        "name": "Intentional mismatch",
        "prompt": "Test only",
        "customer_id": "CUST-001",
        "order_id": "ORD-1001",
        "amount_cents": 50000,
        "expected": "would_allow",
        "reason": "checks_passed"
    }

    report = build_report(
        deepcopy(orders),
        scenarios=[broken_scenario]
    )

    assert report["summary"]["total"] == 1
    assert report["summary"]["failed"] == 1
    assert report["results"][0]["passed"] is False
