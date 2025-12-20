"""
Volatility Surface Modeling

3D volatility surface modeling, interpolation, and extrapolation
for options pricing and risk management.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.interpolate import griddata, RBFInterpolator


def volatility_surface_interpolation(strikes: np.ndarray, maturities: np.ndarray,
                                    implied_vols: np.ndarray,
                                    target_strikes: np.ndarray,
                                    target_maturities: np.ndarray,
                                    method: str = 'cubic') -> np.ndarray:
    """
    Interpolate volatility surface.
    
    Args:
        strikes: Array of strike prices
        maturities: Array of maturities
        implied_vols: Array of implied volatilities
        target_strikes: Target strikes for interpolation
        target_maturities: Target maturities for interpolation
        method: Interpolation method
        
    Returns:
        Interpolated volatility surface
    """
    # Create grid
    strike_grid, maturity_grid = np.meshgrid(target_strikes, target_maturities)
    
    # Prepare input points
    points = np.column_stack([strikes, maturities])
    values = implied_vols
    
    # Interpolate
    if method == 'rbf':
        # Radial Basis Function interpolation
        rbf = RBFInterpolator(points, values)
        target_points = np.column_stack([strike_grid.ravel(), maturity_grid.ravel()])
        vol_surface = rbf(target_points).reshape(strike_grid.shape)
    else:
        # Grid interpolation
        vol_surface = griddata(points, values, (strike_grid, maturity_grid),
                               method=method, fill_value=np.nan)
    
    return vol_surface


def volatility_smile(strikes: np.ndarray, implied_vols: np.ndarray,
                     spot_price: float) -> Dict[str, float]:
    """
    Analyze volatility smile/skew.
    
    Args:
        strikes: Array of strike prices
        implied_vols: Array of implied volatilities
        spot_price: Current spot price
        
    Returns:
        Dictionary with smile metrics
    """
    # Moneyness
    moneyness = strikes / spot_price
    
    # ATM volatility (closest to 1.0 moneyness)
    atm_idx = np.argmin(np.abs(moneyness - 1.0))
    atm_vol = implied_vols[atm_idx]
    
    # Skew (difference between OTM put and OTM call)
    otm_put_idx = np.argmin(np.abs(moneyness - 0.9))  # 90% moneyness
    otm_call_idx = np.argmin(np.abs(moneyness - 1.1))  # 110% moneyness
    
    skew = implied_vols[otm_put_idx] - implied_vols[otm_call_idx]
    
    # Smile curvature (simplified)
    curvature = np.polyfit(moneyness - 1, implied_vols, deg=2)[0]
    
    return {
        'atm_volatility': atm_vol,
        'volatility_skew': skew,
        'smile_curvature': curvature,
        'min_volatility': implied_vols.min(),
        'max_volatility': implied_vols.max()
    }


def volatility_term_structure(maturities: np.ndarray, implied_vols: np.ndarray) -> Dict[str, float]:
    """
    Analyze volatility term structure.
    
    Args:
        maturities: Array of maturities
        implied_vols: Array of implied volatilities
        
    Returns:
        Dictionary with term structure metrics
    """
    # Short-term and long-term volatility
    short_term = implied_vols[maturities <= 0.25].mean() if len(maturities[maturities <= 0.25]) > 0 else implied_vols[0]
    long_term = implied_vols[maturities >= 1.0].mean() if len(maturities[maturities >= 1.0]) > 0 else implied_vols[-1]
    
    # Term structure slope
    slope = (long_term - short_term) / (maturities.max() - maturities.min() + 1e-8)
    
    # Volatility of volatility
    vol_of_vol = np.std(implied_vols)
    
    return {
        'short_term_vol': short_term,
        'long_term_vol': long_term,
        'term_structure_slope': slope,
        'vol_of_vol': vol_of_vol
    }


def stochastic_volatility_surface(spot_price: float, strikes: np.ndarray,
                                  maturities: np.ndarray, v0: float = 0.04,
                                  theta: float = 0.04, kappa: float = 2.0,
                                  sigma_v: float = 0.3, rho: float = -0.7) -> np.ndarray:
    """
    Generate volatility surface using Heston stochastic volatility model.
    Simplified implementation.
    
    Args:
        spot_price: Current spot price
        strikes: Array of strike prices
        maturities: Array of maturities
        v0: Initial variance
        theta: Long-term variance
        kappa: Mean reversion speed
        sigma_v: Volatility of volatility
        rho: Correlation between price and volatility
        
    Returns:
        Volatility surface
    """
    # Simplified Heston surface (in practice, use full Heston formula)
    vol_surface = np.zeros((len(maturities), len(strikes)))
    
    for i, maturity in enumerate(maturities):
        for j, strike in enumerate(strikes):
            # Simplified: base vol + moneyness adjustment
            moneyness = strike / spot_price
            base_vol = np.sqrt(theta + (v0 - theta) * np.exp(-kappa * maturity))
            
            # Skew adjustment
            skew_adjustment = rho * sigma_v * (moneyness - 1.0) * 0.1
            
            vol_surface[i, j] = base_vol + skew_adjustment
    
    return vol_surface


if __name__ == "__main__":
    # Example usage
    print("Volatility Surface Demo")
    print("=" * 50)
    
    # Sample data
    strikes = np.array([80, 90, 100, 110, 120])
    maturities = np.array([0.25, 0.5, 1.0])
    implied_vols = np.array([0.25, 0.23, 0.22, 0.24, 0.26])
    
    # Volatility smile
    smile = volatility_smile(strikes, implied_vols, 100.0)
    print("\nVolatility Smile:")
    for key, value in smile.items():
        print(f"  {key}: {value:.4f}")
