"""
Module: cpa_implementation

This module contains functions for implementing Cost Price Adjustment (CPA) in a quantitative finance portfolio.

CPA is used to adjust the cost price of an asset in accordance with Generally Accepted Accounting Principles (GAAP).

Functions:
- calculate_cpa: Calculate the CPA for an asset based on its historical cost and current market value.
"""

from typing import Union

import numpy as np

def calculate_cpa(historical_cost: Union[float, int], market_value: Union[float, int]) -> float:
    """
    Calculate the Cost Price Adjustment (CPA) for an asset.

    Parameters:
    historical_cost (float): The historical cost of the asset.
    market_value (float): The current market value of the asset.

    Returns:
    float: The calculated CPA for the asset.
    """
    if historical_cost <= 0 or market_value <= 0:
        raise ValueError("Historical cost and market value must be positive numbers.")

    cpa = market_value - historical_cost
    return cpa

if __name__ == "__main__":
    historical_cost = 1000
    market_value = 1200

    cpa = calculate_cpa(historical_cost, market_value)
    print(f"Cost Price Adjustment (CPA): {cpa}")