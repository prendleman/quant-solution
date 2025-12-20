"""
Multi-Asset Class Strategies

Cross-asset strategies including equity-bond, equity-commodity,
and multi-asset portfolio strategies.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.optimize import minimize


def equity_bond_rotation(equity_returns: pd.Series, bond_returns: pd.Series,
                        volatility_threshold: float = 0.15) -> pd.Series:
    """
    Equity-bond rotation strategy based on volatility regime.
    
    Args:
        equity_returns: Equity returns
        bond_returns: Bond returns
        volatility_threshold: Volatility threshold for switching
        
    Returns:
        Series of strategy returns
    """
    # Calculate rolling volatility
    equity_vol = equity_returns.rolling(window=20).std() * np.sqrt(252)
    
    # Strategy: high vol -> bonds, low vol -> equities
    strategy_returns = pd.Series(0.0, index=equity_returns.index)
    
    for i in range(len(equity_returns)):
        if i < 20:
            strategy_returns.iloc[i] = equity_returns.iloc[i]  # Start with equities
        else:
            if equity_vol.iloc[i] > volatility_threshold:
                strategy_returns.iloc[i] = bond_returns.iloc[i]
            else:
                strategy_returns.iloc[i] = equity_returns.iloc[i]
    
    return strategy_returns


def commodity_equity_hedge(equity_returns: pd.Series, commodity_returns: pd.Series,
                           hedge_ratio: float = 0.3) -> pd.Series:
    """
    Commodity-equity hedge strategy.
    
    Args:
        equity_returns: Equity returns
        commodity_returns: Commodity returns
        hedge_ratio: Commodity hedge ratio
        
    Returns:
        Series of hedged portfolio returns
    """
    # Align data
    aligned = pd.DataFrame({
        'equity': equity_returns,
        'commodity': commodity_returns
    }).dropna()
    
    # Hedged portfolio
    hedged_returns = aligned['equity'] - hedge_ratio * aligned['commodity']
    
    return hedged_returns


def risk_parity_multi_asset(returns_df: pd.DataFrame, target_volatility: float = 0.10) -> Dict[str, float]:
    """
    Risk parity portfolio across multiple asset classes.
    
    Args:
        returns_df: DataFrame of asset returns
        target_volatility: Target portfolio volatility
        
    Returns:
        Dictionary with optimal weights
    """
    # Calculate volatilities
    volatilities = returns_df.std() * np.sqrt(252)
    
    # Risk parity: equal risk contribution
    # Weight inversely proportional to volatility
    inv_vol = 1 / (volatilities + 1e-8)
    weights = inv_vol / inv_vol.sum()
    
    # Scale to target volatility
    portfolio_vol = np.sqrt((weights ** 2 * volatilities ** 2).sum())
    if portfolio_vol > 0:
        scale_factor = target_volatility / portfolio_vol
        weights = weights * scale_factor
        weights = weights / weights.sum()  # Renormalize
    
    return {
        'weights': weights.to_dict(),
        'portfolio_volatility': portfolio_vol,
        'target_volatility': target_volatility
    }


def tactical_asset_allocation(returns_df: pd.DataFrame, momentum_window: int = 60,
                             rebalance_frequency: int = 20) -> pd.Series:
    """
    Tactical asset allocation based on momentum.
    
    Args:
        returns_df: DataFrame of asset returns
        momentum_window: Window for momentum calculation
        rebalance_frequency: Rebalancing frequency
        
    Returns:
        Series of portfolio returns
    """
    portfolio_returns = []
    current_weights = pd.Series(1.0 / len(returns_df.columns), index=returns_df.columns)
    
    for i in range(len(returns_df)):
        if i < momentum_window:
            # Equal weights initially
            portfolio_return = (returns_df.iloc[i] * current_weights).sum()
            portfolio_returns.append(portfolio_return)
        else:
            # Rebalance based on momentum
            if i % rebalance_frequency == 0:
                momentum = returns_df.iloc[i-momentum_window:i].mean()
                # Weight by momentum (softmax)
                exp_momentum = np.exp(momentum * 10)  # Scale for better differentiation
                current_weights = exp_momentum / exp_momentum.sum()
            
            portfolio_return = (returns_df.iloc[i] * current_weights).sum()
            portfolio_returns.append(portfolio_return)
    
    return pd.Series(portfolio_returns, index=returns_df.index)


def currency_hedged_portfolio(asset_returns: pd.Series, currency_returns: pd.Series,
                              hedge_ratio: float = 1.0) -> pd.Series:
    """
    Currency-hedged portfolio strategy.
    
    Args:
        asset_returns: Asset returns in local currency
        currency_returns: Currency returns (FX)
        hedge_ratio: Currency hedge ratio (1.0 = fully hedged)
        
    Returns:
        Series of hedged returns
    """
    # Align data
    aligned = pd.DataFrame({
        'asset': asset_returns,
        'currency': currency_returns
    }).dropna()
    
    # Hedged returns: asset return - currency return * hedge_ratio
    hedged_returns = aligned['asset'] - hedge_ratio * aligned['currency']
    
    return hedged_returns


def multi_asset_momentum(returns_df: pd.DataFrame, lookback: int = 60,
                        top_n: int = 3) -> pd.Series:
    """
    Multi-asset momentum strategy - invest in top N assets by momentum.
    
    Args:
        returns_df: DataFrame of asset returns
        lookback: Momentum lookback period
        top_n: Number of top assets to hold
        
    Returns:
        Series of portfolio returns
    """
    portfolio_returns = []
    
    for i in range(len(returns_df)):
        if i < lookback:
            # Equal weights initially
            portfolio_return = returns_df.iloc[i].mean()
            portfolio_returns.append(portfolio_return)
        else:
            # Calculate momentum
            momentum = returns_df.iloc[i-lookback:i].mean()
            
            # Select top N
            top_assets = momentum.nlargest(top_n).index
            weights = pd.Series(0.0, index=returns_df.columns)
            weights[top_assets] = 1.0 / len(top_assets)
            
            portfolio_return = (returns_df.iloc[i] * weights).sum()
            portfolio_returns.append(portfolio_return)
    
    return pd.Series(portfolio_returns, index=returns_df.index)


if __name__ == "__main__":
    # Example usage
    print("Multi-Asset Strategies Demo")
    print("=" * 50)
    
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=252, freq='D')
    equity_returns = pd.Series(np.random.randn(252) * 0.01, index=dates)
    bond_returns = pd.Series(np.random.randn(252) * 0.005, index=dates)
    
    # Equity-bond rotation
    strategy_returns = equity_bond_rotation(equity_returns, bond_returns)
    print(f"\nEquity-Bond Rotation Sharpe: {strategy_returns.mean() / strategy_returns.std() * np.sqrt(252):.4f}")
