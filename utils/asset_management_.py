"""
Module: asset_management

Description:
This module implements asset management functions for a quantitative finance portfolio.

Requirements:
- Proper docstrings, type hints, and error handling
- Use of appropriate libraries: pandas, numpy, matplotlib
- Demonstrate quant skills related to financial analysis and asset management
- Include example usage in __main__ block
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_portfolio_return(weights: pd.Series, returns: pd.DataFrame) -> float:
    """
    Calculate the expected portfolio return based on asset weights and returns.

    Args:
    weights (pd.Series): Series containing asset weights
    returns (pd.DataFrame): DataFrame containing asset returns

    Returns:
    float: Expected portfolio return
    """
    portfolio_return = np.dot(weights, returns.mean())
    return portfolio_return

def calculate_portfolio_volatility(weights: pd.Series, cov_matrix: pd.DataFrame) -> float:
    """
    Calculate the expected portfolio volatility based on asset weights and covariance matrix.

    Args:
    weights (pd.Series): Series containing asset weights
    cov_matrix (pd.DataFrame): DataFrame containing covariance matrix of asset returns

    Returns:
    float: Expected portfolio volatility
    """
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    return portfolio_volatility

if __name__ == "__main__":
    # Example usage
    assets = ['Stock A', 'Stock B', 'Stock C']
    returns_data = {
        'Stock A': [0.05, 0.02, 0.03, 0.01, 0.04],
        'Stock B': [0.03, 0.01, 0.02, 0.04, 0.05],
        'Stock C': [0.04, 0.03, 0.02, 0.01, 0.05]
    }
    returns_df = pd.DataFrame(returns_data)

    cov_matrix = returns_df.cov()

    weights = pd.Series([0.4, 0.3, 0.3], index=assets)

    portfolio_return = calculate_portfolio_return(weights, returns_df)
    portfolio_volatility = calculate_portfolio_volatility(weights, cov_matrix)

    print(f"Expected Portfolio Return: {portfolio_return}")
    print(f"Expected Portfolio Volatility: {portfolio_volatility}")

    # Plotting efficient frontier
    num_portfolios = 1000
    results = np.zeros((3, num_portfolios))

    for i in range(num_portfolios):
        weights = np.random.random(3)
        weights /= np.sum(weights)
        portfolio_return = np.dot(weights, returns_df.mean())
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        results[0, i] = portfolio_return
        results[1, i] = portfolio_volatility
        results[2, i] = portfolio_return / portfolio_volatility

    plt.scatter(results[1, :], results[0, :], c=results[2, :], cmap='viridis')
    plt.title('Efficient Frontier')
    plt.xlabel('Volatility')
    plt.ylabel('Return')
    plt.colorbar(label='Sharpe Ratio')
    plt.show()