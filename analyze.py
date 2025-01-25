"""
Main analysis script for MSTR debt risk assessment.

Runs all parsers and calculates key risk metrics.
"""

from src.parsers.debt_parser import parse_debt_data, calculate_debt_metrics
from src.models.liquidation_calculator import LiquidationCalculator
import pandas as pd


def main():
    print("=" * 60)
    print("MICROSTRATEGY DEBT RISK ANALYSIS")
    print("=" * 60)
    print()

    # Parse debt data
    print("Loading debt data...")
    debt_df = parse_debt_data('data/raw/DEBT/data.html')
    debt_metrics = calculate_debt_metrics(debt_df)

    print(f"\nTotal Debt: ${debt_metrics['total_notional']:,.0f}M")
    print(f"Weighted Avg Coupon: {debt_metrics['weighted_avg_coupon']:.3f}%")
    print(f"Number of Bond Issues: {debt_metrics['num_bonds']}")
    print(f"Maturity Range: {debt_metrics['nearest_maturity'].strftime('%Y-%m-%d')} to {debt_metrics['furthest_maturity'].strftime('%Y-%m-%d')}")

    # Default parameters (update these based on latest data)
    btc_holdings = 447_470  # Update from latest MSTR filings
    btc_price = 100_000  # Update to current BTC price
    total_debt = debt_metrics['total_notional']
    annual_interest = total_debt * (debt_metrics['weighted_avg_coupon'] / 100)

    print(f"\n{'=' * 60}")
    print("LIQUIDATION RISK ANALYSIS")
    print('=' * 60)

    calc = LiquidationCalculator(
        btc_holdings=btc_holdings,
        btc_price=btc_price,
        total_debt=total_debt,
        annual_interest=annual_interest
    )

    print(f"\nCurrent Metrics:")
    print(f"  BTC Holdings: {btc_holdings:,} BTC")
    print(f"  BTC Price: ${btc_price:,}")
    print(f"  BTC Value: ${calc.calculate_btc_value()/1_000_000:,.0f}M")
    print(f"  Total Debt: ${total_debt:,.0f}M")
    print(f"  LTV Ratio: {calc.calculate_ltv_ratio():.2%}")
    print(f"  Collateral Coverage: {calc.calculate_collateral_coverage():.2f}x")

    print(f"\n{'Margin of Safety Analysis':^60}")
    print("-" * 60)

    for target_ltv in [0.50, 0.65, 0.85]:
        safety = calc.calculate_margin_of_safety(target_ltv=target_ltv)
        print(f"\nAt {target_ltv:.0%} LTV threshold:")
        print(f"  Liquidation Price: ${safety['liquidation_price']:,.0f}")
        print(f"  Price Buffer: ${safety['price_drop_dollars']:,.0f} ({safety['price_drop_percent']:.1f}%)")

    print(f"\n\n{'Stress Test Scenarios':^60}")
    print("=" * 60)
    stress_df = calc.stress_test_scenarios()
    print(stress_df.to_string(index=False))

    print("\n\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)

    current_ltv = calc.calculate_ltv_ratio()
    liq_price_85 = calc.calculate_liquidation_price(0.85)
    drop_pct = ((btc_price - liq_price_85) / btc_price) * 100

    print(f"\n✓ Current LTV: {current_ltv:.1%} - {'SAFE' if current_ltv < 0.50 else 'ELEVATED'}")
    print(f"✓ Bitcoin would need to drop {drop_pct:.0f}% before reaching 85% LTV")
    print(f"✓ Liquidation risk at ${liq_price_85:,.0f} BTC price")
    print(f"✓ Current collateral coverage: {calc.calculate_collateral_coverage():.1f}x")

    print("\n")


if __name__ == "__main__":
    main()
