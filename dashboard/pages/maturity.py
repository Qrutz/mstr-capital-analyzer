"""
Maturity analysis page for Streamlit dashboard.
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.parsers.debt_parser import parse_debt_data
from src.models.maturity_analysis import MaturityAnalyzer


st.set_page_config(
    page_title="Maturity Analysis - MSTR",
    page_icon="📅",
    layout="wide"
)


@st.cache_data
def load_data():
    debt_df = parse_debt_data('data/raw/DEBT/data.html')
    return debt_df


def main():
    st.title("📅 Debt Maturity & Refinancing Risk")

    debt_df = load_data()
    analyzer = MaturityAnalyzer(debt_df)

    st.markdown("---")

    # Key metrics
    rollover_3yr = analyzer.calculate_rollover_requirement(3)
    rollover_5yr = analyzer.calculate_rollover_requirement(5)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Debt Maturing in 3 Years",
            f"${rollover_3yr['total_maturing']:,.0f}M",
            f"{rollover_3yr['percentage_of_total']:.1f}% of total"
        )

    with col2:
        st.metric(
            "Debt Maturing in 5 Years",
            f"${rollover_5yr['total_maturing']:,.0f}M",
            f"{rollover_5yr['percentage_of_total']:.1f}% of total"
        )

    with col3:
        schedule = analyzer.get_maturity_schedule()
        avg_years = schedule['Years to Maturity'].mean()
        st.metric(
            "Weighted Avg Maturity",
            f"{avg_years:.1f} years"
        )

    st.markdown("---")

    # Maturity Timeline
    st.subheader("Debt Maturity Timeline")
    fig_timeline = analyzer.plot_maturity_timeline()
    st.plotly_chart(fig_timeline, use_container_width=True)

    # Cumulative Maturity
    st.subheader("Cumulative Debt Maturity")
    fig_cumulative = analyzer.plot_cumulative_maturity()
    st.plotly_chart(fig_cumulative, use_container_width=True)

    st.markdown("---")

    # Refinancing Risk Analysis
    st.subheader("🔄 Refinancing Risk Analysis")

    btc_future_price = st.slider(
        "Expected BTC Price at Maturity ($)",
        min_value=30000,
        max_value=300000,
        value=100000,
        step=10000
    )

    refinancing_df = analyzer.assess_refinancing_risk(btc_future_price)

    st.dataframe(
        refinancing_df,
        use_container_width=True,
        hide_index=True
    )

    total_refinancing = refinancing_df['Cash Requirement ($M)'].sum()

    if total_refinancing > 0:
        st.warning(
            f"⚠️ At ${btc_future_price:,} BTC, MSTR would need to refinance "
            f"${total_refinancing:,.0f}M in cash (bonds won't convert)."
        )
    else:
        st.success(
            f"✅ At ${btc_future_price:,} BTC, all bonds likely convert to equity "
            "(no cash refinancing needed)."
        )

    st.markdown("---")

    # Maturity Wall
    st.subheader("Maturity Wall by Year")

    wall_df = analyzer.calculate_maturity_wall()
    st.dataframe(wall_df, use_container_width=True)


if __name__ == "__main__":
    main()
