"""
Module: Mathematical Skills Implementation

This module contains functions for implementing mathematical skills related to risk management and problem solving in quantitative finance portfolios.

Requirements:
- Generic implementation for a quantitative finance portfolio
- Proper docstrings, type hints, and error handling
- Libraries used: numpy, pandas, scipy
- Demonstrates quant skills: risk management, mathematical skills, problem solving
- Example usage provided in __main__ block
"""

import numpy as np
import pandas as pd
from scipy.stats import norm

def calculate_portfolio_volatility(returns: pd.Series, weights: np.array) -> float:
    """
    Calculate the volatility of a portfolio given the returns of individual assets and their respective weights.

    Args:
    returns (pd.Series): Series of asset returns
    weights (np.array): Array of asset weights in the portfolio

    Returns:
    float: Portfolio volatility
    """
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(returns.cov(), weights)))
    return portfolio_volatility

def calculate_value_at_risk(returns: pd.Series, weights: np.array, confidence_level: float) -> float:
    """
    Calculate the Value at Risk (VaR) of a portfolio at a given confidence level.

    Args:
    returns (pd.Series): Series of asset returns
    weights (np.array): Array of asset weights in the portfolio
    confidence_level (float): Confidence level for VaR calculation

    Returns:
    float: Value at Risk
    """
    portfolio_volatility = calculate_portfolio_volatility(returns, weights)
    var = norm.ppf(1 - confidence_level) * portfolio_volatility
    return var

if __name__ == "__main__":
    # Example usage
    asset_returns = pd.Series([0.01, 0.02, 0.03, 0.015])
    asset_weights = np.array([0.25, 0.25, 0.25, 0.25])
    
    portfolio_volatility = calculate_portfolio_volatility(asset_returns, asset_weights)
    print(f"Portfolio Volatility: {portfolio_volatility}")
    
    confidence_level = 0.95
    var = calculate_value_at_risk(asset_returns, asset_weights, confidence_level)
    print(f"Value at Risk at {confidence_level} confidence level: {var}")