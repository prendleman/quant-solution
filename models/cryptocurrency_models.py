"""
Cryptocurrency Models

Specialized models for cryptocurrency markets including volatility modeling,
liquidity analysis, and crypto-specific risk metrics.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd


def crypto_volatility_modeling(returns: pd.Series, method: str = 'realized') -> pd.Series:
    """
    Cryptocurrency volatility modeling (often higher than traditional assets).
    
    Args:
        returns: Crypto returns
        method: 'realized', 'garch', or 'ewma'
        
    Returns:
        Series of volatility estimates
    """
    if method == 'realized':
        # Realized volatility (rolling standard deviation)
        volatility = returns.rolling(window=24).std() * np.sqrt(365)  # Annualized
    elif method == 'ewma':
        # EWMA volatility
        lambda_param = 0.94
        volatility = returns.ewm(alpha=1-lambda_param).std() * np.sqrt(365)
    else:  # garch (simplified)
        # Simplified GARCH(1,1)
        volatility = returns.rolling(window=24).std() * np.sqrt(365)
    
    return volatility


def crypto_liquidity_analysis(volume: pd.Series, price: pd.Series) -> Dict[str, float]:
    """
    Analyze cryptocurrency liquidity.
    
    Args:
        volume: Trading volume
        price: Price series
        
    Returns:
        Dictionary with liquidity metrics
    """
    # Volume-weighted metrics
    dollar_volume = volume * price
    
    return {
        'avg_daily_volume': volume.mean(),
        'avg_dollar_volume': dollar_volume.mean(),
        'volume_volatility': volume.std(),
        'liquidity_score': (dollar_volume.mean() / (price.std() + 1e-8))
    }


def crypto_correlation_analysis(crypto_returns: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze correlation structure in crypto markets.
    
    Args:
        crypto_returns: DataFrame of crypto returns
        
    Returns:
        Correlation matrix
    """
    return crypto_returns.corr()


def bitcoin_dominance_index(btc_market_cap: pd.Series, total_market_cap: pd.Series) -> pd.Series:
    """
    Calculate Bitcoin dominance index.
    
    Args:
        btc_market_cap: Bitcoin market capitalization
        total_market_cap: Total crypto market cap
        
    Returns:
        Series of dominance index
    """
    return (btc_market_cap / total_market_cap) * 100


def crypto_momentum_factor(returns: pd.Series, lookback: int = 7) -> pd.Series:
    """
    Cryptocurrency momentum factor (often stronger than equity momentum).
    
    Args:
        returns: Crypto returns
        lookback: Lookback period in days
        
    Returns:
        Series of momentum signals
    """
    return returns.rolling(window=lookback).mean()


def stablecoin_peg_analysis(stablecoin_price: pd.Series, peg_price: float = 1.0,
                            threshold: float = 0.01) -> Dict[str, float]:
    """
    Analyze stablecoin peg stability.
    
    Args:
        stablecoin_price: Stablecoin price series
        peg_price: Target peg price (usually 1.0)
        threshold: Deviation threshold
        
    Returns:
        Dictionary with peg analysis
    """
    deviation = stablecoin_price - peg_price
    deviation_pct = (deviation / peg_price) * 100
    
    return {
        'avg_deviation': deviation.mean(),
        'max_deviation': deviation.abs().max(),
        'deviation_std': deviation.std(),
        'peg_breaks': (deviation.abs() > threshold).sum(),
        'peg_stability': 1 - (deviation.abs() > threshold).sum() / len(deviation)
    }


def crypto_fear_greed_index(returns: pd.Series, volatility: pd.Series) -> pd.Series:
    """
    Simplified crypto fear & greed index.
    
    Args:
        returns: Crypto returns
        volatility: Volatility series
        
    Returns:
        Series of fear-greed index (0-100)
    """
    # Normalize returns and volatility
    normalized_returns = (returns - returns.min()) / (returns.max() - returns.min() + 1e-8)
    normalized_vol = 1 - (volatility - volatility.min()) / (volatility.max() - volatility.min() + 1e-8)
    
    # Combine (simplified)
    fear_greed = (normalized_returns * 0.6 + normalized_vol * 0.4) * 100
    
    return fear_greed.clip(0, 100)


if __name__ == "__main__":
    # Example usage
    print("Cryptocurrency Models Demo")
    print("=" * 50)
    
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=365, freq='D')
    returns = pd.Series(np.random.randn(365) * 0.02, index=dates)  # Higher volatility
    
    # Volatility modeling
    vol = crypto_volatility_modeling(returns)
    print(f"\nAverage Crypto Volatility: {vol.mean():.4f}")
