"""
Black-Litterman portfolio optimization model.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Optional, List


class BlackLitterman:
    """Black-Litterman model for portfolio optimization."""
    
    def __init__(self, 
                 risk_free_rate: float = 0.02,
                 tau: float = 0.05):
        """
        Initialize Black-Litterman model.
        
        Args:
            risk_free_rate: Risk-free rate
            tau: Scaling factor for uncertainty
        """
        self.risk_free_rate = risk_free_rate
        self.tau = tau
    
    def calculate_implied_returns(self,
                                  market_weights: np.ndarray,
                                  cov_matrix: np.ndarray,
                                  risk_aversion: float = 3.0) -> np.ndarray:
        """
        Calculate implied equilibrium returns.
        
        Args:
            market_weights: Market capitalization weights
            cov_matrix: Covariance matrix
            risk_aversion: Risk aversion parameter
            
        Returns:
            Implied returns vector
        """
        return risk_aversion * np.dot(cov_matrix, market_weights)
    
    def combine_views(self,
                     implied_returns: np.ndarray,
                     views: np.ndarray,
                     P: np.ndarray,
                     Omega: Optional[np.ndarray] = None,
                     cov_matrix: np.ndarray = None) -> np.ndarray:
        """
        Combine market views with investor views.
        
        Args:
            implied_returns: Implied equilibrium returns
            views: Investor views (expected returns)
            P: Picking matrix (maps views to assets)
            Omega: Uncertainty matrix (if None, uses tau*P*Sigma*P')
            cov_matrix: Covariance matrix
            
        Returns:
            Combined expected returns
        """
        if Omega is None:
            if cov_matrix is None:
                raise ValueError("Either Omega or cov_matrix must be provided")
            Omega = self.tau * np.dot(P, np.dot(cov_matrix, P.T))
        
        # Calculate posterior returns
        tau_sigma = self.tau * cov_matrix
        M1 = np.linalg.inv(tau_sigma)
        M2 = np.dot(P.T, np.dot(np.linalg.inv(Omega), P))
        M3 = np.dot(M1, implied_returns)
        M4 = np.dot(P.T, np.dot(np.linalg.inv(Omega), views))
        
        posterior_cov = np.linalg.inv(M1 + M2)
        posterior_returns = np.dot(posterior_cov, M3 + M4)
        
        return posterior_returns
    
    def optimize_portfolio(self,
                          expected_returns: np.ndarray,
                          cov_matrix: np.ndarray,
                          risk_aversion: float = 3.0) -> dict:
        """
        Optimize portfolio using Black-Litterman expected returns.
        
        Args:
            expected_returns: Expected returns vector
            cov_matrix: Covariance matrix
            risk_aversion: Risk aversion parameter
            
        Returns:
            Dictionary with optimal weights and metrics
        """
        n_assets = len(expected_returns)
        
        # Objective: maximize utility = w'*mu - lambda*w'*Sigma*w
        def objective(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_risk = np.dot(weights.T, np.dot(cov_matrix, weights))
            utility = portfolio_return - 0.5 * risk_aversion * portfolio_risk
            return -utility
        
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_weights = np.array([1.0 / n_assets] * n_assets)
        
        result = minimize(objective, initial_weights,
                         method='SLSQP', bounds=bounds,
                         constraints=constraints)
        
        optimal_weights = result.x
        portfolio_return = np.dot(optimal_weights, expected_returns)
        portfolio_vol = np.sqrt(np.dot(optimal_weights.T,
                                     np.dot(cov_matrix, optimal_weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol
        
        return {
            'weights': optimal_weights,
            'expected_return': portfolio_return,
            'volatility': portfolio_vol,
            'sharpe_ratio': sharpe_ratio
        }

