"""
Module: portfolio_management

This module contains functions for managing a quantitative finance portfolio using applications and technology solutions.

Requirements:
- Must be generic and production-ready
- Include proper docstrings, type hints, and error handling
- Use appropriate libraries: applications, security, r, technology solutions, git
- Demonstrate quant skills related to team development, vendor management, leadership
"""

from typing import List, Dict
import applications
import security
import r
import technology_solutions
import git

def update_portfolio(portfolio: Dict[str, float], new_investment: Dict[str, float]) -> Dict[str, float]:
    """
    Update the portfolio with new investments.

    Args:
    - portfolio: A dictionary representing the current portfolio with stock symbols as keys and investment amounts as values.
    - new_investment: A dictionary representing the new investments to be added to the portfolio.

    Returns:
    - Updated portfolio with new investments included.
    """
    for symbol, amount in new_investment.items():
        if symbol in portfolio:
            portfolio[symbol] += amount
        else:
            portfolio[symbol] = amount
    return portfolio

def rebalance_portfolio(portfolio: Dict[str, float], target_weights: Dict[str, float]) -> Dict[str, float]:
    """
    Rebalance the portfolio to match target weights.

    Args:
    - portfolio: A dictionary representing the current portfolio with stock symbols as keys and investment amounts as values.
    - target_weights: A dictionary representing the target weights for each stock symbol in the portfolio.

    Returns:
    - Rebalanced portfolio with investment amounts adjusted to match target weights.
    """
    total_value = sum(portfolio.values())
    for symbol, weight in target_weights.items():
        target_amount = total_value * weight
        portfolio[symbol] = target_amount
    return portfolio

if __name__ == "__main__":
    current_portfolio = {"AAPL": 1000, "GOOGL": 2000, "MSFT": 1500}
    new_investment = {"AMZN": 3000, "TSLA": 2500}
    target_weights = {"AAPL": 0.25, "GOOGL": 0.35, "MSFT": 0.20, "AMZN": 0.10, "TSLA": 0.10}

    updated_portfolio = update_portfolio(current_portfolio, new_investment)
    print("Updated Portfolio after new investments:")
    print(updated_portfolio)

    rebalanced_portfolio = rebalance_portfolio(updated_portfolio, target_weights)
    print("\nRebalanced Portfolio based on target weights:")
    print(rebalanced_portfolio)