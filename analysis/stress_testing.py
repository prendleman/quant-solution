"""
Stress Testing and Scenario Analysis

Stress testing, scenario analysis, and extreme event modeling for
portfolio risk assessment.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats


def historical_stress_test(returns: pd.Series, stress_periods: List[Tuple[str, str]]) -> Dict[str, float]:
    """
    Perform historical stress test using past crisis periods.
    
    Args:
        returns: Series of returns
        stress_periods: List of (start_date, end_date) tuples for stress periods
        
    Returns:
        Dictionary with stress test results
    """
    results = {}
    
    for i, (start, end) in enumerate(stress_periods):
        period_returns = returns[start:end]
        if len(period_returns) > 0:
            results[f'stress_period_{i+1}_return'] = period_returns.sum()
            results[f'stress_period_{i+1}_volatility'] = period_returns.std() * np.sqrt(252)
            results[f'stress_period_{i+1}_max_drawdown'] = calculate_max_drawdown_from_returns(period_returns)
    
    return results


def scenario_analysis(portfolio_returns: pd.Series, scenarios: Dict[str, float]) -> Dict[str, float]:
    """
    Analyze portfolio performance under different scenarios.
    
    Args:
        portfolio_returns: Series of portfolio returns
        scenarios: Dictionary of scenario_name -> return_multiplier
        
    Returns:
        Dictionary with scenario-adjusted returns
    """
    base_return = portfolio_returns.mean()
    base_vol = portfolio_returns.std()
    
    scenario_results = {}
    for scenario_name, multiplier in scenarios.items():
        scenario_return = base_return * multiplier
        scenario_vol = base_vol * abs(multiplier)  # Volatility scales with return magnitude
        scenario_results[f'{scenario_name}_return'] = scenario_return
        scenario_results[f'{scenario_name}_volatility'] = scenario_vol
        scenario_results[f'{scenario_name}_sharpe'] = scenario_return / (scenario_vol + 1e-8) * np.sqrt(252)
    
    return scenario_results


def monte_carlo_stress_test(returns: pd.Series, n_simulations: int = 10000,
                            stress_multiplier: float = 2.0) -> Dict[str, float]:
    """
    Monte Carlo stress test - simulate extreme scenarios.
    
    Args:
        returns: Series of returns
        n_simulations: Number of Monte Carlo simulations
        stress_multiplier: Multiplier for stress scenario (e.g., 2.0 = 2x volatility)
        
    Returns:
        Dictionary with stress test statistics
    """
    mean_return = returns.mean()
    std_return = returns.std()
    
    # Stress scenario: increased volatility
    stress_std = std_return * stress_multiplier
    
    # Generate stress scenarios
    stress_returns = np.random.normal(mean_return, stress_std, n_simulations)
    
    # Calculate stress metrics
    var_95 = np.percentile(stress_returns, 5)
    var_99 = np.percentile(stress_returns, 1)
    cvar_95 = stress_returns[stress_returns <= var_95].mean()
    cvar_99 = stress_returns[stress_returns <= var_99].mean()
    
    return {
        'stress_var_95': var_95,
        'stress_var_99': var_99,
        'stress_cvar_95': cvar_95,
        'stress_cvar_99': cvar_99,
        'stress_mean': stress_returns.mean(),
        'stress_std': stress_returns.std()
    }


def correlation_stress_test(returns_df: pd.DataFrame, stress_correlation: float = 0.9) -> Dict[str, float]:
    """
    Stress test with increased correlation (crisis scenario).
    
    Args:
        returns_df: DataFrame of asset returns
        stress_correlation: Correlation level in stress scenario
        
    Returns:
        Dictionary with stress test results
    """
    # Normal correlation
    normal_corr = returns_df.corr().values
    normal_corr_mean = normal_corr[np.triu_indices_from(normal_corr, k=1)].mean()
    
    # Stress correlation matrix
    n_assets = len(returns_df.columns)
    stress_corr_matrix = np.ones((n_assets, n_assets)) * stress_correlation
    np.fill_diagonal(stress_corr_matrix, 1.0)
    
    # Portfolio volatility under stress
    weights = np.ones(n_assets) / n_assets  # Equal weights
    normal_vol = np.sqrt(weights @ returns_df.cov().values @ weights)
    stress_vol = np.sqrt(weights @ (stress_corr_matrix * returns_df.std().values.reshape(-1, 1) * returns_df.std().values) @ weights)
    
    return {
        'normal_correlation': normal_corr_mean,
        'stress_correlation': stress_correlation,
        'normal_volatility': normal_vol,
        'stress_volatility': stress_vol,
        'volatility_increase': (stress_vol - normal_vol) / normal_vol * 100
    }


def liquidity_stress_test(portfolio_weights: pd.Series, asset_volumes: pd.Series,
                         stress_days: int = 5) -> Dict[str, float]:
    """
    Stress test for liquidity risk - impact of forced selling.
    
    Args:
        portfolio_weights: Series of portfolio weights
        asset_volumes: Series of average daily volumes
        stress_days: Days available to liquidate
        
    Returns:
        Dictionary with liquidity stress metrics
    """
    # Calculate liquidation impact
    portfolio_value = 1.0  # Normalized
    asset_values = portfolio_weights * portfolio_value
    
    # Daily liquidation capacity
    daily_capacity = asset_volumes * 0.1  # Assume 10% of volume can be traded
    
    # Liquidation time
    liquidation_times = asset_values / daily_capacity
    max_liquidation_time = liquidation_times.max()
    
    # Stress: forced liquidation in stress_days
    stress_impact = {}
    for asset in portfolio_weights.index:
        if asset in asset_volumes.index:
            if liquidation_times[asset] > stress_days:
                # Forced selling at discount
                discount = 0.05 * (liquidation_times[asset] / stress_days - 1)  # 5% per day over
                stress_impact[asset] = discount
            else:
                stress_impact[asset] = 0.0
    
    total_impact = sum(portfolio_weights[asset] * stress_impact.get(asset, 0.0) 
                      for asset in portfolio_weights.index)
    
    return {
        'max_liquidation_time_days': max_liquidation_time,
        'liquidity_stress_impact': total_impact,
        'assets_at_risk': sum(1 for v in stress_impact.values() if v > 0),
        'liquidation_times': liquidation_times.to_dict()
    }


def calculate_max_drawdown_from_returns(returns: pd.Series) -> float:
    """Calculate maximum drawdown from return series."""
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return abs(drawdown.min())


def extreme_value_analysis(returns: pd.Series, threshold: float = 0.95) -> Dict[str, float]:
    """
    Extreme value analysis using EVT (Extreme Value Theory).
    
    Args:
        returns: Series of returns
        threshold: Threshold percentile for extreme events
        
    Returns:
        Dictionary with extreme value statistics
    """
    threshold_value = returns.quantile(threshold)
    extreme_returns = returns[returns <= threshold_value]
    
    if len(extreme_returns) < 5:
        return {
            'extreme_threshold': threshold_value,
            'extreme_mean': 0.0,
            'extreme_std': 0.0,
            'tail_index': 0.0
        }
    
    # Tail index (simplified)
    tail_index = 1 / extreme_returns.std() if extreme_returns.std() > 0 else 0
    
    return {
        'extreme_threshold': threshold_value,
        'extreme_mean': extreme_returns.mean(),
        'extreme_std': extreme_returns.std(),
        'tail_index': tail_index,
        'extreme_count': len(extreme_returns)
    }


if __name__ == "__main__":
    # Example usage
    print("Stress Testing Demo")
    print("=" * 50)
    
    # Generate sample returns
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=252, freq='D')
    returns = pd.Series(np.random.randn(252) * 0.01, index=dates)
    
    # Monte Carlo stress test
    stress = monte_carlo_stress_test(returns, n_simulations=10000)
    print("\nMonte Carlo Stress Test:")
    for key, value in stress.items():
        print(f"  {key}: {value:.4f}")
