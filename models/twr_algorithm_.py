"""
Module: twr_algorithm

This module implements the Time-Weighted Return (TWR) algorithm for a quantitative finance portfolio.

Requirements:
- Generic implementation for portfolio management
- Uses libraries: Advent Geneva, sql, data warehouse platforms, FactSet Attribution, r
- Includes performance analysis and attribution analysis

Example Usage:
    # Initialize portfolio data
    portfolio_data = {
        'date': ['2022-01-01', '2022-02-01', '2022-03-01'],
        'nav': [1000000, 1020000, 1015000],
        'cash_flow': [0, -20000, 0]
    }

    # Calculate TWR
    twr = calculate_twr(portfolio_data)
    print(f'Time-Weighted Return: {twr}')
"""

from typing import Dict, List

def calculate_twr(portfolio_data: Dict[str, List[float]]) -> float:
    """
    Calculate Time-Weighted Return (TWR) for the portfolio.

    Args:
    - portfolio_data: A dictionary containing 'date', 'nav', and 'cash_flow' lists

    Returns:
    - twr: The calculated Time-Weighted Return
    """
    if len(portfolio_data['date']) < 2:
        raise ValueError("Portfolio data must have at least two dates for TWR calculation")

    twr = 0.0
    for i in range(1, len(portfolio_data['date'])):
        beginning_nav = portfolio_data['nav'][i - 1] - portfolio_data['cash_flow'][i - 1]
        ending_nav = portfolio_data['nav'][i]
        twr += (ending_nav - beginning_nav) / beginning_nav

    return twr

if __name__ == "__main__":
    # Example portfolio data
    portfolio_data = {
        'date': ['2022-01-01', '2022-02-01', '2022-03-01'],
        'nav': [1000000, 1020000, 1015000],
        'cash_flow': [0, -20000, 0]
    }

    # Calculate TWR
    twr = calculate_twr(portfolio_data)
    print(f'Time-Weighted Return: {twr}')