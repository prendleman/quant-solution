"""
Module: investment_banking

This module contains functions for quantitative finance portfolio analysis in the context of investment banking.

Requirements:
- r, pandas, python libraries
- Proper docstrings, type hints, and error handling
- Demonstrate quant skills related to investment banking and financial analysis
- Production-ready and portfolio-quality code

Example usage:
    # Calculate expected return
    expected_return = calculate_expected_return(portfolio)

    # Calculate portfolio variance
    portfolio_variance = calculate_portfolio_variance(portfolio)

    # Calculate Sharpe ratio
    sharpe_ratio = calculate_sharpe_ratio(portfolio, risk_free_rate)
"""

import pandas as pd
import numpy as np

def calculate_expected_return(portfolio: pd.DataFrame) -> float:
    """
    Calculate the expected return of a portfolio.

    Args:
        portfolio: Pandas DataFrame with columns representing asset weights and returns

    Returns:
        float: Expected return of the portfolio
    """
    expected_return = np.sum(portfolio['Weight'] * portfolio['Return'])
    return expected_return

def calculate_portfolio_variance(portfolio: pd.DataFrame) -> float:
    """
    Calculate the variance of a portfolio.

    Args:
        portfolio: Pandas DataFrame with columns representing asset weights and returns

    Returns:
        float: Variance of the portfolio
    """
    covariance_matrix = np.cov(portfolio['Return'])
    portfolio_variance = np.dot(np.dot(portfolio['Weight'].T, covariance_matrix), portfolio['Weight'])
    return portfolio_variance

def calculate_sharpe_ratio(portfolio: pd.DataFrame, risk_free_rate: float) -> float:
    """
    Calculate the Sharpe ratio of a portfolio.

    Args:
        portfolio: Pandas DataFrame with columns representing asset weights and returns
        risk_free_rate: Risk-free rate of return

    Returns:
        float: Sharpe ratio of the portfolio
    """
    expected_return = calculate_expected_return(portfolio)
    portfolio_variance = calculate_portfolio_variance(portfolio)
    sharpe_ratio = (expected_return - risk_free_rate) / np.sqrt(portfolio_variance)
    return sharpe_ratio

if __name__ == "__main__":
    # Example usage
    portfolio_data = {
        'Asset': ['A', 'B', 'C'],
        'Weight': [0.4, 0.3, 0.3],
        'Return': [0.05, 0.03, 0.04]
    }
    portfolio = pd.DataFrame(portfolio_data)
    risk_free_rate = 0.02

    expected_return = calculate_expected_return(portfolio)
    portfolio_variance = calculate_portfolio_variance(portfolio)
    sharpe_ratio = calculate_sharpe_ratio(portfolio, risk_free_rate)

    print(f"Expected Return: {expected_return}")
    print(f"Portfolio Variance: {portfolio_variance}")
    print(f"Sharpe Ratio: {sharpe_ratio}")