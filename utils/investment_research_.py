"""
Module: investment_research

This module contains functions for conducting investment research and quantitative analysis for a finance portfolio.

Functions:
- calculate_returns: Calculate the returns of a given asset
- calculate_volatility: Calculate the volatility of a given asset
- calculate_sharpe_ratio: Calculate the Sharpe ratio of a given asset
- calculate_beta: Calculate the beta of a given asset with respect to a benchmark index
- calculate_value_at_risk: Calculate the Value at Risk (VaR) of a given asset
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm

def calculate_returns(prices: pd.Series) -> pd.Series:
    """
    Calculate the returns of a given asset based on its price data.
    
    Args:
    prices: A pandas Series containing the price data of the asset
    
    Returns:
    A pandas Series containing the returns of the asset
    """
    return prices.pct_change()

def calculate_volatility(returns: pd.Series) -> float:
    """
    Calculate the volatility of a given asset based on its returns.
    
    Args:
    returns: A pandas Series containing the returns of the asset
    
    Returns:
    The volatility of the asset
    """
    return np.std(returns)

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float) -> float:
    """
    Calculate the Sharpe ratio of a given asset based on its returns and the risk-free rate.
    
    Args:
    returns: A pandas Series containing the returns of the asset
    risk_free_rate: The risk-free rate
    
    Returns:
    The Sharpe ratio of the asset
    """
    excess_returns = returns - risk_free_rate
    return np.mean(excess_returns) / np.std(excess_returns)

def calculate_beta(asset_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """
    Calculate the beta of a given asset with respect to a benchmark index.
    
    Args:
    asset_returns: A pandas Series containing the returns of the asset
    benchmark_returns: A pandas Series containing the returns of the benchmark index
    
    Returns:
    The beta of the asset
    """
    X = sm.add_constant(benchmark_returns)
    model = sm.OLS(asset_returns, X).fit()
    return model.params[1]

def calculate_value_at_risk(returns: pd.Series, confidence_level: float) -> float:
    """
    Calculate the Value at Risk (VaR) of a given asset based on its returns and a confidence level.
    
    Args:
    returns: A pandas Series containing the returns of the asset
    confidence_level: The confidence level for VaR calculation
    
    Returns:
    The Value at Risk (VaR) of the asset
    """
    return np.percentile(returns, confidence_level * 100)

if __name__ == "__main__":
    # Example usage
    asset_prices = pd.Series([100, 110, 120, 115, 125])
    benchmark_prices = pd.Series([200, 210, 220, 215, 225])
    
    asset_returns = calculate_returns(asset_prices)
    benchmark_returns = calculate_returns(benchmark_prices)
    
    asset_volatility = calculate_volatility(asset_returns)
    asset_sharpe_ratio = calculate_sharpe_ratio(asset_returns, 0.02)
    asset_beta = calculate_beta(asset_returns, benchmark_returns)
    asset_var_95 = calculate_value_at_risk(asset_returns, 0.05)
    
    print("Volatility:", asset_volatility)
    print("Sharpe Ratio:", asset_sharpe_ratio)
    print("Beta:", asset_beta)
    print("Value at Risk (95% confidence):", asset_var_95)