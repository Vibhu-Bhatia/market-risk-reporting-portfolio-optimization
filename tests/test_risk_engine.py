"""Tests for VaR calculations using fixed synthetic return observations."""

import pandas as pd

from src.risk_engine import historical_var, monte_carlo_var, optimize_max_sharpe, parametric_var


def test_99_percent_var_exceeds_95_percent_var() -> None:
    """For a return distribution with losses, higher confidence must give a weakly larger VaR."""
    returns = pd.Series([-0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03] * 20)
    for method in (historical_var, parametric_var, monte_carlo_var):
        assert method(returns, 0.99, 1_000_000) >= method(returns, 0.95, 1_000_000)


def test_optimization_returns_fully_invested_bounded_weights() -> None:
    """Maximum-Sharpe optimization must retain a fully invested portfolio within all box constraints."""
    returns = pd.DataFrame({"A": [0.02, 0.01, -0.01, 0.03], "B": [0.01, 0.0, 0.01, -0.01], "C": [0.0, 0.01, 0.0, 0.01]})
    weights = optimize_max_sharpe(returns, min_weight=0.0, max_weight=0.8)
    assert weights.sum() == pytest.approx(1.0)
    assert weights.between(0.0, 0.8).all()
