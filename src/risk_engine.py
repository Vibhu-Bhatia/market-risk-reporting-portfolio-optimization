"""Value-at-Risk estimation and backtesting."""

from collections.abc import Callable

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm

import config


def _validate_inputs(returns: pd.Series, confidence: float, portfolio_value: float) -> None:
    """Validate finite return observations, a confidence in (0,1), and positive portfolio value."""
    if returns.dropna().empty or not 0 < confidence < 1 or portfolio_value <= 0:
        raise ValueError("Returns, confidence, and portfolio value must be valid.")


def historical_var(returns: pd.Series, confidence: float, portfolio_value: float) -> float:
    """Calculate VaR = -quantile_{1-c}(r_p) * V from empirical return distribution."""
    _validate_inputs(returns, confidence, portfolio_value)
    return float(max(0.0, -returns.dropna().quantile(1 - confidence) * portfolio_value))


def parametric_var(returns: pd.Series, confidence: float, portfolio_value: float) -> float:
    """Calculate Gaussian VaR = max(0, (z_c*sigma - mu) * V) from sample mean and standard deviation."""
    _validate_inputs(returns, confidence, portfolio_value)
    clean = returns.dropna()
    return float(max(0.0, (norm.ppf(confidence) * clean.std(ddof=1) - clean.mean()) * portfolio_value))


def monte_carlo_var(returns: pd.Series, confidence: float, portfolio_value: float, simulations: int = config.MONTE_CARLO_SIMULATIONS, seed: int = config.MOCK_RANDOM_SEED) -> float:
    """Calculate VaR from normal simulations r~N(mu,sigma), using the empirical loss quantile."""
    _validate_inputs(returns, confidence, portfolio_value)
    if simulations <= 0:
        raise ValueError("simulations must be positive.")
    clean = returns.dropna()
    simulated = np.random.default_rng(seed).normal(clean.mean(), clean.std(ddof=1), simulations)
    return float(max(0.0, -np.quantile(simulated, 1 - confidence) * portfolio_value))


def optimize_max_sharpe(asset_returns: pd.DataFrame, risk_free_rate_daily: float = config.RISK_FREE_RATE_DAILY, min_weight: float = config.MIN_WEIGHT, max_weight: float = config.MAX_WEIGHT) -> pd.Series:
    """Solve max_w (mu'w-r_f)/sqrt(w'Sigmaw), subject to sum(w)=1 and configured box constraints."""
    if asset_returns.empty or min_weight < 0 or max_weight <= 0 or min_weight > max_weight:
        raise ValueError("Asset returns and optimization bounds must be valid.")
    count = asset_returns.shape[1]
    if count * min_weight > 1 or count * max_weight < 1:
        raise ValueError("Weight bounds cannot satisfy the fully invested constraint.")
    mean = asset_returns.mean().to_numpy()
    covariance = asset_returns.cov().to_numpy()

    def negative_sharpe(weights: np.ndarray) -> float:
        """Return the negative daily Sharpe ratio so SLSQP maximization is expressed as minimization."""
        volatility = float(np.sqrt(weights @ covariance @ weights))
        return float(-((weights @ mean) - risk_free_rate_daily) / volatility) if volatility > 0 else 0.0

    result = minimize(negative_sharpe, np.repeat(1 / count, count), method="SLSQP", bounds=[(min_weight, max_weight)] * count, constraints={"type": "eq", "fun": lambda weights: weights.sum() - 1})
    if not result.success:
        raise RuntimeError(f"Optimization failed: {result.message}")
    return pd.Series(result.x, index=asset_returns.columns, name="optimized_weight")


def backtest_var(returns: pd.Series, confidence: float, portfolio_value: float, method: Callable[[pd.Series, float, float], float], window: int = config.BACKTEST_WINDOW) -> dict[str, float]:
    """Count losses exceeding rolling one-day VaR and compare them with expected breaches n*(1-c)."""
    clean = returns.dropna()
    if len(clean) <= window:
        raise ValueError("Returns must exceed the backtest window.")
    breaches = 0
    for end in range(window, len(clean)):
        estimate = method(clean.iloc[end - window:end], confidence, portfolio_value)
        breaches += int(-clean.iloc[end] * portfolio_value > estimate)
    observations = len(clean) - window
    return {"observations": float(observations), "breaches": float(breaches), "expected_breaches": observations * (1 - confidence)}
