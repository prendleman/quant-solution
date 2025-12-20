"""
High-Frequency Data Analysis

Analysis of tick data, order flow, and high-frequency trading patterns.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd


def tick_data_analysis(ticks: pd.DataFrame) -> Dict[str, float]:
    """
    Analyze tick-by-tick data.
    
    Args:
        ticks: DataFrame with columns: 'price', 'volume', 'timestamp'
        
    Returns:
        Dictionary with tick analysis metrics
    """
    # Price changes
    price_changes = ticks['price'].diff()
    
    # Tick direction
    tick_direction = np.sign(price_changes)
    
    # Volume-weighted metrics
    vwap = (ticks['price'] * ticks['volume']).sum() / ticks['volume'].sum()
    
    # Trade intensity
    time_diffs = ticks['timestamp'].diff().dt.total_seconds()
    trade_intensity = 1 / (time_diffs.mean() + 1e-8)
    
    return {
        'total_ticks': len(ticks),
        'price_range': ticks['price'].max() - ticks['price'].min(),
        'vwap': vwap,
        'trade_intensity': trade_intensity,
        'up_ticks': (tick_direction > 0).sum(),
        'down_ticks': (tick_direction < 0).sum(),
        'zero_ticks': (tick_direction == 0).sum()
    }


def order_flow_imbalance(bid_volumes: pd.Series, ask_volumes: pd.Series) -> pd.Series:
    """
    Calculate order flow imbalance.
    
    Args:
        bid_volumes: Series of bid volumes
        ask_volumes: Series of ask volumes
        
    Returns:
        Series of order flow imbalance
    """
    total_volume = bid_volumes + ask_volumes
    imbalance = (bid_volumes - ask_volumes) / (total_volume + 1e-8)
    
    return imbalance


def realized_volatility_high_freq(returns: pd.Series, window: int = 5) -> pd.Series:
    """
    Calculate realized volatility from high-frequency returns.
    
    Args:
        returns: High-frequency returns
        window: Aggregation window
        
    Returns:
        Series of realized volatility
    """
    # Sum of squared returns over window
    realized_var = returns.rolling(window=window).apply(lambda x: (x ** 2).sum())
    realized_vol = np.sqrt(realized_var)
    
    return realized_vol


def microstructure_noise(observed_prices: pd.Series, true_prices: Optional[pd.Series] = None) -> Dict[str, float]:
    """
    Estimate microstructure noise.
    
    Args:
        observed_prices: Observed transaction prices
        true_prices: True prices (if None, use mid-price approximation)
        
    Returns:
        Dictionary with noise metrics
    """
    if true_prices is None:
        # Approximate true price as rolling mean
        true_prices = observed_prices.rolling(window=5).mean()
    
    # Noise
    noise = observed_prices - true_prices
    
    return {
        'noise_std': noise.std(),
        'noise_mean': noise.mean(),
        'noise_to_signal_ratio': noise.std() / (observed_prices.std() + 1e-8)
    }


def volume_profile(ticks: pd.DataFrame, price_bins: int = 20) -> pd.DataFrame:
    """
    Calculate volume profile (volume at each price level).
    
    Args:
        ticks: DataFrame with 'price' and 'volume'
        price_bins: Number of price bins
        
    Returns:
        DataFrame with volume profile
    """
    # Create price bins
    price_min = ticks['price'].min()
    price_max = ticks['price'].max()
    bins = np.linspace(price_min, price_max, price_bins + 1)
    
    # Aggregate volume by price bin
    ticks['price_bin'] = pd.cut(ticks['price'], bins=bins)
    volume_profile = ticks.groupby('price_bin')['volume'].sum()
    
    return volume_profile


if __name__ == "__main__":
    # Example usage
    print("High-Frequency Analysis Demo")
    print("=" * 50)
    
    # Generate sample tick data
    np.random.seed(42)
    n_ticks = 1000
    ticks = pd.DataFrame({
        'price': 100 + np.cumsum(np.random.randn(n_ticks) * 0.1),
        'volume': np.random.randint(100, 1000, n_ticks),
        'timestamp': pd.date_range('2020-01-01', periods=n_ticks, freq='1min')
    })
    
    # Tick analysis
    analysis = tick_data_analysis(ticks)
    print("\nTick Data Analysis:")
    for key, value in analysis.items():
        print(f"  {key}: {value:.4f}")
