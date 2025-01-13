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

## Installation

```bash
# Clone the repository
git clone https://github.com/Qrutz/mstr-capital-analyzer.git
cd mstr-capital-analyzer

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Quick Analysis

Run the main analysis script:

```bash
python analyze.py
```

This will output:
- Current debt metrics
- Liquidation prices at various LTV thresholds
- Stress test scenarios
- Key risk findings

### Interactive Dashboard

Launch the Streamlit dashboard:

```bash
streamlit run dashboard/app.py
```

Features:
- Real-time liquidation price calculations
- Interactive LTV ratio gauge
- Configurable BTC price scenarios
- Stress test visualizations
- Maturity timeline analysis

### Jupyter Notebook

For detailed analysis:

```bash
jupyter notebook notebooks/debt_risk_analysis.ipynb
```

## Key Findings

Based on current data (as of Jan 2025):

- **Total Debt**: $8.2B in convertible notes
- **BTC Holdings**: ~447,470 BTC
- **Current LTV**: 18.4% (very safe)
- **Liquidation Buffer**: BTC can drop 78% before reaching 85% LTV
- **Debt Maturity**: 2028-2032 (4.1 years average)
- **Refinancing Risk**: Low - bonds likely convert if BTC remains elevated

## Project Status

✅ **Phase 1**: Data parsing and extraction (Complete)
✅ **Phase 2**: Liquidation calculator & risk models (Complete)
✅ **Phase 3**: Interactive dashboard (Complete)
✅ **Phase 4**: Maturity analysis (Complete)
🚧 **Phase 5**: Database integration & API (In Progress)

## Contributing

This is a personal research project. Feel free to fork and adapt for your own analysis.

## License

MIT License - See LICENSE file for details

## Disclaimer

This project is for educational and research purposes only. Not financial advice.
