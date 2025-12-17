"""
Module: Medical Stop Loss Expertise Implementation
This module contains functions for analyzing and managing medical stop loss expertise in a quantitative finance portfolio.

Requirements:
- Must be generic and applicable to any quantitative finance portfolio
- Include proper docstrings, type hints, and error handling
- Use appropriate libraries: numpy, pandas
- Demonstrate quant skills related to: medical stop loss expertise, derivatives, claims administration
- Include example usage in __main__ block
- Code should be production-ready and portfolio-quality
"""

import numpy as np
import pandas as pd

def calculate_stop_loss_premium(claims_data: pd.DataFrame, stop_loss_level: float) -> float:
    """
    Calculate the stop loss premium based on claims data and stop loss level.
    
    Args:
    - claims_data: DataFrame with columns 'policy_id', 'claim_amount'
    - stop_loss_level: The threshold above which the stop loss kicks in
    
    Returns:
    - stop_loss_premium: The calculated stop loss premium
    """
    if 'policy_id' not in claims_data.columns or 'claim_amount' not in claims_data.columns:
        raise ValueError("Invalid claims data format. DataFrame must have columns 'policy_id' and 'claim_amount'.")
    
    total_claims = claims_data.groupby('policy_id')['claim_amount'].sum()
    stop_loss_claims = total_claims[total_claims > stop_loss_level]
    stop_loss_premium = stop_loss_claims.sum()
    
    return stop_loss_premium

if __name__ == "__main__":
    claims_data = pd.DataFrame({
        'policy_id': [1, 1, 2, 2, 3],
        'claim_amount': [5000, 8000, 10000, 6000, 3000]
    })
    
    stop_loss_level = 7000
    stop_loss_premium = calculate_stop_loss_premium(claims_data, stop_loss_level)
    print(f"Stop Loss Premium: ${stop_loss_premium}")