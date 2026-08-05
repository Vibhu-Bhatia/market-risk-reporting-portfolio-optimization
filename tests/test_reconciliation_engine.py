"""Tests for deterministic reconciliation break detection."""

from src.reconciliation_engine import generate_mock_trades, reconcile


def test_all_planted_breaks_are_detected_and_classified() -> None:
    """A seeded mock book with missing, quantity and price breaks must yield all three classifications."""
    fo, rs = generate_mock_trades(12, seed=7)
    exceptions = reconcile(fo, rs)
    assert set(exceptions["exception_type"]) == {"Missing in RS", "Quantity Break", "Price Break"}
    assert len(exceptions) == 3
