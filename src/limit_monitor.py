"""Portfolio risk-limit control checks."""

from collections.abc import Mapping
from typing import Any


def _result(name: str, current: float, limit: float) -> dict[str, float | str]:
    """Create a breach object using the control rule breach iff current value exceeds its limit."""
    return {"limit_name": name, "current_value": float(current), "limit_value": float(limit), "status": "BREACH" if current > limit else "PASS"}


def check_limits(var_estimate: float, portfolio_weights: Mapping[str, float], sector_map: Mapping[str, str], settings: Any) -> list[dict[str, float | str]]:
    """Test VaR, single-name weights and aggregated sector weights against configured upper limits."""
    results = [_result("VaR", var_estimate, settings.VAR_LIMIT)]
    for ticker, weight in portfolio_weights.items():
        results.append(_result(f"Single name: {ticker}", weight, settings.CONCENTRATION_LIMIT))
    sector_weights: dict[str, float] = {}
    for ticker, weight in portfolio_weights.items():
        sector = sector_map[ticker]
        sector_weights[sector] = sector_weights.get(sector, 0.0) + weight
    results.extend(_result(f"Sector: {sector}", weight, settings.SECTOR_LIMIT) for sector, weight in sector_weights.items())
    return results
