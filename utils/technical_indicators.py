"""
Technical Indicators

Comprehensive collection of technical analysis indicators.
Generated as part of quant portfolio development.
"""

from typing import Optional, Tuple
import numpy as np
import pandas as pd


def moving_average(prices: pd.Series, window: int, ma_type: str = 'simple') -> pd.Series:
    """
    Calculate moving average.
    
    Args:
        prices: Price series
        window: Window size
        ma_type: 'simple', 'exponential', or 'weighted'
        
    Returns:
        Moving average series
    """
    if ma_type == 'simple':
        return prices.rolling(window=window).mean()
    elif ma_type == 'exponential':
        return prices.ewm(span=window, adjust=False).mean()
    elif ma_type == 'weighted':
        weights = np.arange(1, window + 1)
        return prices.rolling(window=window).apply(
            lambda x: np.average(x, weights=weights), raw=True
        )
    else:
        raise ValueError(f"Unknown MA type: {ma_type}")


def bollinger_bands(prices: pd.Series, window: int = 20, num_std: float = 2) -> pd.DataFrame:
    """
    Calculate Bollinger Bands.
    
    Args:
        prices: Price series
        window: Moving average window
        num_std: Number of standard deviations
        
    Returns:
        DataFrame with upper, middle, lower bands
    """
    ma = moving_average(prices, window)
    std = prices.rolling(window=window).std()
    
    upper = ma + (std * num_std)
    lower = ma - (std * num_std)
    
    return pd.DataFrame({
        'upper': upper,
        'middle': ma,
        'lower': lower
    })


def macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    Args:
        prices: Price series
        fast: Fast EMA period
        slow: Slow EMA period
        signal: Signal line EMA period
        
    Returns:
        DataFrame with MACD, signal, and histogram
    """
    ema_fast = moving_average(prices, fast, 'exponential')
    ema_slow = moving_average(prices, slow, 'exponential')
    
    macd_line = ema_fast - ema_slow
    signal_line = moving_average(macd_line, signal, 'exponential')
    histogram = macd_line - signal_line
    
    return pd.DataFrame({
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    })


def stochastic_oscillator(high: pd.Series, low: pd.Series, close: pd.Series,
                          k_window: int = 14, d_window: int = 3) -> pd.DataFrame:
    """
    Calculate Stochastic Oscillator.
    
    Args:
        high: High prices
        low: Low prices
        close: Close prices
        k_window: %K period
        d_window: %D period
        
    Returns:
        DataFrame with %K and %D
    """
    lowest_low = low.rolling(window=k_window).min()
    highest_high = high.rolling(window=k_window).max()
    
    k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    d_percent = k_percent.rolling(window=d_window).mean()
    
    return pd.DataFrame({
        'k_percent': k_percent,
        'd_percent': d_percent
    })


def atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    """
    Calculate Average True Range (ATR).
    
    Args:
        high: High prices
        low: Low prices
        close: Close prices
        window: ATR period
        
    Returns:
        ATR series
    """
    high_low = high - low
    high_close = np.abs(high - close.shift())
    low_close = np.abs(low - close.shift())
    
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=window).mean()
    
    return atr


def adx(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    """
    Calculate Average Directional Index (ADX).
    
    Args:
        high: High prices
        low: Low prices
        close: Close prices
        window: ADX period
        
    Returns:
        ADX series
    """
    # Calculate +DM and -DM
    high_diff = high.diff()
    low_diff = -low.diff()
    
    plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
    minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
    
    # Calculate ATR
    atr_series = atr(high, low, close, window)
    
    # Calculate +DI and -DI
    plus_di = 100 * (plus_dm.rolling(window=window).mean() / atr_series)
    minus_di = 100 * (minus_dm.rolling(window=window).mean() / atr_series)
    
    # Calculate DX
    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
    
    # Calculate ADX
    adx = dx.rolling(window=window).mean()
    
    return adx


def williams_r(high: pd.Series, low: pd.Series, close: pd.Series,
               window: int = 14) -> pd.Series:
    """
    Calculate Williams %R.
    
    Args:
        high: High prices
        low: Low prices
        close: Close prices
        window: Period
        
    Returns:
        Williams %R series
    """
    highest_high = high.rolling(window=window).max()
    lowest_low = low.rolling(window=window).min()
    
    wr = -100 * ((highest_high - close) / (highest_high - lowest_low))
    
    return wr


def commodity_channel_index(high: pd.Series, low: pd.Series, close: pd.Series,
                           window: int = 20) -> pd.Series:
    """
    Calculate Commodity Channel Index (CCI).
    
    Args:
        high: High prices
        low: Low prices
        close: Close prices
        window: Period
        
    Returns:
        CCI series
    """
    typical_price = (high + low + close) / 3
    sma = typical_price.rolling(window=window).mean()
    mad = typical_price.rolling(window=window).apply(
        lambda x: np.abs(x - x.mean()).mean()
    )
    
    cci = (typical_price - sma) / (0.015 * mad)
    
    return cci


def fibonacci_retracement(high: float, low: float) -> Dict[str, float]:
    """
    Calculate Fibonacci retracement levels.
    
    Args:
        high: High price
        low: Low price
        
    Returns:
        Dictionary with retracement levels
    """
    diff = high - low
    levels = [0.236, 0.382, 0.5, 0.618, 0.786]
    
    retracements = {}
    for level in levels:
        retracements[f'level_{level}'] = high - (diff * level)
    
    return retracements


if __name__ == "__main__":
    # Example usage
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    prices = pd.Series(100 + np.cumsum(np.random.randn(500) * 0.5), index=dates)
    high = prices * 1.01
    low = prices * 0.99
    
    # Moving averages
    sma = moving_average(prices, 20)
    ema = moving_average(prices, 20, 'exponential')
    print(f"Current SMA: {sma.iloc[-1]:.2f}, EMA: {ema.iloc[-1]:.2f}")
    
    # Bollinger Bands
    bb = bollinger_bands(prices)
    print(f"\nBollinger Bands:")
    print(f"  Upper: {bb['upper'].iloc[-1]:.2f}")
    print(f"  Lower: {bb['lower'].iloc[-1]:.2f}")
    
    # MACD
    macd_data = macd(prices)
    print(f"\nMACD: {macd_data['macd'].iloc[-1]:.4f}")
    print(f"Signal: {macd_data['signal'].iloc[-1]:.4f}")
