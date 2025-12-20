"""
Commodities Models

Pricing and analysis models for commodities including oil, metals,
agricultural products, and energy markets.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import minimize


def futures_price(spot_price: float, risk_free_rate: float, time_to_maturity: float,
                 storage_cost: float = 0.0, convenience_yield: float = 0.0) -> float:
    """
    Calculate futures price using cost-of-carry model.
    
    Args:
        spot_price: Current spot price
        risk_free_rate: Risk-free interest rate
        time_to_maturity: Time to maturity in years
        storage_cost: Storage cost rate (annual)
        convenience_yield: Convenience yield (annual)
        
    Returns:
        Futures price
    """
    cost_of_carry = risk_free_rate + storage_cost - convenience_yield
    futures_price = spot_price * np.exp(cost_of_carry * time_to_maturity)
    return futures_price


def commodities_roll_yield(futures_prices: pd.Series, spot_price: float) -> float:
    """
    Calculate roll yield from futures curve.
    
    Args:
        futures_prices: Series of futures prices at different maturities
        spot_price: Current spot price
        
    Returns:
        Roll yield (annualized)
    """
    if len(futures_prices) < 2:
        return 0.0
    
    # Calculate roll yield (contango vs backwardation)
    front_month = futures_prices.iloc[0]
    roll_yield = (front_month - spot_price) / spot_price
    
    return roll_yield


def commodities_carry_trade(spot_price: float, futures_price: float,
                            risk_free_rate: float, storage_cost: float,
                            time_to_maturity: float) -> Dict[str, float]:
    """
    Analyze commodities carry trade opportunity.
    
    Args:
        spot_price: Current spot price
        futures_price: Futures price
        risk_free_rate: Risk-free rate
        storage_cost: Storage cost
        time_to_maturity: Time to maturity
        
    Returns:
        Dictionary with carry trade metrics
    """
    # Theoretical futures price
    theoretical_futures = futures_price(spot_price, risk_free_rate, time_to_maturity,
                                        storage_cost, convenience_yield=0.0)
    
    # Arbitrage opportunity
    arbitrage_pct = (futures_price - theoretical_futures) / spot_price * 100
    
    # Carry return
    carry_return = (futures_price - spot_price) / spot_price / time_to_maturity
    
    return {
        'theoretical_futures': theoretical_futures,
        'arbitrage_pct': arbitrage_pct,
        'carry_return': carry_return,
        'is_backwardated': futures_price < spot_price,
        'is_contango': futures_price > spot_price
    }


def oil_spread_analysis(wti_price: pd.Series, brent_price: pd.Series) -> Dict[str, float]:
    """
    Analyze WTI-Brent spread and trading opportunities.
    
    Args:
        wti_price: Series of WTI crude oil prices
        brent_price: Series of Brent crude oil prices
        
    Returns:
        Dictionary with spread analysis
    """
    spread = brent_price - wti_price
    spread_mean = spread.mean()
    spread_std = spread.std()
    
    # Z-score for mean reversion
    current_spread = spread.iloc[-1] if len(spread) > 0 else 0
    z_score = (current_spread - spread_mean) / (spread_std + 1e-8)
    
    # Correlation
    correlation = wti_price.corr(brent_price)
    
    return {
        'spread_mean': spread_mean,
        'spread_std': spread_std,
        'current_spread': current_spread,
        'z_score': z_score,
        'correlation': correlation,
        'mean_reversion_signal': 'long' if z_score < -2 else ('short' if z_score > 2 else 'neutral')
    }


def metals_basis_analysis(spot_price: float, futures_price: float,
                          delivery_location: str = "") -> Dict[str, float]:
    """
    Calculate basis (spot-futures spread) for metals.
    
    Args:
        spot_price: Spot price
        futures_price: Futures price
        delivery_location: Delivery location (for context)
        
    Returns:
        Dictionary with basis metrics
    """
    basis = spot_price - futures_price
    basis_pct = (basis / spot_price) * 100
    
    return {
        'basis': basis,
        'basis_pct': basis_pct,
        'is_normal': basis < 0,  # Normal: futures > spot
        'is_inverted': basis > 0  # Inverted: spot > futures
    }


def agricultural_seasonality(price_series: pd.Series, period: str = 'monthly') -> pd.Series:
    """
    Calculate seasonal patterns in agricultural commodity prices.
    
    Args:
        price_series: Series of commodity prices with datetime index
        period: 'monthly' or 'quarterly'
        
    Returns:
        Series of seasonal factors
    """
    if period == 'monthly':
        seasonal = price_series.groupby(price_series.index.month).mean()
        overall_mean = price_series.mean()
        seasonal_factors = seasonal / overall_mean
    else:  # quarterly
        seasonal = price_series.groupby(price_series.index.quarter).mean()
        overall_mean = price_series.mean()
        seasonal_factors = seasonal / overall_mean
    
    return seasonal_factors


def energy_volatility_smile(strikes: np.ndarray, implied_vols: np.ndarray,
                            spot_price: float) -> Dict[str, float]:
    """
    Analyze volatility smile for energy derivatives.
    
    Args:
        strikes: Array of strike prices
        implied_vols: Array of implied volatilities
        spot_price: Current spot price
        
    Returns:
        Dictionary with volatility smile metrics
    """
    moneyness = strikes / spot_price
    
    # Fit polynomial
    coeffs = np.polyfit(moneyness - 1, implied_vols, deg=2)
    
    # Skew and kurtosis
    skew = coeffs[1]
    kurtosis = coeffs[0] * 2
    atm_vol = np.polyval(coeffs, 0)
    
    return {
        'atm_volatility': atm_vol,
        'volatility_skew': skew,
        'volatility_kurtosis': kurtosis,
        'smile_coefficients': coeffs.tolist()
    }


if __name__ == "__main__":
    # Example usage
    print("Commodities Models Demo")
    print("=" * 50)
    
    # Futures pricing example
    futures = futures_price(100, 0.03, 0.25, storage_cost=0.02)
    print(f"\nFutures Price: ${futures:.2f}")
    
    # Carry trade example
    carry = commodities_carry_trade(100, 102, 0.03, 0.02, 0.25)
    print("\nCarry Trade Analysis:")
    for key, value in carry.items():
        print(f"  {key}: {value:.4f}")
