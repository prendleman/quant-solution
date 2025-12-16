"""
Derivatives Pricing and Analysis

Options pricing, Greeks calculation, and derivatives analysis.
Generated as part of quant portfolio development.
"""

from typing import Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import norm


def black_scholes_price(S: float, K: float, T: float, r: float, sigma: float, option_type: str = 'call') -> float:
    """
    Calculate Black-Scholes option price.
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (in years)
        r: Risk-free interest rate
        sigma: Volatility
        option_type: 'call' or 'put'
        
    Returns:
        Option price
    """
    if T <= 0:
        return max(S - K, 0) if option_type == 'call' else max(K - S, 0)
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == 'call':
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:  # put
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    return price


def calculate_greeks(S: float, K: float, T: float, r: float, sigma: float, option_type: str = 'call') -> dict:
    """
    Calculate option Greeks (Delta, Gamma, Theta, Vega, Rho).
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (in years)
        r: Risk-free interest rate
        sigma: Volatility
        option_type: 'call' or 'put'
        
    Returns:
        Dictionary with Greeks values
    """
    if T <= 0:
        return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0}
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    # Delta
    if option_type == 'call':
        delta = norm.cdf(d1)
    else:
        delta = norm.cdf(d1) - 1
    
    # Gamma (same for call and put)
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    
    # Theta
    if option_type == 'call':
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) - 
                 r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
    else:
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) + 
                 r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
    
    # Vega (same for call and put)
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100
    
    # Rho
    if option_type == 'call':
        rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100
    else:
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100
    
    return {
        'delta': delta,
        'gamma': gamma,
        'theta': theta,
        'vega': vega,
        'rho': rho
    }


def monte_carlo_option_price(S: float, K: float, T: float, r: float, sigma: float, 
                            option_type: str = 'call', n_simulations: int = 100000) -> Tuple[float, float]:
    """
    Calculate option price using Monte Carlo simulation.
    
    Args:
        S: Current stock price
        K: Strike price
        T: Time to expiration (in years)
        r: Risk-free interest rate
        sigma: Volatility
        option_type: 'call' or 'put'
        n_simulations: Number of Monte Carlo simulations
        
    Returns:
        Tuple of (option_price, standard_error)
    """
    # Generate random stock prices at expiration
    random_shocks = np.random.normal(0, 1, n_simulations)
    stock_prices = S * np.exp((r - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * random_shocks)
    
    # Calculate payoffs
    if option_type == 'call':
        payoffs = np.maximum(stock_prices - K, 0)
    else:
        payoffs = np.maximum(K - stock_prices, 0)
    
    # Discount to present value
    option_price = np.exp(-r * T) * np.mean(payoffs)
    standard_error = np.exp(-r * T) * np.std(payoffs) / np.sqrt(n_simulations)
    
    return option_price, standard_error


if __name__ == "__main__":
    # Example usage
    S, K, T, r, sigma = 100, 105, 0.25, 0.05, 0.2
    
    # Black-Scholes pricing
    call_price = black_scholes_price(S, K, T, r, sigma, 'call')
    put_price = black_scholes_price(S, K, T, r, sigma, 'put')
    print(f"Call option price: ${call_price:.2f}")
    print(f"Put option price: ${put_price:.2f}")
    
    # Greeks
    greeks = calculate_greeks(S, K, T, r, sigma, 'call')
    print(f"\nGreeks for call option:")
    for greek, value in greeks.items():
        print(f"  {greek.capitalize()}: {value:.4f}")
    
    # Monte Carlo pricing
    mc_price, se = monte_carlo_option_price(S, K, T, r, sigma, 'call', 100000)
    print(f"\nMonte Carlo call price: ${mc_price:.2f} (SE: ${se:.4f})")
