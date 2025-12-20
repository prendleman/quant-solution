"""
Factor Timing Strategies

Dynamic factor exposure, factor rotation, and timing strategies
based on factor performance and regime changes.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd


def factor_momentum_timing(factor_returns: pd.DataFrame, lookback: int = 60) -> pd.Series:
    """
    Generate factor timing signals based on momentum.
    
    Args:
        factor_returns: DataFrame of factor returns
        lookback: Momentum lookback period
        
    Returns:
        Series of factor timing signals
    """
    # Calculate momentum for each factor
    momentum = factor_returns.rolling(window=lookback).mean()
    
    # Select factor with highest momentum
    best_factor = momentum.idxmax(axis=1)
    
    # Signal: 1 for best factor, 0 otherwise
    signals = pd.Series(0, index=factor_returns.index)
    for i, factor in enumerate(best_factor):
        signals.iloc[i] = 1 if not pd.isna(factor) else 0
    
    return signals


def factor_regime_timing(factor_returns: pd.DataFrame, market_regime: pd.Series) -> Dict[str, pd.Series]:
    """
    Time factor exposure based on market regime.
    
    Args:
        factor_returns: DataFrame of factor returns
        market_regime: Series of market regime indicators
        
    Returns:
        Dictionary with regime-specific factor exposures
    """
    regime_exposures = {}
    
    for regime in market_regime.unique():
        regime_mask = market_regime == regime
        regime_returns = factor_returns[regime_mask]
        
        if len(regime_returns) > 10:
            # Factor performance in this regime
            factor_performance = regime_returns.mean()
            # Weight by performance
            exposures = factor_performance / (factor_performance.abs().sum() + 1e-8)
            regime_exposures[f'regime_{regime}'] = exposures
    
    return regime_exposures


def factor_rotation_strategy(factor_returns: pd.DataFrame, rebalance_frequency: int = 20) -> pd.Series:
    """
    Factor rotation strategy - rotate to best-performing factors.
    
    Args:
        factor_returns: DataFrame of factor returns
        rebalance_frequency: Rebalancing frequency
        
    Returns:
        Series of portfolio returns
    """
    portfolio_returns = []
    current_weights = pd.Series(1.0 / len(factor_returns.columns), index=factor_returns.columns)
    
    for i in range(len(factor_returns)):
        # Rebalance periodically
        if i > 0 and i % rebalance_frequency == 0:
            # Recent factor performance
            recent_performance = factor_returns.iloc[i-20:i].mean()
            
            # Rotate to top factors
            top_factors = recent_performance.nlargest(3).index
            current_weights = pd.Series(0.0, index=factor_returns.columns)
            current_weights[top_factors] = 1.0 / len(top_factors)
        
        # Portfolio return
        portfolio_return = (factor_returns.iloc[i] * current_weights).sum()
        portfolio_returns.append(portfolio_return)
    
    return pd.Series(portfolio_returns, index=factor_returns.index)


def dynamic_factor_exposure(returns: pd.Series, factor_returns: pd.DataFrame,
                           window: int = 60) -> pd.Series:
    """
    Calculate dynamic factor exposure using rolling regression.
    
    Args:
        returns: Asset returns
        factor_returns: Factor returns
        window: Rolling window size
        
    Returns:
        Series of dynamic factor exposures
    """
    from sklearn.linear_model import LinearRegression
    
    exposures = []
    
    for i in range(window, len(returns)):
        y = returns.iloc[i-window:i]
        X = factor_returns.iloc[i-window:i]
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Total exposure (sum of absolute betas)
        total_exposure = np.abs(model.coef_).sum()
        exposures.append(total_exposure)
    
    # Pad with initial exposure
    initial_exposures = [exposures[0]] * window if exposures else [0.0] * window
    
    return pd.Series(initial_exposures + exposures, index=returns.index)


if __name__ == "__main__":
    # Example usage
    print("Factor Timing Strategies Demo")
    print("=" * 50)
    
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=252, freq='D')
    factor_returns = pd.DataFrame({
        'Value': np.random.randn(252) * 0.01,
        'Momentum': np.random.randn(252) * 0.01,
        'Quality': np.random.randn(252) * 0.01
    }, index=dates)
    
    # Factor rotation
    strategy_returns = factor_rotation_strategy(factor_returns)
    print(f"\nFactor Rotation Sharpe: {strategy_returns.mean() / strategy_returns.std() * np.sqrt(252):.4f}")
