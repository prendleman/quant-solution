"""
Market Making Strategies

Bid-ask spread strategies, inventory management, and market making
algorithms for quantitative trading.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd


def optimal_bid_ask_spread(mid_price: float, volatility: float, inventory: float,
                          max_inventory: float, risk_aversion: float = 1.0) -> Dict[str, float]:
    """
    Calculate optimal bid-ask spread for market making.
    
    Args:
        mid_price: Mid price
        volatility: Price volatility
        inventory: Current inventory position
        max_inventory: Maximum inventory limit
        risk_aversion: Risk aversion parameter
        
    Returns:
        Dictionary with optimal bid and ask prices
    """
    # Optimal spread based on volatility and inventory
    base_spread = volatility * 2  # Base spread proportional to volatility
    
    # Inventory adjustment
    inventory_ratio = inventory / max_inventory if max_inventory > 0 else 0
    inventory_adjustment = risk_aversion * inventory_ratio * volatility
    
    # Bid and ask prices
    half_spread = (base_spread + inventory_adjustment) / 2
    bid_price = mid_price - half_spread
    ask_price = mid_price + half_spread
    
    return {
        'bid_price': bid_price,
        'ask_price': ask_price,
        'spread': ask_price - bid_price,
        'spread_bps': (ask_price - bid_price) / mid_price * 10000
    }


def inventory_risk_management(current_inventory: float, target_inventory: float,
                             max_inventory: float, price: float) -> Dict[str, float]:
    """
    Inventory risk management for market making.
    
    Args:
        current_inventory: Current inventory position
        target_inventory: Target inventory (usually 0)
        max_inventory: Maximum inventory limit
        price: Current price
        
    Returns:
        Dictionary with inventory metrics and recommendations
    """
    inventory_ratio = current_inventory / max_inventory if max_inventory > 0 else 0
    
    # Risk level
    if abs(inventory_ratio) < 0.3:
        risk_level = 'low'
    elif abs(inventory_ratio) < 0.7:
        risk_level = 'medium'
    else:
        risk_level = 'high'
    
    # Inventory value
    inventory_value = current_inventory * price
    
    # Recommendation
    if abs(inventory_ratio) > 0.8:
        recommendation = 'reduce_inventory'
    elif abs(inventory_ratio) > 0.5:
        recommendation = 'moderate_inventory'
    else:
        recommendation = 'maintain'
    
    return {
        'inventory_ratio': inventory_ratio,
        'inventory_value': inventory_value,
        'risk_level': risk_level,
        'recommendation': recommendation,
        'distance_to_target': current_inventory - target_inventory
    }


def market_making_pnl(bid_prices: pd.Series, ask_prices: pd.Series,
                     bid_fills: pd.Series, ask_fills: pd.Series,
                     mid_prices: pd.Series) -> Dict[str, float]:
    """
    Calculate market making P&L.
    
    Args:
        bid_prices: Series of bid prices quoted
        ask_prices: Series of ask prices quoted
        bid_fills: Series of bid fills (quantities)
        ask_fills: Series of ask fills (quantities)
        mid_prices: Series of mid prices
        
    Returns:
        Dictionary with P&L metrics
    """
    # Bid P&L (buy at bid, mark to mid)
    bid_pnl = (mid_prices - bid_prices) * bid_fills
    
    # Ask P&L (sell at ask, mark to mid)
    ask_pnl = (ask_prices - mid_prices) * ask_fills
    
    # Total P&L
    total_pnl = bid_pnl.sum() + ask_pnl.sum()
    
    # Inventory P&L (mark-to-market)
    inventory = (bid_fills - ask_fills).cumsum()
    inventory_pnl = inventory * (mid_prices - mid_prices.shift(1)).fillna(0)
    
    return {
        'bid_pnl': bid_pnl.sum(),
        'ask_pnl': ask_pnl.sum(),
        'spread_pnl': total_pnl,
        'inventory_pnl': inventory_pnl.sum(),
        'total_pnl': total_pnl + inventory_pnl.sum(),
        'fill_rate': (bid_fills.sum() + ask_fills.sum()) / len(bid_prices) if len(bid_prices) > 0 else 0
    }


def avellaneda_stoikov_spread(mid_price: float, volatility: float, time_to_end: float,
                              risk_aversion: float = 1.0, arrival_rate: float = 1.0) -> Dict[str, float]:
    """
    Avellaneda-Stoikov optimal market making spread.
    
    Args:
        mid_price: Mid price
        volatility: Price volatility
        time_to_end: Time remaining until end of trading period
        risk_aversion: Risk aversion parameter
        arrival_rate: Order arrival rate
        
    Returns:
        Dictionary with optimal spread
    """
    # Optimal half-spread from Avellaneda-Stoikov
    half_spread = volatility * np.sqrt(time_to_end) * np.sqrt(risk_aversion / arrival_rate)
    
    bid_price = mid_price - half_spread
    ask_price = mid_price + half_spread
    
    return {
        'bid_price': bid_price,
        'ask_price': ask_price,
        'half_spread': half_spread,
        'spread': 2 * half_spread
    }


def dynamic_spread_adjustment(base_spread: float, volatility: float,
                              volume: float, avg_volume: float) -> float:
    """
    Dynamically adjust spread based on market conditions.
    
    Args:
        base_spread: Base spread
        volatility: Current volatility
        volume: Current volume
        avg_volume: Average volume
        
    Returns:
        Adjusted spread
    """
    # Volatility adjustment
    vol_adjustment = volatility / 0.02  # Normalize to 2% volatility
    
    # Volume adjustment (lower volume = wider spread)
    volume_ratio = avg_volume / (volume + 1e-8)
    volume_adjustment = 1 + 0.5 * (volume_ratio - 1)
    
    adjusted_spread = base_spread * vol_adjustment * volume_adjustment
    
    return adjusted_spread


if __name__ == "__main__":
    # Example usage
    print("Market Making Strategies Demo")
    print("=" * 50)
    
    # Optimal spread
    spread = optimal_bid_ask_spread(100.0, 0.02, 0.0, 1000, risk_aversion=1.0)
    print("\nOptimal Bid-Ask Spread:")
    print(f"  Bid: ${spread['bid_price']:.2f}")
    print(f"  Ask: ${spread['ask_price']:.2f}")
    print(f"  Spread: {spread['spread_bps']:.2f} bps")
