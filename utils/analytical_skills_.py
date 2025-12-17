"""
Module: analytical_skills_implementation

This module contains functions for implementing analytical skills in a quantitative finance portfolio,
including interest rate risk management, strategic vision, and liquidity risk management.
"""

import numpy as np
import pandas as pd

def calculate_duration_and_convexity(cash_flows: pd.Series, discount_rates: pd.Series) -> tuple:
    """
    Calculate the duration and convexity of a series of cash flows given discount rates.
    
    Args:
    cash_flows (pd.Series): Series of cash flows
    discount_rates (pd.Series): Series of discount rates corresponding to each cash flow
    
    Returns:
    tuple: (duration, convexity)
    """
    if len(cash_flows) != len(discount_rates):
        raise ValueError("Length of cash_flows and discount_rates must be the same")
    
    present_values = cash_flows / (1 + discount_rates)
    weights = present_values / present_values.sum()
    
    duration = np.sum(weights * np.arange(1, len(cash_flows) + 1))
    convexity = np.sum(weights * ((np.arange(1, len(cash_flows) + 1) ** 2) * (1 + discount_rates)))
    
    return duration, convexity

def calculate_liquidity_ratio(liquid_assets: float, current_liabilities: float) -> float:
    """
    Calculate the liquidity ratio of a portfolio given liquid assets and current liabilities.
    
    Args:
    liquid_assets (float): Total liquid assets in the portfolio
    current_liabilities (float): Total current liabilities of the portfolio
    
    Returns:
    float: Liquidity ratio
    """
    if current_liabilities == 0:
        raise ValueError("Current liabilities cannot be zero")
    
    return liquid_assets / current_liabilities

if __name__ == "__main__":
    cash_flows = pd.Series([100, 200, 300, 400, 500])
    discount_rates = pd.Series([0.05, 0.06, 0.07, 0.08, 0.09])
    
    duration, convexity = calculate_duration_and_convexity(cash_flows, discount_rates)
    print(f"Duration: {duration}, Convexity: {convexity}")
    
    liquid_assets = 100000
    current_liabilities = 50000
    liquidity_ratio = calculate_liquidity_ratio(liquid_assets, current_liabilities)
    print(f"Liquidity Ratio: {liquidity_ratio}")