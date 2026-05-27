# ALGOCODE — Algorithmic Trading Infrastructure

Built by a trader with 7 years of live market experience.  
This is not academic code — it's the infrastructure I use to test and validate real strategies across multiple asset classes.

My edge is not just technical: I understand the problem from the inside.  
I know what a real drawdown feels like, why friction costs destroy most strategies, and how to build systems that survive out-of-sample.

---

## What This System Does

- Downloads and normalizes high-frequency OHLCV data (ETL pipeline)
- Runs structured backtests with dynamic Stop-Loss and strict friction auditing
- Validates strategies using Walk-Forward (In-Sample / Out-of-Sample splits)
- Analyzes portfolio diversification via Pearson correlation matrices
- Visualizes return consistency and seasonality through performance heatmaps

---

## Results

### Equity Curve — Multi-Asset Portfolio (NAS100 · SPX500 · USDCAD)
*5-year backtest · Net PnL in R-multiples after all broker costs*

![Equity Curve](assets/equity_curve.png)

---

### Institutional Audit — Year-by-Year Breakdown with Friction Costs
*Full cost transparency: spread, slippage, and broker fees deducted from every trade*

![Auditoria Institucional](assets/auditoria_resultados.png)

---

### Monthly Return Heatmap — Crypto Portfolio (BTC · ETH · SOL · AVAX)
*Return consistency audit across 6 years · Values in R-multiples*

![Heatmap Crypto](assets/heatmap_crypto.png)

---

### Strategy Correlation Matrix — Crypto Portfolio
*Daily return correlation between strategies · Near-zero cross-correlation confirms diversification*

![Correlacion Crypto](assets/correlacion_crypto.png)

---

## Repository Structure

| File | Description |
|---|---|
| `binance_futures_etl.py` | Automated ETL pipeline for high-frequency OHLCV data from Binance Vision |
| `institutional_momentum_engine.py` | OOP backtesting engine with dynamic Stop-Loss and full friction cost auditing |
| `walk_forward_optimizer.py` | Generic strategy validator with In-Sample / Out-of-Sample splitting |
| `correlation_analysis.py` | Portfolio diversification analysis via Pearson correlation matrices |
| `performance_heatmaps.py` | Return consistency and seasonality visualization |

---

## Confidentiality Note

This repository contains examples of **technical structure**, **data architecture**, and **class design**.  
The exact entry/exit logic and parameters of my active strategies have been omitted or replaced with simulated data.

---

## Stack

Python · Pandas · NumPy · pandas-ta · Matplotlib · Seaborn · Binance API

---

*Developed by Augusto Danna*  
[LinkedIn](#) · [augusto@email.com](#)
