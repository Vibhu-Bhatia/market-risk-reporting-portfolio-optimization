"""Tests for OLS factor exposure calculation."""

import numpy as np
import pandas as pd
import pytest

from src.factor_model import regress_factor_exposures


def test_market_factor_beta_is_one_for_matching_return_series() -> None:
    """When excess portfolio return equals Mkt-RF, estimated market beta should equal one."""
    index = pd.date_range("2025-01-01", periods=12, freq="B")
    market = np.linspace(-0.02, 0.02, len(index))
    factors = pd.DataFrame({"Mkt-RF": market, "SMB": np.zeros(len(index)), "HML": np.zeros(len(index)), "RF": np.zeros(len(index))}, index=index)
    result = regress_factor_exposures(pd.Series(market, index=index), factors)
    assert result["market_beta"] == pytest.approx(1.0)
