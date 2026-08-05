"""Central configuration for the Automated Market Risk Reporting System."""

from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parent
RAW_DATA_DIR: Path = PROJECT_ROOT / "data" / "raw"
MOCK_DATA_DIR: Path = PROJECT_ROOT / "data" / "mock"
REPORTS_DIR: Path = PROJECT_ROOT / "outputs" / "reports"
EXCEPTIONS_DIR: Path = PROJECT_ROOT / "outputs" / "exceptions"

TICKERS: list[str] = ["JPM", "MS", "BAC", "AAPL", "MSFT", "XOM", "JNJ", "SPY"]
PORTFOLIO_WEIGHTS: dict[str, float] = {
    "JPM": 0.16, "MS": 0.12, "BAC": 0.10, "AAPL": 0.14,
    "MSFT": 0.14, "XOM": 0.12, "JNJ": 0.10, "SPY": 0.12,
}
SECTOR_MAP: dict[str, str] = {
    "JPM": "Financials", "MS": "Financials", "BAC": "Financials",
    "AAPL": "Technology", "MSFT": "Technology", "XOM": "Energy",
    "JNJ": "Healthcare", "SPY": "Index ETF",
}
PORTFOLIO_VALUE: float = 1_000_000.0
CONFIDENCE_LEVELS: tuple[float, ...] = (0.95, 0.99)
LOOKBACK_DAYS: int = 504
CACHE_MAX_AGE_HOURS: int = 24
TRADING_DAYS_PER_YEAR: int = 252
MONTE_CARLO_SIMULATIONS: int = 10_000
BACKTEST_WINDOW: int = 252
RISK_FREE_RATE_DAILY: float = 0.0
MIN_WEIGHT: float = 0.0
MAX_WEIGHT: float = 0.30
VAR_LIMIT: float = 45_000.0
CONCENTRATION_LIMIT: float = 0.20
SECTOR_LIMIT: float = 0.40
RECONCILIATION_TOLERANCE: float = 0.01
MOCK_TRADE_COUNT: int = 40
MOCK_RANDOM_SEED: int = 42
PRICE_BREAK_AMOUNT: float = 1.0
PDF_PAGE_WIDTH: float = 612.0
PDF_PAGE_HEIGHT: float = 792.0
PDF_MARGIN: float = 42.0
PDF_LINE_HEIGHT: float = 14.0
