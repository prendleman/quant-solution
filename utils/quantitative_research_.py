"""
Quantitative Research Tools

Research frameworks, signal generation, and hypothesis testing for quant strategies.
Generated as part of quant portfolio development.
"""

from typing import Optional, Dict, List, Tuple
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize


def signal_to_noise_ratio(returns: pd.Series, lookback: int = 60) -> pd.Series:
    """
    Calculate signal-to-noise ratio (mean return / volatility).
    
    Args:
        returns: Return series
        lookback: Rolling window size
        
    Returns:
        Series of signal-to-noise ratios
    """
    rolling_mean = returns.rolling(window=lookback).mean()
    rolling_std = returns.rolling(window=lookback).std()
    snr = rolling_mean / rolling_std
    return snr


def calculate_information_coefficient(predictions: pd.Series, actuals: pd.Series,
                                     window: int = 60) -> pd.Series:
    """
    Calculate Information Coefficient (IC) - correlation between predictions and actuals.
    
    Args:
        predictions: Predicted returns/signals
        actuals: Actual returns
        window: Rolling window for IC calculation
        
    Returns:
        Series of Information Coefficients
    """
    aligned = pd.concat([predictions, actuals], axis=1).dropna()
    predictions_aligned = aligned.iloc[:, 0]
    actuals_aligned = aligned.iloc[:, 1]
    
    ic_series = []
    for i in range(window, len(aligned)):
        pred_window = predictions_aligned.iloc[i-window:i]
        actual_window = actuals_aligned.iloc[i-window:i]
        ic = pred_window.corr(actual_window)
        ic_series.append(ic)
    
    return pd.Series(ic_series, index=aligned.index[window:])


def factor_analysis(returns: pd.DataFrame, n_factors: int = 3) -> Dict:
    """
    Principal Component Analysis for factor identification.
    
    Args:
        returns: DataFrame of asset returns
        n_factors: Number of factors to extract
        
    Returns:
        Dictionary with factor loadings and explained variance
    """
    from sklearn.decomposition import PCA
    
    # Remove NaN
    returns_clean = returns.dropna()
    
    # Standardize
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    returns_scaled = scaler.fit_transform(returns_clean)
    
    # PCA
    pca = PCA(n_components=n_factors)
    factors = pca.fit_transform(returns_scaled)
    
    # Factor loadings
    factor_loadings = pd.DataFrame(
        pca.components_.T,
        columns=[f'Factor_{i+1}' for i in range(n_factors)],
        index=returns_clean.columns
    )
    
    return {
        'factors': pd.DataFrame(factors, index=returns_clean.index),
        'factor_loadings': factor_loadings,
        'explained_variance': pca.explained_variance_ratio_,
        'cumulative_variance': np.cumsum(pca.explained_variance_ratio_)
    }


def regime_detection(returns: pd.Series, n_regimes: int = 2, window: int = 60) -> pd.Series:
    """
    Detect market regimes using rolling statistics.
    
    Args:
        returns: Return series
        n_regimes: Number of regimes to detect
        window: Rolling window size
        
    Returns:
        Series of regime labels
    """
    # Calculate rolling volatility
    rolling_vol = returns.rolling(window=window).std()
    
    # Simple threshold-based regime detection
    vol_threshold = rolling_vol.quantile(0.5)
    regimes = pd.Series(0, index=returns.index)
    regimes[rolling_vol > vol_threshold] = 1  # High volatility regime
    
    return regimes


def sharpe_ratio_test(returns1: pd.Series, returns2: pd.Series) -> Dict:
    """
    Test for difference in Sharpe ratios between two strategies.
    
    Args:
        returns1: First strategy returns
        returns2: Second strategy returns
        
    Returns:
        Dictionary with test results
    """
    # Calculate Sharpe ratios
    sharpe1 = returns1.mean() / returns1.std() * np.sqrt(252)
    sharpe2 = returns2.mean() / returns2.std() * np.sqrt(252)
    
    # Difference
    diff = sharpe1 - sharpe2
    
    # Simplified test (for demonstration)
    # In practice, use more sophisticated tests like Jobson-Korkie test
    se_diff = np.sqrt((1 / len(returns1)) + (1 / len(returns2)))
    z_stat = diff / se_diff
    p_value = 2 * (1 - norm.cdf(abs(z_stat)))
    
    return {
        'sharpe1': sharpe1,
        'sharpe2': sharpe2,
        'difference': diff,
        'z_statistic': z_stat,
        'p_value': p_value,
        'is_significant': p_value < 0.05
    }


def research_backtest(signals: pd.Series, returns: pd.Series,
                     transaction_cost: float = 0.001) -> Dict:
    """
    Simple research backtest to evaluate signal quality.
    
    Args:
        signals: Trading signals (-1, 0, 1)
        returns: Asset returns
        transaction_cost: Cost per trade
        
    Returns:
        Dictionary with backtest results
    """
    aligned = pd.concat([signals, returns], axis=1).dropna()
    signals_aligned = aligned.iloc[:, 0]
    returns_aligned = aligned.iloc[:, 1]
    
    # Strategy returns
    strategy_returns = signals_aligned.shift(1) * returns_aligned
    
    # Transaction costs
    trades = (signals_aligned.diff() != 0).astype(int)
    costs = trades * transaction_cost
    net_returns = strategy_returns - costs
    
    # Metrics
    total_return = (1 + net_returns).prod() - 1
    sharpe = net_returns.mean() / net_returns.std() * np.sqrt(252) if net_returns.std() > 0 else 0
    win_rate = (net_returns > 0).sum() / len(net_returns[net_returns != 0]) if (net_returns != 0).any() else 0
    
    return {
        'total_return': total_return,
        'sharpe_ratio': sharpe,
        'win_rate': win_rate,
        'num_trades': trades.sum(),
        'strategy_returns': net_returns
    }


def feature_importance_analysis(returns: pd.Series, features: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze feature importance for return prediction.
    
    Args:
        returns: Target returns
        features: DataFrame of features
        
    Returns:
        DataFrame with feature importance scores
    """
    from sklearn.ensemble import RandomForestRegressor
    
    # Align data
    aligned = pd.concat([returns, features], axis=1).dropna()
    y = aligned.iloc[:, 0]
    X = aligned.iloc[:, 1:]
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Feature importance
    importance_df = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    return importance_df


if __name__ == "__main__":
    # Example usage
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    returns = pd.Series(np.random.randn(500) * 0.01, index=dates)
    
    # Signal-to-noise ratio
    snr = signal_to_noise_ratio(returns)
    print(f"Current Signal-to-Noise Ratio: {snr.iloc[-1]:.4f}")
    
    # Regime detection
    regimes = regime_detection(returns)
    print(f"\nRegime Distribution:")
    print(regimes.value_counts())
    
    # Feature importance (example)
    features = pd.DataFrame({
        'momentum': returns.rolling(10).mean(),
        'volatility': returns.rolling(20).std(),
        'rsi': returns.rolling(14).apply(lambda x: 100 - 100/(1 + (x[x>0].sum()/abs(x[x<0].sum())) if (x<0).any() else 1))
    }, index=dates)
    
    importance = feature_importance_analysis(returns, features)
    print(f"\nFeature Importance:")
    print(importance)
