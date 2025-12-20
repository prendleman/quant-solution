"""
Credit Risk Models

Probability of Default (PD), Loss Given Default (LGD), Exposure at Default (EAD),
and credit portfolio risk analytics.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize


def probability_of_default(credit_score: float, model_type: str = 'logistic') -> float:
    """
    Estimate Probability of Default (PD) from credit score.
    
    Args:
        credit_score: Credit score (typically 300-850)
        model_type: 'logistic' or 'probit'
        
    Returns:
        Probability of default (0-1)
    """
    # Normalize credit score to 0-1 range
    normalized_score = (credit_score - 300) / (850 - 300)
    normalized_score = max(0, min(1, normalized_score))
    
    if model_type == 'logistic':
        # Logistic transformation: PD decreases as score increases
        pd_value = 1 / (1 + np.exp(10 * (normalized_score - 0.5)))
    else:  # probit
        # Probit transformation
        z_score = stats.norm.ppf(1 - normalized_score)
        pd_value = stats.norm.cdf(-z_score)
    
    return pd_value


def loss_given_default(recovery_rate: float) -> float:
    """
    Calculate Loss Given Default (LGD) from recovery rate.
    
    Args:
        recovery_rate: Recovery rate (0-1, e.g., 0.4 = 40% recovery)
        
    Returns:
        Loss Given Default (0-1)
    """
    return 1 - recovery_rate


def exposure_at_default(current_exposure: float, credit_conversion_factor: float = 1.0) -> float:
    """
    Calculate Exposure at Default (EAD).
    
    Args:
        current_exposure: Current exposure amount
        credit_conversion_factor: CCF for off-balance sheet items
        
    Returns:
        Exposure at Default
    """
    return current_exposure * credit_conversion_factor


def expected_loss(pd: float, lgd: float, ead: float) -> float:
    """
    Calculate Expected Loss (EL) = PD * LGD * EAD.
    
    Args:
        pd: Probability of Default
        lgd: Loss Given Default
        ead: Exposure at Default
        
    Returns:
        Expected Loss
    """
    return pd * lgd * ead


def unexpected_loss(pd: float, lgd: float, ead: float, pd_volatility: float = 0.0) -> float:
    """
    Calculate Unexpected Loss (UL) - standard deviation of loss distribution.
    
    Args:
        pd: Probability of Default
        lgd: Loss Given Default
        ead: Exposure at Default
        pd_volatility: Volatility of PD (optional)
        
    Returns:
        Unexpected Loss
    """
    # Simplified: UL = sqrt(PD * (1 - PD)) * LGD * EAD
    if pd_volatility > 0:
        ul = pd_volatility * lgd * ead
    else:
        ul = np.sqrt(pd * (1 - pd)) * lgd * ead
    
    return ul


def credit_value_at_risk(portfolio_losses: pd.Series, confidence_level: float = 0.95) -> float:
    """
    Calculate Credit Value at Risk (CVaR) from portfolio loss distribution.
    
    Args:
        portfolio_losses: Series of portfolio losses
        confidence_level: Confidence level (e.g., 0.95 for 95% VaR)
        
    Returns:
        Credit VaR
    """
    return portfolio_losses.quantile(confidence_level)


def credit_correlation_matrix(default_indicators: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate default correlation matrix from historical default data.
    
    Args:
        default_indicators: DataFrame with binary default indicators (1=default, 0=no default)
        
    Returns:
        Correlation matrix
    """
    return default_indicators.corr()


