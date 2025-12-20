"""
Yield Curve Models

Nelson-Siegel, Svensson, and other yield curve modeling techniques
for fixed income analysis.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import minimize


def nelson_siegel_yield(maturity: float, beta0: float, beta1: float,
                       beta2: float, lambda_param: float = 1.0) -> float:
    """
    Nelson-Siegel yield curve model.
    
    Args:
        maturity: Time to maturity (years)
        beta0: Long-term yield level
        beta1: Short-term component
        beta2: Medium-term component
        lambda_param: Decay parameter
        
    Returns:
        Yield at given maturity
    """
    if maturity == 0:
        return beta0 + beta1
    
    term1 = beta0
    term2 = beta1 * ((1 - np.exp(-lambda_param * maturity)) / (lambda_param * maturity))
    term3 = beta2 * (((1 - np.exp(-lambda_param * maturity)) / (lambda_param * maturity)) - 
                    np.exp(-lambda_param * maturity))
    
    return term1 + term2 + term3


def fit_nelson_siegel(maturities: np.ndarray, yields: np.ndarray,
                     lambda_param: Optional[float] = None) -> Dict[str, float]:
    """
    Fit Nelson-Siegel model to observed yields.
    
    Args:
        maturities: Array of maturities
        yields: Array of observed yields
        lambda_param: Fixed lambda (if None, optimized)
        
    Returns:
        Dictionary with fitted parameters
    """
    def objective(params):
        if lambda_param is None:
            beta0, beta1, beta2, lam = params
        else:
            beta0, beta1, beta2 = params
            lam = lambda_param
        
        fitted_yields = [nelson_siegel_yield(m, beta0, beta1, beta2, lam) for m in maturities]
        return np.sum((fitted_yields - yields) ** 2)
    
    # Initial guess
    if lambda_param is None:
        initial_params = [yields.mean(), yields[0] - yields.mean(), 0.0, 1.0]
        bounds = [(-1, 1), (-1, 1), (-1, 1), (0.01, 10)]
        result = minimize(objective, initial_params, method='L-BFGS-B', bounds=bounds)
        beta0, beta1, beta2, lam = result.x
    else:
        initial_params = [yields.mean(), yields[0] - yields.mean(), 0.0]
        bounds = [(-1, 1), (-1, 1), (-1, 1)]
        result = minimize(objective, initial_params, method='L-BFGS-B', bounds=bounds)
        beta0, beta1, beta2 = result.x
        lam = lambda_param
    
    return {
        'beta0': beta0,
        'beta1': beta1,
        'beta2': beta2,
        'lambda': lam,
        'rmse': np.sqrt(result.fun / len(maturities))
    }


def svensson_yield(maturity: float, beta0: float, beta1: float, beta2: float,
                  beta3: float, lambda1: float, lambda2: float) -> float:
    """
    Svensson extended yield curve model.
    
    Args:
        maturity: Time to maturity (years)
        beta0: Long-term yield level
        beta1: Short-term component
        beta2: First medium-term component
        beta3: Second medium-term component
        lambda1: First decay parameter
        lambda2: Second decay parameter
        
    Returns:
        Yield at given maturity
    """
    if maturity == 0:
        return beta0 + beta1
    
    term1 = beta0
    term2 = beta1 * ((1 - np.exp(-lambda1 * maturity)) / (lambda1 * maturity))
    term3 = beta2 * (((1 - np.exp(-lambda1 * maturity)) / (lambda1 * maturity)) - 
                     np.exp(-lambda1 * maturity))
    term4 = beta3 * (((1 - np.exp(-lambda2 * maturity)) / (lambda2 * maturity)) - 
                     np.exp(-lambda2 * maturity))
    
    return term1 + term2 + term3 + term4


def yield_curve_interpolation(maturities: np.ndarray, yields: np.ndarray,
                              target_maturities: np.ndarray,
                              method: str = 'cubic') -> np.ndarray:
    """
    Interpolate yield curve to target maturities.
    
    Args:
        maturities: Observed maturities
        yields: Observed yields
        target_maturities: Target maturities for interpolation
        method: Interpolation method ('linear', 'cubic', 'spline')
        
    Returns:
        Interpolated yields
    """
    from scipy.interpolate import interp1d
    
    if method == 'linear':
        interp_func = interp1d(maturities, yields, kind='linear', 
                              fill_value='extrapolate')
    elif method == 'cubic':
        interp_func = interp1d(maturities, yields, kind='cubic',
                              fill_value='extrapolate')
    else:  # spline
        from scipy.interpolate import UnivariateSpline
        interp_func = UnivariateSpline(maturities, yields, s=0)
    
    return interp_func(target_maturities)


def forward_rate_curve(spot_rates: pd.Series) -> pd.Series:
    """
    Calculate forward rate curve from spot rates.
    
    Args:
        spot_rates: Series of spot rates indexed by maturity
        
    Returns:
        Series of forward rates
    """
    maturities = spot_rates.index.values
    forward_rates = []
    
    for i in range(1, len(maturities)):
        t1 = maturities[i-1]
        t2 = maturities[i]
        r1 = spot_rates.iloc[i-1]
        r2 = spot_rates.iloc[i]
        
        # Forward rate: (r2*t2 - r1*t1) / (t2 - t1)
        if t2 != t1:
            forward_rate = (r2 * t2 - r1 * t1) / (t2 - t1)
        else:
            forward_rate = r2
        
        forward_rates.append(forward_rate)
    
    # First forward rate equals first spot rate
    forward_rates.insert(0, spot_rates.iloc[0])
    
    return pd.Series(forward_rates, index=spot_rates.index)


def yield_curve_slope(maturities: np.ndarray, yields: np.ndarray) -> float:
    """
    Calculate yield curve slope (10Y - 2Y).
    
    Args:
        maturities: Array of maturities
        yields: Array of yields
        
    Returns:
        Yield curve slope
    """
    # Find closest to 2Y and 10Y
    idx_2y = np.argmin(np.abs(maturities - 2))
    idx_10y = np.argmin(np.abs(maturities - 10))
    
    slope = yields[idx_10y] - yields[idx_2y]
    
    return slope


if __name__ == "__main__":
    # Example usage
    print("Yield Curve Models Demo")
    print("=" * 50)
    
    # Sample yield curve
    maturities = np.array([0.25, 0.5, 1, 2, 5, 10, 30])
    yields = np.array([0.02, 0.022, 0.025, 0.028, 0.032, 0.035, 0.038])
    
    # Fit Nelson-Siegel
    ns_params = fit_nelson_siegel(maturities, yields)
    print("\nNelson-Siegel Parameters:")
    for key, value in ns_params.items():
        print(f"  {key}: {value:.4f}")
