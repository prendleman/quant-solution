"""
Execution Algorithms for Quantitative Trading

Advanced execution algorithms including TWAP, VWAP, Implementation Shortfall,
and adaptive execution strategies for optimal trade execution.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def twap_execution(target_quantity: float, start_time: datetime, end_time: datetime,
                   n_intervals: int = 10) -> pd.DataFrame:
    """
    Time-Weighted Average Price (TWAP) execution algorithm.
    Splits order into equal time intervals.
    
    Args:
        target_quantity: Total quantity to execute
        start_time: Start time of execution
        end_time: End time of execution
        n_intervals: Number of time intervals
        
    Returns:
        DataFrame with execution schedule (time, quantity)
    """
    time_delta = (end_time - start_time) / n_intervals
    quantity_per_interval = target_quantity / n_intervals
    
    schedule = []
    current_time = start_time
    
    for i in range(n_intervals):
        schedule.append({
            'time': current_time,
            'quantity': quantity_per_interval,
            'cumulative_quantity': (i + 1) * quantity_per_interval
        })
        current_time += time_delta
    
    return pd.DataFrame(schedule)


def vwap_execution(target_quantity: float, historical_volume: pd.Series,
                   start_time: datetime, end_time: datetime) -> pd.DataFrame:
    """
    Volume-Weighted Average Price (VWAP) execution algorithm.
    Executes order proportionally to historical volume profile.
    
    Args:
        target_quantity: Total quantity to execute
        historical_volume: Historical volume time series
        start_time: Start time of execution
        end_time: End time of execution
        
    Returns:
        DataFrame with execution schedule
    """
    # Filter historical volume to execution window
    mask = (historical_volume.index >= start_time) & (historical_volume.index <= end_time)
    window_volume = historical_volume[mask]
    
    if len(window_volume) == 0:
        # Fallback to TWAP if no volume data
        return twap_execution(target_quantity, start_time, end_time)
    
    total_volume = window_volume.sum()
    volume_weights = window_volume / total_volume
    execution_quantities = volume_weights * target_quantity
    
    schedule = pd.DataFrame({
        'time': execution_quantities.index,
        'quantity': execution_quantities.values,
        'cumulative_quantity': execution_quantities.cumsum().values
    })
    
    return schedule


def implementation_shortfall(entry_price: float, execution_prices: pd.Series,
                            target_quantity: float, executed_quantities: pd.Series,
                            benchmark_price: Optional[float] = None) -> Dict[str, float]:
    """
    Calculate Implementation Shortfall (IS) - the difference between decision price
    and execution price, including market impact and opportunity cost.
    
    Args:
        entry_price: Price at which decision was made
        execution_prices: Series of execution prices
        target_quantity: Target quantity to execute
        executed_quantities: Series of executed quantities
        benchmark_price: Benchmark price (default: entry_price)
        
    Returns:
        Dictionary with IS components: total_cost, market_impact, timing_cost, opportunity_cost
    """
    if benchmark_price is None:
        benchmark_price = entry_price
    
    # Calculate weighted average execution price
    total_executed = executed_quantities.sum()
    if total_executed == 0:
        return {
            'total_cost': 0.0,
            'market_impact': 0.0,
            'timing_cost': 0.0,
            'opportunity_cost': 0.0,
            'execution_price': entry_price
        }
    
    weighted_execution_price = (execution_prices * executed_quantities).sum() / total_executed
    
    # Implementation shortfall components
    market_impact = (weighted_execution_price - entry_price) * total_executed
    timing_cost = (weighted_execution_price - benchmark_price) * total_executed
    opportunity_cost = (benchmark_price - entry_price) * (target_quantity - total_executed)
    total_cost = market_impact + timing_cost + opportunity_cost
    
    return {
        'total_cost': total_cost,
        'market_impact': market_impact,
        'timing_cost': timing_cost,
        'opportunity_cost': opportunity_cost,
        'execution_price': weighted_execution_price,
        'execution_shortfall_pct': (weighted_execution_price - entry_price) / entry_price * 100
    }


def adaptive_execution(target_quantity: float, current_price: float, 
                      volatility: float, urgency: float = 0.5,
                      max_slippage: float = 0.001) -> pd.DataFrame:
    """
    Adaptive execution algorithm that adjusts execution speed based on market conditions.
    
    Args:
        target_quantity: Total quantity to execute
        current_price: Current market price
        volatility: Current volatility estimate
        urgency: Urgency factor (0-1, higher = more urgent)
        max_slippage: Maximum acceptable slippage
        
    Returns:
        DataFrame with adaptive execution schedule
    """
    # Base execution time based on urgency
    base_intervals = int(10 / (urgency + 0.1))
    
    # Adjust for volatility (higher volatility = slower execution)
    volatility_adjustment = 1 + volatility * 2
    n_intervals = max(1, int(base_intervals * volatility_adjustment))
    
    # Calculate quantity per interval (front-loading for high urgency)
    if urgency > 0.7:
        # Aggressive: front-loaded
        weights = np.exp(np.linspace(0, -2, n_intervals))
    elif urgency < 0.3:
        # Conservative: back-loaded
        weights = np.exp(np.linspace(-2, 0, n_intervals))
    else:
        # Balanced: uniform
        weights = np.ones(n_intervals)
    
    weights = weights / weights.sum()
    quantities = weights * target_quantity
    
    schedule = pd.DataFrame({
        'interval': range(n_intervals),
        'quantity': quantities,
        'cumulative_quantity': quantities.cumsum(),
        'urgency': urgency,
        'volatility': volatility
    })
    
    return schedule


def optimal_execution(target_quantity: float, price_series: pd.Series,
                     volume_series: pd.Series, risk_aversion: float = 0.5) -> pd.DataFrame:
    """
    Optimal execution using Almgren-Chriss model.
    Balances market impact cost and execution risk.
    
    Args:
        target_quantity: Total quantity to execute
        price_series: Historical price series
        volume_series: Historical volume series
        risk_aversion: Risk aversion parameter (0-1)
        
    Returns:
        DataFrame with optimal execution schedule
    """
    # Estimate market impact parameters
    returns = price_series.pct_change().dropna()
    volatility = returns.std() * np.sqrt(252)  # Annualized
    
    # Estimate temporary market impact (simplified)
    avg_volume = volume_series.mean()
    market_impact_coef = volatility / (avg_volume ** 0.5) if avg_volume > 0 else 0.001
    
    # Almgren-Chriss optimal execution
    # Simplified version: exponential decay schedule
    n_intervals = 20
    lambda_param = risk_aversion * volatility / market_impact_coef
    
    # Optimal trading rate (exponential decay)
    times = np.linspace(0, 1, n_intervals)
    if lambda_param > 0:
        rates = np.exp(-lambda_param * times)
        rates = rates / rates.sum()
    else:
        rates = np.ones(n_intervals) / n_intervals
    
    quantities = rates * target_quantity
    
    schedule = pd.DataFrame({
        'interval': range(n_intervals),
        'quantity': quantities,
        'cumulative_quantity': quantities.cumsum(),
        'trading_rate': rates,
        'risk_aversion': risk_aversion
    })
    
    return schedule


def evaluate_execution_quality(execution_schedule: pd.DataFrame,
                               actual_executions: pd.DataFrame,
                               benchmark_price: float) -> Dict[str, float]:
    """
    Evaluate execution quality metrics.
    
    Args:
        execution_schedule: Planned execution schedule
        actual_executions: Actual execution results
        benchmark_price: Benchmark price for comparison
        
    Returns:
        Dictionary with execution quality metrics
    """
    if len(actual_executions) == 0:
        return {
            'completion_rate': 0.0,
            'slippage': 0.0,
            'participation_rate': 0.0,
            'efficiency': 0.0
        }
    
    target_quantity = execution_schedule['quantity'].sum()
    actual_quantity = actual_executions['quantity'].sum()
    
    completion_rate = actual_quantity / target_quantity if target_quantity > 0 else 0.0
    
    # Calculate weighted average execution price
    if 'price' in actual_executions.columns:
        execution_price = (actual_executions['price'] * actual_executions['quantity']).sum() / actual_quantity
        slippage = (execution_price - benchmark_price) / benchmark_price * 100
    else:
        slippage = 0.0
    
    # Participation rate (simplified)
    participation_rate = completion_rate
    
    # Efficiency (inverse of slippage, normalized)
    efficiency = max(0, 100 - abs(slippage))
    
    return {
        'completion_rate': completion_rate,
        'slippage_pct': slippage,
        'participation_rate': participation_rate,
        'efficiency': efficiency,
        'target_quantity': target_quantity,
        'actual_quantity': actual_quantity
    }


if __name__ == "__main__":
    # Example usage
    print("Execution Algorithms Demo")
    print("=" * 50)
    
    # TWAP example
    start = datetime.now()
    end = start + timedelta(hours=1)
    twap_schedule = twap_execution(1000, start, end, n_intervals=10)
    print("\nTWAP Execution Schedule:")
    print(twap_schedule.head())
    
    # VWAP example
    dates = pd.date_range(start, end, periods=20)
    historical_volume = pd.Series(np.random.uniform(100, 500, 20), index=dates)
    vwap_schedule = vwap_execution(1000, historical_volume, start, end)
    print("\nVWAP Execution Schedule:")
    print(vwap_schedule.head())
    
    # Implementation Shortfall example
    entry_price = 100.0
    exec_prices = pd.Series([100.1, 100.2, 100.15, 100.3, 100.25])
    exec_quantities = pd.Series([200, 200, 200, 200, 200])
    is_result = implementation_shortfall(entry_price, exec_prices, 1000, exec_quantities)
    print("\nImplementation Shortfall:")
    for key, value in is_result.items():
        print(f"  {key}: {value:.4f}")
    
    # Adaptive execution example
    adaptive_schedule = adaptive_execution(1000, 100.0, 0.02, urgency=0.7)
    print("\nAdaptive Execution Schedule:")
    print(adaptive_schedule.head())
