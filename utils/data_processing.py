"""
Data Processing and Cleaning

Financial data cleaning, normalization, and preprocessing utilities.
Generated as part of quant portfolio development.
"""

from typing import Optional, List, Dict, Tuple
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler, RobustScaler


def clean_financial_data(data: pd.DataFrame, method: str = 'forward_fill') -> pd.DataFrame:
    """
    Clean financial data by handling missing values and outliers.
    
    Args:
        data: DataFrame with financial data
        method: 'forward_fill', 'backward_fill', 'interpolate', or 'drop'
        
    Returns:
        Cleaned DataFrame
    """
    cleaned = data.copy()
    
    # Handle missing values
    if method == 'forward_fill':
        cleaned = cleaned.fillna(method='ffill').fillna(method='bfill')
    elif method == 'backward_fill':
        cleaned = cleaned.fillna(method='bfill').fillna(method='ffill')
    elif method == 'interpolate':
        cleaned = cleaned.interpolate(method='linear')
    elif method == 'drop':
        cleaned = cleaned.dropna()
    
    return cleaned


def winsorize_data(data: pd.Series, limits: Tuple[float, float] = (0.01, 0.99)) -> pd.Series:
    """
    Winsorize data to handle outliers.
    
    Args:
        data: Data series
        limits: Tuple of (lower_percentile, upper_percentile)
        
    Returns:
        Winsorized series
    """
    lower = data.quantile(limits[0])
    upper = data.quantile(limits[1])
    
    winsorized = data.copy()
    winsorized[winsorized < lower] = lower
    winsorized[winsorized > upper] = upper
    
    return winsorized


def normalize_returns(returns: pd.Series, method: str = 'zscore') -> pd.Series:
    """
    Normalize return series.
    
    Args:
        returns: Return series
        method: 'zscore', 'minmax', or 'robust'
        
    Returns:
        Normalized series
    """
    if method == 'zscore':
        return (returns - returns.mean()) / returns.std()
    elif method == 'minmax':
        return (returns - returns.min()) / (returns.max() - returns.min())
    elif method == 'robust':
        scaler = RobustScaler()
        return pd.Series(
            scaler.fit_transform(returns.values.reshape(-1, 1)).flatten(),
            index=returns.index
        )
    else:
        raise ValueError(f"Unknown method: {method}")


def calculate_rolling_zscore(data: pd.Series, window: int = 60) -> pd.Series:
    """
    Calculate rolling z-score.
    
    Args:
        data: Data series
        window: Rolling window size
        
    Returns:
        Series of z-scores
    """
    rolling_mean = data.rolling(window=window).mean()
    rolling_std = data.rolling(window=window).std()
    zscore = (data - rolling_mean) / rolling_std
    return zscore


def detect_structural_breaks(data: pd.Series, method: str = 'cusum') -> List[int]:
    """
    Detect structural breaks in time series.
    
    Args:
        data: Time series data
        method: 'cusum' (Cumulative Sum) or 'chow'
        
    Returns:
        List of indices where breaks occur
    """
    if method == 'cusum':
        # CUSUM test for structural breaks
        mean = data.mean()
        cumsum = (data - mean).cumsum()
        cumsum_abs = cumsum.abs()
        
        # Find points where cumulative sum deviates significantly
        threshold = cumsum_abs.std() * 2
        breaks = []
        
        for i in range(1, len(cumsum_abs)):
            if cumsum_abs.iloc[i] > threshold and cumsum_abs.iloc[i-1] <= threshold:
                breaks.append(i)
        
        return breaks
    else:
        # Simplified Chow test
        n = len(data)
        breaks = []
        
        for i in range(n // 4, 3 * n // 4, n // 10):
            # Split data and test for difference in means
            segment1 = data.iloc[:i]
            segment2 = data.iloc[i:]
            
            if len(segment1) > 10 and len(segment2) > 10:
                mean1 = segment1.mean()
                mean2 = segment2.mean()
                std1 = segment1.std()
                std2 = segment2.std()
                
                # Simple test
                if abs(mean1 - mean2) > (std1 + std2) / 2:
                    breaks.append(i)
        
        return breaks


def align_dataframes(df1: pd.DataFrame, df2: pd.DataFrame,
                    method: str = 'inner') -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Align two DataFrames by index.
    
    Args:
        df1: First DataFrame
        df2: Second DataFrame
        method: 'inner', 'outer', 'left', or 'right'
        
    Returns:
        Tuple of aligned DataFrames
    """
    if method == 'inner':
        common_index = df1.index.intersection(df2.index)
    elif method == 'outer':
        common_index = df1.index.union(df2.index)
    elif method == 'left':
        common_index = df1.index
    elif method == 'right':
        common_index = df2.index
    else:
        raise ValueError(f"Unknown method: {method}")
    
    df1_aligned = df1.reindex(common_index)
    df2_aligned = df2.reindex(common_index)
    
    return df1_aligned, df2_aligned


def calculate_returns_from_prices(prices: pd.DataFrame, method: str = 'simple') -> pd.DataFrame:
    """
    Calculate returns from price data.
    
    Args:
        prices: DataFrame of prices
        method: 'simple' or 'log'
        
    Returns:
        DataFrame of returns
    """
    if method == 'simple':
        return prices.pct_change().dropna()
    elif method == 'log':
        return np.log(prices / prices.shift(1)).dropna()
    else:
        raise ValueError(f"Unknown method: {method}")


def resample_data(data: pd.Series, freq: str = 'W', method: str = 'last') -> pd.Series:
    """
    Resample time series data to different frequency.
    
    Args:
        data: Time series data
        freq: Target frequency ('D', 'W', 'M', 'Q', 'Y')
        method: 'last', 'first', 'mean', 'sum'
        
    Returns:
        Resampled series
    """
    if method == 'last':
        return data.resample(freq).last()
    elif method == 'first':
        return data.resample(freq).first()
    elif method == 'mean':
        return data.resample(freq).mean()
    elif method == 'sum':
        return data.resample(freq).sum()
    else:
        raise ValueError(f"Unknown method: {method}")


if __name__ == "__main__":
    # Example usage
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    prices = pd.Series(100 + np.cumsum(np.random.randn(500) * 0.5), index=dates)
    
    # Clean data
    prices_with_nan = prices.copy()
    prices_with_nan.iloc[10:15] = np.nan
    cleaned = clean_financial_data(pd.DataFrame({'price': prices_with_nan}))
    print(f"Cleaned data: {len(cleaned)} rows")
    
    # Winsorize
    winsorized = winsorize_data(prices, limits=(0.05, 0.95))
    print(f"\nWinsorized data range: [{winsorized.min():.2f}, {winsorized.max():.2f}]")
    
    # Structural breaks
    breaks = detect_structural_breaks(prices)
    print(f"\nStructural breaks detected at indices: {breaks}")
