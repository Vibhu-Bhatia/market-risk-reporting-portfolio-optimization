"""Reproducible front-office versus risk-system trade reconciliation."""

from collections.abc import Sequence

import numpy as np
import pandas as pd

import config


def generate_mock_trades(n_trades: int, break_types: Sequence[str] = ("missing", "quantity", "price"), seed: int = config.MOCK_RANDOM_SEED) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generate matching trade books then deliberately plant one deterministic break of each requested type."""
    if n_trades < len(break_types) + 1:
        raise ValueError("n_trades must accommodate each configured planted break.")
    valid = {"missing", "quantity", "price"}
    if not set(break_types).issubset(valid):
        raise ValueError("Unsupported break type.")
    rng = np.random.default_rng(seed)
    trade_ids = [f"T{number:04d}" for number in range(1, n_trades + 1)]
    fo = pd.DataFrame({"trade_id": trade_ids, "ticker": rng.choice(config.TICKERS, n_trades), "quantity": rng.integers(10, 500, n_trades), "price": rng.uniform(50, 500, n_trades).round(2), "trade_date": pd.Timestamp("2026-01-02")})
    rs = fo.copy()
    cursor = 0
    if "missing" in break_types:
        rs = rs[rs["trade_id"] != trade_ids[cursor]].copy()
        cursor += 1
    if "quantity" in break_types:
        rs.loc[rs["trade_id"] == trade_ids[cursor], "quantity"] += 1
        cursor += 1
    if "price" in break_types:
        rs.loc[rs["trade_id"] == trade_ids[cursor], "price"] += config.PRICE_BREAK_AMOUNT
    return fo, rs


def reconcile(fo_df: pd.DataFrame, rs_df: pd.DataFrame, tolerance: float = config.RECONCILIATION_TOLERANCE) -> pd.DataFrame:
    """Outer-join trade IDs, classifying absent records then quantity/price differences above tolerance."""
    merged = fo_df.merge(rs_df, on="trade_id", how="outer", suffixes=("_fo", "_rs"), indicator=True)
    rows: list[dict[str, object]] = []
    for _, row in merged.iterrows():
        if row["_merge"] == "left_only":
            kind = "Missing in RS"
        elif row["_merge"] == "right_only":
            kind = "Missing in FO"
        elif abs(float(row["quantity_fo"]) - float(row["quantity_rs"])) > tolerance:
            kind = "Quantity Break"
        elif abs(float(row["price_fo"]) - float(row["price_rs"])) > tolerance:
            kind = "Price Break"
        else:
            continue
        rows.append({"trade_id": row["trade_id"], "exception_type": kind, "age_days": 0, "quantity_fo": row.get("quantity_fo"), "quantity_rs": row.get("quantity_rs"), "price_fo": row.get("price_fo"), "price_rs": row.get("price_rs")})
    return pd.DataFrame(rows, columns=["trade_id", "exception_type", "age_days", "quantity_fo", "quantity_rs", "price_fo", "price_rs"])