def portfolio_credit_risk(portfolio: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate portfolio-level credit risk metrics.
    
    Args:
        portfolio: DataFrame with columns: 'pd', 'lgd', 'ead', 'exposure'
        
    Returns:
        Dictionary with portfolio risk metrics
    """
    # Individual expected losses
    portfolio['el'] = portfolio['pd'] * portfolio['lgd'] * portfolio['ead']
    portfolio['ul'] = np.sqrt(portfolio['pd'] * (1 - portfolio['pd'])) * portfolio['lgd'] * portfolio['ead']
    
    # Portfolio metrics
    total_el = portfolio['el'].sum()
    total_exposure = portfolio['ead'].sum()
    
    # Portfolio UL (simplified, assumes independence)
    portfolio_ul = np.sqrt((portfolio['ul'] ** 2).sum())
    
    # Weighted average PD
    weighted_pd = (portfolio['pd'] * portfolio['ead']).sum() / total_exposure if total_exposure > 0 else 0
    
    # Concentration risk (Herfindahl index)
    weights = portfolio['ead'] / total_exposure if total_exposure > 0 else portfolio['ead'] * 0
    herfindahl = (weights ** 2).sum()
    
    return {
        'total_expected_loss': total_el,
        'total_unexpected_loss': portfolio_ul,
        'weighted_average_pd': weighted_pd,
        'concentration_index': herfindahl,
        'total_exposure': total_exposure,
        'loss_rate': total_el / total_exposure if total_exposure > 0 else 0
    }


def merton_structural_model(asset_value: float, debt_value: float, volatility: float,
                           risk_free_rate: float, time_to_maturity: float) -> Dict[str, float]:
    """
    Merton structural credit risk model - treats equity as a call option on assets.
    
    Args:
        asset_value: Current asset value
        debt_value: Face value of debt
        volatility: Asset volatility
        risk_free_rate: Risk-free rate
        time_to_maturity: Time to debt maturity
        
    Returns:
        Dictionary with PD, distance to default, and credit spread
    """
    from utils.derivatives_ import black_scholes_price
    
    # Distance to default
    d1 = (np.log(asset_value / debt_value) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_maturity) / (volatility * np.sqrt(time_to_maturity))
    d2 = d1 - volatility * np.sqrt(time_to_maturity)
    
    # Probability of default (P(asset < debt))
    pd = stats.norm.cdf(-d2)
    
    # Distance to default
    distance_to_default = d2
    
    # Credit spread (simplified)
    credit_spread = -np.log(1 - pd) / time_to_maturity - risk_free_rate
    
    return {
        'probability_of_default': pd,
        'distance_to_default': distance_to_default,
        'credit_spread': max(0, credit_spread),
        'leverage_ratio': debt_value / asset_value
    }


def credit_migration_matrix(ratings_history: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate credit rating migration matrix from historical ratings.
    
    Args:
        ratings_history: DataFrame with credit ratings over time
        
    Returns:
        Migration matrix (transition probabilities)
    """
    ratings = ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC', 'D']
    migration_matrix = pd.DataFrame(0.0, index=ratings, columns=ratings)
    
    for i in range(len(ratings_history) - 1):
        current_rating = ratings_history.iloc[i]
        next_rating = ratings_history.iloc[i + 1]
        
        if current_rating in ratings and next_rating in ratings:
            migration_matrix.loc[current_rating, next_rating] += 1
    
    # Normalize to probabilities
    for rating in ratings:
        total = migration_matrix.loc[rating].sum()
        if total > 0:
            migration_matrix.loc[rating] = migration_matrix.loc[rating] / total
    
    return migration_matrix


if __name__ == "__main__":
    # Example usage
    print("Credit Risk Models Demo")
    print("=" * 50)
    
    # PD example
    pd = probability_of_default(650, model_type='logistic')
    print(f"\nProbability of Default (score=650): {pd:.4f}")
    
    # Expected Loss example
    lgd = loss_given_default(0.4)
    ead = exposure_at_default(1000000)
    el = expected_loss(pd, lgd, ead)
    print(f"\nExpected Loss: ${el:,.2f}")
    
    # Merton model example
    merton = merton_structural_model(1000000, 800000, 0.2, 0.03, 1.0)
    print("\nMerton Model Results:")
    for key, value in merton.items():
        print(f"  {key}: {value:.4f}")
