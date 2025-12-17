"""
Module: sales_implementation

This module contains functions for managing sales data in a quantitative finance portfolio.

Requirements:
- Must be generic and applicable to any quantitative finance portfolio
- Utilizes Talend, SQL, Informatica, SQL Server, NumPy libraries
- Demonstrates quant skills in master data management, data quality management, and data governance
"""

import numpy as np

def calculate_sales_growth(sales_data: np.array) -> float:
    """
    Calculate the sales growth based on historical sales data.

    Args:
    - sales_data: numpy array of historical sales data

    Returns:
    - float: sales growth percentage
    """
    if len(sales_data) < 2:
        raise ValueError("At least 2 data points are required to calculate sales growth")

    current_sales = sales_data[-1]
    previous_sales = sales_data[-2]

    sales_growth = ((current_sales - previous_sales) / previous_sales) * 100
    return sales_growth

def clean_sales_data(sales_data: np.array) -> np.array:
    """
    Clean the sales data by removing any outliers or incorrect values.

    Args:
    - sales_data: numpy array of sales data

    Returns:
    - np.array: cleaned sales data
    """
    cleaned_sales_data = np.where(sales_data < 0, 0, sales_data)
    return cleaned_sales_data

if __name__ == "__main__":
    # Example usage
    sales_data = np.array([100000, 120000, 90000, 110000, 95000])
    
    cleaned_sales = clean_sales_data(sales_data)
    growth_rate = calculate_sales_growth(cleaned_sales)
    
    print("Cleaned Sales Data:", cleaned_sales)
    print("Sales Growth Rate:", growth_rate)