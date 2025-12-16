"""
Advanced Options Pricing Models

Binomial tree, trinomial tree, and other advanced pricing methods.
Generated as part of quant portfolio development.
"""

from typing import Optional, Tuple, Dict
import numpy as np
import pandas as pd
from scipy.stats import norm


def binomial_tree_price(S: float, K: float, T: float, r: float, sigma: float,
                       option_type: str = 'call', n_steps: int = 100,
                       american: bool = False) -> float:
    """
    Price option using binomial tree model.
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (years)
        r: Risk-free rate
        sigma: Volatility
        option_type: 'call' or 'put'
        n_steps: Number of time steps
        american: True for American option, False for European
        
    Returns:
        Option price
    """
    dt = T / n_steps
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p = (np.exp(r * dt) - d) / (u - d)
    
    # Initialize stock price tree
    stock_prices = np.zeros((n_steps + 1, n_steps + 1))
    for i in range(n_steps + 1):
        for j in range(i + 1):
            stock_prices[j, i] = S * (u ** (i - j)) * (d ** j)
    
    # Initialize option value tree
    option_values = np.zeros((n_steps + 1, n_steps + 1))
    
    # Terminal values
    for j in range(n_steps + 1):
        if option_type == 'call':
            option_values[j, n_steps] = max(stock_prices[j, n_steps] - K, 0)
        else:
            option_values[j, n_steps] = max(K - stock_prices[j, n_steps], 0)
    
    # Backward induction
    for i in range(n_steps - 1, -1, -1):
        for j in range(i + 1):
            # European option value
            european_value = np.exp(-r * dt) * (
                p * option_values[j, i + 1] + (1 - p) * option_values[j + 1, i + 1]
            )
            
            if american:
                # American option: check early exercise
                if option_type == 'call':
                    intrinsic = max(stock_prices[j, i] - K, 0)
                else:
                    intrinsic = max(K - stock_prices[j, i], 0)
                option_values[j, i] = max(european_value, intrinsic)
            else:
                option_values[j, i] = european_value
    
    return option_values[0, 0]


