"""
Module: data_analytics_portfolio

This module contains functions for data analytics related to a quantitative finance portfolio.

Requirements:
- Must be generic and applicable to any quantitative finance portfolio
- Include proper docstrings, type hints, and error handling
- Use appropriate libraries: pandas, numpy, matplotlib
- Demonstrate quant skills related to data analysis, proposal preparation, and strategic guidance
- Include example usage in __main__ block
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_performance_metrics(returns: pd.Series) -> dict:
    """
    Calculate performance metrics for a given series of returns.

    Parameters:
    returns (pd.Series): Series of returns for the portfolio

    Returns:
    dict: Dictionary containing performance metrics such as mean return, volatility, Sharpe ratio
    """
    mean_return = returns.mean()
    volatility = returns.std()
    sharpe_ratio = mean_return / volatility

    return {
        'mean_return': mean_return,
        'volatility': volatility,
        'sharpe_ratio': sharpe_ratio
    }

def plot_returns(returns: pd.Series):
    """
    Plot the returns of the portfolio over time.

    Parameters:
    returns (pd.Series): Series of returns for the portfolio
    """
    returns.plot()
    plt.title('Portfolio Returns Over Time')
    plt.xlabel('Date')
    plt.ylabel('Returns')
    plt.show()

if __name__ == '__main__':
    # Example usage
    returns_data = pd.Series([0.01, 0.02, -0.01, 0.005, 0.015])
    performance_metrics = calculate_performance_metrics(returns_data)
    print(performance_metrics)

    plot_returns(returns_data)