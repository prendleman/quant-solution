"""
Tail Risk and Extreme Risk Analysis

Advanced tail risk measures including Expected Shortfall, Tail VaR,
and extreme event modeling.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats


def expected_shortfall(returns: pd.Series, confidence_level: float = 0.95) -> float:
    """
    Calculate Expected Shortfall (Conditional VaR) - average loss beyond VaR.
    
    Args:
        returns: Series of returns
        confidence_level: Confidence level (e.g., 0.95 for 95%)
        
    Returns:
        Expected Shortfall
    """
    var = returns.quantile(1 - confidence_level)
    tail_losses = returns[returns <= var]
    
    if len(tail_losses) == 0:
        return returns.min()
    
    return tail_losses.mean()


def tail_value_at_risk(returns: pd.Series, confidence_level: float = 0.95) -> float:
    """
    Tail VaR - same as Expected Shortfall.
    
    Args:
        returns: Series of returns
        confidence_level: Confidence level
        
    Returns:
        Tail VaR
    """
    return expected_shortfall(returns, confidence_level)


def maximum_drawdown_duration(equity_curve: pd.Series) -> Dict[str, float]:
    """
    Calculate maximum drawdown duration.
    
    Args:
        equity_curve: Series of cumulative returns or equity values
        
    Returns:
        Dictionary with drawdown duration metrics
    """
    running_max = equity_curve.expanding().max()
    drawdown = (equity_curve - running_max) / running_max
    
    # Find drawdown periods
    in_drawdown = drawdown < 0
    drawdown_durations = []
    current_duration = 0
    
    for is_dd in in_drawdown:
        if is_dd:
            current_duration += 1
        else:
            if current_duration > 0:
                drawdown_durations.append(current_duration)
            current_duration = 0
    
    if current_duration > 0:
        drawdown_durations.append(current_duration)
    
    if len(drawdown_durations) == 0:
        return {
            'max_drawdown_duration': 0,
            'avg_drawdown_duration': 0,
            'total_drawdown_periods': 0
        }
    
    return {
        'max_drawdown_duration': max(drawdown_durations),
        'avg_drawdown_duration': np.mean(drawdown_durations),
        'total_drawdown_periods': len(drawdown_durations)
    }


def tail_expectation(returns: pd.Series, threshold: float = 0.05) -> Dict[str, float]:
    """
    Calculate tail expectation metrics.
    
    Args:
        returns: Series of returns
        threshold: Tail threshold (e.g., 0.05 for bottom 5%)
        
    Returns:
        Dictionary with tail metrics
    """
    tail_threshold = returns.quantile(threshold)
    tail_returns = returns[returns <= tail_threshold]
    
    if len(tail_returns) == 0:
        return {
            'tail_mean': 0.0,
            'tail_std': 0.0,
            'tail_skewness': 0.0,
            'tail_kurtosis': 0.0
        }
    
    return {
        'tail_mean': tail_returns.mean(),
        'tail_std': tail_returns.std(),
        'tail_skewness': stats.skew(tail_returns),
        'tail_kurtosis': stats.kurtosis(tail_returns),
        'tail_count': len(tail_returns)
    }


def extreme_value_theory_var(returns: pd.Series, confidence_level: float = 0.95,
                            threshold: float = 0.05) -> float:
    """
    Calculate VaR using Extreme Value Theory (EVT).
    
    Args:
        returns: Series of returns
        confidence_level: Confidence level
        threshold: Threshold for extreme values
        
    Returns:
        EVT-based VaR
    """
    # Identify extreme values
    threshold_value = returns.quantile(threshold)
    extreme_returns = returns[returns <= threshold_value]
    
    if len(extreme_returns) < 5:
        # Fallback to standard VaR
        return returns.quantile(1 - confidence_level)
    
    # Fit Generalized Pareto Distribution (simplified)
    # Use empirical distribution of extremes
    evt_var = extreme_returns.quantile(1 - confidence_level)
    
    return evt_var


def tail_dependence(returns1: pd.Series, returns2: pd.Series,
                   threshold: float = 0.05) -> Dict[str, float]:
    """
    Calculate tail dependence between two return series.
    
    Args:
        returns1: First return series
        returns2: Second return series
        threshold: Tail threshold
        
    Returns:
        Dictionary with tail dependence metrics
    """
    # Align data
    aligned = pd.DataFrame({
        'r1': returns1,
        'r2': returns2
    }).dropna()
    
    if len(aligned) < 10:
        return {
            'lower_tail_dependence': 0.0,
            'upper_tail_dependence': 0.0
        }
    
    # Lower tail (both negative)
    lower_threshold_r1 = aligned['r1'].quantile(threshold)
    lower_threshold_r2 = aligned['r2'].quantile(threshold)
    
    lower_tail_both = ((aligned['r1'] <= lower_threshold_r1) & 
                       (aligned['r2'] <= lower_threshold_r2)).sum()
    lower_tail_r1 = (aligned['r1'] <= lower_threshold_r1).sum()
    lower_tail_dep = lower_tail_both / lower_tail_r1 if lower_tail_r1 > 0 else 0.0
    
    # Upper tail (both positive)
    upper_threshold_r1 = aligned['r1'].quantile(1 - threshold)
    upper_threshold_r2 = aligned['r2'].quantile(1 - threshold)
    
    upper_tail_both = ((aligned['r1'] >= upper_threshold_r1) & 
                      (aligned['r2'] >= upper_threshold_r2)).sum()
    upper_tail_r1 = (aligned['r1'] >= upper_threshold_r1).sum()
    upper_tail_dep = upper_tail_both / upper_tail_r1 if upper_tail_r1 > 0 else 0.0
    
    return {
        'lower_tail_dependence': lower_tail_dep,
        'upper_tail_dependence': upper_tail_dep
    }


def tail_risk_decomposition(portfolio_returns: pd.Series,
                            asset_returns: pd.DataFrame,
                            weights: pd.Series) -> Dict[str, float]:
    """
    Decompose portfolio tail risk into asset contributions.
    
    Args:
        portfolio_returns: Portfolio returns
        asset_returns: Asset returns DataFrame
        weights: Portfolio weights
        
    Returns:
        Dictionary with tail risk decomposition
    """
    # Portfolio ES
    portfolio_es = expected_shortfall(portfolio_returns)
    
    # Individual asset ES
    asset_es = {}
    for asset in asset_returns.columns:
        if asset in weights.index:
            asset_es[asset] = expected_shortfall(asset_returns[asset])
    
    # Contribution to portfolio ES
    contributions = {}
    for asset, weight in weights.items():
        if asset in asset_es:
            contributions[asset] = weight * asset_es[asset]
    
    total_contribution = sum(contributions.values())
    
    return {
        'portfolio_es': portfolio_es,
        'asset_contributions': contributions,
        'total_contribution': total_contribution
    }


if __name__ == "__main__":
    # Example usage
    print("Tail Risk Analysis Demo")
    print("=" * 50)
    
    # Generate sample returns
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=252, freq='D')
    returns = pd.Series(np.random.randn(252) * 0.01, index=dates)
    
    # Expected Shortfall
    es = expected_shortfall(returns, confidence_level=0.95)
    print(f"\nExpected Shortfall (95%): {es:.4f}")
    
    # Tail expectation
    tail = tail_expectation(returns, threshold=0.05)
    print("\nTail Expectation Metrics:")
    for key, value in tail.items():
        print(f"  {key}: {value:.4f}")
