"""
Alternative Risk Measures

Advanced risk metrics beyond standard deviation: Sortino ratio,
Omega ratio, Calmar ratio, and other sophisticated risk measures.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats


def sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.02,
                  target_return: float = 0.0) -> float:
    """
    Calculate Sortino ratio - risk-adjusted return using downside deviation.
    
    Args:
        returns: Series of returns
        risk_free_rate: Risk-free rate (annual)
        target_return: Target return (default: 0)
        
    Returns:
        Sortino ratio
    """
    excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
    
    # Downside deviation (only negative deviations from target)
    downside_returns = excess_returns[excess_returns < target_return]
    
    if len(downside_returns) == 0:
        return np.inf if excess_returns.mean() > 0 else 0.0
    
    downside_deviation = downside_returns.std() * np.sqrt(252)
    mean_return = excess_returns.mean() * 252  # Annualized
    
    if downside_deviation == 0:
        return np.inf if mean_return > 0 else 0.0
    
    return mean_return / downside_deviation


def omega_ratio(returns: pd.Series, threshold: float = 0.0) -> float:
    """
    Calculate Omega ratio - probability-weighted ratio of gains to losses.
    
    Args:
        returns: Series of returns
        threshold: Return threshold (default: 0)
        
    Returns:
        Omega ratio
    """
    gains = returns[returns > threshold] - threshold
    losses = threshold - returns[returns <= threshold]
    
    if len(losses) == 0 or losses.sum() == 0:
        return np.inf if len(gains) > 0 else 1.0
    
    gains_sum = gains.sum()
    losses_sum = losses.sum()
    
    return gains_sum / losses_sum if losses_sum > 0 else np.inf


def calmar_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """
    Calculate Calmar ratio - annual return / maximum drawdown.
    
    Args:
        returns: Series of returns
        risk_free_rate: Risk-free rate
        
    Returns:
        Calmar ratio
    """
    # Annualized return
    annual_return = returns.mean() * 252 - risk_free_rate
    
    # Maximum drawdown
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = abs(drawdown.min())
    
    if max_drawdown == 0:
        return np.inf if annual_return > 0 else 0.0
    
    return annual_return / max_drawdown


def sterling_ratio(returns: pd.Series, risk_free_rate: float = 0.02,
                  lookback: int = 36) -> float:
    """
    Calculate Sterling ratio - return / average drawdown.
    
    Args:
        returns: Series of returns
        risk_free_rate: Risk-free rate
        lookback: Lookback period for average drawdown
        
    Returns:
        Sterling ratio
    """
    # Annualized return
    annual_return = returns.mean() * 252 - risk_free_rate
    
    # Average drawdown over lookback periods
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    
    # Average of largest drawdowns
    drawdowns = drawdown[drawdown < 0].abs()
    if len(drawdowns) == 0:
        return np.inf if annual_return > 0 else 0.0
    
    # Average of top N drawdowns
    top_drawdowns = drawdowns.nlargest(min(lookback, len(drawdowns)))
    avg_drawdown = top_drawdowns.mean()
    
    if avg_drawdown == 0:
        return np.inf if annual_return > 0 else 0.0
    
    return annual_return / avg_drawdown


def kappa_ratio(returns: pd.Series, kappa: int = 3, risk_free_rate: float = 0.02) -> float:
    """
    Calculate Kappa ratio - return / kappa-th moment of downside.
    
    Args:
        returns: Series of returns
        kappa: Moment order (3 = Kappa-3, similar to Sortino)
        risk_free_rate: Risk-free rate
        
    Returns:
        Kappa ratio
    """
    excess_returns = returns - (risk_free_rate / 252)
    
    # Downside returns
    downside_returns = excess_returns[excess_returns < 0]
    
    if len(downside_returns) == 0:
        return np.inf if excess_returns.mean() > 0 else 0.0
    
    # Kappa-th moment of downside
    downside_moment = (downside_returns ** kappa).mean() ** (1 / kappa)
    mean_return = excess_returns.mean() * 252
    
    if downside_moment == 0:
        return np.inf if mean_return > 0 else 0.0
    
    return mean_return / (downside_moment * np.sqrt(252))


def gain_to_pain_ratio(returns: pd.Series) -> float:
    """
    Calculate Gain-to-Pain ratio - sum of gains / sum of losses.
    
    Args:
        returns: Series of returns
        
    Returns:
        Gain-to-Pain ratio
    """
    gains = returns[returns > 0].sum()
    losses = abs(returns[returns < 0].sum())
    
    if losses == 0:
        return np.inf if gains > 0 else 0.0
    
    return gains / losses


def ulcer_index(returns: pd.Series) -> float:
    """
    Calculate Ulcer Index - measure of downside volatility.
    
    Args:
        returns: Series of returns
        
    Returns:
        Ulcer Index
    """
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = ((cumulative - running_max) / running_max) * 100
    
    # Ulcer Index: root mean square of drawdowns
    ulcer = np.sqrt((drawdown ** 2).mean())
    
    return ulcer


def pain_index(returns: pd.Series) -> float:
    """
    Calculate Pain Index - average drawdown.
    
    Args:
        returns: Series of returns
        
    Returns:
        Pain Index
    """
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    
    # Average of negative drawdowns
    negative_drawdowns = drawdown[drawdown < 0].abs()
    
    if len(negative_drawdowns) == 0:
        return 0.0
    
    return negative_drawdowns.mean() * 100


def risk_adjusted_return_metrics(returns: pd.Series, risk_free_rate: float = 0.02) -> Dict[str, float]:
    """
    Calculate comprehensive set of risk-adjusted return metrics.
    
    Args:
        returns: Series of returns
        risk_free_rate: Risk-free rate
        
    Returns:
        Dictionary with all risk metrics
    """
    return {
        'sharpe_ratio': returns.mean() / (returns.std() + 1e-8) * np.sqrt(252) - risk_free_rate / (returns.std() + 1e-8),
        'sortino_ratio': sortino_ratio(returns, risk_free_rate),
        'calmar_ratio': calmar_ratio(returns, risk_free_rate),
        'omega_ratio': omega_ratio(returns),
        'sterling_ratio': sterling_ratio(returns, risk_free_rate),
        'kappa_3_ratio': kappa_ratio(returns, kappa=3, risk_free_rate=risk_free_rate),
        'gain_to_pain_ratio': gain_to_pain_ratio(returns),
        'ulcer_index': ulcer_index(returns),
        'pain_index': pain_index(returns)
    }


if __name__ == "__main__":
    # Example usage
    print("Alternative Risk Measures Demo")
    print("=" * 50)
    
    # Generate sample returns
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=252, freq='D')
    returns = pd.Series(np.random.randn(252) * 0.01, index=dates)
    
    # Calculate all metrics
    metrics = risk_adjusted_return_metrics(returns)
    print("\nRisk-Adjusted Return Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")
