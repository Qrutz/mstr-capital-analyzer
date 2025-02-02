"""
Maturity timeline and refinancing risk analysis.

Analyzes when bonds mature and assesses refinancing risk
under various BTC price scenarios.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px


class MaturityAnalyzer:
    """Analyze debt maturity schedule and refinancing risk."""

    def __init__(self, debt_df):
        """
        Initialize with debt DataFrame.

        Args:
            debt_df: DataFrame with debt information including maturity dates
        """
        self.debt_df = debt_df.copy()
        self.debt_df['Maturity'] = pd.to_datetime(self.debt_df['Maturity'])
        self.debt_df = self.debt_df.sort_values('Maturity')

    def get_maturity_schedule(self):
        """
        Get maturity schedule showing when each bond comes due.

        Returns:
            DataFrame with maturity timeline
        """
        schedule = self.debt_df[['Name', 'Maturity', 'Notional ($M)', 'Coupon', 'Put Date']].copy()
        schedule['Put Date'] = pd.to_datetime(schedule['Put Date'])

        now = pd.Timestamp.now()
        schedule['Years to Maturity'] = (
            (schedule['Maturity'] - now).dt.days / 365.25
        ).round(2)
        schedule['Years to Put'] = (
            (schedule['Put Date'] - now).dt.days / 365.25
        ).round(2)

        return schedule

    def calculate_maturity_wall(self):
        """
        Calculate maturity concentration by year.

        Returns:
            DataFrame showing debt maturing each year
        """
        schedule = self.get_maturity_schedule()
        schedule['Maturity Year'] = schedule['Maturity'].dt.year

        wall = schedule.groupby('Maturity Year').agg({
            'Notional ($M)': 'sum',
            'Name': 'count'
        }).rename(columns={'Name': 'Number of Bonds'})

        wall['Percentage of Total'] = (
            wall['Notional ($M)'] / wall['Notional ($M)'].sum() * 100
        ).round(1)

        return wall

    def assess_refinancing_risk(self, btc_price_at_maturity):
        """
        Assess refinancing risk for each bond based on future BTC price.

        Args:
            btc_price_at_maturity: Expected BTC price when bonds mature

        Returns:
            DataFrame with refinancing risk assessment
        """
        schedule = self.get_maturity_schedule()

        # Merge with original debt_df to get conversion prices
        schedule = schedule.merge(
            self.debt_df[['Name', 'Conversion Price']],
            on='Name',
            how='left'
        )

        # Calculate if bonds will be in the money (ITM) to convert
        # Bond converts if current stock price > conversion price
        # For simplicity, assume MSTR stock moves with BTC
        schedule['In the Money'] = (
            schedule['Conversion Price'].notna() &
            (btc_price_at_maturity > 50000)  # Simplified assumption
        )

        # If ITM, likely converts to equity (good - no cash needed)
        # If OTM, needs cash refinancing (risk)
        schedule['Refinancing Needed'] = ~schedule['In the Money']
        schedule['Cash Requirement ($M)'] = np.where(
            schedule['Refinancing Needed'],
            schedule['Notional ($M)'],
            0
        )

        schedule['Status'] = np.where(
            schedule['In the Money'],
            '✅ Likely Converts',
            '⚠️ Needs Refinancing'
        )

        return schedule[[
            'Name',
            'Maturity',
            'Notional ($M)',
            'Status',
            'Cash Requirement ($M)',
            'Years to Maturity'
        ]]

    def plot_maturity_timeline(self):
        """
        Create visual timeline of debt maturities.

        Returns:
            Plotly figure
        """
        schedule = self.get_maturity_schedule()

        fig = go.Figure()

        # Add bars for each bond
        fig.add_trace(go.Bar(
            x=schedule['Maturity'],
            y=schedule['Notional ($M)'],
            text=schedule['Name'],
            textposition='auto',
            marker_color='lightblue',
            hovertemplate='<b>%{text}</b><br>' +
                          'Maturity: %{x|%Y-%m-%d}<br>' +
                          'Amount: $%{y:,.0f}M<br>' +
                          '<extra></extra>'
        ))

        # Add put date markers
        for idx, row in schedule.iterrows():
            if pd.notna(row['Put Date']):
                # Convert pandas Timestamp to datetime for Plotly compatibility
                put_date = pd.to_datetime(row['Put Date']).to_pydatetime()
                fig.add_vline(
                    x=put_date,
                    line_dash="dash",
                    line_color="orange",
                    opacity=0.5,
                    annotation_text=f"{row['Name']} Put"
                )

        fig.update_layout(
            title="Debt Maturity Timeline",
            xaxis_title="Maturity Date",
            yaxis_title="Notional Amount ($M)",
            hovermode='x unified',
            height=500
        )

        return fig

    def plot_cumulative_maturity(self):
        """
        Plot cumulative debt maturing over time.

        Returns:
            Plotly figure
        """
        schedule = self.get_maturity_schedule()
        schedule = schedule.sort_values('Maturity')
        schedule['Cumulative Debt ($M)'] = schedule['Notional ($M)'].cumsum()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=schedule['Maturity'],
            y=schedule['Cumulative Debt ($M)'],
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color='red', width=3),
            marker=dict(size=10),
            text=schedule['Name'],
            hovertemplate='<b>%{text}</b><br>' +
                          'Date: %{x|%Y-%m-%d}<br>' +
                          'Cumulative: $%{y:,.0f}M<br>' +
                          '<extra></extra>'
        ))

        fig.update_layout(
            title="Cumulative Debt Maturity",
            xaxis_title="Date",
            yaxis_title="Cumulative Debt Maturing ($M)",
            hovermode='x unified',
            height=400
        )

        return fig

    def calculate_rollover_requirement(self, years_ahead=5):
        """
        Calculate total debt that needs to be rolled over in next N years.

        Args:
            years_ahead: Number of years to look ahead

        Returns:
            dict with rollover metrics
        """
        schedule = self.get_maturity_schedule()
        cutoff_date = datetime.now() + timedelta(days=years_ahead * 365.25)

        maturing_soon = schedule[schedule['Maturity'] <= cutoff_date]

        return {
            'total_maturing': maturing_soon['Notional ($M)'].sum(),
            'number_of_bonds': len(maturing_soon),
            'years_analyzed': years_ahead,
            'percentage_of_total': (
                maturing_soon['Notional ($M)'].sum() /
                schedule['Notional ($M)'].sum() * 100
            )
        }


if __name__ == "__main__":
    from parsers.debt_parser import parse_debt_data

    # Test the analyzer
    debt_df = parse_debt_data('../../data/raw/DEBT/data.html')
    analyzer = MaturityAnalyzer(debt_df)

    print("=== Maturity Schedule ===")
    print(analyzer.get_maturity_schedule())

    print("\n=== Maturity Wall ===")
    print(analyzer.calculate_maturity_wall())

    print("\n=== Refinancing Risk (BTC @ $100k) ===")
    print(analyzer.assess_refinancing_risk(btc_price_at_maturity=100000))

    print("\n=== Rollover Requirement (5 years) ===")
    rollover = analyzer.calculate_rollover_requirement(5)
    for key, value in rollover.items():
        print(f"{key}: {value}")
