"""Fama-French factor loading calculations."""

import io
import zipfile
from pathlib import Path
from urllib.request import urlopen

import numpy as np
import pandas as pd

import config

FAMA_FRENCH_URL: str = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip"


def load_fama_french_factors(cache_path: Path) -> pd.DataFrame:
    """Download/cache Ken French daily factors and convert percentage observations to decimal returns."""
    if not cache_path.exists():
        with urlopen(FAMA_FRENCH_URL, timeout=30) as response:
            archive = zipfile.ZipFile(io.BytesIO(response.read()))
            content = archive.read(archive.namelist()[0]).decode("latin-1")
        lines = content.splitlines()
        start = next(i for i, line in enumerate(lines) if line.startswith("Date"))
        end = next(i for i, line in enumerate(lines[start + 1:], start + 1) if not line.strip() or not line[:1].isdigit())
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text("\n".join(lines[start:end]), encoding="utf-8")
    factors = pd.read_csv(cache_path, index_col=0)
    factors.index = pd.to_datetime(factors.index.astype(str), format="%Y%m%d")
    return factors.apply(pd.to_numeric, errors="coerce").dropna() / 100.0


def regress_factor_exposures(portfolio_returns: pd.Series, factors: pd.DataFrame) -> dict[str, float]:
    """OLS estimates y=alpha+b_M(Mkt-RF)+b_S(SMB)+b_H(HML)+epsilon for excess portfolio returns."""
    joined = pd.concat([portfolio_returns.rename("portfolio"), factors], axis="columns", join="inner").dropna()
    required = ["Mkt-RF", "SMB", "HML", "RF"]
    if joined.empty or not set(required).issubset(joined.columns):
        raise ValueError("Portfolio returns and all Fama-French factors are required.")
    x = np.column_stack([np.ones(len(joined)), joined[["Mkt-RF", "SMB", "HML"]].to_numpy()])
    coefficients = np.linalg.lstsq(x, (joined["portfolio"] - joined["RF"]).to_numpy(), rcond=None)[0]
    return {"alpha_daily": float(coefficients[0]), "market_beta": float(coefficients[1]), "smb_beta": float(coefficients[2]), "hml_beta": float(coefficients[3])}
