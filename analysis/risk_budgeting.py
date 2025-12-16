"""
Risk Budgeting and Allocation

Risk parity, risk budgeting, and risk-based position sizing.
Generated as part of quant portfolio development.
"""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from scipy.optimize import minimize


def risk_parity_weights(cov_matrix: pd.DataFrame, target_risk: Optional[float] = None) -> Dict:
    """
    Calculate risk parity portfolio weights.
    
    Args:
        cov_matrix: Covariance matrix of returns
        target_risk: Target portfolio risk (volatility)
        
    Returns:
        Dictionary with weights and risk metrics
    """
    n_assets = len(cov_matrix)
    
    def risk_contribution(weights: np.ndarray) -> np.ndarray:
        """Calculate risk contribution of each asset"""
        portfolio_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
        marginal_contrib = np.dot(cov_matrix, weights) / portfolio_vol
        contrib = weights * marginal_contrib
        return contrib
    
    def objective(weights: np.ndarray) -> float:
        """Minimize sum of squared differences in risk contributions"""
        contrib = risk_contribution(weights)
        target_contrib = np.ones(n_assets) / n_assets * np.sum(contrib)
        return np.sum((contrib - target_contrib) ** 2)
    
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
    bounds = tuple((0, 1) for _ in range(n_assets))
    initial_weights = np.array([1/n_assets] * n_assets)
    
    result = minimize(objective, initial_weights, method='SLSQP',
                     bounds=bounds, constraints=constraints)
    
    optimal_weights = result.x
    risk_contrib = risk_contribution(optimal_weights)
    portfolio_vol = np.sqrt(np.dot(optimal_weights, np.dot(cov_matrix, optimal_weights)))
    
    return {
        'weights': dict(zip(cov_matrix.index, optimal_weights)),
        'risk_contributions': dict(zip(cov_matrix.index, risk_contrib)),
        'portfolio_volatility': portfolio_vol,
        'target_risk': target_risk
    }


def risk_budget_optimization(cov_matrix: pd.DataFrame, risk_budgets: Dict[str, float]) -> Dict:
    """
    Optimize portfolio to match target risk budgets.
    
    Args:
        cov_matrix: Covariance matrix
        risk_budgets: Dictionary of target risk budgets per asset
        
    Returns:
        Dictionary with optimized weights
    """
    n_assets = len(cov_matrix)
    target_contrib = np.array([risk_budgets.get(asset, 1/n_assets) 
                               for asset in cov_matrix.index])
    target_contrib = target_contrib / target_contrib.sum()  # Normalize
    
    def risk_contribution(weights: np.ndarray) -> np.ndarray:
        portfolio_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
        marginal_contrib = np.dot(cov_matrix, weights) / portfolio_vol
        contrib = weights * marginal_contrib
        return contrib
    
    def objective(weights: np.ndarray) -> float:
        contrib = risk_contribution(weights)
        total_risk = np.sum(contrib)
        target_contrib_scaled = target_contrib * total_risk
        return np.sum((contrib - target_contrib_scaled) ** 2)
    
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
    bounds = tuple((0, 1) for _ in range(n_assets))
    initial_weights = np.array([1/n_assets] * n_assets)
    
    result = minimize(objective, initial_weights, method='SLSQP',
                     bounds=bounds, constraints=constraints)
    
    optimal_weights = result.x
    risk_contrib = risk_contribution(optimal_weights)
    
    return {
        'weights': dict(zip(cov_matrix.index, optimal_weights)),
        'risk_contributions': dict(zip(cov_matrix.index, risk_contrib)),
        'target_budgets': risk_budgets
    }


def kelly_criterion_position_size(win_rate: float, avg_win: float, avg_loss: float,
                                 account_size: float) -> float:
    """
    Calculate optimal position size using Kelly Criterion.
    
    Args:
        win_rate: Probability of winning
        avg_win: Average win amount
        avg_loss: Average loss amount
        account_size: Total account size
        
    Returns:
        Optimal position size
    """
    if avg_loss == 0:
        return 0
    
    win_loss_ratio = avg_win / abs(avg_loss)
    kelly_fraction = (win_rate * (win_loss_ratio + 1) - 1) / win_loss_ratio
    
    # Conservative: use half Kelly
    kelly_fraction = max(0, min(0.25, kelly_fraction / 2))
    
    return account_size * kelly_fraction


def volatility_targeting(returns: pd.Series, target_vol: float = 0.15,
                         lookback: int = 60) -> pd.Series:
    """
    Calculate position sizes to target specific volatility.
    
    Args:
        returns: Return series
        target_vol: Target annualized volatility
        lookback: Lookback period for volatility estimation
        
    Returns:
        Series of position multipliers
    """
    rolling_vol = returns.rolling(window=lookback).std() * np.sqrt(252)
    position_multiplier = target_vol / rolling_vol
    position_multiplier = position_multiplier.clip(0, 2)  # Cap at 2x
    
    return position_multiplier


def risk_decomposition(weights: Dict[str, float], cov_matrix: pd.DataFrame) -> pd.DataFrame:
    """
    Decompose portfolio risk by asset.
    
    Args:
        weights: Dictionary of asset weights
        cov_matrix: Covariance matrix
        
    Returns:
        DataFrame with risk decomposition
    """
    weight_array = np.array([weights.get(asset, 0) for asset in cov_matrix.index])
    portfolio_vol = np.sqrt(np.dot(weight_array, np.dot(cov_matrix, weight_array)))
    
    # Marginal contribution to risk
    marginal_contrib = np.dot(cov_matrix, weight_array) / portfolio_vol
    
    # Component contribution
    component_contrib = weight_array * marginal_contrib
    
    # Percentage contribution
    pct_contrib = component_contrib / portfolio_vol
    
    decomposition = pd.DataFrame({
        'weight': weight_array,
        'marginal_risk': marginal_contrib,
        'component_risk': component_contrib,
        'percent_contribution': pct_contrib
    }, index=cov_matrix.index)
    
    return decomposition


if __name__ == "__main__":
    # Example usage
    dates = pd.date_range('2020-01-01', periods=252, freq='D')
    assets = ['Asset1', 'Asset2', 'Asset3']
    
    returns_data = pd.DataFrame(
        np.random.randn(252, 3) * 0.01,
        index=dates,
        columns=assets
    )
    
    cov_matrix = returns_data.cov()
    
    # Risk parity
    rp_result = risk_parity_weights(cov_matrix)
    print("Risk Parity Portfolio:")
    print(f"  Weights: {rp_result['weights']}")
    print(f"  Portfolio Volatility: {rp_result['portfolio_volatility']:.4f}")
    
    # Risk decomposition
    decomposition = risk_decomposition(rp_result['weights'], cov_matrix)
    print(f"\nRisk Decomposition:")
    print(decomposition)
