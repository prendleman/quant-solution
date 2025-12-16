"""
Momentum Trading Strategies

Price momentum, earnings momentum, and cross-sectional momentum strategies.
Generated as part of quant portfolio development.
"""

from typing import Optional, Dict, List
import numpy as np
import pandas as pd
from scipy import stats


def price_momentum_signals(prices: pd.Series, lookback: int = 20,
                          holding_period: int = 5) -> pd.DataFrame:
    """
    Generate momentum signals based on price performance.
    
    Args:
        prices: Price series
        lookback: Lookback period for momentum calculation
        holding_period: Holding period for positions
        
    Returns:
        DataFrame with signals and positions
    """
    # Calculate momentum (return over lookback period)
    momentum = prices.pct_change(lookback)
    
    # Rank momentum
    momentum_rank = momentum.rolling(window=60).rank(pct=True)
    
    # Generate signals: buy top decile, sell bottom decile
    signals = pd.Series(0, index=prices.index)
    signals[momentum_rank > 0.9] = 1  # Top 10%
    signals[momentum_rank < 0.1] = -1  # Bottom 10%
    
    # Positions with holding period
    positions = pd.Series(0, index=prices.index)
    current_position = 0
    hold_count = 0
    
    for i in range(len(signals)):
        if hold_count > 0:
            hold_count -= 1
            positions.iloc[i] = current_position
        else:
            if signals.iloc[i] != 0:
                current_position = signals.iloc[i]
                hold_count = holding_period
                positions.iloc[i] = current_position
            else:
                current_position = 0
                positions.iloc[i] = 0
    
    return pd.DataFrame({
        'momentum': momentum,
        'momentum_rank': momentum_rank,
        'signals': signals,
        'positions': positions
    })


def cross_sectional_momentum(returns: pd.DataFrame, lookback: int = 20,
                            top_n: int = 10) -> pd.DataFrame:
    """
    Cross-sectional momentum strategy (rank assets by momentum).
    
    Args:
        returns: DataFrame of asset returns (columns = assets, rows = time)
        lookback: Lookback period for momentum
        top_n: Number of top assets to select
        
    Returns:
        DataFrame with selected assets and weights
    """
    # Calculate momentum for each asset
    momentum = returns.rolling(window=lookback).apply(lambda x: (1 + x).prod() - 1)
    
    # Rank assets at each time point
    rankings = momentum.rank(axis=1, ascending=False)
    
    # Select top N assets
    selected = rankings <= top_n
    
    # Equal weights for selected assets
    weights = selected.astype(float)
    weights = weights.div(weights.sum(axis=1), axis=0).fillna(0)
    
    return pd.DataFrame({
        'selected_assets': selected.sum(axis=1),
        'portfolio_weights': weights,
        'momentum_scores': momentum
    })


def earnings_momentum_signals(earnings: pd.Series, prices: pd.Series,
                             lookback: int = 4) -> pd.Series:
    """
    Generate signals based on earnings momentum.
    
    Args:
        earnings: Earnings per share series
        prices: Price series
        lookback: Number of quarters to look back
        
    Returns:
        Series of trading signals
    """
    # Calculate earnings growth
    earnings_growth = earnings.pct_change(lookback)
    
    # Calculate price-to-earnings ratio
    pe_ratio = prices / earnings
    
    # Signal: positive earnings growth and reasonable P/E
    signals = pd.Series(0, index=earnings.index)
    signals[(earnings_growth > 0) & (pe_ratio < pe_ratio.quantile(0.75))] = 1
    signals[(earnings_growth < 0) & (pe_ratio > pe_ratio.quantile(0.25))] = -1
    
    return signals


def relative_strength_index_momentum(prices: pd.Series, period: int = 14,
                                    overbought: float = 70,
                                    oversold: float = 30) -> pd.DataFrame:
    """
    Momentum strategy using RSI.
    
    Args:
        prices: Price series
        period: RSI period
        overbought: Overbought threshold
        oversold: Oversold threshold
        
    Returns:
        DataFrame with RSI and signals
    """
    # Calculate RSI
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # Generate signals
    signals = pd.Series(0, index=prices.index)
    signals[rsi < oversold] = 1  # Buy when oversold
    signals[rsi > overbought] = -1  # Sell when overbought
    
    return pd.DataFrame({
        'rsi': rsi,
        'signals': signals
    })


def momentum_factor_analysis(returns: pd.DataFrame, market_returns: pd.Series) -> Dict:
    """
    Analyze momentum factor performance.
    
    Args:
        returns: Asset returns
        market_returns: Market returns
        
    Returns:
        Dictionary with momentum factor analysis
    """
    # Calculate momentum for each asset
    momentum = returns.rolling(20).apply(lambda x: (1 + x).prod() - 1)
    
    # Form momentum portfolios (quintiles)
    momentum_quintiles = []
    for i in range(5):
        threshold_low = momentum.quantile(0.2 * i, axis=1)
        threshold_high = momentum.quantile(0.2 * (i + 1), axis=1)
        
        # Select assets in quintile
        in_quintile = (momentum >= threshold_low.values.reshape(-1, 1)) & \
                     (momentum < threshold_high.values.reshape(-1, 1))
        
        # Equal-weighted portfolio returns
        quintile_returns = (returns * in_quintile).mean(axis=1)
        momentum_quintiles.append(quintile_returns)
    
    # Long-short portfolio (top quintile - bottom quintile)
    momentum_factor = momentum_quintiles[4] - momentum_quintiles[0]
    
    # Performance metrics
    factor_sharpe = momentum_factor.mean() / momentum_factor.std() * np.sqrt(252) if momentum_factor.std() > 0 else 0
    factor_alpha = momentum_factor.mean() - market_returns.mean()
    
    return {
        'momentum_factor': momentum_factor,
        'quintile_returns': momentum_quintiles,
        'sharpe_ratio': factor_sharpe,
        'alpha': factor_alpha,
        'mean_return': momentum_factor.mean() * 252
    }


if __name__ == "__main__":
    # Example usage
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    prices = pd.Series(100 + np.cumsum(np.random.randn(500) * 0.5), index=dates)
    
    # Price momentum
    momentum_signals = price_momentum_signals(prices, lookback=20)
    print("Price Momentum Strategy:")
    print(f"  Total signals: {momentum_signals['signals'][momentum_signals['signals'] != 0].count()}")
    
    # RSI momentum
    rsi_momentum = relative_strength_index_momentum(prices)
    print(f"\nRSI Momentum:")
    print(f"  Current RSI: {rsi_momentum['rsi'].iloc[-1]:.2f}")
    print(f"  Current signal: {rsi_momentum['signals'].iloc[-1]}")
