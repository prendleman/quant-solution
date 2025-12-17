"""
Module: Cost Containment Implementation

This module contains functions for implementing cost containment strategies in a quantitative finance portfolio.

Requirements:
- Must be generic (no company names, job titles, or role-specific details)
- Include proper docstrings, type hints, and error handling
- Use appropriate libraries: r
- Demonstrate quant skills related to: medical stop loss expertise, derivatives, claims administration
- Include example usage in __main__ block
- Code should be production-ready and portfolio-quality
"""

import r

def calculate_stop_loss_premium(claims: List[float], stop_loss_level: float) -> float:
    """
    Calculate the stop loss premium based on the claims data and stop loss level.

    Args:
    - claims: List of claim amounts
    - stop_loss_level: Stop loss level for the portfolio

    Returns:
    - stop_loss_premium: Premium for the stop loss coverage
    """
    total_claims = sum(claims)
    stop_loss_claims = sum([claim for claim in claims if claim > stop_loss_level])
    stop_loss_premium = max(0, stop_loss_claims - stop_loss_level)

    return stop_loss_premium

def calculate_derivative_price(underlying_price: float, strike_price: float, volatility: float, time_to_maturity: float) -> float:
    """
    Calculate the price of a derivative based on the Black-Scholes model.

    Args:
    - underlying_price: Current price of the underlying asset
    - strike_price: Strike price of the derivative
    - volatility: Volatility of the underlying asset
    - time_to_maturity: Time to maturity of the derivative

    Returns:
    - derivative_price: Price of the derivative
    """
    d1 = (math.log(underlying_price / strike_price) + (0.5 * volatility**2) * time_to_maturity) / (volatility * math.sqrt(time_to_maturity))
    d2 = d1 - volatility * math.sqrt(time_to_maturity)

    derivative_price = underlying_price * norm.cdf(d1) - strike_price * norm.cdf(d2)

    return derivative_price

if __name__ == "__main__":
    claims_data = [10000, 15000, 20000, 25000, 30000]
    stop_loss_level = 20000
    stop_loss_premium = calculate_stop_loss_premium(claims_data, stop_loss_level)
    print(f"Stop Loss Premium: ${stop_loss_premium}")

    underlying_price = 100
    strike_price = 110
    volatility = 0.2
    time_to_maturity = 0.5
    derivative_price = calculate_derivative_price(underlying_price, strike_price, volatility, time_to_maturity)
    print(f"Derivative Price: ${derivative_price}")