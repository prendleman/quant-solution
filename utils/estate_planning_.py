"""
Module: Estate Planning Implementation

This module provides functions for estate planning implementation in a quantitative finance portfolio.

Functions:
- calculate_inheritance_tax: Calculate the inheritance tax based on the estate value.
- calculate_legacy_distribution: Calculate the distribution of legacy based on specified proportions.

Dependencies:
- numpy
"""

from typing import List

import numpy as np

def calculate_inheritance_tax(estate_value: float) -> float:
    """
    Calculate the inheritance tax based on the estate value.

    Args:
    estate_value (float): The total value of the estate.

    Returns:
    float: The calculated inheritance tax.
    """
    if estate_value <= 0:
        raise ValueError("Estate value must be greater than 0.")
    
    tax_rate = 0.4
    tax_amount = estate_value * tax_rate
    return tax_amount

def calculate_legacy_distribution(estate_value: float, proportions: List[float]) -> List[float]:
    """
    Calculate the distribution of legacy based on specified proportions.

    Args:
    estate_value (float): The total value of the estate.
    proportions (List[float]): List of proportions for each beneficiary.

    Returns:
    List[float]: List of legacy amounts for each beneficiary.
    """
    if estate_value <= 0:
        raise ValueError("Estate value must be greater than 0.")
    
    total_proportion = sum(proportions)
    if total_proportion != 1:
        raise ValueError("Proportions must sum up to 1.")
    
    legacy_distribution = [estate_value * proportion for proportion in proportions]
    return legacy_distribution

if __name__ == "__main__":
    estate_value = 1000000
    inheritance_tax = calculate_inheritance_tax(estate_value)
    print(f"Inheritance tax for estate value of {estate_value}: ${inheritance_tax}")

    proportions = [0.4, 0.3, 0.3]
    legacy_distribution = calculate_legacy_distribution(estate_value, proportions)
    print(f"Legacy distribution for estate value of {estate_value} with proportions {proportions}: {legacy_distribution}")