"""Tests for control-limit results."""

import config
from src.limit_monitor import check_limits


def test_single_name_over_limit_is_flagged() -> None:
    """A 25% holding against a 20% cap must be returned as a breach."""
    weights = {"JPM": 0.25, "MS": 0.75}
    sectors = {"JPM": "Financials", "MS": "Financials"}
    results = check_limits(0.0, weights, sectors, config)
    assert next(item for item in results if item["limit_name"] == "Single name: JPM")["status"] == "BREACH"
