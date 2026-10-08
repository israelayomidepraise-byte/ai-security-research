
import json
from datetime import datetime, timezone
from pathlib import Path

from app.main import orders
from app.offline_replay import SCENARIOS, replay_scenario


def build_report(original_orders, scenarios=None):
    selected = SCENARIOS if scenarios is None else scenarios

    results = [
        replay_scenario(scenario, original_orders)
        for scenario in selected
    ]

    passed = sum(item["passed"] for item in results)

    return {
        "project": "AI Agent Security Testing Lab",
        "test_type": "offline_policy_replay",
        "model_used": False,
        "transactions_executed": False,
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "summary": {
            "total": len(results),
            "passed": passed,
            "failed": len(results) - passed
        },
        "results": results
    }


def save_report(report, directory="reports"):
    output = Path(directory)
    output.mkdir(parents=True, exist_ok=True)

    json_path = output / "offline-replay.json"
    markdown_path = output / "offline-replay.md"

    json_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8"
    )

    lines = [
        "# Offline Security Replay Report",
        "",
        "**Project:** AI Agent Security Testing Lab",
        "",
        "**Testing method:** Deterministic policy replay",
        "",
        "**AI model used:** No",
        "",
        "**Financial transactions executed:** No",
        "",
        f"**Generated:** {report['generated_at']}",
        "",
        "## Summary",
        "",
        f"- Total: {report['summary']['total']}",
        f"- Passed: {report['summary']['passed']}",
        f"- Failed: {report['summary']['failed']}",
        "",
        "## Scenario Results",
        "",
        "| Scenario | Expected | Actual | Result |",
        "|---|---|---|---|"
    ]

    for result in report["results"]:
        status = "PASS" if result["passed"] else "FAIL"

        lines.append(
            f"| {result['scenario_id']} "
            f"| {result['expected']} "
            f"| {result['actual']} "
            f"| {status} |"
        )

    lines.extend([
        "",
        "## Limitations",
        "",
        "These tests replay predefined proposed actions.",
        "They do not measure actual language-model behaviour.",
        "No real payments or production systems are involved."
    ])

    markdown_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )

    return json_path, markdown_path


if __name__ == "__main__":
    report = build_report(orders)
    json_file, markdown_file = save_report(report)

    print(json.dumps(report["summary"], indent=2))
    print(f"JSON report: {json_file}")
    print(f"Markdown report: {markdown_file}")

    if report["summary"]["failed"] > 0:
        raise SystemExit(1)
