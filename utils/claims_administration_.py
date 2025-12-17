"""
Module: Claims Administration Implementation
Description: This module provides functionality for claims administration in a quantitative finance portfolio.
"""

import numpy as np
import pandas as pd

def calculate_stop_loss_premium(claims_data: pd.DataFrame, stop_loss_level: float) -> float:
    """
    Calculate the stop loss premium based on claims data and stop loss level.
    
    Args:
    - claims_data: DataFrame containing claims information
    - stop_loss_level: Stop loss level as a percentage
    
    Returns:
    - stop_loss_premium: Calculated stop loss premium
    """
    if not isinstance(claims_data, pd.DataFrame):
        raise TypeError("claims_data must be a pandas DataFrame")
    
    if not isinstance(stop_loss_level, (int, float)):
        raise TypeError("stop_loss_level must be a numeric value")
    
    total_claims = claims_data['claim_amount'].sum()
    stop_loss_threshold = stop_loss_level * total_claims
    stop_loss_claims = claims_data[claims_data['claim_amount'] > stop_loss_threshold]
    stop_loss_premium = stop_loss_claims['claim_amount'].sum()
    
    return stop_loss_premium

if __name__ == "__main__":
    # Example usage
    claims_data = pd.DataFrame({'claim_amount': [10000, 20000, 30000, 40000]})
    stop_loss_level = 0.8
    stop_loss_premium = calculate_stop_loss_premium(claims_data, stop_loss_level)
    print(f"Stop loss premium: {stop_loss_premium}")