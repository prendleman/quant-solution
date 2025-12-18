"""
Module: historical_var_algorithm

This module implements the Historical Value at Risk (VaR) algorithm for a quantitative finance portfolio.

The Historical VaR algorithm calculates the potential loss in value of a portfolio over a specified time horizon 
at a given confidence level, based on historical data.

This implementation uses historical returns data to calculate the VaR.

Requirements:
- Python 3.6+
- Libraries: numpy, pandas

"""

import numpy as np
import pandas as pd

def historical_var(data: pd.DataFrame, confidence_level: float, horizon: int) -> float:
    """
    Calculate Historical Value at Risk (VaR) for a portfolio.

    Parameters:
    data (pd.DataFrame): DataFrame containing historical returns data for the portfolio.
    confidence_level (float): Desired confidence level for the VaR calculation.
    horizon (int): Time horizon for the VaR calculation.

    Returns:
    float: Historical VaR value for the portfolio.
    """
    returns = data.pct_change().dropna()
    var = np.percentile(returns.sum(axis=1), 100-confidence_level*100)
    return var

if __name__ == "__main__":
    # Example usage
    data = pd.DataFrame({
        'Asset1': [0.01, 0.02, -0.01, 0.005, -0.015],
        'Asset2': [0.015, -0.02, 0.025, -0.01, 0.02]
    })
    
    confidence_level = 0.95
    horizon = 1
    
    var = historical_var(data, confidence_level, horizon)
    print(f"Historical VaR at {confidence_level} confidence level for a horizon of {horizon} day(s): {var}")