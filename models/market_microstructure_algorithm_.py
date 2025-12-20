"""
Market Microstructure Models

Order book analysis, bid-ask spread modeling, market impact estimation,
and high-frequency market microstructure analytics.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats


def calculate_volume_weighted_average_price(data: pd.DataFrame) -> float:
    """
    Calculate the volume-weighted average price (VWAP) for a given dataset.

    Args:
        data: DataFrame containing 'price' and 'volume' columns

    Returns:
        Volume-weighted average price
    """
    if 'price' not in data.columns or 'volume' not in data.columns:
        raise ValueError("Input data must contain 'price' and 'volume' columns")

    total_volume = data['volume'].sum()
    if total_volume == 0:
        return data['price'].mean()
    
    vwap = (data['price'] * data['volume']).sum() / total_volume
    return vwap


def calculate_bid_ask_spread(data: pd.DataFrame) -> float:
    """
    Calculate the bid-ask spread for a given dataset.

    Args:
        data: DataFrame containing 'bid' and 'ask' columns

    Returns:
        Bid-ask spread
    """
    if 'bid' not in data.columns or 'ask' not in data.columns:
        raise ValueError("Input data must contain 'bid' and 'ask' columns")

    bid_ask_spread = data['ask'].mean() - data['bid'].mean()
    return bid_ask_spread


def calculate_effective_spread(trade_prices: pd.Series, mid_prices: pd.Series) -> float:
    """
    Calculate effective spread - actual trading cost relative to mid price.
    
    Args:
        trade_prices: Series of trade prices
        mid_prices: Series of mid prices (bid+ask)/2
        
    Returns:
        Average effective spread
    """
    if len(trade_prices) != len(mid_prices):
        raise ValueError("Trade prices and mid prices must have same length")
    
    effective_spreads = 2 * abs(trade_prices - mid_prices)
    return effective_spreads.mean()


def order_book_imbalance(bid_volumes: pd.Series, ask_volumes: pd.Series) -> pd.Series:
    """
    Calculate order book imbalance - indicator of short-term price pressure.
    
    Args:
        bid_volumes: Series of bid-side volumes
        ask_volumes: Series of ask-side volumes
        
    Returns:
        Series of order book imbalance (-1 to 1)
    """
    total_volume = bid_volumes + ask_volumes
    imbalance = (bid_volumes - ask_volumes) / total_volume
    return imbalance.fillna(0)


def kyle_lambda_model(trade_volumes: pd.Series, price_changes: pd.Series) -> Dict[str, float]:
    """
    Estimate Kyle's Lambda (price impact coefficient) from trade data.
    
    Args:
        trade_volumes: Series of trade volumes (signed: positive=buy, negative=sell)
        price_changes: Series of subsequent price changes
        
    Returns:
        Dictionary with lambda estimate and statistics
    """
    # Remove zeros and align
    data = pd.DataFrame({
        'volume': trade_volumes,
        'price_change': price_changes
    }).dropna()
    
    if len(data) < 10:
        return {
            'lambda': 0.0,
            'r_squared': 0.0,
            't_statistic': 0.0
        }
    
    # Linear regression: price_change = lambda * volume + error
    from sklearn.linear_model import LinearRegression
    
    X = data[['volume']].values
    y = data['price_change'].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    lambda_est = model.coef_[0]
    r_squared = model.score(X, y)
    
    # T-statistic
    residuals = y - model.predict(X)
    mse = np.mean(residuals ** 2)
    se_lambda = np.sqrt(mse / np.sum((X - X.mean()) ** 2))
    t_stat = lambda_est / se_lambda if se_lambda > 0 else 0
    
    return {
        'lambda': lambda_est,
        'r_squared': r_squared,
        't_statistic': t_stat,
        'intercept': model.intercept_
    }


def amihud_illiquidity_measure(returns: pd.Series, volumes: pd.Series) -> float:
    """
    Calculate Amihud illiquidity measure - average price impact per unit volume.
    
    Args:
        returns: Series of returns
        volumes: Series of trading volumes
        
    Returns:
        Amihud illiquidity measure
    """
    data = pd.DataFrame({
        'returns': returns,
        'volumes': volumes
    }).dropna()
    
    # Remove zero volumes
    data = data[data['volumes'] > 0]
    
    if len(data) == 0:
        return np.nan
    
    # Amihud = mean(|return| / volume)
    amihud = (abs(data['returns']) / data['volumes']).mean()
    return amihud


def roll_spread_model(returns: pd.Series) -> float:
    """
    Estimate bid-ask spread using Roll's model (serial covariance method).
    
    Args:
        returns: Series of returns
        
    Returns:
        Estimated spread (as percentage)
    """
    if len(returns) < 2:
        return 0.0
    
    # Calculate serial covariance
    returns_lag = returns.shift(1)
    covariance = returns.cov(returns_lag)
    
    # Roll spread = 2 * sqrt(-covariance) if covariance < 0
    if covariance < 0:
        spread = 2 * np.sqrt(-covariance)
    else:
        spread = 0.0
    
    return spread * 100  # Convert to percentage


def market_impact_function(trade_size: float, average_volume: float,
                          volatility: float, alpha: float = 0.5) -> float:
    """
    Estimate permanent market impact using power law function.
    
    Args:
        trade_size: Size of the trade
        average_volume: Average daily volume
        volatility: Asset volatility
        alpha: Impact exponent (typically 0.5 for square root)
        
    Returns:
        Estimated price impact (as percentage)
    """
    participation_rate = trade_size / average_volume if average_volume > 0 else 0
    
    # Power law: impact = volatility * (participation_rate ^ alpha)
    impact = volatility * (participation_rate ** alpha) * 100
    
    return impact


def order_flow_imbalance(buy_volumes: pd.Series, sell_volumes: pd.Series) -> pd.Series:
    """
    Calculate order flow imbalance - net buying pressure.
    
    Args:
        buy_volumes: Series of buy volumes
        sell_volumes: Series of sell volumes
        
    Returns:
        Series of order flow imbalance
    """
    total_volume = buy_volumes + sell_volumes
    imbalance = (buy_volumes - sell_volumes) / total_volume
    return imbalance.fillna(0)


def price_impact_curve(trade_sizes: np.ndarray, price_impacts: np.ndarray) -> Dict[str, float]:
    """
    Fit price impact curve and estimate parameters.
    
    Args:
        trade_sizes: Array of trade sizes
        price_impacts: Array of observed price impacts
        
    Returns:
        Dictionary with curve parameters
    """
    # Remove zeros and invalid values
    mask = (trade_sizes > 0) & (price_impacts > 0) & np.isfinite(price_impacts)
    trade_sizes = trade_sizes[mask]
    price_impacts = price_impacts[mask]
    
    if len(trade_sizes) < 3:
        return {
            'alpha': 0.5,
            'beta': 1.0,
            'r_squared': 0.0
        }
    
    # Log-linear regression: log(impact) = alpha * log(size) + beta
    log_sizes = np.log(trade_sizes)
    log_impacts = np.log(price_impacts)
    
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    model.fit(log_sizes.reshape(-1, 1), log_impacts)
    
    alpha = model.coef_[0]
    beta = np.exp(model.intercept_)
    r_squared = model.score(log_sizes.reshape(-1, 1), log_impacts)
    
    return {
        'alpha': alpha,
        'beta': beta,
        'r_squared': r_squared,
        'impact_function': f'{beta:.4f} * size^{alpha:.4f}'
    }


def depth_cost_model(bid_depths: pd.Series, ask_depths: pd.Series,
                    trade_size: float) -> Dict[str, float]:
    """
    Estimate execution cost based on order book depth.
    
    Args:
        bid_depths: Series of bid-side depth at best price
        ask_depths: Series of ask-side depth at best price
        trade_size: Size of trade to execute
        
    Returns:
        Dictionary with execution cost estimates
    """
    avg_bid_depth = bid_depths.mean()
    avg_ask_depth = ask_depths.mean()
    
    # Cost if consuming all depth at best price
    if trade_size <= avg_bid_depth:
        bid_cost = 0.0  # Can execute at best bid
    else:
        bid_cost = (trade_size - avg_bid_depth) / trade_size  # Partial execution at worse prices
    
    if trade_size <= avg_ask_depth:
        ask_cost = 0.0
    else:
        ask_cost = (trade_size - avg_ask_depth) / trade_size
    
    return {
        'bid_execution_cost': bid_cost,
        'ask_execution_cost': ask_cost,
        'average_cost': (bid_cost + ask_cost) / 2,
        'liquidity_score': min(avg_bid_depth, avg_ask_depth) / trade_size if trade_size > 0 else 0
    }


if __name__ == "__main__":
    # Example usage
    print("Market Microstructure Models Demo")
    print("=" * 50)
    
    # VWAP example
    data = pd.DataFrame({
        'price': [100, 101, 102, 101, 100],
        'volume': [1000, 2000, 1500, 1800, 1200]
    })
    vwap = calculate_volume_weighted_average_price(data)
    print(f"\nVWAP: ${vwap:.2f}")
    
    # Bid-ask spread example
    spread_data = pd.DataFrame({
        'bid': [99.8, 99.9, 100.0, 99.9, 99.8],
        'ask': [100.2, 100.1, 100.0, 100.1, 100.2]
    })
    spread = calculate_bid_ask_spread(spread_data)
    print(f"\nAverage Bid-Ask Spread: ${spread:.2f}")
    
    # Kyle's Lambda example
    trade_volumes = pd.Series([100, 200, -150, 300, -100])
    price_changes = pd.Series([0.1, 0.2, -0.15, 0.3, -0.1])
    kyle = kyle_lambda_model(trade_volumes, price_changes)
    print("\nKyle's Lambda:")
    for key, value in kyle.items():
        print(f"  {key}: {value:.4f}")
