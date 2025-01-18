"""
Configuration settings for MSTR debt analyzer.
"""

# Default risk thresholds
RISK_THRESHOLDS = {
    'safe_ltv': 0.50,        # LTV below 50% is considered safe
    'caution_ltv': 0.65,     # LTV 50-65% requires caution
    'warning_ltv': 0.85,     # LTV 65-85% is concerning
    'danger_ltv': 0.85,      # LTV above 85% is dangerous
}

# Default BTC parameters
DEFAULT_BTC_PRICE = 100_000
DEFAULT_BTC_HOLDINGS = 447_470

# Stress test scenarios
STRESS_TEST_SCENARIOS = [
    ('Current', 1.0),
    ('-20%', 0.8),
    ('-30%', 0.7),
    ('-40%', 0.6),
    ('-50%', 0.5),
    ('-60%', 0.4),
    ('-70%', 0.3),
]

# Dashboard settings
DASHBOARD_CONFIG = {
    'page_title': 'MSTR Debt Risk Analyzer',
    'page_icon': '📊',
    'layout': 'wide',
    'theme': {
        'primaryColor': '#1f77b4',
        'backgroundColor': '#ffffff',
        'secondaryBackgroundColor': '#f0f2f6',
    }
}

# Data file paths
DATA_PATHS = {
    'debt': 'data/raw/DEBT/data.html',
    'btc': 'data/raw/BTC/data.html',
    'purchases': 'data/raw/Purchases/data.html',
    'shares': 'data/raw/Shares/data.html',
}

# Export settings
EXPORT_FORMATS = ['csv', 'json', 'excel']
OUTPUT_DIR = 'output/'

# Analysis parameters
ANALYSIS_CONFIG = {
    'lookback_years': 5,
    'forward_years': 10,
    'simulation_runs': 10000,
    'confidence_intervals': [0.05, 0.25, 0.5, 0.75, 0.95],
}