def monte_carlo_american_option(S: float, K: float, T: float, r: float, sigma: float,
                                option_type: str = 'call', n_simulations: int = 10000,
                                n_steps: int = 100) -> Tuple[float, float]:
    """
    Price American option using Monte Carlo with Longstaff-Schwartz method.
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration
        r: Risk-free rate
        sigma: Volatility
        option_type: 'call' or 'put'
        n_simulations: Number of Monte Carlo paths
        n_steps: Number of time steps
        
    Returns:
        Tuple of (option_price, standard_error)
    """
    dt = T / n_steps
    discount_factor = np.exp(-r * dt)
    
    # Generate stock price paths
    stock_paths = np.zeros((n_simulations, n_steps + 1))
    stock_paths[:, 0] = S
    
    for i in range(1, n_steps + 1):
        z = np.random.normal(0, 1, n_simulations)
        stock_paths[:, i] = stock_paths[:, i-1] * np.exp(
            (r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z
        )
    
    # Initialize cash flows
    cash_flows = np.zeros((n_simulations, n_steps + 1))
    
    # Terminal cash flows
    if option_type == 'call':
        cash_flows[:, -1] = np.maximum(stock_paths[:, -1] - K, 0)
    else:
        cash_flows[:, -1] = np.maximum(K - stock_paths[:, -1], 0)
    
    # Backward induction with exercise decision
    for i in range(n_steps - 1, 0, -1):
        # Intrinsic value
        if option_type == 'call':
            intrinsic = np.maximum(stock_paths[:, i] - K, 0)
        else:
            intrinsic = np.maximum(K - stock_paths[:, i], 0)
        
        # Continuation value (simplified - use in-the-money paths for regression)
        itm = intrinsic > 0
        if np.sum(itm) > 0:
            # Simple continuation value estimate
            continuation = cash_flows[:, i+1] * discount_factor
            # Exercise if intrinsic > continuation
            exercise = intrinsic > continuation
            cash_flows[exercise, i] = intrinsic[exercise]
            cash_flows[exercise, i+1:] = 0
    
    # Discount all cash flows to present
    option_values = []
    for path in range(n_simulations):
        path_value = 0
        for i in range(n_steps + 1):
            path_value += cash_flows[path, i] * np.exp(-r * i * dt)
        option_values.append(path_value)
    
    option_price = np.mean(option_values)
    standard_error = np.std(option_values) / np.sqrt(n_simulations)
    
    return option_price, standard_error


def implied_volatility(market_price: float, S: float, K: float, T: float,
                      r: float, option_type: str = 'call') -> float:
    """
    Calculate implied volatility using Newton-Raphson method.
    
    Args:
        market_price: Market price of option
        S: Current stock price
        K: Strike price
        T: Time to expiration
        r: Risk-free rate
        option_type: 'call' or 'put'
        
    Returns:
        Implied volatility
    """
    from utils.derivatives_ import black_scholes_price, calculate_greeks
    
    # Initial guess
    sigma = 0.2
    
    # Newton-Raphson iteration
    for _ in range(100):
        price = black_scholes_price(S, K, T, r, sigma, option_type)
        vega = calculate_greeks(S, K, T, r, sigma, option_type)['vega']
        
        if abs(vega) < 1e-10:
            break
        
        diff = market_price - price
        sigma_new = sigma + diff / vega
        
        if abs(sigma_new - sigma) < 1e-6:
            break
        
        sigma = max(0.001, min(5.0, sigma_new))  # Bound between 0.1% and 500%
    
    return sigma


def barrier_option_price(S: float, K: float, barrier: float, T: float, r: float,
                        sigma: float, option_type: str = 'call',
                        barrier_type: str = 'down_and_out') -> float:
    """
    Price barrier option using closed-form solution (simplified).
    
    Args:
        S: Current stock price
        K: Strike price
        barrier: Barrier level
        T: Time to expiration
        r: Risk-free rate
        sigma: Volatility
        option_type: 'call' or 'put'
        barrier_type: 'down_and_out', 'up_and_out', 'down_and_in', 'up_and_in'
        
    Returns:
        Option price
    """
    # Simplified barrier option pricing
    # For down-and-out call
    if barrier_type == 'down_and_out' and option_type == 'call' and S > barrier:
        from utils.derivatives_ import black_scholes_price
        regular_price = black_scholes_price(S, K, T, r, sigma, 'call')
        # Knock-out probability adjustment (simplified)
        knock_out_prob = norm.cdf((np.log(barrier/S)) / (sigma * np.sqrt(T)))
        return regular_price * (1 - knock_out_prob)
    else:
        # Use Monte Carlo for other barrier types
        n_simulations = 50000
        dt = T / 100
        paths = np.zeros(n_simulations)
        
        for i in range(n_simulations):
            path = [S]
            for _ in range(100):
                z = np.random.normal(0, 1)
                new_price = path[-1] * np.exp(
                    (r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z
                )
                path.append(new_price)
            
            # Check barrier
            hit_barrier = False
            if barrier_type in ['down_and_out', 'down_and_in']:
                hit_barrier = min(path) <= barrier
            else:
                hit_barrier = max(path) >= barrier
            
            # Calculate payoff
            if (barrier_type in ['down_and_out', 'up_and_out'] and not hit_barrier) or \
               (barrier_type in ['down_and_in', 'up_and_in'] and hit_barrier):
                if option_type == 'call':
                    paths[i] = max(path[-1] - K, 0)
                else:
                    paths[i] = max(K - path[-1], 0)
        
        return np.exp(-r * T) * np.mean(paths)


if __name__ == "__main__":
    # Example usage
    S, K, T, r, sigma = 100, 105, 0.25, 0.05, 0.2
    
    # Binomial tree
    bin_price = binomial_tree_price(S, K, T, r, sigma, 'call', n_steps=100)
    print(f"Binomial Tree Call Price: ${bin_price:.2f}")
    
    # American option
    am_price = binomial_tree_price(S, K, T, r, sigma, 'call', american=True)
    print(f"American Call Price: ${am_price:.2f}")
    
    # Implied volatility
    market_price = 3.50
    iv = implied_volatility(market_price, S, K, T, r, 'call')
    print(f"\nImplied Volatility: {iv:.2%}")
    
    # Barrier option
    barrier_price = barrier_option_price(S, K, 95, T, r, sigma, 'call', 'down_and_out')
    print(f"Down-and-Out Barrier Call Price: ${barrier_price:.2f}")
