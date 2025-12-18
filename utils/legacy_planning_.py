"""
Module: Legacy Planning implementation

This module contains functions for legacy planning implementation in a quantitative finance portfolio.

Requirements:
- Must be generic (no company names, job titles, or role-specific details)
- Include proper docstrings, type hints, and error handling
- Use appropriate libraries: pandas, numpy
- Demonstrate quant skills related to: estate planning, tax accounting, legacy planning
- Include example usage in __main__ block
- Code should be production-ready and portfolio-quality
"""

import pandas as pd
import numpy as np

def calculate_inheritance_tax(estate_value: float, tax_rate: float) -> float:
    """
    Calculate the inheritance tax based on the estate value and tax rate.

    Args:
    estate_value (float): The total value of the estate
    tax_rate (float): The tax rate for inheritance tax

    Returns:
    float: The amount of inheritance tax to be paid
    """
    if estate_value < 0:
        raise ValueError("Estate value cannot be negative")
    
    if tax_rate < 0:
        raise ValueError("Tax rate cannot be negative")
    
    return estate_value * tax_rate

def calculate_legacy_distribution(estate_value: float, num_heirs: int) -> float:
    """
    Calculate the amount each heir will receive from the estate.

    Args:
    estate_value (float): The total value of the estate
    num_heirs (int): The number of heirs

    Returns:
    float: The amount each heir will receive
    """
    if estate_value < 0:
        raise ValueError("Estate value cannot be negative")
    
    if num_heirs <= 0:
        raise ValueError("Number of heirs must be greater than 0")
    
    return estate_value / num_heirs

if __name__ == "__main__":
    estate_value = 1000000
    tax_rate = 0.2
    num_heirs = 4

    inheritance_tax = calculate_inheritance_tax(estate_value, tax_rate)
    legacy_distribution = calculate_legacy_distribution(estate_value, num_heirs)

    print(f"Inheritance tax to be paid: ${inheritance_tax}")
    print(f"Amount each heir will receive: ${legacy_distribution}")