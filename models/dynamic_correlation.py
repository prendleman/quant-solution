"""
Dynamic Correlation Models

Time-varying correlation models including DCC-GARCH, rolling correlation,
and regime-dependent correlations.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd


def rolling_correlation(returns1: pd.Series, returns2: pd.Series,
                       window: int = 60) -> pd.Series:
    """
    Calculate rolling correlation between two return series.
    
    Args:
        returns1: First return series
        returns2: Second return series
        window: Rolling window size
        
    Returns:
        Series of rolling correlations
    """
    aligned = pd.DataFrame({
        'r1': returns1,
        'r2': returns2
    }).dropna()
    
    rolling_corr = aligned['r1'].rolling(window=window).corr(aligned['r2'])
    
    return rolling_corr


def dcc_garch_correlation(returns_df: pd.DataFrame, window: int = 60) -> pd.DataFrame:
    """
    Simplified DCC-GARCH correlation model.
    
    Args:
        returns_df: DataFrame of returns
        window: Estimation window
        
    Returns:
        DataFrame of dynamic correlations
    """
    # Simplified DCC: use rolling correlation with volatility adjustment
    n_assets = len(returns_df.columns)
    correlations = pd.DataFrame(index=returns_df.index, columns=returns_df.columns)
    
    for i, asset1 in enumerate(returns_df.columns):
        for j, asset2 in enumerate(returns_df.columns):
            if i == j:
                correlations.loc[:, asset1] = 1.0
            else:
                # Rolling correlation
                rolling_corr = returns_df[asset1].rolling(window=window).corr(returns_df[asset2])
                correlations.loc[:, asset1] = rolling_corr.fillna(0.5)  # Default correlation
    
    return correlations


def regime_dependent_correlation(returns_df: pd.DataFrame, regimes: pd.Series) -> Dict[str, pd.DataFrame]:
    """
    Calculate correlation matrices for different regimes.
    
    Args:
        returns_df: DataFrame of returns
        regimes: Series of regime indicators
        
    Returns:
        Dictionary with correlation matrices for each regime
    """
    regime_correlations = {}
    
    for regime in regimes.unique():
        regime_mask = regimes == regime
        regime_returns = returns_df[regime_mask]
        
        if len(regime_returns) > 10:
            corr_matrix = regime_returns.corr()
            regime_correlations[f'regime_{regime}'] = corr_matrix
    
    return regime_correlations


def correlation_break_detection(returns1: pd.Series, returns2: pd.Series,
                                window: int = 60) -> Dict[str, pd.Series]:
    """
    Detect structural breaks in correlation.
    
    Args:
        returns1: First return series
        returns2: Second return series
        window: Rolling window
        
    Returns:
        Dictionary with break detection results
    """
    # Rolling correlation
    rolling_corr = rolling_correlation(returns1, returns2, window)
    
    # Detect breaks (significant changes)
    corr_changes = rolling_corr.diff().abs()
    break_threshold = corr_changes.quantile(0.95)
    breaks = corr_changes > break_threshold
    
    return {
        'rolling_correlation': rolling_corr,
        'correlation_changes': corr_changes,
        'break_points': breaks,
        'n_breaks': breaks.sum()
    }


def average_correlation_matrix(returns_df: pd.DataFrame, window: int = 60) -> pd.DataFrame:
    """
    Calculate average correlation matrix over rolling windows.
    
    Args:
        returns_df: DataFrame of returns
        window: Rolling window size
        
    Returns:
        Average correlation matrix
    """
    n_assets = len(returns_df.columns)
    avg_corr = np.zeros((n_assets, n_assets))
    
    for i in range(window, len(returns_df)):
        window_returns = returns_df.iloc[i-window:i]
        corr_matrix = window_returns.corr().values
        avg_corr += corr_matrix
    
    avg_corr = avg_corr / (len(returns_df) - window)
    
    return pd.DataFrame(avg_corr, index=returns_df.columns, columns=returns_df.columns)


if __name__ == "__main__":
    # Example usage
    print("Dynamic Correlation Models Demo")
    print("=" * 50)
    
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=252, freq='D')
    returns1 = pd.Series(np.random.randn(252) * 0.01, index=dates)
    returns2 = pd.Series(np.random.randn(252) * 0.01, index=dates)
    
    # Rolling correlation
    rolling_corr = rolling_correlation(returns1, returns2, window=60)
    print(f"\nAverage Rolling Correlation: {rolling_corr.mean():.4f}")
