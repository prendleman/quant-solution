"""
Module: sas_portfolio_analysis

This module contains functions for performing data analysis and management for a quantitative finance portfolio using SAS.
"""

import saspy
import pandas as pd

def read_sas_data(sas_session: saspy.SASsession, sas_table: str) -> pd.DataFrame:
    """
    Read data from a SAS table and return as a pandas DataFrame.

    Args:
    sas_session: SAS session object
    sas_table: Name of the SAS table to read

    Returns:
    Pandas DataFrame containing the data from the SAS table
    """
    try:
        sas_data = sas_session.sasdata(sas_table).to_df()
        return sas_data
    except Exception as e:
        raise Exception(f"Error reading SAS data: {str(e)}")

def write_sas_data(sas_session: saspy.SASsession, sas_table: str, data: pd.DataFrame):
    """
    Write data to a SAS table.

    Args:
    sas_session: SAS session object
    sas_table: Name of the SAS table to write to
    data: Pandas DataFrame containing the data to write
    """
    try:
        sas_data = saspy.SASdata(sas_session, sas_table, data=data)
        sas_data.save()
    except Exception as e:
        raise Exception(f"Error writing SAS data: {str(e)}")

if __name__ == "__main__":
    # Example usage
    sas_session = saspy.SASsession()
    
    # Read data from SAS table
    sas_table = "portfolio_data"
    portfolio_data = read_sas_data(sas_session, sas_table)
    print(portfolio_data.head())
    
    # Perform data analysis and management
    # (Add your analysis and management code here)
    
    # Write data to SAS table
    new_portfolio_data = portfolio_data.copy()
    write_sas_data(sas_session, "updated_portfolio_data", new_portfolio_data)