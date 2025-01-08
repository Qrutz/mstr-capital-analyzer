"""
Chart generation utilities for debt risk visualizations.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


def create_ltv_heatmap(calc, btc_price_range, debt_range):
    """
    Create heatmap showing LTV across different BTC prices and debt levels.

    Args:
        calc: LiquidationCalculator instance
        btc_price_range: Range of BTC prices to test
        debt_range: Range of debt levels (multipliers of current debt)

    Returns:
        Plotly figure
    """
    btc_prices = np.linspace(btc_price_range[0], btc_price_range[1], 20)
    debt_multipliers = np.linspace(debt_range[0], debt_range[1], 15)

    ltv_matrix = np.zeros((len(debt_multipliers), len(btc_prices)))

    original_debt = calc.total_debt

    for i, debt_mult in enumerate(debt_multipliers):
        for j, btc_price in enumerate(btc_prices):
            calc.total_debt = original_debt * debt_mult
            ltv_matrix[i, j] = calc.calculate_ltv_ratio(btc_price) * 100

    calc.total_debt = original_debt  # Reset

    fig = go.Figure(data=go.Heatmap(
        z=ltv_matrix,
        x=btc_prices,
        y=debt_multipliers,
        colorscale='RdYlGn_r',
        hovertemplate='BTC: $%{x:,.0f}<br>' +
                      'Debt Mult: %{y:.2f}x<br>' +
                      'LTV: %{z:.1f}%<br>' +
                      '<extra></extra>',
        colorbar=dict(title="LTV %")
    ))

    fig.update_layout(
        title="LTV Sensitivity: BTC Price vs Debt Level",
        xaxis_title="Bitcoin Price ($)",
        yaxis_title="Debt Level (Multiplier)",
        height=500
    )

    return fig


def create_waterfall_chart(debt_df):
    """
    Create waterfall chart showing debt structure.

    Args:
        debt_df: DataFrame with debt information

    Returns:
        Plotly figure
    """
    bonds = debt_df['Name'].tolist()
    amounts = debt_df['Notional ($M)'].tolist()

    fig = go.Figure(go.Waterfall(
        name="Debt",
        orientation="v",
        measure=["relative"] * len(bonds) + ["total"],
        x=bonds + ["Total"],
        y=amounts + [sum(amounts)],
        text=[f"${amt:,.0f}M" for amt in amounts] + [f"${sum(amounts):,.0f}M"],
        textposition="outside",
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))

    fig.update_layout(
        title="Convertible Debt Structure",
        yaxis_title="Notional Amount ($M)",
        height=500,
        showlegend=False
    )

    return fig


def create_risk_gauge(ltv_current, ltv_threshold):
    """
    Create gauge chart for risk level.

    Args:
        ltv_current: Current LTV ratio (0-1)
        ltv_threshold: Danger threshold (0-1)

    Returns:
        Plotly figure
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=ltv_current * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Risk Level (LTV %)"},
        delta={'reference': ltv_threshold * 100, 'suffix': "% from danger"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgreen"},
                {'range': [50, 65], 'color': "yellow"},
                {'range': [65, 85], 'color': "orange"},
                {'range': [85, 100], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': ltv_threshold * 100
            }
        }
    ))

    fig.update_layout(height=350)
    return fig


def create_scenario_comparison(scenarios_data):
    """
    Create bar chart comparing different scenarios.

    Args:
        scenarios_data: DataFrame with scenario analysis

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=scenarios_data['Scenario'],
        y=scenarios_data['LTV Ratio'].str.rstrip('%').astype(float),
        marker_color=['green' if 'Safe' in status else 'yellow' if 'Caution' in status
                      else 'orange' if 'Warning' in status else 'red'
                      for status in scenarios_data['Status']],
        text=scenarios_data['LTV Ratio'],
        textposition='auto',
    ))

    fig.add_hline(y=50, line_dash="dash", line_color="yellow",
                  annotation_text="Caution Zone")
    fig.add_hline(y=85, line_dash="dash", line_color="red",
                  annotation_text="Danger Zone")

    fig.update_layout(
        title="Stress Test: LTV Across Scenarios",
        xaxis_title="BTC Price Scenario",
        yaxis_title="LTV Ratio (%)",
        height=400,
        showlegend=False
    )

    return fig
