"""
Parser for MicroStrategy Bitcoin holdings data.
Extracts current BTC holdings, market value, and volatility metrics.
"""

from bs4 import BeautifulSoup
import re


def parse_currency(value_str):
    """Convert currency string to float."""
    if not value_str or value_str == '—':
        return None
    cleaned = re.sub(r'[$,]', '', value_str)
    return float(cleaned)


def parse_percentage(value_str):
    """Convert percentage string to float."""
    if not value_str or value_str == '—':
        return None
    cleaned = value_str.replace('%', '')
    return float(cleaned)


def parse_btc_holdings(html_file_path):
    """
    Parse Bitcoin holdings data from HTML.

    Args:
        html_file_path: Path to HTML file containing BTC data

    Returns:
        dict with BTC holdings information
    """
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'lxml')

    # Find all metric elements
    metrics = {}

    # Look for the grid items containing the data
    grid_items = soup.find_all('div', class_=re.compile('numberGridTitle'))

    for item in grid_items:
        title_elem = item.find('span')
        if not title_elem:
            continue

        title = title_elem.get('aria-label', title_elem.get_text(strip=True))

        # Find the associated value
        value_elem = item.find_next_sibling('p', class_=re.compile('numberGridLargeValue'))
        if value_elem:
            value = value_elem.get_text(strip=True)

            # Parse based on title
            if 'BTC' in title and 'Price' in title:
                metrics['btc_price'] = parse_currency(value)
            elif 'BTC' in title and 'Hold' in title:
                metrics['btc_holdings'] = parse_currency(value)
            elif 'Market' in title and 'Val' in title:
                metrics['btc_market_value'] = parse_currency(value)
            elif 'Volatility' in title:
                metrics['btc_volatility'] = parse_percentage(value)

    return metrics


if __name__ == "__main__":
    # Test the parser
    btc_data = parse_btc_holdings('../../data/raw/BTC/data.html')
    print("BTC Holdings Data:")
    for key, value in btc_data.items():
        print(f"{key}: {value}")
