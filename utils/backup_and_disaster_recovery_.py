"""
Module: Backup And Disaster Recovery implementation for quantitative finance portfolio
"""

from typing import List, Dict
import pandas as pd
import numpy as np
import os
import shutil

def backup_data(data: pd.DataFrame, destination: str) -> None:
    """
    Backup data to specified destination
    Args:
    - data: pandas DataFrame containing the portfolio data
    - destination: str, path to backup destination
    """
    try:
        if not os.path.exists(destination):
            os.makedirs(destination)
        data.to_csv(os.path.join(destination, 'portfolio_data.csv'), index=False)
        print("Data backup successful")
    except Exception as e:
        print(f"Error during data backup: {e}")

def restore_data(source: str) -> pd.DataFrame:
    """
    Restore data from specified source
    Args:
    - source: str, path to backup source
    Returns:
    - pandas DataFrame containing the restored portfolio data
    """
    try:
        data = pd.read_csv(os.path.join(source, 'portfolio_data.csv'))
        print("Data restore successful")
        return data
    except Exception as e:
        print(f"Error during data restore: {e}")
        return pd.DataFrame()

def disaster_recovery(data: pd.DataFrame, destination: str) -> None:
    """
    Perform disaster recovery by backing up data and storing in a separate location
    Args:
    - data: pandas DataFrame containing the portfolio data
    - destination: str, path to disaster recovery destination
    """
    try:
        backup_data(data, destination)
        print("Disaster recovery successful")
    except Exception as e:
        print(f"Error during disaster recovery: {e}")

if __name__ == "__main__":
    # Example usage
    portfolio_data = pd.DataFrame({
        'symbol': ['AAPL', 'GOOGL', 'MSFT'],
        'quantity': [100, 50, 75],
        'price': [150.25, 1200.75, 250.50]
    })
    
    backup_destination = 'backup_folder'
    disaster_recovery_destination = 'disaster_recovery_folder'
    
    backup_data(portfolio_data, backup_destination)
    restored_data = restore_data(backup_destination)
    
    disaster_recovery(portfolio_data, disaster_recovery_destination)