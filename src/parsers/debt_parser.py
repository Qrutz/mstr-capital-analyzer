"""
Parser for MicroStrategy convertible debt data.
Extracts bond information including maturity dates, coupons, conversion prices, etc.
"""

from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re


def parse_currency(value_str):
    """Convert currency string to float."""
    if not value_str or value_str == '—':
        return None
    # Remove $, commas, and convert to float
    cleaned = re.sub(r'[$,]', '', value_str)
    return float(cleaned)


def parse_percentage(value_str):
    """Convert percentage string to float."""
    if not value_str or value_str == '—':
        return None
    # Remove % and convert to float
    cleaned = value_str.replace('%', '')
    return float(cleaned)


def parse_date(date_str):
    """Convert date string to datetime object."""
    if not date_str or date_str == '—':
        return None
    try:
        return datetime.strptime(date_str, '%m/%d/%Y')
    except ValueError:
        return None


def parse_debt_data(html_file_path):
    """
    Parse convertible debt HTML data into structured DataFrame.

    Args:
        html_file_path: Path to HTML file containing debt data

    Returns:
        pandas.DataFrame with parsed debt information
    """
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'lxml')

    # Find the table with debt data
    table = soup.find('table')
    if not table:
        raise ValueError("No table found in HTML")

    # Extract headers
    headers = []
    header_row = table.find('thead').find('tr')
    for th in header_row.find_all('th'):
        # Get aria-label if available, otherwise get text
        label = th.get('aria-label', th.get_text(strip=True))
        headers.append(label)

    # Extract data rows
    tbody = table.find('tbody')
    rows_data = []

    for tr in tbody.find_all('tr', recursive=False):
        # Skip totals row
        classes = tr.get('class', [])
        if any('totalsRow' in cls for cls in classes):
            continue

        cells = tr.find_all('td')
        if not cells:
            continue

        row_data = []
        for cell in cells:
            text = cell.get_text(strip=True)
            row_data.append(text)

        rows_data.append(row_data)

    # Create DataFrame
    df = pd.DataFrame(rows_data, columns=headers)

    # Clean and convert data types
    df['Issue Date'] = df['Issue Date'].apply(parse_date)
    df['Maturity'] = df['Maturity'].apply(parse_date)
    df['Put Date'] = df['Put Date'].apply(parse_date)
    df['Earliest Call Date'] = df['Earliest Call Date'].apply(parse_date)

    df['Price'] = df['Price'].apply(parse_currency)
    df['Coupon'] = df['Coupon'].apply(parse_percentage)
    df['Notional ($M)'] = df['Notional ($M)'].apply(parse_currency)
    df['Market Val ($M)'] = df['Market Val ($M)'].apply(parse_currency)
    df['BTC Par'] = df['BTC Par'].apply(parse_currency)
    df['Ref Price'] = df['Ref Price'].apply(parse_currency)
    df['Conversion Price'] = df['Conversion Price'].apply(parse_currency)

    return df


def calculate_debt_metrics(df):
    """
    Calculate key debt metrics from parsed data.

    Args:
        df: DataFrame with parsed debt data

    Returns:
        dict with calculated metrics
    """
    metrics = {
        'total_notional': df['Notional ($M)'].sum(),
        'total_market_value': df['Market Val ($M)'].sum(),
        'weighted_avg_coupon': (df['Coupon'] * df['Notional ($M)']).sum() / df['Notional ($M)'].sum(),
        'weighted_avg_conversion_price': (df['Conversion Price'] * df['Notional ($M)']).sum() / df['Notional ($M)'].sum(),
        'num_bonds': len(df),
        'nearest_maturity': df['Maturity'].min(),
        'furthest_maturity': df['Maturity'].max(),
    }

    return metrics


if __name__ == "__main__":
    # Test the parser
    df = parse_debt_data('../../data/raw/DEBT/data.html')
    print("Parsed Debt Data:")
    print(df)
    print("\nDebt Metrics:")
    print(calculate_debt_metrics(df))

    # Save to CSV
    df.to_csv('../../data/processed/debt_data.csv', index=False)
    print("\nSaved to data/processed/debt_data.csv")
