"""
Regime Switching Models

Markov-switching models for detecting and modeling different market regimes
(e.g., bull/bear markets, high/low volatility regimes).

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy, statsmodels (optional)
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize


def markov_switching_regime(returns: pd.Series, n_regimes: int = 2) -> Dict[str, pd.Series]:
    """
    Simple Markov-switching model to identify market regimes.
    
    Args:
        returns: Series of returns
        n_regimes: Number of regimes (typically 2: bull/bear)
        
    Returns:
        Dictionary with regime probabilities and parameters
    """
    # Initialize parameters
    mu_regimes = np.linspace(returns.mean() - returns.std(), returns.mean() + returns.std(), n_regimes)
    sigma_regimes = np.array([returns.std()] * n_regimes)
    
    # Transition probabilities (simplified)
    transition_matrix = np.ones((n_regimes, n_regimes)) / n_regimes
    
    # Regime probabilities (simplified - using volatility clustering)
    volatility = returns.rolling(window=20).std()
    high_vol_threshold = volatility.quantile(0.7)
    
    regime_probs = pd.Series(0, index=returns.index)
    regime_probs[volatility > high_vol_threshold] = 1  # High volatility regime
    
    return {
        'regime_probabilities': regime_probs,
        'regime_means': pd.Series(mu_regimes),
        'regime_volatilities': pd.Series(sigma_regimes),
        'transition_matrix': pd.DataFrame(transition_matrix)
    }


def bull_bear_detection(returns: pd.Series, lookback: int = 60) -> pd.Series:
    """
    Detect bull and bear market regimes.
    
    Args:
        returns: Series of returns
        lookback: Lookback period for trend calculation
        
    Returns:
        Series with regime indicators (1=bull, -1=bear, 0=neutral)
    """
    # Calculate rolling return
    rolling_return = returns.rolling(window=lookback).mean() * 252  # Annualized
    
    # Regime detection
    regimes = pd.Series(0, index=returns.index)
    regimes[rolling_return > 0.05] = 1   # Bull market (>5% annual return)
    regimes[rolling_return < -0.05] = -1  # Bear market (<-5% annual return)
    
    return regimes


def volatility_regime_detection(returns: pd.Series, threshold: float = 0.7) -> pd.Series:
    """
    Detect high and low volatility regimes.
    
    Args:
        returns: Series of returns
        threshold: Percentile threshold for high volatility
        
    Returns:
        Series with volatility regime (1=high vol, 0=low vol)
    """
    volatility = returns.rolling(window=20).std()
    vol_threshold = volatility.quantile(threshold)
    
    regimes = pd.Series(0, index=returns.index)
    regimes[volatility > vol_threshold] = 1
    
    return regimes


def regime_conditional_returns(returns: pd.Series, regimes: pd.Series) -> Dict[str, float]:
    """
    Calculate conditional returns for each regime.
    
    Args:
        returns: Series of returns
        regimes: Series of regime indicators
        
    Returns:
        Dictionary with regime-specific statistics
    """
    results = {}
    
    for regime in regimes.unique():
        regime_returns = returns[regimes == regime]
        if len(regime_returns) > 0:
            results[f'regime_{regime}_mean'] = regime_returns.mean()
            results[f'regime_{regime}_std'] = regime_returns.std()
            results[f'regime_{regime}_sharpe'] = regime_returns.mean() / (regime_returns.std() + 1e-8) * np.sqrt(252)
            results[f'regime_{regime}_count'] = len(regime_returns)
    
    return results


def regime_switching_portfolio_optimization(returns: pd.DataFrame, regimes: pd.Series) -> Dict[str, pd.DataFrame]:
    """
    Optimize portfolio separately for each regime.
    
    Args:
        returns: DataFrame of asset returns
        regimes: Series of regime indicators
        
    Returns:
        Dictionary with optimal weights for each regime
    """
    from models.portfolio_optimization import mean_variance_optimization
    
    regime_weights = {}
    
    for regime in regimes.unique():
        regime_mask = regimes == regime
        regime_returns = returns[regime_mask]
        
        if len(regime_returns) > 10:
            try:
                result = mean_variance_optimization(regime_returns, risk_free_rate=0.02)
                regime_weights[f'regime_{regime}'] = result['weights']
            except:
                # Equal weights if optimization fails
                n_assets = len(returns.columns)
                regime_weights[f'regime_{regime}'] = pd.Series(1.0 / n_assets, index=returns.columns)
    
    return regime_weights


def hidden_markov_model_states(returns: pd.Series, n_states: int = 2) -> Dict[str, np.ndarray]:
    """
    Estimate hidden Markov model states from returns.
    Simplified implementation using k-means clustering on volatility.
    
    Args:
        returns: Series of returns
        n_states: Number of hidden states
        
    Returns:
        Dictionary with state probabilities and parameters
    """
    from sklearn.cluster import KMeans
    
    # Features: volatility and mean return
    volatility = returns.rolling(window=20).std().fillna(returns.std())
    mean_return = returns.rolling(window=20).mean().fillna(returns.mean())
    
    features = np.column_stack([volatility.values, mean_return.values])
    features = features[~np.isnan(features).any(axis=1)]
    
    if len(features) < n_states:
        return {
            'state_probabilities': np.ones(len(returns)) / n_states,
            'state_means': np.array([returns.mean()] * n_states),
            'state_volatilities': np.array([returns.std()] * n_states)
        }
    
    # K-means clustering
    kmeans = KMeans(n_clusters=n_states, random_state=42, n_init=10)
    states = kmeans.fit_predict(features)
    
    # Calculate state parameters
    state_means = []
    state_volatilities = []
    
    for state in range(n_states):
        state_mask = states == state
        if state_mask.sum() > 0:
            state_returns = returns.iloc[state_mask]
            state_means.append(state_returns.mean())
            state_volatilities.append(state_returns.std())
        else:
            state_means.append(returns.mean())
            state_volatilities.append(returns.std())
    
    # State probabilities
    state_probs = np.array([(states == i).sum() / len(states) for i in range(n_states)])
    
    return {
        'state_probabilities': state_probs,
        'state_means': np.array(state_means),
        'state_volatilities': np.array(state_volatilities),
        'state_assignments': states
    }


if __name__ == "__main__":
    # Example usage
    print("Regime Switching Models Demo")
    print("=" * 50)
    
    # Generate sample returns
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=252, freq='D')
    returns = pd.Series(np.random.randn(252) * 0.01, index=dates)
    
    # Bull/bear detection
    regimes = bull_bear_detection(returns)
    print(f"\nBull/Bear Regimes:")
    print(f"  Bull periods: {(regimes == 1).sum()}")
    print(f"  Bear periods: {(regimes == -1).sum()}")
    print(f"  Neutral periods: {(regimes == 0).sum()}")
