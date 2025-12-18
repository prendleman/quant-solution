"""
Module: vba_portfolio_analysis

This module contains functions for analyzing a quantitative finance portfolio using VBA.

Requirements:
- Must be generic (no company names, job titles, or role-specific details)
- Include proper docstrings, type hints, and error handling
- Use appropriate libraries: R, matlab, VBA, python, java
- Demonstrate quant skills related to: quantitative research, statistical analysis, statistics
- Include example usage in __main__ block
- Code should be production-ready and portfolio-quality
"""

from typing import List
import numpy as np

def calculate_portfolio_return(weights: List[float], returns: List[float]) -> float:
    """
    Calculate the return of a portfolio based on the weights of assets and their returns.

    Args:
    weights: List of floats representing the weights of assets in the portfolio
    returns: List of floats representing the returns of assets in the portfolio

    Returns:
    float: The return of the portfolio
    """
    if len(weights) != len(returns):
        raise ValueError("Number of weights must match number of returns")

    portfolio_return = np.dot(weights, returns)
    return portfolio_return

def calculate_portfolio_volatility(weights: List[float], cov_matrix: np.ndarray) -> float:
    """
    Calculate the volatility of a portfolio based on the weights of assets and the covariance matrix.

    Args:
    weights: List of floats representing the weights of assets in the portfolio
    cov_matrix: Numpy array representing the covariance matrix of asset returns

    Returns:
    float: The volatility of the portfolio
    """
    if len(weights) != cov_matrix.shape[0]:
        raise ValueError("Number of weights must match number of assets in covariance matrix")

    portfolio_volatility = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
    return portfolio_volatility

if __name__ == "__main__":
    weights = [0.3, 0.5, 0.2]
    returns = [0.1, 0.05, 0.08]
    cov_matrix = np.array([[0.1, 0.03, 0.02],
                            [0.03, 0.12, 0.04],
                            [0.02, 0.04, 0.15]])

    portfolio_return = calculate_portfolio_return(weights, returns)
    portfolio_volatility = calculate_portfolio_volatility(weights, cov_matrix)

    print(f"Portfolio Return: {portfolio_return}")
    print(f"Portfolio Volatility: {portfolio_volatility}")