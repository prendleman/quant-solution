"""
Module: modified_dietz_algorithm

This module implements the Modified Dietz algorithm for calculating the rate of return on a portfolio.

Requirements:
- Quantitative finance portfolio
- Generic implementation
- Proper docstrings, type hints, error handling
- Libraries: Advent Geneva, sql, data warehouse platforms, FactSet Attribution, r
- Quant skills: portfolio management, performance analysis, attribution analysis
- Example usage in __main__ block
- Production-ready code

"""

from typing import List, Tuple
import pandas as pd

def modified_dietz_algorithm(cash_flows: List[float], market_values: List[float], start_date: str, end_date: str) -> float:
    """
    Calculate the rate of return using the Modified Dietz algorithm.

    Args:
    cash_flows: List of cash flows for the period
    market_values: List of market values for the period
    start_date: Start date of the period
    end_date: End date of the period

    Returns:
    float: Rate of return calculated using Modified Dietz algorithm
    """
    if len(cash_flows) != len(market_values):
        raise ValueError("Length of cash flows and market values should be the same")

    cash_flow_total = sum(cash_flows)
    weighted_market_values = [cf * mv for cf, mv in zip(cash_flows, market_values)]
    weighted_market_value_total = sum(weighted_market_values)

    return (weighted_market_value_total - cash_flow_total) / (sum(market_values) + cash_flow_total)

if __name__ == "__main__":
    cash_flows = [10000, -5000, -2000, 3000]
    market_values = [50000, 55000, 60000, 62000]
    start_date = "2022-01-01"
    end_date = "2022-12-31"

    rate_of_return = modified_dietz_algorithm(cash_flows, market_values, start_date, end_date)
    print(f"Rate of return for the period: {rate_of_return}")