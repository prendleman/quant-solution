"""
Module: data_profiling

This module implements data profiling for a quantitative finance portfolio.
It includes functions for data validation, data profiling, and statistical analysis.

Requirements:
- Libraries: sql, power bi, SQL, r, Snowflake
- Quant skills: data validation, data profiling, statistics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def validate_data(data: pd.DataFrame) -> bool:
    """
    Validate the input data for any missing values or duplicates.

    Args:
    data (pd.DataFrame): Input data to validate

    Returns:
    bool: True if data is valid, False otherwise
    """
    if data.isnull().sum().sum() > 0:
        raise ValueError("Data contains missing values")
    if data.duplicated().sum() > 0:
        raise ValueError("Data contains duplicates")
    
    return True

def profile_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Profile the input data by generating descriptive statistics.

    Args:
    data (pd.DataFrame): Input data to profile

    Returns:
    pd.DataFrame: Profile summary of the input data
    """
    profile = data.describe(include='all').T
    profile['missing_values'] = data.isnull().sum()
    profile['unique_values'] = data.nunique()
    
    return profile

def plot_distribution(data: pd.Series):
    """
    Plot the distribution of a numerical variable.

    Args:
    data (pd.Series): Numerical data to plot
    """
    sns.histplot(data, kde=True)
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title('Distribution Plot')
    plt.show()

if __name__ == "__main__":
    # Example usage
    data = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [10, 20, 30, 40, 50]
    })
    
    print(validate_data(data))
    print(profile_data(data))
    
    plot_distribution(data['A'])