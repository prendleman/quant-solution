"""
Module: Quantitative Risk Models

This module implements various quantitative risk models for a finance portfolio.

The following libraries are used:
- c++
- java
- git
- Java
- r
"""

import numpy as np
import pandas as pd

def calculate_var(returns: pd.Series, confidence_level: float) -> float:
    """
    Calculate Value at Risk (VaR) for a given portfolio returns series at a specified confidence level.

    Args:
    returns (pd.Series): Time series of portfolio returns
    confidence_level (float): Confidence level for VaR calculation

    Returns:
    float: Value at Risk (VaR) for the portfolio
    """
    sorted_returns = np.sort(returns)
    var_index = int(np.floor(returns.size * (1 - confidence_level)))
    return np.abs(sorted_returns[var_index])

def calculate_cvar(returns: pd.Series, confidence_level: float) -> float:
    """
    Calculate Conditional Value at Risk (CVaR) for a given portfolio returns series at a specified confidence level.

    Args:
    returns (pd.Series): Time series of portfolio returns
    confidence_level (float): Confidence level for CVaR calculation

    Returns:
    float: Conditional Value at Risk (CVaR) for the portfolio
    """
    sorted_returns = np.sort(returns)
    var_index = int(np.floor(returns.size * (1 - confidence_level)))
    return np.abs(sorted_returns[0:var_index].mean())

if __name__ == "__main__":
    # Example usage
    returns = pd.Series([0.01, -0.02, 0.03, -0.01, 0.02, -0.03])
    confidence_level = 0.95

    var = calculate_var(returns, confidence_level)
    cvar = calculate_cvar(returns, confidence_level)

    print(f"Value at Risk (VaR) at {confidence_level} confidence level: {var}")
    print(f"Conditional Value at Risk (CVaR) at {confidence_level} confidence level: {cvar}")