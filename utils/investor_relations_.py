"""
Module: investor_relations

This module contains functions related to investor relations in quantitative finance portfolios.

Functions:
- calculate_investor_return: Calculate the return on investment for a given investor
- calculate_portfolio_return: Calculate the return on investment for the entire portfolio
"""

from typing import List, Dict

def calculate_investor_return(investor_id: int, investment_amount: float, returns: Dict[int, List[float]]) -> float:
    """
    Calculate the return on investment for a specific investor.

    Args:
    investor_id (int): The unique identifier for the investor
    investment_amount (float): The amount of money invested by the investor
    returns (Dict[int, List[float]]): A dictionary mapping investor IDs to a list of returns

    Returns:
    float: The return on investment for the specified investor
    """
    if investor_id not in returns:
        raise ValueError("Investor ID not found in returns data")

    total_return = sum(returns[investor_id])
    return (total_return / investment_amount) * 100

def calculate_portfolio_return(returns: Dict[int, List[float]]) -> float:
    """
    Calculate the return on investment for the entire portfolio.

    Args:
    returns (Dict[int, List[float]]): A dictionary mapping investor IDs to a list of returns

    Returns:
    float: The return on investment for the entire portfolio
    """
    total_investment = sum(sum(investor_returns) for investor_returns in returns.values())
    total_return = sum(sum(investor_returns) for investor_returns in returns.values())
    return (total_return / total_investment) * 100

if __name__ == "__main__":
    example_returns = {
        1: [0.05, 0.03, 0.02],
        2: [0.08, 0.06, 0.04],
        3: [0.10, 0.07, 0.05]
    }

    investor1_return = calculate_investor_return(1, 10000, example_returns)
    print(f"Investor 1 return: {investor1_return}%")

    portfolio_return = calculate_portfolio_return(example_returns)
    print(f"Portfolio return: {portfolio_return}%")