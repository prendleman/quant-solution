"""
Financial Data Analysis

Statistical analysis, correlation analysis, and data quality checks.
Generated as part of quant portfolio development.
"""

from typing import Optional, Dict, List
import numpy as np
import pandas as pd
from scipy import stats


def analyze_returns(returns: pd.Series) -> Dict:
    """
    Comprehensive analysis of return series.
    
    Args:
        returns: Series of returns
        
    Returns:
        Dictionary with statistical metrics
    """
    results = {
        'mean': returns.mean(),
        'std': returns.std(),
        'skewness': stats.skew(returns.dropna()),
        'kurtosis': stats.kurtosis(returns.dropna()),
        'min': returns.min(),
        'max': returns.max(),
        'sharpe_ratio': returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0,
        'positive_days': (returns > 0).sum(),
        'negative_days': (returns < 0).sum(),
        'zero_days': (returns == 0).sum()
    }
    
    # Percentiles
    for p in [1, 5, 25, 50, 75, 95, 99]:
        results[f'percentile_{p}'] = returns.quantile(p / 100)
    
    return results


def correlation_analysis(data: pd.DataFrame, method: str = 'pearson') -> pd.DataFrame:
    """
    Calculate correlation matrix and identify significant relationships.
    
    Args:
        data: DataFrame with numeric columns
        method: Correlation method ('pearson', 'spearman', 'kendall')
        
    Returns:
        Correlation matrix
    """
    return data.corr(method=method)


def detect_outliers(data: pd.Series, method: str = 'iqr', threshold: float = 3.0) -> pd.Series:
    """
    Detect outliers in data series.
    
    Args:
        data: Data series
        method: 'iqr' (Interquartile Range) or 'zscore'
        threshold: Threshold for outlier detection
        
    Returns:
        Boolean series indicating outliers
    """
    if method == 'iqr':
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        outliers = (data < lower_bound) | (data > upper_bound)
    else:  # zscore
        z_scores = np.abs(stats.zscore(data.dropna()))
        outliers = pd.Series(False, index=data.index)
        outliers[data.dropna().index] = z_scores > threshold
    
    return outliers


def rolling_statistics(data: pd.Series, window: int = 30) -> pd.DataFrame:
    """
    Calculate rolling statistics for time series.
    
    Args:
        data: Time series data
        window: Rolling window size
        
    Returns:
        DataFrame with rolling statistics
    """
    stats_df = pd.DataFrame(index=data.index)
    stats_df['mean'] = data.rolling(window).mean()
    stats_df['std'] = data.rolling(window).std()
    stats_df['min'] = data.rolling(window).min()
    stats_df['max'] = data.rolling(window).max()
    stats_df['skew'] = data.rolling(window).apply(lambda x: stats.skew(x.dropna()))
    stats_df['kurtosis'] = data.rolling(window).apply(lambda x: stats.kurtosis(x.dropna()))
    
    return stats_df


def stationarity_test(data: pd.Series, test_type: str = 'adf') -> Dict:
    """
    Test for stationarity using Augmented Dickey-Fuller test.
    
    Args:
        data: Time series data
        test_type: Type of test ('adf' for Augmented Dickey-Fuller)
        
    Returns:
        Dictionary with test results
    """
    from statsmodels.tsa.stattools import adfuller
    
    if test_type == 'adf':
        result = adfuller(data.dropna())
        return {
            'adf_statistic': result[0],
            'p_value': result[1],
            'critical_values': result[4],
            'is_stationary': result[1] < 0.05
        }
    else:
        return {'error': f'Unknown test type: {test_type}'}


def data_quality_report(data: pd.DataFrame) -> pd.DataFrame:
    """
    Generate data quality report.
    
    Args:
        data: DataFrame to analyze
        
    Returns:
        DataFrame with quality metrics per column
    """
    report = pd.DataFrame(index=data.columns)
    report['dtype'] = data.dtypes
    report['non_null_count'] = data.count()
    report['null_count'] = data.isnull().sum()
    report['null_percentage'] = (data.isnull().sum() / len(data)) * 100
    report['unique_values'] = data.nunique()
    report['duplicate_rows'] = data.duplicated().sum()
    
    # For numeric columns
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        report.loc[col, 'mean'] = data[col].mean()
        report.loc[col, 'std'] = data[col].std()
        report.loc[col, 'min'] = data[col].min()
        report.loc[col, 'max'] = data[col].max()
    
    return report


if __name__ == "__main__":
    # Example usage
    dates = pd.date_range('2020-01-01', periods=252, freq='D')
    returns = pd.Series(np.random.randn(252) * 0.01, index=dates)
    
    # Analyze returns
    analysis = analyze_returns(returns)
    print("Return Analysis:")
    print(f"  Mean: {analysis['mean']:.4f}")
    print(f"  Std: {analysis['std']:.4f}")
    print(f"  Sharpe Ratio: {analysis['sharpe_ratio']:.4f}")
    print(f"  Skewness: {analysis['skewness']:.4f}")
    
    # Rolling statistics
    rolling_stats = rolling_statistics(returns, window=30)
    print(f"\nRolling Statistics (30-day window):")
    print(f"  Current Mean: {rolling_stats['mean'].iloc[-1]:.4f}")
    print(f"  Current Std: {rolling_stats['std'].iloc[-1]:.4f}")
    
    # Outlier detection
    outliers = detect_outliers(returns, method='iqr')
    print(f"\nOutliers detected: {outliers.sum()} ({outliers.sum()/len(returns)*100:.2f}%)")
