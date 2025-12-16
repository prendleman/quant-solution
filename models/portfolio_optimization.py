"""
Portfolio Optimization

Mean-variance optimization, risk parity, and other portfolio construction methods.
Generated as part of quant portfolio development.
"""

from typing import Optional, List, Dict, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.linalg import inv


def mean_variance_optimization(returns: pd.DataFrame, risk_free_rate: float = 0.02,
                               target_return: Optional[float] = None,
                               risk_aversion: float = 1.0) -> Dict:
    """
    Mean-variance portfolio optimization (Markowitz).
    
    Args:
        returns: DataFrame of asset returns (columns = assets, rows = time)
        risk_free_rate: Risk-free rate
        target_return: Target portfolio return (if None, maximizes Sharpe ratio)
        risk_aversion: Risk aversion parameter (higher = more risk averse)
        
    Returns:
        Dictionary with optimal weights and metrics
    """
    n_assets = returns.shape[1]
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    
    def portfolio_performance(weights: np.ndarray) -> Tuple[float, float]:
        """Calculate portfolio return and volatility"""
        portfolio_return = np.sum(mean_returns * weights)
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return portfolio_return, portfolio_vol
    
    def negative_sharpe(weights: np.ndarray) -> float:
        """Negative Sharpe ratio for minimization"""
        ret, vol = portfolio_performance(weights)
        return -(ret - risk_free_rate) / vol if vol > 0 else 1e10
    
    def negative_utility(weights: np.ndarray) -> float:
        """Negative utility function (mean-variance)"""
        ret, vol = portfolio_performance(weights)
        return -(ret - 0.5 * risk_aversion * vol ** 2)
    
    # Constraints: weights sum to 1
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
    bounds = tuple((0, 1) for _ in range(n_assets))
    initial_weights = np.array([1/n_assets] * n_assets)
    
    if target_return is not None:
        # Optimize for target return with minimum variance
        def portfolio_variance(weights: np.ndarray) -> float:
            return np.dot(weights.T, np.dot(cov_matrix, weights))
        
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
            {'type': 'eq', 'fun': lambda x: np.sum(mean_returns * x) - target_return}
        ]
        
        result = minimize(portfolio_variance, initial_weights, method='SLSQP',
                         bounds=bounds, constraints=constraints)
    else:
        # Maximize Sharpe ratio
        result = minimize(negative_sharpe, initial_weights, method='SLSQP',
                         bounds=bounds, constraints=constraints)
    
    optimal_weights = result.x
    ret, vol = portfolio_performance(optimal_weights)
    sharpe = (ret - risk_free_rate) / vol if vol > 0 else 0
    
    return {
        'weights': dict(zip(returns.columns, optimal_weights)),
        'expected_return': ret,
        'volatility': vol,
        'sharpe_ratio': sharpe,
        'optimization_success': result.success
    }


def risk_parity_optimization(returns: pd.DataFrame) -> Dict:
    """
    Risk parity portfolio optimization (equal risk contribution).
    
    Args:
        returns: DataFrame of asset returns
        
    Returns:
        Dictionary with optimal weights and metrics
    """
    n_assets = returns.shape[1]
    cov_matrix = returns.cov().values
    
    def risk_contribution(weights: np.ndarray) -> np.ndarray:
        """Calculate risk contribution of each asset"""
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        marginal_contrib = np.dot(cov_matrix, weights) / portfolio_vol
        contrib = weights * marginal_contrib
        return contrib
    
    def risk_parity_objective(weights: np.ndarray) -> float:
        """Objective: minimize sum of squared differences in risk contributions"""
        contrib = risk_contribution(weights)
        target_contrib = np.ones(n_assets) / n_assets * np.sum(contrib)
        return np.sum((contrib - target_contrib) ** 2)
    
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
    bounds = tuple((0, 1) for _ in range(n_assets))
    initial_weights = np.array([1/n_assets] * n_assets)
    
    result = minimize(risk_parity_objective, initial_weights, method='SLSQP',
                     bounds=bounds, constraints=constraints)
    
    optimal_weights = result.x
    mean_returns = returns.mean()
    portfolio_return = np.sum(mean_returns * optimal_weights)
    portfolio_vol = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
    
    return {
        'weights': dict(zip(returns.columns, optimal_weights)),
        'expected_return': portfolio_return,
        'volatility': portfolio_vol,
        'risk_contributions': risk_contribution(optimal_weights).tolist(),
        'optimization_success': result.success
    }


