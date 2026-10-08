
from copy import deepcopy

import pytest

from app.main import orders
from app.offline_replay import (
    SCENARIOS,
    replay_scenario
)


@pytest.mark.parametrize(
    "scenario",
    SCENARIOS,
    ids=[case["id"] for case in SCENARIOS]
)
def test_adversarial_scenario(scenario):
    result = replay_scenario(scenario, orders)

    assert result["passed"] is True
    assert result["executed"] is False
    assert result["actual"] == scenario["expected"]
    assert result["reason"] == scenario["reason"]


def test_replay_does_not_modify_orders():
    before = deepcopy(orders)

    for scenario in SCENARIOS:
        replay_scenario(scenario, orders)

    assert orders == before
