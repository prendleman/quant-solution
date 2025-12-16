"""
Volatility Modeling

GARCH, EWMA, and other volatility estimation models.
Generated as part of quant portfolio development.
"""

from typing import Optional, Tuple, Dict
import numpy as np
import pandas as pd
from scipy.optimize import minimize


def ewma_volatility(returns: pd.Series, lambda_param: float = 0.94) -> pd.Series:
    """
    Calculate Exponentially Weighted Moving Average (EWMA) volatility.
    
    Args:
        returns: Series of returns
        lambda_param: Decay factor (typically 0.94 for daily, 0.97 for monthly)
        
    Returns:
        Series of EWMA volatility estimates
    """
    squared_returns = returns ** 2
    ewma_var = squared_returns.ewm(alpha=1-lambda_param, adjust=False).mean()
    ewma_vol = np.sqrt(ewma_var) * np.sqrt(252)  # Annualized
    return ewma_vol


def garch_volatility(returns: pd.Series, p: int = 1, q: int = 1) -> Dict:
    """
    Estimate GARCH(p,q) volatility model.
    
    Args:
        returns: Series of returns
        p: Number of ARCH terms
        q: Number of GARCH terms
        
    Returns:
        Dictionary with volatility estimates and parameters
    """
    # Remove mean
    demeaned_returns = returns - returns.mean()
    squared_returns = demeaned_returns ** 2
    
    # Initial parameters: [omega, alpha, beta]
    initial_params = [returns.var() * 0.1, 0.1, 0.8]
    
    def garch_likelihood(params: np.ndarray) -> float:
        """Calculate negative log-likelihood for GARCH model"""
        omega, alpha, beta = params[0], params[1], params[2] if len(params) > 2 else 0.8
        
        # Ensure stationarity: alpha + beta < 1
        if alpha + beta >= 1 or omega <= 0 or alpha < 0 or beta < 0:
            return 1e10
        
        # Initialize variance
        var_t = [squared_returns.iloc[0]]
        
        # Calculate conditional variance
        for i in range(1, len(squared_returns)):
            var_t.append(omega + alpha * squared_returns.iloc[i-1] + beta * var_t[-1])
        
        var_series = pd.Series(var_t, index=squared_returns.index)
        vol_series = np.sqrt(var_series) * np.sqrt(252)  # Annualized
        
        # Log-likelihood (simplified)
        log_likelihood = -0.5 * np.sum(np.log(2 * np.pi * var_series) + 
                                      squared_returns / var_series)
        
        return -log_likelihood  # Negative for minimization
    
    # Optimize parameters
    bounds = [(1e-6, None), (1e-6, 0.99), (1e-6, 0.99)]
    result = minimize(garch_likelihood, initial_params, method='L-BFGS-B', bounds=bounds)
    
    # Calculate fitted volatility
    omega, alpha, beta = result.x[0], result.x[1], result.x[2] if len(result.x) > 2 else 0.8
    var_t = [squared_returns.iloc[0]]
    for i in range(1, len(squared_returns)):
        var_t.append(omega + alpha * squared_returns.iloc[i-1] + beta * var_t[-1])
    
    vol_series = pd.Series(np.sqrt(var_t), index=returns.index) * np.sqrt(252)
    
    return {
        'volatility': vol_series,
        'parameters': {'omega': omega, 'alpha': alpha, 'beta': beta},
        'long_term_volatility': np.sqrt(omega / (1 - alpha - beta)) * np.sqrt(252),
        'optimization_success': result.success
    }


def realized_volatility(returns: pd.Series, window: int = 20) -> pd.Series:
    """
    Calculate realized volatility using rolling window.
    
    Args:
        returns: Series of returns
        window: Rolling window size
        
    Returns:
        Series of realized volatility (annualized)
    """
    return returns.rolling(window=window).std() * np.sqrt(252)


def volatility_forecast(returns: pd.Series, method: str = 'ewma', 
                      forecast_horizon: int = 1) -> float:
    """
    Forecast future volatility.
    
    Args:
        returns: Historical returns
        method: 'ewma', 'garch', or 'realized'
        forecast_horizon: Number of periods ahead to forecast
        
    Returns:
        Forecasted volatility (annualized)
    """
    if method == 'ewma':
        vol_series = ewma_volatility(returns)
        return vol_series.iloc[-1]
    elif method == 'garch':
        garch_result = garch_volatility(returns)
        # GARCH forecast: converges to long-term volatility
        alpha = garch_result['parameters']['alpha']
        beta = garch_result['parameters']['beta']
        current_vol = garch_result['volatility'].iloc[-1] / np.sqrt(252)
        long_term_vol = garch_result['long_term_volatility'] / np.sqrt(252)
        # Forecast converges to long-term
        forecast_vol = current_vol * ((alpha + beta) ** forecast_horizon) + \
                      long_term_vol * (1 - (alpha + beta) ** forecast_horizon)
        return forecast_vol * np.sqrt(252)
    else:  # realized
        vol_series = realized_volatility(returns)
        return vol_series.iloc[-1]


def volatility_clustering_test(returns: pd.Series) -> Dict:
    """
    Test for volatility clustering (ARCH effects).
    
    Args:
        returns: Series of returns
        
    Returns:
        Dictionary with test results
    """
    squared_returns = returns ** 2
    autocorr = squared_returns.autocorr(lag=1)
    
    # Ljung-Box test (simplified)
    n = len(squared_returns)
    q_stat = n * (n + 2) * (autocorr ** 2) / (n - 1)
    
    return {
        'autocorrelation_lag1': autocorr,
        'q_statistic': q_stat,
        'has_clustering': abs(autocorr) > 0.1
    }


if __name__ == "__main__":
    # Example usage
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    returns = pd.Series(np.random.randn(500) * 0.01, index=dates)
    
    # EWMA volatility
    ewma_vol = ewma_volatility(returns)
    print(f"EWMA Volatility (current): {ewma_vol.iloc[-1]:.2%}")
    
    # GARCH volatility
    garch_result = garch_volatility(returns)
    print(f"\nGARCH Volatility:")
    print(f"  Current: {garch_result['volatility'].iloc[-1]:.2%}")
    print(f"  Long-term: {garch_result['long_term_volatility']:.2%}")
    print(f"  Parameters: {garch_result['parameters']}")
    
    # Volatility forecast
    forecast = volatility_forecast(returns, method='garch', forecast_horizon=5)
    print(f"\n5-day Volatility Forecast: {forecast:.2%}")
    
    # Volatility clustering test
    clustering = volatility_clustering_test(returns)
    print(f"\nVolatility Clustering Test:")
    print(f"  Has clustering: {clustering['has_clustering']}")
    print(f"  Autocorrelation: {clustering['autocorrelation_lag1']:.4f}")
