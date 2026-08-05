"""Tests for pure market-data transforms."""

import pandas as pd
import pytest

from src.data_pipeline import build_portfolio_returns, compute_returns


def test_simple_returns_and_weighted_portfolio() -> None:
    """Verify r=P_t/P_t-1-1 and a 60/40 weighted return have known values."""
    prices = pd.DataFrame({"A": [100.0, 110.0], "B": [100.0, 105.0]})
    returns = compute_returns(prices)
    portfolio = build_portfolio_returns(returns, {"A": 0.6, "B": 0.4})
    assert returns.iloc[0].tolist() == pytest.approx([0.10, 0.05])
    assert portfolio.iloc[0] == pytest.approx(0.08)
