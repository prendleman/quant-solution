"""
Module: Credit Risk Management Implementation
Description: This module provides functions for managing credit risk in a quantitative finance portfolio.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats

def calculate_credit_rating(credit_score: int) -> str:
    """
    Calculate credit rating based on credit score.
    
    Parameters:
    credit_score (int): The credit score of the borrower.
    
    Returns:
    str: The credit rating corresponding to the credit score.
    """
    if credit_score >= 750:
        return "Excellent"
    elif credit_score >= 700:
        return "Good"
    elif credit_score >= 650:
        return "Fair"
    else:
        return "Poor"

def calculate_credit_loss(prob_default: float, exposure: float) -> float:
    """
    Calculate credit loss based on probability of default and exposure.
    
    Parameters:
    prob_default (float): The probability of default for the borrower.
    exposure (float): The exposure amount to the borrower.
    
    Returns:
    float: The credit loss amount.
    """
    return prob_default * exposure

def calculate_expected_loss(prob_default: float, exposure: float, loss_given_default: float) -> float:
    """
    Calculate expected loss based on probability of default, exposure, and loss given default.
    
    Parameters:
    prob_default (float): The probability of default for the borrower.
    exposure (float): The exposure amount to the borrower.
    loss_given_default (float): The loss given default percentage.
    
    Returns:
    float: The expected loss amount.
    """
    return prob_default * exposure * loss_given_default

if __name__ == "__main__":
    credit_score = 720
    prob_default = 0.05
    exposure = 1000000
    loss_given_default = 0.50
    
    credit_rating = calculate_credit_rating(credit_score)
    credit_loss = calculate_credit_loss(prob_default, exposure)
    expected_loss = calculate_expected_loss(prob_default, exposure, loss_given_default)
    
    print(f"Credit Rating: {credit_rating}")
    print(f"Credit Loss: ${credit_loss}")
    print(f"Expected Loss: ${expected_loss}")