# MicroStrategy Debt Risk & Liquidation Analysis

A quantitative risk analysis system for evaluating MicroStrategy's debt structure and liquidation scenarios.

## Overview

MicroStrategy holds significant Bitcoin positions funded through convertible debt and preferred shares. This project analyzes:

- **Liquidation Price Calculation**: At what BTC price does MSTR face margin calls or covenant violations?
- **Debt Service Coverage**: Can MSTR service its debt obligations under various BTC price scenarios?
- **Maturity Risk Timeline**: Analysis of $8.2B in debt maturities and refinancing risk
- **Stress Testing**: Scenario analysis across BTC price shocks, interest rate changes, and market conditions
- **Collateral Coverage**: BTC holdings vs debt obligations with conversion dilution modeling

## Project Structure

```
mstr-capital-analyzer/
├── data/
│   ├── raw/           # Raw HTML data from MSTR tracker
│   └── processed/     # Cleaned CSV/JSON data
├── src/
│   ├── parsers/       # HTML data extraction
│   ├── models/        # Risk calculation models
│   └── visualizations/# Dashboard and charts
├── notebooks/         # Analysis notebooks
└── dashboard/         # Streamlit dashboard
```

## Key Metrics Calculated

1. **Liquidation Price**: Minimum BTC price before covenant violations
2. **Interest Coverage Ratio**: Operating cash flow / Interest payments
3. **Debt-to-BTC Ratio**: Total debt / BTC market value
4. **Maturity Wall**: Concentration of debt maturities
5. **Conversion Trigger Price**: When bondholders convert to equity

## Tech Stack

- Python (pandas, numpy, scipy)
- BeautifulSoup4 (HTML parsing)
- Streamlit (Interactive dashboard)
- PostgreSQL (Data storage)
- Plotly (Visualizations)

## Status

🚧 Phase 1: Data parsing and extraction (In Progress)
