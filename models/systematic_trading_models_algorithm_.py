"""
Module: systematic_trading_models

This module contains implementations of various systematic trading models for a quantitative finance portfolio.

The models included are:
- Moving Average Crossover
- Mean Reversion
- Momentum

Each model takes in historical price data and generates trading signals based on specific criteria.

Author: Anonymous
Date: 2022
"""

from typing import List, Tuple
import numpy as np
import pandas as pd

def moving_average_crossover(data: pd.DataFrame, short_window: int, long_window: int) -> pd.DataFrame:
    """
    Generate trading signals based on moving average crossover strategy.
    
    Parameters:
    data (pd.DataFrame): Historical price data
    short_window (int): Short moving average window
    long_window (int): Long moving average window
    
    Returns:
    pd.DataFrame: DataFrame with trading signals (1: buy, -1: sell, 0: hold)
    """
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0
    
    signals['short_mavg'] = data['Close'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['long_mavg'] = data['Close'].rolling(window=long_window, min_periods=1, center=False).mean()
    
    signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1, -1)
    
    return signals

def mean_reversion(data: pd.DataFrame, lookback_period: int, z_score_threshold: float) -> pd.DataFrame:
    """
    Generate trading signals based on mean reversion strategy.
    
    Parameters:
    data (pd.DataFrame): Historical price data
    lookback_period (int): Number of periods to look back for calculating z-score
    z_score_threshold (float): Threshold for z-score to trigger a trade
    
    Returns:
    pd.DataFrame: DataFrame with trading signals (1: buy, -1: sell, 0: hold)
    """
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0
    
    signals['rolling_mean'] = data['Close'].rolling(window=lookback_period, min_periods=1, center=False).mean()
    signals['rolling_std'] = data['Close'].rolling(window=lookback_period, min_periods=1, center=False).std()
    
    signals['z_score'] = (data['Close'] - signals['rolling_mean']) / signals['rolling_std']
    
    signals['signal'] = np.where(signals['z_score'] > z_score_threshold, -1, 1)
    
    return signals

def momentum(data: pd.DataFrame, lookback_period: int) -> pd.DataFrame:
    """
    Generate trading signals based on momentum strategy.
    
    Parameters:
    data (pd.DataFrame): Historical price data
    lookback_period (int): Number of periods to look back for calculating momentum
    
    Returns:
    pd.DataFrame: DataFrame with trading signals (1: buy, -1: sell, 0: hold)
    """
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0
    
    signals['momentum'] = data['Close'].pct_change(periods=lookback_period)
    
    signals['signal'] = np.where(signals['momentum'] > 0, 1, -1)
    
    return signals

if __name__ == "__main__":
    # Example usage
    data = pd.DataFrame({'Close': [100, 110, 120, 130, 140]})
    
    # Moving Average Crossover
    signals_ma = moving_average_crossover(data, short_window=2, long_window=4)
    print("Moving Average Crossover Signals:")
    print(signals_ma)
    
    # Mean Reversion
    signals_mr = mean_reversion(data, lookback_period=3, z_score_threshold=1.0)
    print("\nMean Reversion Signals:")
    print(signals_mr)
    
    # Momentum
    signals_mom = momentum(data, lookback_period=2)
    print("\nMomentum Signals:")
    print(signals_mom)