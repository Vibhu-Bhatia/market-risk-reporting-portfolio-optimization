# Automated Market Risk Reporting & Portfolio Optimization

A finance-analytics portfolio project that simulates an institutional daily risk workflow: live market-data ingestion, portfolio optimization-ready analytics, Value at Risk (VaR), factor exposure, limit controls, trade reconciliation, a management PDF risk pack, and Tableau-ready CSV exports.

## Why this project

It demonstrates the analytical, control, and reporting skills relevant to financial analyst, business analytics, corporate finance, investment banking, market-risk, and risk-control roles. The deliverable is designed for a senior-management audience, not just a model notebook.

## Capabilities

- Constrained maximum-Sharpe portfolio optimization, plus historical, parametric, and Monte Carlo VaR at 95% and 99% confidence.
- Fama-French three-factor regression for portfolio market, size, and value exposures.
- VaR, single-name concentration, and sector-concentration controls.
- Deterministic front-office vs risk-system reconciliation breaks.
- One-page PDF daily risk pack and clean Tableau Public CSV extracts.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest tests/
python run_daily_report.py
```

The first daily run downloads adjusted prices from Yahoo Finance and daily Fama-French factors from the Ken French Data Library. Both sources cache locally under `data/raw/`; prices refresh only when their cache is older than one day.

## Architecture

```text
Yahoo Finance + Ken French factors
              |
        data_pipeline
              |
      risk_engine + factor_model
              |
   limit_monitor + reconciliation_engine
              |
 report_generator (PDF) + Tableau CSV export
```

## Risk methodology

Historical VaR uses the empirical lower-tail portfolio-return quantile. Parametric VaR assumes normally distributed returns and estimates the loss quantile from historical mean and volatility. Monte Carlo VaR simulates normal portfolio returns from the same parameters and measures their lower-tail loss quantile.

## Controls

The limit monitor identifies breaches of VaR, individual position concentration, and sector concentration limits. Reconciliation deliberately plants missing, quantity, and price differences, then detects and labels every exception reproducibly.

## Outputs

- `outputs/reports/daily_risk_pack_<date>.pdf`
- `outputs/exceptions/var_history.csv`
- `outputs/exceptions/breach_log.csv`
- `outputs/exceptions/reconciliation_exceptions.csv`
- `outputs/exceptions/sector_exposure.csv`

## Next steps

Add constrained mean-variance / Black-Litterman optimization with PyPortfolioOpt, options positions with Black-Scholes Greeks, and screenshots of the Tableau Public dashboard.
