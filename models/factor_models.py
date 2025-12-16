"""
Factor Models

Fama-French style factor models and factor analysis.
Generated as part of quant portfolio development.
"""

from typing import Optional, List, Dict
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from scipy import stats


def fama_french_regression(returns: pd.Series, market_factor: pd.Series,
                          smb_factor: Optional[pd.Series] = None,
                          hml_factor: Optional[pd.Series] = None,
                          rmw_factor: Optional[pd.Series] = None,
                          cma_factor: Optional[pd.Series] = None) -> Dict:
    """
    Run Fama-French factor model regression.
    
    Args:
        returns: Asset/portfolio returns
        market_factor: Market excess returns (Mkt-Rf)
        smb_factor: Small minus Big factor (optional)
        hml_factor: High minus Low factor (optional)
        rmw_factor: Robust minus Weak profitability (optional)
        cma_factor: Conservative minus Aggressive investment (optional)
        
    Returns:
        Dictionary with regression results
    """
    # Prepare factors
    factors = pd.DataFrame({'Market': market_factor}, index=returns.index)
    
    if smb_factor is not None:
        factors['SMB'] = smb_factor
    if hml_factor is not None:
        factors['HML'] = hml_factor
    if rmw_factor is not None:
        factors['RMW'] = rmw_factor
    if cma_factor is not None:
        factors['CMA'] = cma_factor
    
    # Align indices
    aligned_data = pd.concat([returns, factors], axis=1).dropna()
    y = aligned_data[returns.name] if returns.name else aligned_data.iloc[:, 0]
    X = aligned_data[factors.columns]
    
    # Run regression
    model = LinearRegression()
    model.fit(X, y)
    
    # Calculate metrics
    y_pred = model.predict(X)
    residuals = y - y_pred
    r_squared = model.score(X, y)
    
    # T-statistics
    n = len(y)
    k = X.shape[1]
    mse = np.sum(residuals ** 2) / (n - k - 1)
    var_coef = mse * np.linalg.inv(X.T @ X)
    se_coef = np.sqrt(np.diag(var_coef))
    t_stats = model.coef_ / se_coef
    
    # Factor loadings
    factor_loadings = dict(zip(factors.columns, model.coef_))
    factor_loadings['Alpha'] = model.intercept_
    
    return {
        'alpha': model.intercept_,
        'factor_loadings': factor_loadings,
        'r_squared': r_squared,
        't_statistics': dict(zip(factors.columns, t_stats)),
        'residuals': residuals,
        'fitted_values': y_pred
    }


def calculate_factor_exposure(returns: pd.Series, factors: pd.DataFrame) -> pd.Series:
    """
    Calculate factor exposures using rolling regression.
    
    Args:
        returns: Asset returns
        factors: DataFrame of factor returns
        
    Returns:
        Series of factor exposures (betas)
    """
    # Align data
    aligned = pd.concat([returns, factors], axis=1).dropna()
    asset_returns = aligned[returns.name] if returns.name else aligned.iloc[:, 0]
    factor_data = aligned[factors.columns]
    
    # Rolling regression
    window = 60  # 60-day rolling window
    betas = []
    
    for i in range(window, len(aligned)):
        y = asset_returns.iloc[i-window:i]
        X = factor_data.iloc[i-window:i]
        
        model = LinearRegression()
        model.fit(X, y)
        betas.append(model.coef_[0])  # First factor beta
    
    beta_series = pd.Series(betas, index=aligned.index[window:])
    return beta_series


def factor_attribution(returns: pd.Series, factor_returns: pd.DataFrame,
                      factor_loadings: Dict[str, float]) -> pd.DataFrame:
    """
    Attribute returns to factors.
    
    Args:
        returns: Asset returns
        factor_returns: DataFrame of factor returns
        factor_loadings: Dictionary of factor loadings (betas)
        
    Returns:
        DataFrame with factor contributions
    """
    # Align data
    aligned = pd.concat([returns, factor_returns], axis=1).dropna()
    asset_returns = aligned[returns.name] if returns.name else aligned.iloc[:, 0]
    
    # Calculate factor contributions
    contributions = pd.DataFrame(index=aligned.index)
    
    for factor, beta in factor_loadings.items():
        if factor in factor_returns.columns:
            contributions[f'{factor}_contribution'] = beta * aligned[factor]
    
    contributions['total_attributed'] = contributions.sum(axis=1)
    contributions['residual'] = asset_returns - contributions['total_attributed']
    contributions['actual_return'] = asset_returns
    
    return contributions


def style_analysis(returns: pd.Series, style_factors: pd.DataFrame) -> Dict:
    """
    Style analysis (Sharpe style regression with constraints).
    
    Args:
        returns: Portfolio returns
        style_factors: DataFrame of style factor returns
        
    Returns:
        Dictionary with style weights
    """
    # Align data
    aligned = pd.concat([returns, style_factors], axis=1).dropna()
    y = aligned[returns.name] if returns.name else aligned.iloc[:, 0]
    X = aligned[style_factors.columns]
    
    # Constrained regression: weights sum to 1, all non-negative
    from scipy.optimize import minimize
    
    def objective(weights):
        return np.sum((y - X @ weights) ** 2)
    
    constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
    bounds = [(0, 1) for _ in range(len(style_factors.columns))]
    initial_weights = np.array([1/len(style_factors.columns)] * len(style_factors.columns))
    
    result = minimize(objective, initial_weights, method='SLSQP',
                     bounds=bounds, constraints=constraints)
    
    style_weights = dict(zip(style_factors.columns, result.x))
    
    # Calculate R-squared
    y_pred = X @ result.x
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    
    return {
        'style_weights': style_weights,
        'r_squared': r_squared,
        'tracking_error': np.std(y - y_pred)
    }


if __name__ == "__main__":
    # Example usage
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    
    # Generate sample data
    market_returns = pd.Series(np.random.randn(500) * 0.01, index=dates, name='Market')
    asset_returns = market_returns * 1.2 + np.random.randn(500) * 0.005
    
    # Fama-French regression
    ff_result = fama_french_regression(asset_returns, market_returns)
    print("Fama-French Regression:")
    print(f"  Alpha: {ff_result['alpha']:.4f}")
    print(f"  Market Beta: {ff_result['factor_loadings']['Market']:.4f}")
    print(f"  R²: {ff_result['r_squared']:.4f}")
    
    # Factor exposure
    factors_df = pd.DataFrame({'Market': market_returns}, index=dates)
    exposure = calculate_factor_exposure(asset_returns, factors_df)
    print(f"\nAverage Factor Exposure: {exposure.mean():.4f}")
    
    # Style analysis
    style_factors = pd.DataFrame({
        'Growth': np.random.randn(500) * 0.008,
        'Value': np.random.randn(500) * 0.008,
        'Momentum': np.random.randn(500) * 0.008
    }, index=dates)
    
    style_result = style_analysis(asset_returns, style_factors)
    print(f"\nStyle Analysis:")
    print(f"  Style Weights: {style_result['style_weights']}")
    print(f"  R²: {style_result['r_squared']:.4f}")
