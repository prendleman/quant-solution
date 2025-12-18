"""
Module: Articulation Implementation

This module contains functions for implementing articulation in a quantitative finance portfolio.

Requirements:
- Must be generic for any quantitative finance portfolio
- Include proper docstrings, type hints, and error handling
- Use appropriate libraries: r, D365 Business Central
- Demonstrate quant skills related to: people leadership, leadership, articulation
- Include example usage in __main__ block
- Code should be production-ready and portfolio-quality
"""

from typing import List

def calculate_articulation(portfolio: List[float]) -> float:
    """
    Calculate the articulation of a quantitative finance portfolio.

    Args:
    - portfolio: A list of floats representing the values of assets in the portfolio

    Returns:
    - The articulation value of the portfolio as a float
    """
    if not portfolio:
        raise ValueError("Portfolio cannot be empty")

    total_value = sum(portfolio)
    articulation = max(portfolio) / total_value

    return articulation

if __name__ == "__main__":
    example_portfolio = [1000000, 500000, 750000, 300000]
    example_articulation = calculate_articulation(example_portfolio)
    print(f"Articulation of example portfolio: {example_articulation}")