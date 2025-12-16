"""
Statistical Arbitrage Strategies

Pairs trading, mean reversion, and cointegration-based strategies.
Generated as part of quant portfolio development.
"""

from typing import Optional, Tuple, Dict
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import norm


def calculate_half_life(spread: pd.Series) -> float:
    """
    Calculate half-life of mean reversion for spread series.
    
    Args:
        spread: Spread series (price difference or ratio)
        
    Returns:
        Half-life in periods
    """
    spread_lag = spread.shift(1)
    spread_diff = spread - spread_lag
    spread_lag = spread_lag.dropna()
    spread_diff = spread_diff.dropna()
    
    # OLS regression: spread_diff = alpha + beta * spread_lag
    beta = np.cov(spread_lag, spread_diff)[0, 1] / np.var(spread_lag)
    half_life = -np.log(2) / beta if beta < 0 else np.inf
    
    return half_life


def cointegration_test(series1: pd.Series, series2: pd.Series) -> Dict:
    """
    Test for cointegration between two time series (Engle-Granger test).
    
    Args:
        series1: First time series
        series2: Second time series
        
    Returns:
        Dictionary with test results
    """
    from statsmodels.tsa.stattools import coint
    
    # Run cointegration test
    score, pvalue, _ = coint(series1, series2)
    
    return {
        'cointegrated': pvalue < 0.05,
        'p_value': pvalue,
        'test_statistic': score
    }


def calculate_zscore(spread: pd.Series, window: int = 30) -> pd.Series:
    """
    Calculate z-score of spread for mean reversion trading.
    
    Args:
        spread: Spread series
        window: Rolling window for mean and std calculation
        
    Returns:
        Z-score series
    """
    rolling_mean = spread.rolling(window=window).mean()
    rolling_std = spread.rolling(window=window).std()
    zscore = (spread - rolling_mean) / rolling_std
    return zscore


def pairs_trading_signals(price1: pd.Series, price2: pd.Series,
                         entry_threshold: float = 2.0,
                         exit_threshold: float = 0.5,
                         window: int = 30) -> pd.DataFrame:
    """
    Generate pairs trading signals based on z-score of spread.
    
    Args:
        price1: First asset price series
        price2: Second asset price series
        entry_threshold: Z-score threshold for entry (default 2.0)
        exit_threshold: Z-score threshold for exit (default 0.5)
        window: Rolling window for z-score calculation
        
    Returns:
        DataFrame with signals and positions
    """
    # Calculate spread (price ratio)
    spread = price1 / price2
    zscore = calculate_zscore(spread, window)
    
    # Initialize signals
    signals = pd.Series(0, index=price1.index)
    positions = pd.Series(0, index=price1.index)
    position = 0
    
    for i in range(len(zscore)):
        z = zscore.iloc[i]
        
        # Entry signals
        if position == 0:
            if z > entry_threshold:
                # Spread is too high, short spread (short asset1, long asset2)
                signals.iloc[i] = -1
                position = -1
            elif z < -entry_threshold:
                # Spread is too low, long spread (long asset1, short asset2)
                signals.iloc[i] = 1
                position = 1
        
        # Exit signals
        elif position != 0:
            if (position == -1 and z < exit_threshold) or (position == 1 and z > -exit_threshold):
                signals.iloc[i] = -position  # Close position
                position = 0
        
        positions.iloc[i] = position
    
    return pd.DataFrame({
        'spread': spread,
        'zscore': zscore,
        'signals': signals,
        'positions': positions
    })


def mean_reversion_strategy(returns: pd.Series, lookback: int = 20,
                           entry_threshold: float = 2.0,
                           exit_threshold: float = 0.0) -> pd.DataFrame:
    """
    Mean reversion strategy based on z-score of returns.
    
    Args:
        returns: Return series
        lookback: Lookback period for z-score
        entry_threshold: Z-score threshold for entry
        exit_threshold: Z-score threshold for exit
        
    Returns:
        DataFrame with signals and positions
    """
    zscore = calculate_zscore(returns, window=lookback)
    
    signals = pd.Series(0, index=returns.index)
    positions = pd.Series(0, index=returns.index)
    position = 0
    
    for i in range(len(zscore)):
        z = zscore.iloc[i]
        
        if position == 0:
            if z < -entry_threshold:
                signals.iloc[i] = 1  # Buy (oversold)
                position = 1
            elif z > entry_threshold:
                signals.iloc[i] = -1  # Sell (overbought)
                position = -1
        else:
            if (position == 1 and z > -exit_threshold) or (position == -1 and z < exit_threshold):
                signals.iloc[i] = -position  # Exit
                position = 0
        
        positions.iloc[i] = position
    
    return pd.DataFrame({
        'returns': returns,
        'zscore': zscore,
        'signals': signals,
        'positions': positions
    })


def calculate_pairs_correlation(price1: pd.Series, price2: pd.Series,
                                window: int = 60) -> pd.Series:
    """
    Calculate rolling correlation between two price series.
    
    Args:
        price1: First price series
        price2: Second price series
        window: Rolling window size
        
    Returns:
        Rolling correlation series
    """
    returns1 = price1.pct_change()
    returns2 = price2.pct_change()
    
    rolling_corr = returns1.rolling(window=window).corr(returns2)
    return rolling_corr


def hedge_ratio_calculation(price1: pd.Series, price2: pd.Series,
                           method: str = 'ols') -> float:
    """
    Calculate hedge ratio between two assets.
    
    Args:
        price1: First price series
        price2: Second price series
        method: 'ols' (ordinary least squares) or 'ratio'
        
    Returns:
        Hedge ratio
    """
    if method == 'ols':
        # OLS regression: price1 = alpha + beta * price2
        beta = np.cov(price1, price2)[0, 1] / np.var(price2)
        return beta
    else:  # ratio
        return price1.mean() / price2.mean()


if __name__ == "__main__":
    # Example usage
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    
    # Generate correlated price series
    np.random.seed(42)
    price1 = 100 + np.cumsum(np.random.randn(500) * 0.5)
    price2 = 100 + np.cumsum(np.random.randn(500) * 0.5) + 0.7 * (price1 - 100)
    price1_series = pd.Series(price1, index=dates)
    price2_series = pd.Series(price2, index=dates)
    
    # Cointegration test
    coint_result = cointegration_test(price1_series, price2_series)
    print(f"Cointegration test:")
    print(f"  Cointegrated: {coint_result['cointegrated']}")
    print(f"  P-value: {coint_result['p_value']:.4f}")
    
    # Pairs trading signals
    pairs_signals = pairs_trading_signals(price1_series, price2_series)
    print(f"\nPairs Trading Signals:")
    print(f"  Total signals: {pairs_signals['signals'][pairs_signals['signals'] != 0].count()}")
    print(f"  Current position: {pairs_signals['positions'].iloc[-1]}")
    
    # Hedge ratio
    hedge_ratio = hedge_ratio_calculation(price1_series, price2_series)
    print(f"\nHedge Ratio: {hedge_ratio:.4f}")
    
    # Mean reversion strategy
    returns = price1_series.pct_change()
    mr_signals = mean_reversion_strategy(returns)
    print(f"\nMean Reversion Strategy:")
    print(f"  Total signals: {mr_signals['signals'][mr_signals['signals'] != 0].count()}")
