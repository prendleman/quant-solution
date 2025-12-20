"""
ESG Integration Models

Environmental, Social, and Governance (ESG) factor integration into
quantitative investment strategies and risk models.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import minimize


def esg_factor_exposure(returns: pd.Series, esg_scores: pd.Series) -> Dict[str, float]:
    """
    Calculate ESG factor exposure in returns.
    
    Args:
        returns: Asset returns
        esg_scores: ESG scores (higher = better)
        
    Returns:
        Dictionary with ESG exposure metrics
    """
    # Align data
    aligned = pd.DataFrame({
        'returns': returns,
        'esg': esg_scores
    }).dropna()
    
    if len(aligned) < 10:
        return {
            'esg_beta': 0.0,
            'esg_correlation': 0.0,
            'esg_alpha': 0.0
        }
    
    # ESG factor regression
    esg_beta = aligned['returns'].cov(aligned['esg']) / aligned['esg'].var()
    esg_alpha = aligned['returns'].mean() - esg_beta * aligned['esg'].mean()
    esg_correlation = aligned['returns'].corr(aligned['esg'])
    
    return {
        'esg_beta': esg_beta,
        'esg_correlation': esg_correlation,
        'esg_alpha': esg_alpha
    }


def esg_tilted_portfolio(returns: pd.DataFrame, esg_scores: pd.Series,
                        base_weights: Optional[pd.Series] = None,
                        esg_tilt: float = 0.2) -> pd.Series:
    """
    Create ESG-tilted portfolio.
    
    Args:
        returns: Asset returns DataFrame
        esg_scores: ESG scores for each asset
        base_weights: Base portfolio weights (if None, equal weights)
        esg_tilt: ESG tilt strength (0-1)
        
    Returns:
        ESG-tilted portfolio weights
    """
    if base_weights is None:
        base_weights = pd.Series(1.0 / len(returns.columns), index=returns.columns)
    
    # Normalize ESG scores
    esg_normalized = (esg_scores - esg_scores.min()) / (esg_scores.max() - esg_scores.min() + 1e-8)
    
    # Tilt weights toward high ESG
    tilted_weights = base_weights * (1 + esg_tilt * esg_normalized)
    tilted_weights = tilted_weights / tilted_weights.sum()
    
    return tilted_weights


def esg_risk_adjustment(returns: pd.Series, esg_scores: pd.Series,
                       risk_free_rate: float = 0.02) -> Dict[str, float]:
    """
    Calculate ESG-adjusted risk metrics.
    
    Args:
        returns: Asset returns
        esg_scores: ESG scores
        risk_free_rate: Risk-free rate
        
    Returns:
        Dictionary with ESG-adjusted metrics
    """
    # Align data
    aligned = pd.DataFrame({
        'returns': returns,
        'esg': esg_scores
    }).dropna()
    
    if len(aligned) < 10:
        return {
            'esg_adjusted_sharpe': 0.0,
            'esg_risk_premium': 0.0
        }
    
    # ESG-adjusted return (penalize low ESG)
    esg_penalty = (1 - aligned['esg'].mean()) * 0.01  # 1% penalty for low ESG
    adjusted_returns = aligned['returns'] - esg_penalty
    
    # ESG-adjusted Sharpe
    esg_sharpe = (adjusted_returns.mean() - risk_free_rate / 252) / (adjusted_returns.std() + 1e-8) * np.sqrt(252)
    
    return {
        'esg_adjusted_sharpe': esg_sharpe,
        'esg_risk_premium': esg_penalty,
        'original_sharpe': (aligned['returns'].mean() - risk_free_rate / 252) / (aligned['returns'].std() + 1e-8) * np.sqrt(252)
    }


def carbon_footprint_analysis(portfolio_weights: pd.Series,
                              carbon_intensities: pd.Series) -> Dict[str, float]:
    """
    Calculate portfolio carbon footprint.
    
    Args:
        portfolio_weights: Portfolio weights
        carbon_intensities: Carbon intensity (tons CO2 per $ invested)
        
    Returns:
        Dictionary with carbon metrics
    """
    # Portfolio carbon intensity
    portfolio_carbon = (portfolio_weights * carbon_intensities).sum()
    
    # Carbon reduction potential
    avg_carbon = carbon_intensities.mean()
    carbon_reduction = (avg_carbon - portfolio_carbon) / avg_carbon * 100
    
    return {
        'portfolio_carbon_intensity': portfolio_carbon,
        'average_carbon_intensity': avg_carbon,
        'carbon_reduction_pct': carbon_reduction
    }


def esg_momentum_factor(esg_scores: pd.DataFrame) -> pd.Series:
    """
    Calculate ESG momentum factor (improving ESG scores).
    
    Args:
        esg_scores: DataFrame of ESG scores over time
        
    Returns:
        Series of ESG momentum scores
    """
    # Calculate ESG score changes
    esg_changes = esg_scores.diff(periods=4)  # Quarterly changes
    
    # Momentum: average improvement
    esg_momentum = esg_changes.mean(axis=1)
    
    return esg_momentum


def esg_risk_factor_model(returns: pd.Series, esg_scores: pd.Series,
                          market_returns: pd.Series) -> Dict[str, float]:
    """
    Multi-factor model including ESG risk factor.
    
    Args:
        returns: Asset returns
        esg_scores: ESG scores
        market_returns: Market returns
        
    Returns:
        Dictionary with factor loadings
    """
    # Align data
    aligned = pd.DataFrame({
        'returns': returns,
        'esg': esg_scores,
        'market': market_returns
    }).dropna()
    
    if len(aligned) < 10:
        return {
            'market_beta': 0.0,
            'esg_beta': 0.0,
            'alpha': 0.0
        }
    
    # Multi-factor regression
    from sklearn.linear_model import LinearRegression
    
    X = aligned[['market', 'esg']]
    y = aligned['returns']
    
    model = LinearRegression()
    model.fit(X, y)
    
    return {
        'market_beta': model.coef_[0],
        'esg_beta': model.coef_[1],
        'alpha': model.intercept_
    }


if __name__ == "__main__":
    # Example usage
    print("ESG Integration Demo")
    print("=" * 50)
    
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=252, freq='D')
    returns = pd.Series(np.random.randn(252) * 0.01, index=dates)
    esg_scores = pd.Series(np.random.uniform(50, 100, 252), index=dates)
    
    # ESG factor exposure
    exposure = esg_factor_exposure(returns, esg_scores)
    print("\nESG Factor Exposure:")
    for key, value in exposure.items():
        print(f"  {key}: {value:.4f}")
