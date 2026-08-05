"""Market-data retrieval and return-series construction."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

import config


def cache_is_fresh(path: Path, max_age_hours: int) -> bool:
    """Return whether cache age is at most `max_age_hours` based on UTC modification time."""
    if not path.exists():
        return False
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return datetime.now(timezone.utc) - modified <= timedelta(hours=max_age_hours)


def fetch_prices(tickers: list[str], lookback_days: int, cache_path: Path) -> pd.DataFrame:
    """Load adjusted closes, downloading only when cache is absent/stale; rows are trading dates."""
    if cache_is_fresh(cache_path, config.CACHE_MAX_AGE_HOURS):
        return pd.read_csv(cache_path, index_col=0, parse_dates=True)
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=lookback_days * 2)
    raw = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True, progress=False)
    prices = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw[["Close"]]
    if isinstance(prices, pd.Series):
        prices = prices.to_frame(name=tickers[0])
    prices = prices.rename_axis(index="date").dropna(how="all").tail(lookback_days)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    prices.to_csv(cache_path)
    return prices


def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Compute simple daily returns r_t = P_t / P_(t-1) - 1, dropping the undefined first row."""
    return prices.pct_change(fill_method=None).dropna(how="any")


def build_portfolio_returns(asset_returns: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    """Compute portfolio return r_p,t = sum_i(w_i * r_i,t) after validating fully specified weights."""
    aligned = pd.Series(weights, dtype=float).reindex(asset_returns.columns)
    if aligned.isna().any() or not pd.Series(weights).index.isin(asset_returns.columns).all():
        raise ValueError("Weights and asset-return columns must contain exactly the same tickers.")
    if not abs(aligned.sum() - 1.0) < 1e-9:
        raise ValueError("Portfolio weights must sum to 1.0.")
    return asset_returns.mul(aligned, axis="columns").sum(axis="columns").rename("portfolio_return")


def load_portfolio() -> tuple[pd.DataFrame, pd.Series]:
    """Return cached/downloaded daily asset returns and their configured weighted portfolio return."""
    prices = fetch_prices(config.TICKERS, config.LOOKBACK_DAYS, config.RAW_DATA_DIR / "prices.csv")
    returns = compute_returns(prices).loc[:, config.TICKERS]
    return returns, build_portfolio_returns(returns, config.PORTFOLIO_WEIGHTS)
