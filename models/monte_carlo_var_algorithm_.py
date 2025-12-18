"""
Module: monte_carlo_var_algorithm

This module implements the Monte Carlo Value at Risk (VaR) algorithm for a quantitative finance portfolio.

Requirements:
- Must be generic and applicable to any financial portfolio
- Utilizes Monte Carlo simulation for risk assessment
- Provides a quantitative analysis of portfolio risk
- Includes proper documentation, type hints, and error handling
- Uses appropriate libraries for financial calculations

Example usage:
    # Create a portfolio
    portfolio = {
        'AAPL': 0.3,
        'GOOGL': 0.2,
        'MSFT': 0.5
    }

    # Define parameters
    initial_investment = 1000000
    num_simulations = 1000
    confidence_level = 0.95

    # Calculate VaR using Monte Carlo simulation
    var = calculate_monte_carlo_var(portfolio, initial_investment, num_simulations, confidence_level)
    print(f"VaR at {confidence_level} confidence level: {var}")
"""

from typing import Dict, List
import numpy as np

def calculate_monte_carlo_var(portfolio: Dict[str, float], initial_investment: float, num_simulations: int, confidence_level: float) -> float:
    """
    Calculate Value at Risk (VaR) using Monte Carlo simulation for a given portfolio.

    Args:
        portfolio (Dict[str, float]): Dictionary of asset weights in the portfolio
        initial_investment (float): Initial investment amount in the portfolio
        num_simulations (int): Number of Monte Carlo simulations to run
        confidence_level (float): Desired confidence level for VaR calculation

    Returns:
        float: Value at Risk (VaR) at the specified confidence level
    """
    # Generate random returns for each asset in the portfolio
    returns = np.random.normal(0.001, 0.02, (num_simulations, len(portfolio)))

    # Calculate portfolio value for each simulation
    portfolio_values = []
    for i in range(num_simulations):
        simulation_returns = returns[i]
        portfolio_value = initial_investment
        for asset, weight in portfolio.items():
            asset_return = simulation_returns.pop(0)
            asset_value = portfolio_value * weight * (1 + asset_return)
            portfolio_value += asset_value
        portfolio_values.append(portfolio_value)

    # Calculate VaR based on confidence level
    var = np.percentile(portfolio_values, (1 - confidence_level) * 100)
    return var

if __name__ == "__main__":
    # Example usage
    portfolio = {
        'AAPL': 0.3,
        'GOOGL': 0.2,
        'MSFT': 0.5
    }

    initial_investment = 1000000
    num_simulations = 1000
    confidence_level = 0.95

    var = calculate_monte_carlo_var(portfolio, initial_investment, num_simulations, confidence_level)
    print(f"VaR at {confidence_level} confidence level: {var}")