"""Tidy CSV exports for Tableau Public."""

from pathlib import Path

import pandas as pd


def export_for_tableau(var_history: pd.DataFrame, breaches: list[dict[str, object]], exceptions: pd.DataFrame, sector_exposure: dict[str, float], output_dir: Path) -> list[Path]:
    """Write one normalized CSV per Tableau view, preserving standard columns and no presentation formatting."""
    output_dir.mkdir(parents=True, exist_ok=True)
    frames = {
        "var_history.csv": var_history,
        "breach_log.csv": pd.DataFrame(breaches),
        "reconciliation_exceptions.csv": exceptions,
        "sector_exposure.csv": pd.DataFrame(sector_exposure.items(), columns=["sector", "weight"]),
    }
    paths = []
    for filename, frame in frames.items():
        path = output_dir / filename
        frame.to_csv(path, index=False)
        paths.append(path)
    return paths