def minimum_variance_portfolio(returns: pd.DataFrame) -> Dict:
    """
    Minimum variance portfolio (global minimum variance).
    
    Args:
        returns: DataFrame of asset returns
        
    Returns:
        Dictionary with optimal weights and metrics
    """
    n_assets = returns.shape[1]
    cov_matrix = returns.cov().values
    mean_returns = returns.mean()
    
    # Closed-form solution for minimum variance portfolio
    ones = np.ones(n_assets)
    inv_cov = inv(cov_matrix)
    
    denominator = np.dot(ones, np.dot(inv_cov, ones))
    optimal_weights = np.dot(inv_cov, ones) / denominator
    
    portfolio_return = np.sum(mean_returns * optimal_weights)
    portfolio_vol = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
    
    return {
        'weights': dict(zip(returns.columns, optimal_weights)),
        'expected_return': portfolio_return,
        'volatility': portfolio_vol
    }


def efficient_frontier(returns: pd.DataFrame, n_points: int = 50,
                      risk_free_rate: float = 0.02) -> pd.DataFrame:
    """
    Generate efficient frontier points.
    
    Args:
        returns: DataFrame of asset returns
        n_points: Number of points on efficient frontier
        risk_free_rate: Risk-free rate
        
    Returns:
        DataFrame with return, volatility, and Sharpe ratio for each point
    """
    mean_returns = returns.mean()
    min_return = mean_returns.min()
    max_return = mean_returns.max()
    target_returns = np.linspace(min_return, max_return, n_points)
    
    frontier_points = []
    for target_ret in target_returns:
        try:
            result = mean_variance_optimization(returns, risk_free_rate, 
                                              target_return=target_ret)
            if result['optimization_success']:
                frontier_points.append({
                    'return': result['expected_return'],
                    'volatility': result['volatility'],
                    'sharpe_ratio': result['sharpe_ratio']
                })
        except:
            continue
    
    return pd.DataFrame(frontier_points)


def calculate_portfolio_metrics(returns: pd.DataFrame, weights: Dict[str, float]) -> Dict:
    """
    Calculate portfolio performance metrics.
    
    Args:
        returns: DataFrame of asset returns
        weights: Dictionary of asset weights
        
    Returns:
        Dictionary with portfolio metrics
    """
    # Convert weights to array in same order as returns columns
    weight_array = np.array([weights.get(asset, 0) for asset in returns.columns])
    
    # Portfolio returns
    portfolio_returns = (returns * weight_array).sum(axis=1)
    
    # Metrics
    mean_return = portfolio_returns.mean()
    std_return = portfolio_returns.std()
    sharpe_ratio = mean_return / std_return * np.sqrt(252) if std_return > 0 else 0
    
    # Cumulative returns
    cumulative_returns = (1 + portfolio_returns).cumprod()
    total_return = cumulative_returns.iloc[-1] - 1
    
    # Max drawdown
    running_max = cumulative_returns.expanding().max()
    drawdown = (cumulative_returns - running_max) / running_max
    max_drawdown = drawdown.min()
    
    return {
        'mean_return': mean_return,
        'volatility': std_return,
        'sharpe_ratio': sharpe_ratio,
        'total_return': total_return,
        'max_drawdown': max_drawdown,
        'cumulative_returns': cumulative_returns
    }


if __name__ == "__main__":
    # Example usage
    dates = pd.date_range('2020-01-01', periods=252, freq='D')
    assets = ['Asset1', 'Asset2', 'Asset3', 'Asset4']
    
    # Generate correlated returns
    np.random.seed(42)
    returns_data = pd.DataFrame(
        np.random.randn(252, 4) * 0.01,
        index=dates,
        columns=assets
    )
    
    # Mean-variance optimization
    print("Mean-Variance Optimization:")
    mv_result = mean_variance_optimization(returns_data, risk_free_rate=0.02)
    print(f"  Optimal weights: {mv_result['weights']}")
    print(f"  Expected return: {mv_result['expected_return']:.4f}")
    print(f"  Volatility: {mv_result['volatility']:.4f}")
    print(f"  Sharpe ratio: {mv_result['sharpe_ratio']:.4f}")
    
    # Risk parity
    print("\nRisk Parity Optimization:")
    rp_result = risk_parity_optimization(returns_data)
    print(f"  Optimal weights: {rp_result['weights']}")
    print(f"  Expected return: {rp_result['expected_return']:.4f}")
    print(f"  Volatility: {rp_result['volatility']:.4f}")
    
    # Minimum variance
    print("\nMinimum Variance Portfolio:")
    minvar_result = minimum_variance_portfolio(returns_data)
    print(f"  Optimal weights: {minvar_result['weights']}")
    print(f"  Expected return: {minvar_result['expected_return']:.4f}")
    print(f"  Volatility: {minvar_result['volatility']:.4f}")
    
    # Efficient frontier
    print("\nEfficient Frontier:")
    frontier = efficient_frontier(returns_data, n_points=20)
    print(f"  Generated {len(frontier)} points")
    print(f"  Max Sharpe: {frontier['sharpe_ratio'].max():.4f}")
