"""
Liquidation and debt risk calculator for MicroStrategy.

Calculates:
- Minimum BTC price before covenant violations
- Debt service coverage ratios
- Collateral coverage ratios
- Margin of safety
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class LiquidationCalculator:
    """Calculate liquidation scenarios for MSTR's debt structure."""

    def __init__(self, btc_holdings, btc_price, total_debt, annual_interest):
        """
        Initialize calculator with current positions.

        Args:
            btc_holdings: Number of BTC held
            btc_price: Current BTC price
            total_debt: Total debt notional in millions
            annual_interest: Annual interest payments in millions
        """
        self.btc_holdings = btc_holdings
        self.btc_price = btc_price
        self.total_debt = total_debt * 1_000_000  # Convert to actual dollars
        self.annual_interest = annual_interest * 1_000_000

    def calculate_btc_value(self, btc_price=None):
        """Calculate total BTC holdings value at given price."""
        price = btc_price or self.btc_price
        return self.btc_holdings * price

    def calculate_ltv_ratio(self, btc_price=None):
        """
        Calculate Loan-to-Value ratio.

        LTV = Total Debt / BTC Market Value

        Lower is better. High LTV means dangerous leverage.
        """
        btc_value = self.calculate_btc_value(btc_price)
        return self.total_debt / btc_value

    def calculate_collateral_coverage(self, btc_price=None):
        """
        Calculate collateral coverage ratio.

        Coverage = BTC Market Value / Total Debt

        >1.0 means overcollateralized
        <1.0 means undercollateralized (danger zone)
        """
        return 1 / self.calculate_ltv_ratio(btc_price)

    def calculate_liquidation_price(self, target_ltv=0.85):
        """
        Calculate BTC price at which LTV reaches dangerous threshold.

        Typical covenant: LTV < 85% (0.85)
        Conservative: LTV < 65% (0.65)

        Args:
            target_ltv: Maximum LTV before liquidation risk

        Returns:
            BTC price at target LTV
        """
        # LTV = Debt / (BTC_holdings * BTC_price)
        # Solving for BTC_price:
        # BTC_price = Debt / (BTC_holdings * LTV)
        liquidation_price = self.total_debt / (self.btc_holdings * target_ltv)
        return liquidation_price

    def calculate_margin_of_safety(self, target_ltv=0.85):
        """
        Calculate margin of safety - how far BTC can drop before danger.

        Returns:
            dict with absolute price drop and percentage drop
        """
        liq_price = self.calculate_liquidation_price(target_ltv)
        price_drop = self.btc_price - liq_price
        pct_drop = (price_drop / self.btc_price) * 100

        return {
            'current_price': self.btc_price,
            'liquidation_price': liq_price,
            'price_drop_dollars': price_drop,
            'price_drop_percent': pct_drop,
            'current_ltv': self.calculate_ltv_ratio(),
            'target_ltv': target_ltv
        }

    def calculate_interest_coverage(self, operating_income_annual=0):
        """
        Calculate interest coverage ratio.

        Coverage = Operating Income / Interest Expense

        >1.0 means they can pay interest from operations
        <1.0 means they need to sell BTC or refinance
        """
        if self.annual_interest == 0:
            return float('inf')
        return operating_income_annual * 1_000_000 / self.annual_interest

    def stress_test_scenarios(self):
        """
        Run stress tests across various BTC price scenarios.

        Returns:
            DataFrame with scenarios and metrics
        """
        current_price = self.btc_price
        scenarios = [
            ('Current', current_price),
            ('-20%', current_price * 0.8),
            ('-30%', current_price * 0.7),
            ('-40%', current_price * 0.6),
            ('-50%', current_price * 0.5),
            ('-60%', current_price * 0.4),
            ('-70%', current_price * 0.3),
        ]

        results = []
        for name, price in scenarios:
            ltv = self.calculate_ltv_ratio(price)
            collateral_cov = self.calculate_collateral_coverage(price)
            btc_value = self.calculate_btc_value(price)

            results.append({
                'Scenario': name,
                'BTC Price': f'${price:,.0f}',
                'BTC Holdings Value (M)': f'${btc_value/1_000_000:,.0f}',
                'LTV Ratio': f'{ltv:.2%}',
                'Collateral Coverage': f'{collateral_cov:.2f}x',
                'Status': self._get_status(ltv)
            })

        return pd.DataFrame(results)

    def _get_status(self, ltv):
        """Determine risk status based on LTV."""
        if ltv < 0.50:
            return '🟢 Safe'
        elif ltv < 0.65:
            return '🟡 Caution'
        elif ltv < 0.85:
            return '🟠 Warning'
        else:
            return '🔴 Danger'


if __name__ == "__main__":
    # Example usage with approximate MSTR data
    calc = LiquidationCalculator(
        btc_holdings=447_470,  # Approximate BTC holdings
        btc_price=100_000,  # Current BTC price
        total_debt=8_214,  # Total debt in millions
        annual_interest=8_214 * 0.00421  # Weighted avg coupon
    )

    print("=== MSTR Liquidation Analysis ===\n")

    print("Current Metrics:")
    print(f"BTC Holdings Value: ${calc.calculate_btc_value()/1_000_000:,.0f}M")
    print(f"Total Debt: ${calc.total_debt/1_000_000:,.0f}M")
    print(f"LTV Ratio: {calc.calculate_ltv_ratio():.2%}")
    print(f"Collateral Coverage: {calc.calculate_collateral_coverage():.2f}x")

    print("\n=== Margin of Safety ===")
    safety = calc.calculate_margin_of_safety(target_ltv=0.85)
    print(f"Current BTC Price: ${safety['current_price']:,.0f}")
    print(f"Liquidation Price (85% LTV): ${safety['liquidation_price']:,.0f}")
    print(f"Buffer: ${safety['price_drop_dollars']:,.0f} ({safety['price_drop_percent']:.1f}%)")

    print("\n=== Stress Test Scenarios ===")
    print(calc.stress_test_scenarios().to_string(index=False))
