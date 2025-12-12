"""
Modern Portfolio Theory (MPT) optimization.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Optional


class ModernPortfolioTheory:
    """Modern Portfolio Theory optimizer."""
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize MPT optimizer.
        
        Args:
            risk_free_rate: Risk-free rate (annual)
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate_returns(self, prices: pd.DataFrame) -> pd.DataFrame:
        """Calculate returns from prices."""
        return prices.pct_change().dropna()
    
    def optimize_portfolio(self,
                          returns: pd.DataFrame,
                          target_return: Optional[float] = None,
                          risk_aversion: float = 1.0) -> dict:
        """
        Optimize portfolio using mean-variance optimization.
        
        Args:
            returns: DataFrame of asset returns
            target_return: Target portfolio return (if None, maximize Sharpe)
            risk_aversion: Risk aversion parameter
            
        Returns:
            Dictionary with weights, expected return, and volatility
        """
        n_assets = returns.shape[1]
        mean_returns = returns.mean() * 252  # Annualized
        cov_matrix = returns.cov() * 252  # Annualized
        
        # Objective function: minimize negative Sharpe ratio
        def objective(weights):
            portfolio_return = np.dot(weights, mean_returns)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol
            return -sharpe
        
        # Constraints
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        
        # Bounds: weights between 0 and 1
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Initial guess: equal weights
        initial_weights = np.array([1.0 / n_assets] * n_assets)
        
        # Optimize
        result = minimize(objective, initial_weights, 
                         method='SLSQP', bounds=bounds, 
                         constraints=constraints)
        
        optimal_weights = result.x
        portfolio_return = np.dot(optimal_weights, mean_returns)
        portfolio_vol = np.sqrt(np.dot(optimal_weights.T, 
                                       np.dot(cov_matrix, optimal_weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol
        
        return {
            'weights': pd.Series(optimal_weights, index=returns.columns),
            'expected_return': portfolio_return,
            'volatility': portfolio_vol,
            'sharpe_ratio': sharpe_ratio
        }
    
    def efficient_frontier(self, 
                          returns: pd.DataFrame, 
                          n_points: int = 50) -> pd.DataFrame:
        """
        Calculate efficient frontier.
        
        Args:
            returns: DataFrame of asset returns
            n_points: Number of points on frontier
            
        Returns:
            DataFrame with returns, volatilities, and weights
        """
        mean_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252
        
        min_ret = mean_returns.min()
        max_ret = mean_returns.max()
        target_returns = np.linspace(min_ret, max_ret, n_points)
        
        n_assets = returns.shape[1]
        efficient_portfolios = []
        
        for target_ret in target_returns:
            # Minimize volatility subject to target return
            def objective(weights):
                return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
                {'type': 'eq', 'fun': lambda w: np.dot(w, mean_returns) - target_ret}
            ]
            
            bounds = tuple((0, 1) for _ in range(n_assets))
            initial_weights = np.array([1.0 / n_assets] * n_assets)
            
            result = minimize(objective, initial_weights,
                             method='SLSQP', bounds=bounds,
                             constraints=constraints)
            
            if result.success:
                vol = result.fun
                efficient_portfolios.append({
                    'return': target_ret,
                    'volatility': vol,
                    'sharpe': (target_ret - self.risk_free_rate) / vol,
                    'weights': result.x
                })
        
        return pd.DataFrame(efficient_portfolios)

