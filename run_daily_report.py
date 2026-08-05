"""Thin runner that executes the daily market-risk reporting workflow."""

from datetime import date

import pandas as pd

import config
from dashboard.export_for_tableau import export_for_tableau
from src.data_pipeline import load_portfolio
from src.factor_model import load_fama_french_factors, regress_factor_exposures
from src.limit_monitor import check_limits
from src.reconciliation_engine import generate_mock_trades, reconcile
from src.report_generator import generate_risk_pack
from src.risk_engine import historical_var, monte_carlo_var, parametric_var


def main() -> None:
    """Run prices -> VaR -> controls -> reconciliation -> PDF/CSV outputs in the configured directories."""
    asset_returns, portfolio_returns = load_portfolio()
    var_summary = {
        "Historical 95%": historical_var(portfolio_returns, config.CONFIDENCE_LEVELS[0], config.PORTFOLIO_VALUE),
        "Historical 99%": historical_var(portfolio_returns, config.CONFIDENCE_LEVELS[1], config.PORTFOLIO_VALUE),
        "Parametric 95%": parametric_var(portfolio_returns, config.CONFIDENCE_LEVELS[0], config.PORTFOLIO_VALUE),
        "Parametric 99%": parametric_var(portfolio_returns, config.CONFIDENCE_LEVELS[1], config.PORTFOLIO_VALUE),
        "Monte Carlo 95%": monte_carlo_var(portfolio_returns, config.CONFIDENCE_LEVELS[0], config.PORTFOLIO_VALUE),
        "Monte Carlo 99%": monte_carlo_var(portfolio_returns, config.CONFIDENCE_LEVELS[1], config.PORTFOLIO_VALUE),
    }
    breaches = check_limits(var_summary["Parametric 99%"], config.PORTFOLIO_WEIGHTS, config.SECTOR_MAP, config)
    fo_trades, rs_trades = generate_mock_trades(config.MOCK_TRADE_COUNT)
    exceptions = reconcile(fo_trades, rs_trades)
    report_path = config.REPORTS_DIR / f"daily_risk_pack_{date.today().isoformat()}.pdf"
    generate_risk_pack(var_summary, breaches, exceptions, report_path)
    factors = load_fama_french_factors(config.RAW_DATA_DIR / "fama_french_daily.csv")
    exposures = regress_factor_exposures(portfolio_returns, factors)
    sector_exposure = pd.Series(config.PORTFOLIO_WEIGHTS).groupby(pd.Series(config.SECTOR_MAP)).sum().to_dict()
    var_history = pd.DataFrame([{"date": date.today().isoformat(), **var_summary, **exposures}])
    export_for_tableau(var_history, breaches, exceptions, sector_exposure, config.EXCEPTIONS_DIR)
    print(f"Risk pack: {report_path}")


if __name__ == "__main__":
    main()
