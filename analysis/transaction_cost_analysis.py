"""
Transaction Cost Analysis

Comprehensive transaction cost modeling including market impact,
bid-ask spread, commissions, and optimal execution cost estimation.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd


def market_impact_cost(trade_size: float, average_volume: float,
                      volatility: float, alpha: float = 0.5) -> float:
    """
    Estimate permanent market impact cost.
    
    Args:
        trade_size: Size of the trade
        average_volume: Average daily volume
        volatility: Asset volatility
        alpha: Impact exponent (typically 0.5)
        
    Returns:
        Market impact cost (as percentage)
    """
    participation_rate = trade_size / average_volume if average_volume > 0 else 0
    impact = volatility * (participation_rate ** alpha) * 100
    return impact


def bid_ask_spread_cost(bid_price: float, ask_price: float, trade_size: float) -> float:
    """
    Calculate bid-ask spread cost.
    
    Args:
        bid_price: Bid price
        ask_price: Ask price
        trade_size: Trade size
        
    Returns:
        Spread cost in dollars
    """
    spread = ask_price - bid_price
    mid_price = (bid_price + ask_price) / 2
    spread_cost = (spread / mid_price) * trade_size * mid_price
    return spread_cost


def total_transaction_cost(trade_size: float, price: float, bid_price: float, ask_price: float,
                          average_volume: float, volatility: float,
                          commission_rate: float = 0.001) -> Dict[str, float]:
    """
    Calculate total transaction cost including all components.
    
    Args:
        trade_size: Number of shares to trade
        price: Execution price
        bid_price: Current bid price
        ask_price: Current ask price
        average_volume: Average daily volume
        volatility: Asset volatility
        commission_rate: Commission rate (as fraction)
        
    Returns:
        Dictionary with cost breakdown
    """
    trade_value = trade_size * price
    
    # Market impact
    market_impact_pct = market_impact_cost(trade_size, average_volume, volatility)
    market_impact_cost_dollars = trade_value * market_impact_pct / 100
    
    # Bid-ask spread
    spread_cost = bid_ask_spread_cost(bid_price, ask_price, trade_size)
    
    # Commission
    commission = trade_value * commission_rate
    
    # Total cost
    total_cost = market_impact_cost_dollars + spread_cost + commission
    
    return {
        'market_impact_pct': market_impact_pct,
        'market_impact_cost': market_impact_cost_dollars,
        'spread_cost': spread_cost,
        'commission': commission,
        'total_cost': total_cost,
        'total_cost_pct': (total_cost / trade_value) * 100
    }


def optimal_trade_size(target_position: float, current_position: float,
                      average_volume: float, volatility: float,
                      max_impact_pct: float = 0.01) -> Dict[str, float]:
    """
    Calculate optimal trade size to minimize transaction costs.
    
    Args:
        target_position: Target position size
        current_position: Current position size
        average_volume: Average daily volume
        volatility: Asset volatility
        max_impact_pct: Maximum acceptable market impact (as percentage)
        
    Returns:
        Dictionary with optimal trade size and costs
    """
    desired_trade = target_position - current_position
    
    # Calculate market impact for desired trade
    impact = market_impact_cost(abs(desired_trade), average_volume, volatility)
    
    # If impact too high, reduce trade size
    if impact > max_impact_pct * 100:
        # Solve for optimal size
        optimal_size = average_volume * ((max_impact_pct * 100 / volatility) ** (1 / 0.5))
        optimal_size = min(optimal_size, abs(desired_trade))
        optimal_size = optimal_size * np.sign(desired_trade)
    else:
        optimal_size = desired_trade
    
    # Calculate costs
    optimal_impact = market_impact_cost(abs(optimal_size), average_volume, volatility)
    
    return {
        'desired_trade_size': desired_trade,
        'optimal_trade_size': optimal_size,
        'market_impact_pct': optimal_impact,
        'execution_days': abs(optimal_size) / (average_volume * 0.1) if average_volume > 0 else 0
    }


def round_trip_cost(trade_size: float, price: float, bid_price: float, ask_price: float,
                   average_volume: float, volatility: float,
                   commission_rate: float = 0.001) -> float:
    """
    Calculate round-trip transaction cost (buy and sell).
    
    Args:
        trade_size: Number of shares
        price: Execution price
        bid_price: Current bid price
        ask_price: Current ask price
        average_volume: Average daily volume
        volatility: Asset volatility
        commission_rate: Commission rate
        
    Returns:
        Round-trip cost (as percentage)
    """
    # Buy cost
    buy_cost = total_transaction_cost(trade_size, ask_price, bid_price, ask_price,
                                    average_volume, volatility, commission_rate)
    
    # Sell cost (use bid price)
    sell_cost = total_transaction_cost(trade_size, bid_price, bid_price, ask_price,
                                     average_volume, volatility, commission_rate)
    
    trade_value = trade_size * price
    total_round_trip = buy_cost['total_cost'] + sell_cost['total_cost']
    
    return (total_round_trip / trade_value) * 100


def transaction_cost_attribution(portfolio_returns: pd.Series,
                                  trade_costs: pd.Series) -> Dict[str, float]:
    """
    Attribute portfolio performance impact from transaction costs.
    
    Args:
        portfolio_returns: Series of portfolio returns
        trade_costs: Series of transaction costs (as percentages)
        
    Returns:
        Dictionary with cost attribution
    """
    # Align data
    aligned = pd.DataFrame({
        'returns': portfolio_returns,
        'costs': trade_costs
    }).dropna()
    
    if len(aligned) == 0:
        return {
            'total_cost_impact': 0.0,
            'cost_per_return': 0.0,
            'net_return': 0.0
        }
    
    # Net returns after costs
    net_returns = aligned['returns'] - aligned['costs']
    
    # Cost impact
    total_cost = aligned['costs'].sum()
    total_return = aligned['returns'].sum()
    net_return = net_returns.sum()
    
    return {
        'total_cost_impact': total_cost,
        'gross_return': total_return,
        'net_return': net_return,
        'cost_per_return': total_cost / abs(total_return) if total_return != 0 else 0.0,
        'cost_drag_pct': (total_return - net_return) / abs(total_return) * 100 if total_return != 0 else 0.0
    }


def implementation_shortfall_analysis(decision_price: float, execution_prices: pd.Series,
                                     executed_quantities: pd.Series,
                                     benchmark_price: Optional[float] = None) -> Dict[str, float]:
    """
    Detailed Implementation Shortfall analysis.
    
    Args:
        decision_price: Price at which trading decision was made
        execution_prices: Series of execution prices
        executed_quantities: Series of executed quantities
        benchmark_price: Benchmark price (default: VWAP)
        
    Returns:
        Dictionary with IS components
    """
    if benchmark_price is None:
        # Use VWAP as benchmark
        total_quantity = executed_quantities.sum()
        if total_quantity > 0:
            benchmark_price = (execution_prices * executed_quantities).sum() / total_quantity
        else:
            benchmark_price = decision_price
    
    total_quantity = executed_quantities.sum()
    if total_quantity == 0:
        return {
            'total_shortfall': 0.0,
            'execution_cost': 0.0,
            'opportunity_cost': 0.0,
            'market_impact': 0.0
        }
    
    # Weighted average execution price
    execution_price = (execution_prices * executed_quantities).sum() / total_quantity
    
    # Implementation shortfall components
    execution_cost = (execution_price - decision_price) * total_quantity
    opportunity_cost = (benchmark_price - decision_price) * total_quantity
    market_impact = (execution_price - benchmark_price) * total_quantity
    
    total_shortfall = execution_cost + opportunity_cost
    
    return {
        'total_shortfall': total_shortfall,
        'execution_cost': execution_cost,
        'opportunity_cost': opportunity_cost,
        'market_impact': market_impact,
        'execution_price': execution_price,
        'shortfall_pct': (execution_price - decision_price) / decision_price * 100
    }


if __name__ == "__main__":
    # Example usage
    print("Transaction Cost Analysis Demo")
    print("=" * 50)
    
    # Total transaction cost example
    cost = total_transaction_cost(1000, 100.0, 99.9, 100.1, 10000, 0.02)
    print("\nTotal Transaction Cost:")
    for key, value in cost.items():
        print(f"  {key}: {value:.4f}")
