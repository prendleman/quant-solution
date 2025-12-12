"""
Risk parity portfolio optimization.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Optional


class RiskParity:
    """Risk parity portfolio optimization."""
    
    def __init__(self):
        """Initialize risk parity optimizer."""
        pass
    
    def optimize_portfolio(self,
                          cov_matrix: np.ndarray,
                          target_risk_contributions: Optional[np.ndarray] = None) -> dict:
        """
        Optimize portfolio using risk parity.
        
        Args:
            cov_matrix: Covariance matrix
            target_risk_contributions: Target risk contributions (if None, equal)
            
        Returns:
            Dictionary with weights and risk contributions
        """
        n_assets = cov_matrix.shape[0]
        
        if target_risk_contributions is None:
            target_risk_contributions = np.ones(n_assets) / n_assets
        
        def risk_contributions(weights):
            """Calculate risk contributions."""
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            marginal_contrib = np.dot(cov_matrix, weights) / portfolio_vol
            contrib = weights * marginal_contrib
            return contrib / portfolio_vol
        
        def objective(weights):
            """Minimize squared difference from target contributions."""
            actual_contrib = risk_contributions(weights)
            return np.sum((actual_contrib - target_risk_contributions) ** 2)
        
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_weights = np.array([1.0 / n_assets] * n_assets)
        
        result = minimize(objective, initial_weights,
                         method='SLSQP', bounds=bounds,
                         constraints=constraints)
        
        optimal_weights = result.x
        risk_contrib = risk_contributions(optimal_weights)
        portfolio_vol = np.sqrt(np.dot(optimal_weights.T,
                                      np.dot(cov_matrix, optimal_weights)))
        
        return {
            'weights': pd.Series(optimal_weights, index=range(n_assets)),
            'risk_contributions': risk_contrib,
            'volatility': portfolio_vol
        }

