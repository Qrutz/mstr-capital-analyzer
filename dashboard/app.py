"""
Streamlit dashboard for MSTR debt risk analysis.
Interactive visualization of liquidation scenarios and stress tests.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.parsers.debt_parser import parse_debt_data, calculate_debt_metrics
from src.models.liquidation_calculator import LiquidationCalculator


st.set_page_config(
    page_title="MSTR Debt Risk Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data
def load_debt_data():
    """Load and cache debt data."""
    df = parse_debt_data('data/raw/DEBT/data.html')
    metrics = calculate_debt_metrics(df)
    return df, metrics


def main():
    st.markdown('<h1 class="main-header">📊 MicroStrategy Debt Risk Analyzer</h1>',
                unsafe_allow_html=True)

    st.markdown("---")

    # Load data
    debt_df, debt_metrics = load_debt_data()

    # Sidebar inputs
    st.sidebar.header("⚙️ Scenario Parameters")

    btc_price = st.sidebar.number_input(
        "Bitcoin Price ($)",
        min_value=10000,
        max_value=500000,
        value=100000,
        step=5000,
        help="Current or hypothetical BTC price"
    )

    btc_holdings = st.sidebar.number_input(
        "BTC Holdings",
        min_value=100000,
        max_value=1000000,
        value=447470,
        step=1000,
        help="Number of BTC held by MSTR"
    )

    ltv_threshold = st.sidebar.slider(
        "LTV Danger Threshold (%)",
        min_value=50,
        max_value=95,
        value=85,
        step=5,
        help="LTV ratio that triggers liquidation concern"
    ) / 100

    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "This tool analyzes MicroStrategy's debt structure and calculates "
        "liquidation risk based on Bitcoin price movements."
    )

    # Initialize calculator
    calc = LiquidationCalculator(
        btc_holdings=btc_holdings,
        btc_price=btc_price,
        total_debt=debt_metrics['total_notional'],
        annual_interest=debt_metrics['total_notional'] * (debt_metrics['weighted_avg_coupon'] / 100)
    )

    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "BTC Holdings Value",
            f"${calc.calculate_btc_value()/1_000_000:,.0f}M",
            help="Total value of BTC at current price"
        )

    with col2:
        st.metric(
            "Total Debt",
            f"${debt_metrics['total_notional']:,.0f}M",
            help="Total notional value of convertible bonds"
        )

    with col3:
        ltv = calc.calculate_ltv_ratio()
        st.metric(
            "LTV Ratio",
            f"{ltv:.1%}",
            delta=f"{ltv - ltv_threshold:.1%} from danger",
            delta_color="inverse",
            help="Loan-to-Value ratio (lower is safer)"
        )

    with col4:
        coverage = calc.calculate_collateral_coverage()
        st.metric(
            "Collateral Coverage",
            f"{coverage:.2f}x",
            help="BTC value / Total debt (higher is safer)"
        )

    st.markdown("---")

    # Liquidation Analysis Section
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🎯 Liquidation Price Analysis")

        safety = calc.calculate_margin_of_safety(target_ltv=ltv_threshold)

        st.metric(
            "Liquidation Price",
            f"${safety['liquidation_price']:,.0f}",
            help=f"BTC price at {ltv_threshold:.0%} LTV threshold"
        )

        st.metric(
            "Price Buffer",
            f"${safety['price_drop_dollars']:,.0f}",
            delta=f"{safety['price_drop_percent']:.1f}% drop allowed",
            help="How much BTC can drop before danger zone"
        )

        # Create gauge chart for current LTV
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=ltv * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Current LTV %"},
            delta={'reference': ltv_threshold * 100, 'suffix': "% from threshold"},
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

        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        st.subheader("📉 Stress Test Scenarios")

        stress_df = calc.stress_test_scenarios()

        st.dataframe(
            stress_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )

    st.markdown("---")

    # Price vs LTV Chart
    st.subheader("📈 Bitcoin Price vs LTV Ratio")

    # Generate data for chart
    price_range = range(20000, 150000, 5000)
    ltv_values = [calc.calculate_ltv_ratio(p) * 100 for p in price_range]

    fig_line = go.Figure()

    fig_line.add_trace(go.Scatter(
        x=list(price_range),
        y=ltv_values,
        mode='lines',
        name='LTV Ratio',
        line=dict(color='blue', width=3)
    ))

    # Add threshold lines
    fig_line.add_hline(
        y=ltv_threshold * 100,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Danger Threshold ({ltv_threshold:.0%})"
    )

    fig_line.add_hline(
        y=50,
        line_dash="dot",
        line_color="orange",
        annotation_text="Caution Zone (50%)"
    )

    # Add current price marker
    fig_line.add_vline(
        x=btc_price,
        line_dash="dash",
        line_color="green",
        annotation_text=f"Current Price (${btc_price:,})"
    )

    fig_line.update_layout(
        xaxis_title="Bitcoin Price ($)",
        yaxis_title="LTV Ratio (%)",
        hovermode='x unified',
        height=400
    )

    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")

    # Debt Details
    st.subheader("💳 Convertible Debt Details")

    # Format the debt dataframe for display
    display_df = debt_df.copy()
    display_df['Issue Date'] = pd.to_datetime(display_df['Issue Date']).dt.strftime('%Y-%m-%d')
    display_df['Maturity'] = pd.to_datetime(display_df['Maturity']).dt.strftime('%Y-%m-%d')

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


if __name__ == "__main__":
    main()
