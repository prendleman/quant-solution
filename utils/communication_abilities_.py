"""
Module: communication_abilities

This module contains functions related to communication abilities in the context of quantitative finance portfolios.
"""

import pandas as pd
import numpy as np

def calculate_portfolio_return(portfolio_weights: pd.Series, asset_returns: pd.DataFrame) -> float:
    """
    Calculate the return of a portfolio based on the weights of assets and their returns.

    Parameters:
    portfolio_weights (pd.Series): Series containing weights of assets in the portfolio
    asset_returns (pd.DataFrame): DataFrame containing returns of assets

    Returns:
    float: Portfolio return
    """
    if not isinstance(portfolio_weights, pd.Series) or not isinstance(asset_returns, pd.DataFrame):
        raise TypeError("Input data types are not correct")

    if not portfolio_weights.index.equals(asset_returns.columns):
        raise ValueError("Index of portfolio weights does not match columns of asset returns")

    portfolio_return = np.dot(portfolio_weights, asset_returns.mean())
    return portfolio_return

if __name__ == "__main__":
    weights = pd.Series([0.3, 0.4, 0.3], index=['Asset1', 'Asset2', 'Asset3'])
    returns = pd.DataFrame({
        'Asset1': [0.05, 0.03, 0.02],
        'Asset2': [0.04, 0.02, 0.01],
        'Asset3': [0.06, 0.05, 0.03]
    })

    portfolio_return = calculate_portfolio_return(weights, returns)
    print("Portfolio return:", portfolio_return)