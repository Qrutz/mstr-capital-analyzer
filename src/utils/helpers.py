"""
Utility helper functions for data processing and calculations.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def calculate_annualized_return(initial_value, final_value, days):
    """
    Calculate annualized return.

    Args:
        initial_value: Starting value
        final_value: Ending value
        days: Number of days

    Returns:
        Annualized return as percentage
    """
    if initial_value <= 0 or days <= 0:
        return 0

    total_return = (final_value / initial_value) - 1
    years = days / 365.25
    annualized = ((1 + total_return) ** (1 / years)) - 1

    return annualized * 100


def calculate_sharpe_ratio(returns, risk_free_rate=0.04):
    """
    Calculate Sharpe ratio.

    Args:
        returns: Array of returns
        risk_free_rate: Annual risk-free rate

    Returns:
        Sharpe ratio
    """
    if len(returns) == 0:
        return 0

    excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
    if excess_returns.std() == 0:
        return 0

    sharpe = np.sqrt(252) * (excess_returns.mean() / excess_returns.std())
    return sharpe


def calculate_max_drawdown(values):
    """
    Calculate maximum drawdown from peak.

    Args:
        values: Array of portfolio values

    Returns:
        Maximum drawdown as percentage
    """
    if len(values) == 0:
        return 0

    cummax = np.maximum.accumulate(values)
    drawdown = (values - cummax) / cummax
    return drawdown.min() * 100


def format_currency(amount, decimals=0):
    """
    Format number as currency string.

    Args:
        amount: Number to format
        decimals: Number of decimal places

    Returns:
        Formatted string
    """
    if amount >= 1_000_000_000:
        return f"${amount/1_000_000_000:.{decimals}f}B"
    elif amount >= 1_000_000:
        return f"${amount/1_000_000:.{decimals}f}M"
    elif amount >= 1_000:
        return f"${amount/1_000:.{decimals}f}K"
    else:
        return f"${amount:.{decimals}f}"


def calculate_days_until(target_date):
    """
    Calculate days from now until target date.

    Args:
        target_date: Target datetime

    Returns:
        Number of days
    """
    if pd.isna(target_date):
        return None

    if isinstance(target_date, str):
        target_date = pd.to_datetime(target_date)

    delta = target_date - datetime.now()
    return delta.days


def calculate_yield_to_maturity(price, face_value, coupon, years_to_maturity):
    """
    Approximate yield to maturity for a bond.

    Args:
        price: Current bond price
        face_value: Face value (typically 100)
        coupon: Annual coupon rate (as percentage)
        years_to_maturity: Years until maturity

    Returns:
        Approximate YTM as percentage
    """
    if years_to_maturity <= 0:
        return 0

    annual_coupon = face_value * (coupon / 100)
    ytm = (annual_coupon + (face_value - price) / years_to_maturity) / ((face_value + price) / 2)

    return ytm * 100


def calculate_bond_duration(price, face_value, coupon, years_to_maturity):
    """
    Calculate Macaulay duration of a bond.

    Args:
        price: Current bond price
        face_value: Face value
        coupon: Annual coupon rate (as percentage)
        years_to_maturity: Years until maturity

    Returns:
        Duration in years
    """
    if years_to_maturity <= 0:
        return 0

    annual_coupon = face_value * (coupon / 100)
    ytm = calculate_yield_to_maturity(price, face_value, coupon, years_to_maturity) / 100

    if ytm == 0:
        return years_to_maturity

    # Simplified duration calculation
    pv_coupons = sum([
        (annual_coupon * t) / ((1 + ytm) ** t)
        for t in range(1, int(years_to_maturity) + 1)
    ])

    pv_face = (face_value * years_to_maturity) / ((1 + ytm) ** years_to_maturity)

    duration = (pv_coupons + pv_face) / price

    return duration
