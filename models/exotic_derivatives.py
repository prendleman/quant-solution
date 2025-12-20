"""
Exotic Derivatives Pricing

Pricing models for exotic options including Asian, Barrier, Lookback,
and other path-dependent options.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.stats import norm


def asian_option_price(spot_price: float, strike: float, time_to_maturity: float,
                      risk_free_rate: float, volatility: float, option_type: str = 'call',
                      averaging_type: str = 'arithmetic') -> float:
    """
    Price Asian option (average price option).
    
    Args:
        spot_price: Current spot price
        strike: Strike price
        time_to_maturity: Time to maturity in years
        risk_free_rate: Risk-free rate
        volatility: Volatility
        option_type: 'call' or 'put'
        averaging_type: 'arithmetic' or 'geometric'
        
    Returns:
        Option price
    """
    # Geometric average (closed form)
    if averaging_type == 'geometric':
        adjusted_vol = volatility / np.sqrt(3)
        adjusted_rate = (risk_free_rate - volatility ** 2 / 6) / 2
        
        d1 = (np.log(spot_price / strike) + (adjusted_rate + adjusted_vol ** 2 / 2) * time_to_maturity) / (adjusted_vol * np.sqrt(time_to_maturity))
        d2 = d1 - adjusted_vol * np.sqrt(time_to_maturity)
        
        if option_type == 'call':
            price = spot_price * np.exp((adjusted_rate - risk_free_rate) * time_to_maturity) * norm.cdf(d1) - strike * np.exp(-risk_free_rate * time_to_maturity) * norm.cdf(d2)
        else:  # put
            price = strike * np.exp(-risk_free_rate * time_to_maturity) * norm.cdf(-d2) - spot_price * np.exp((adjusted_rate - risk_free_rate) * time_to_maturity) * norm.cdf(-d1)
        
        return price
    else:
        # Arithmetic average (Monte Carlo approximation)
        n_simulations = 10000
        dt = time_to_maturity / 252
        n_steps = 252
        
        payoffs = []
        for _ in range(n_simulations):
            prices = [spot_price]
            for _ in range(n_steps):
                prices.append(prices[-1] * np.exp((risk_free_rate - 0.5 * volatility ** 2) * dt + volatility * np.sqrt(dt) * np.random.randn()))
            
            avg_price = np.mean(prices)
            if option_type == 'call':
                payoff = max(0, avg_price - strike)
            else:
                payoff = max(0, strike - avg_price)
            payoffs.append(payoff)
        
        return np.exp(-risk_free_rate * time_to_maturity) * np.mean(payoffs)


def barrier_option_price(spot_price: float, strike: float, barrier: float,
                        time_to_maturity: float, risk_free_rate: float,
                        volatility: float, option_type: str = 'call',
                        barrier_type: str = 'down_and_out') -> float:
    """
    Price barrier option.
    
    Args:
        spot_price: Current spot price
        strike: Strike price
        barrier: Barrier level
        time_to_maturity: Time to maturity
        risk_free_rate: Risk-free rate
        volatility: Volatility
        option_type: 'call' or 'put'
        barrier_type: 'down_and_out', 'up_and_out', 'down_and_in', 'up_and_in'
        
    Returns:
        Option price
    """
    # Simplified barrier option pricing (Monte Carlo)
    n_simulations = 10000
    dt = time_to_maturity / 252
    n_steps = 252
    
    payoffs = []
    for _ in range(n_simulations):
        prices = [spot_price]
        barrier_hit = False
        
        for _ in range(n_steps):
            prices.append(prices[-1] * np.exp((risk_free_rate - 0.5 * volatility ** 2) * dt + volatility * np.sqrt(dt) * np.random.randn()))
            
            # Check barrier
            if barrier_type in ['down_and_out', 'down_and_in']:
                if prices[-1] <= barrier:
                    barrier_hit = True
            else:  # up_and_out, up_and_in
                if prices[-1] >= barrier:
                    barrier_hit = True
        
        final_price = prices[-1]
        
        # Calculate payoff based on barrier type
        if barrier_type in ['down_and_out', 'up_and_out']:
            # Out option: payoff only if barrier not hit
            if not barrier_hit:
                if option_type == 'call':
                    payoff = max(0, final_price - strike)
                else:
                    payoff = max(0, strike - final_price)
            else:
                payoff = 0
        else:  # in options
            # In option: payoff only if barrier hit
            if barrier_hit:
                if option_type == 'call':
                    payoff = max(0, final_price - strike)
                else:
                    payoff = max(0, strike - final_price)
            else:
                payoff = 0
        
        payoffs.append(payoff)
    
    return np.exp(-risk_free_rate * time_to_maturity) * np.mean(payoffs)


def lookback_option_price(spot_price: float, time_to_maturity: float,
                          risk_free_rate: float, volatility: float,
                          option_type: str = 'call', lookback_type: str = 'floating') -> float:
    """
    Price lookback option (option on maximum/minimum price).
    
    Args:
        spot_price: Current spot price
        time_to_maturity: Time to maturity
        risk_free_rate: Risk-free rate
        volatility: Volatility
        option_type: 'call' or 'put'
        lookback_type: 'floating' (strike = min/max) or 'fixed' (strike fixed)
        
    Returns:
        Option price
    """
    # Monte Carlo pricing
    n_simulations = 10000
    dt = time_to_maturity / 252
    n_steps = 252
    
    payoffs = []
    for _ in range(n_simulations):
        prices = [spot_price]
        for _ in range(n_steps):
            prices.append(prices[-1] * np.exp((risk_free_rate - 0.5 * volatility ** 2) * dt + volatility * np.sqrt(dt) * np.random.randn()))
        
        if lookback_type == 'floating':
            if option_type == 'call':
                # Call: max price - min price
                payoff = max(prices) - min(prices)
            else:
                # Put: max price - min price (same for floating)
                payoff = max(prices) - min(prices)
        else:  # fixed strike
            strike = spot_price
            if option_type == 'call':
                payoff = max(0, max(prices) - strike)
            else:
                payoff = max(0, strike - min(prices))
        
        payoffs.append(payoff)
    
    return np.exp(-risk_free_rate * time_to_maturity) * np.mean(payoffs)


def binary_option_price(spot_price: float, strike: float, time_to_maturity: float,
                       risk_free_rate: float, volatility: float,
                       option_type: str = 'call', payoff: float = 1.0) -> float:
    """
    Price binary (digital) option.
    
    Args:
        spot_price: Current spot price
        strike: Strike price
        time_to_maturity: Time to maturity
        risk_free_rate: Risk-free rate
        volatility: Volatility
        option_type: 'call' or 'put'
        payoff: Binary payoff amount
        
    Returns:
        Option price
    """
    d2 = (np.log(spot_price / strike) + (risk_free_rate - 0.5 * volatility ** 2) * time_to_maturity) / (volatility * np.sqrt(time_to_maturity))
    
    if option_type == 'call':
        price = payoff * np.exp(-risk_free_rate * time_to_maturity) * norm.cdf(d2)
    else:  # put
        price = payoff * np.exp(-risk_free_rate * time_to_maturity) * norm.cdf(-d2)
    
    return price


def chooser_option_price(spot_price: float, strike: float, time_to_maturity: float,
                        choice_date: float, risk_free_rate: float,
                        volatility: float) -> float:
    """
    Price chooser option (choose call or put at choice_date).
    
    Args:
        spot_price: Current spot price
        strike: Strike price
        time_to_maturity: Time to maturity
        choice_date: Date to choose option type
        risk_free_rate: Risk-free rate
        volatility: Volatility
        
    Returns:
        Option price
    """
    # Simplified: value as max of call and put at choice date
    time_to_choice = choice_date
    remaining_time = time_to_maturity - choice_date
    
    # Value call and put at choice date
    from utils.derivatives_ import black_scholes_price
    
    call_value = black_scholes_price(spot_price, strike, remaining_time, risk_free_rate, volatility, 'call')
    put_value = black_scholes_price(spot_price, strike, remaining_time, risk_free_rate, volatility, 'put')
    
    # Chooser value = max(call, put) discounted to today
    chooser_value = max(call_value, put_value) * np.exp(-risk_free_rate * time_to_choice)
    
    return chooser_value


if __name__ == "__main__":
    # Example usage
    print("Exotic Derivatives Demo")
    print("=" * 50)
    
    # Asian option
    asian_price = asian_option_price(100, 100, 0.25, 0.03, 0.2, 'call', 'geometric')
    print(f"\nAsian Option Price: ${asian_price:.2f}")
    
    # Binary option
    binary_price = binary_option_price(100, 100, 0.25, 0.03, 0.2, 'call')
    print(f"Binary Option Price: ${binary_price:.2f}")
