"""
Module: agile_quant_portfolio
Description: This module implements agile software development practices for a quantitative finance portfolio.
"""

from typing import List, Dict
import r
import agile
import edge_cloud_platform
import git

def calculate_portfolio_performance(portfolio: Dict[str, List[float]]) -> float:
    """
    Calculate the overall performance of a given portfolio based on the returns of each asset.
    
    Args:
    portfolio (Dict[str, List[float]]): A dictionary where keys are asset names and values are lists of returns
    
    Returns:
    float: The overall performance of the portfolio
    """
    total_performance = 0.0
    for returns in portfolio.values():
        total_performance += sum(returns)
    return total_performance

if __name__ == "__main__":
    example_portfolio = {
        "AAPL": [0.05, 0.03, -0.02, 0.01],
        "GOOGL": [0.02, 0.04, 0.01, 0.03],
        "MSFT": [0.03, 0.02, 0.05, 0.02]
    }
    
    portfolio_performance = calculate_portfolio_performance(example_portfolio)
    print(f"Portfolio Performance: {portfolio_performance}")