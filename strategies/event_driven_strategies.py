"""
Event-Driven Trading Strategies

Strategies based on corporate events: earnings announcements, M&A, 
dividend announcements, and other event-based trading signals.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def earnings_announcement_strategy(returns: pd.Series, announcement_dates: pd.DatetimeIndex,
                                  lookback: int = 5, lookforward: int = 5) -> Dict[str, float]:
    """
    Analyze returns around earnings announcements.
    
    Args:
        returns: Series of stock returns
        announcement_dates: DatetimeIndex of earnings announcement dates
        lookback: Days before announcement to analyze
        lookforward: Days after announcement to analyze
        
    Returns:
        Dictionary with event study results
    """
    event_returns = []
    
    for date in announcement_dates:
        if date in returns.index:
            idx = returns.index.get_loc(date)
            if idx >= lookback and idx + lookforward < len(returns):
                window_returns = returns.iloc[idx - lookback:idx + lookforward + 1]
                event_returns.append(window_returns.values)
    
    if len(event_returns) == 0:
        return {
            'average_cumulative_return': 0.0,
            'positive_events_pct': 0.0,
            'pre_announcement_return': 0.0,
            'post_announcement_return': 0.0
        }
    
    # Calculate average cumulative returns
    event_returns_array = np.array(event_returns)
    avg_cumulative = event_returns_array.mean(axis=0).cumsum()
    
    # Pre and post announcement returns
    pre_return = avg_cumulative[lookback]
    post_return = avg_cumulative[-1] - avg_cumulative[lookback]
    
    # Positive events percentage
    positive_events = sum(1 for er in event_returns if er.sum() > 0)
    positive_pct = positive_events / len(event_returns) * 100
    
    return {
        'average_cumulative_return': avg_cumulative[-1],
        'positive_events_pct': positive_pct,
        'pre_announcement_return': pre_return,
        'post_announcement_return': post_return,
        'event_window_returns': avg_cumulative
    }


def merger_arbitrage_spread(target_price: float, acquirer_price: float,
                            offer_price: float, deal_probability: float = 0.8) -> Dict[str, float]:
    """
    Calculate merger arbitrage spread and expected return.
    
    Args:
        target_price: Current target company stock price
        acquirer_price: Current acquirer stock price
        offer_price: Offer price per share
        deal_probability: Probability of deal completion
        
    Returns:
        Dictionary with arbitrage metrics
    """
    # Current spread
    current_spread = offer_price - target_price
    
    # Expected return
    if current_spread > 0:
        expected_return = (deal_probability * current_spread - 
                          (1 - deal_probability) * (target_price - offer_price * 0.9)) / target_price
    else:
        expected_return = 0.0
    
    # Annualized return (assuming 3-month deal)
    annualized_return = expected_return * 4
    
    return {
        'current_spread': current_spread,
        'spread_pct': (current_spread / target_price) * 100,
        'expected_return': expected_return,
        'annualized_return': annualized_return,
        'deal_probability': deal_probability
    }


def dividend_capture_strategy(ex_dividend_dates: pd.DatetimeIndex, prices: pd.Series,
                             dividends: pd.Series, transaction_cost: float = 0.001) -> Dict[str, float]:
    """
    Analyze dividend capture strategy profitability.
    
    Args:
        ex_dividend_dates: DatetimeIndex of ex-dividend dates
        prices: Series of stock prices
        dividends: Series of dividend amounts
        transaction_cost: Transaction cost as fraction
        
    Returns:
        Dictionary with strategy metrics
    """
    strategy_returns = []
    
    for ex_date in ex_dividend_dates:
        if ex_date in prices.index:
            idx = prices.index.get_loc(ex_date)
            if idx > 0 and idx < len(prices) - 1:
                # Buy before ex-date, sell after
                buy_price = prices.iloc[idx - 1]
                sell_price = prices.iloc[idx + 1]
                dividend = dividends.get(ex_date, 0)
                
                # Return after transaction costs
                gross_return = (sell_price + dividend - buy_price) / buy_price
                net_return = gross_return - 2 * transaction_cost  # Buy and sell
                strategy_returns.append(net_return)
    
    if len(strategy_returns) == 0:
        return {
            'average_return': 0.0,
            'win_rate': 0.0,
            'total_return': 0.0
        }
    
    strategy_returns = np.array(strategy_returns)
    
    return {
        'average_return': strategy_returns.mean(),
        'win_rate': (strategy_returns > 0).sum() / len(strategy_returns) * 100,
        'total_return': strategy_returns.sum(),
        'sharpe_ratio': strategy_returns.mean() / (strategy_returns.std() + 1e-8) * np.sqrt(252)
    }


def event_momentum_strategy(event_returns: pd.Series, lookback: int = 5) -> pd.Series:
    """
    Generate trading signals based on event momentum.
    
    Args:
        event_returns: Series of event-driven returns
        lookback: Lookback period for momentum
        
    Returns:
        Series of trading signals
    """
    momentum = event_returns.rolling(window=lookback).mean()
    signals = pd.Series(0, index=event_returns.index)
    
    # Buy if positive momentum, sell if negative
    signals[momentum > 0.02] = 1
    signals[momentum < -0.02] = -1
    
    return signals


def post_earnings_announcement_drift(earnings_surprise: pd.Series, 
                                     returns: pd.Series,
                                     window: int = 60) -> Dict[str, float]:
    """
    Analyze post-earnings announcement drift (PEAD) - continuation of returns
    after earnings surprises.
    
    Args:
        earnings_surprise: Series of earnings surprises (actual - expected)
        returns: Series of stock returns
        window: Days after announcement to analyze
        
    Returns:
        Dictionary with PEAD metrics
    """
    # Align data
    aligned = pd.DataFrame({
        'surprise': earnings_surprise,
        'returns': returns
    }).dropna()
    
    if len(aligned) < 10:
        return {
            'positive_surprise_return': 0.0,
            'negative_surprise_return': 0.0,
            'drift_magnitude': 0.0
        }
    
    # Positive surprises
    positive_surprises = aligned[aligned['surprise'] > 0]
    negative_surprises = aligned[aligned['surprise'] < 0]
    
    pos_return = positive_surprises['returns'].mean() if len(positive_surprises) > 0 else 0.0
    neg_return = negative_surprises['returns'].mean() if len(negative_surprises) > 0 else 0.0
    
    drift_magnitude = pos_return - neg_return
    
    return {
        'positive_surprise_return': pos_return,
        'negative_surprise_return': neg_return,
        'drift_magnitude': drift_magnitude,
        'drift_persistence': abs(drift_magnitude) / (aligned['returns'].std() + 1e-8)
    }


if __name__ == "__main__":
    # Example usage
    print("Event-Driven Strategies Demo")
    print("=" * 50)
    
    # Merger arbitrage example
    merger = merger_arbitrage_spread(50, 100, 55, deal_probability=0.8)
    print("\nMerger Arbitrage:")
    for key, value in merger.items():
        print(f"  {key}: {value:.4f}")
