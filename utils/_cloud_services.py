"""
Module: cloud_services_portfolio
This module implements a quantitative finance portfolio using cloud services.
"""

import pandas as pd
import numpy as np

def calculate_portfolio_returns(returns: pd.DataFrame, weights: pd.Series) -> pd.Series:
    """
    Calculate portfolio returns based on asset returns and weights.
    
    Args:
    returns (pd.DataFrame): DataFrame of asset returns
    weights (pd.Series): Series of asset weights
    
    Returns:
    pd.Series: Portfolio returns
    """
    portfolio_returns = returns.dot(weights)
    return portfolio_returns

def calculate_portfolio_volatility(returns: pd.DataFrame, weights: pd.Series) -> float:
    """
    Calculate portfolio volatility based on asset returns and weights.
    
    Args:
    returns (pd.DataFrame): DataFrame of asset returns
    weights (pd.Series): Series of asset weights
    
    Returns:
    float: Portfolio volatility
    """
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(returns.cov(), weights)))
    return portfolio_volatility

if __name__ == "__main__":
    # Example usage
    asset_returns = pd.DataFrame({
        'Asset1': [0.01, 0.02, -0.01, 0.005],
        'Asset2': [0.015, -0.02, 0.03, 0.01],
        'Asset3': [-0.005, 0.01, 0.02, -0.015]
    })
    
    asset_weights = pd.Series([0.4, 0.3, 0.3], index=['Asset1', 'Asset2', 'Asset3'])
    
    portfolio_returns = calculate_portfolio_returns(asset_returns, asset_weights)
    portfolio_volatility = calculate_portfolio_volatility(asset_returns, asset_weights)
    
    print("Portfolio Returns:")
    print(portfolio_returns)
    
    print("Portfolio Volatility:")
    print(portfolio_volatility)