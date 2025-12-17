"""
Module: interest_rate_risk_management

This module provides functions for managing interest rate risk in a quantitative finance portfolio.

Functions:
- calculate_duration: Calculate the duration of a bond
- calculate_macaulay_duration: Calculate the Macaulay duration of a bond
- calculate_modified_duration: Calculate the modified duration of a bond
- calculate_convexity: Calculate the convexity of a bond
- calculate_yield_to_maturity: Calculate the yield to maturity of a bond
"""

from typing import Union

def calculate_duration(price: float, coupon_payment: float, par_value: float, yield_to_maturity: float) -> float:
    """
    Calculate the duration of a bond.
    
    Args:
    price (float): Current price of the bond
    coupon_payment (float): Annual coupon payment of the bond
    par_value (float): Par value of the bond
    yield_to_maturity (float): Yield to maturity of the bond
    
    Returns:
    float: Duration of the bond
    """
    # Implementation goes here

def calculate_macaulay_duration(duration: float, yield_to_maturity: float) -> float:
    """
    Calculate the Macaulay duration of a bond.
    
    Args:
    duration (float): Duration of the bond
    yield_to_maturity (float): Yield to maturity of the bond
    
    Returns:
    float: Macaulay duration of the bond
    """
    # Implementation goes here

def calculate_modified_duration(macaulay_duration: float, yield_change: float) -> float:
    """
    Calculate the modified duration of a bond.
    
    Args:
    macaulay_duration (float): Macaulay duration of the bond
    yield_change (float): Change in yield
    
    Returns:
    float: Modified duration of the bond
    """
    # Implementation goes here

def calculate_convexity(price: float, coupon_payment: float, par_value: float, yield_to_maturity: float) -> float:
    """
    Calculate the convexity of a bond.
    
    Args:
    price (float): Current price of the bond
    coupon_payment (float): Annual coupon payment of the bond
    par_value (float): Par value of the bond
    yield_to_maturity (float): Yield to maturity of the bond
    
    Returns:
    float: Convexity of the bond
    """
    # Implementation goes here

def calculate_yield_to_maturity(price: float, coupon_payment: float, par_value: float, years_to_maturity: int) -> float:
    """
    Calculate the yield to maturity of a bond.
    
    Args:
    price (float): Current price of the bond
    coupon_payment (float): Annual coupon payment of the bond
    par_value (float): Par value of the bond
    years_to_maturity (int): Years to maturity of the bond
    
    Returns:
    float: Yield to maturity of the bond
    """
    # Implementation goes here

if __name__ == "__main__":
    # Example usage
    price = 950.0
    coupon_payment = 50.0
    par_value = 1000.0
    yield_to_maturity = 0.05
    years_to_maturity = 5
    
    duration = calculate_duration(price, coupon_payment, par_value, yield_to_maturity)
    macaulay_duration = calculate_macaulay_duration(duration, yield_to_maturity)
    modified_duration = calculate_modified_duration(macaulay_duration, 0.01)
    convexity = calculate_convexity(price, coupon_payment, par_value, yield_to_maturity)
    new_yield_to_maturity = calculate_yield_to_maturity(price, coupon_payment, par_value, years_to_maturity)
    
    print("Duration:", duration)
    print("Macaulay Duration:", macaulay_duration)
    print("Modified Duration:", modified_duration)
    print("Convexity:", convexity)
    print("New Yield to Maturity:", new_yield_to_maturity)