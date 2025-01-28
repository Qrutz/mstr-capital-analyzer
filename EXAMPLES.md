# Usage Examples

## Basic Liquidation Analysis

```python
from src.parsers.debt_parser import parse_debt_data, calculate_debt_metrics
from src.models.liquidation_calculator import LiquidationCalculator

# Load debt data
debt_df = parse_debt_data('data/raw/DEBT/data.html')
debt_metrics = calculate_debt_metrics(debt_df)

# Initialize calculator
calc = LiquidationCalculator(
    btc_holdings=447_470,
    btc_price=100_000,
    total_debt=debt_metrics['total_notional'],
    annual_interest=debt_metrics['total_notional'] * 0.00421
)

# Get liquidation price at 85% LTV
liq_price = calc.calculate_liquidation_price(target_ltv=0.85)
print(f"Liquidation price: ${liq_price:,.0f}")

# Run stress test
stress_results = calc.stress_test_scenarios()
print(stress_results)
```

## Maturity Analysis

```python
from src.models.maturity_analysis import MaturityAnalyzer

# Initialize analyzer
analyzer = MaturityAnalyzer(debt_df)

# Get maturity schedule
schedule = analyzer.get_maturity_schedule()
print(schedule)

# Check refinancing risk at $150k BTC
refinancing = analyzer.assess_refinancing_risk(btc_price_at_maturity=150_000)
print(refinancing)

# Calculate rollover requirements
rollover_5yr = analyzer.calculate_rollover_requirement(years_ahead=5)
print(f"Maturing in 5 years: ${rollover_5yr['total_maturing']:,.0f}M")
```

## Custom Scenarios

```python
# Scenario: BTC drops to $50k
btc_crash_price = 50_000

ltv = calc.calculate_ltv_ratio(btc_crash_price)
coverage = calc.calculate_collateral_coverage(btc_crash_price)

print(f"At ${btc_crash_price:,} BTC:")
print(f"  LTV: {ltv:.1%}")
print(f"  Coverage: {coverage:.2f}x")
print(f"  Status: {'Safe' if ltv < 0.5 else 'Danger'}")
```

## Margin of Safety

```python
# Conservative threshold (50% LTV)
safety_conservative = calc.calculate_margin_of_safety(target_ltv=0.50)
print(f"Conservative liquidation: ${safety_conservative['liquidation_price']:,.0f}")
print(f"Buffer: {safety_conservative['price_drop_percent']:.1f}%")

# Aggressive threshold (85% LTV)
safety_aggressive = calc.calculate_margin_of_safety(target_ltv=0.85)
print(f"Aggressive liquidation: ${safety_aggressive['liquidation_price']:,.0f}")
print(f"Buffer: {safety_aggressive['price_drop_percent']:.1f}%")
```

## Export Results

```python
import pandas as pd

# Create summary report
summary = {
    'Current LTV': f"{calc.calculate_ltv_ratio():.2%}",
    'Collateral Coverage': f"{calc.calculate_collateral_coverage():.2f}x",
    'Total Debt': f"${debt_metrics['total_notional']:,.0f}M",
    'BTC Holdings Value': f"${calc.calculate_btc_value()/1_000_000:,.0f}M",
    'Liquidation Price (85% LTV)': f"${calc.calculate_liquidation_price(0.85):,.0f}"
}

summary_df = pd.DataFrame([summary])
summary_df.to_csv('output/risk_summary.csv', index=False)
print("Summary saved to output/risk_summary.csv")
```

## Visualization Example

```python
import matplotlib.pyplot as plt
import numpy as np

# Generate LTV curve
prices = np.arange(20000, 200000, 5000)
ltvs = [calc.calculate_ltv_ratio(p) * 100 for p in prices]

plt.figure(figsize=(12, 6))
plt.plot(prices, ltvs, linewidth=2)
plt.axhline(y=50, color='yellow', linestyle='--', label='Caution')
plt.axhline(y=85, color='red', linestyle='--', label='Danger')
plt.xlabel('Bitcoin Price ($)')
plt.ylabel('LTV Ratio (%)')
plt.title('LTV Sensitivity to BTC Price')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('output/ltv_sensitivity.png', dpi=300, bbox_inches='tight')
print("Chart saved to output/ltv_sensitivity.png")
```
