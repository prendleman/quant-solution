"""
Financial Modeling and Valuation

DCF valuation, financial statement analysis, and modeling tools.
Generated as part of quant portfolio development.
"""

from typing import Optional, List, Dict
import numpy as np
import pandas as pd
from scipy import stats


def dcf_valuation(free_cash_flows: List[float], terminal_value: float, 
                 discount_rate: float, terminal_growth_rate: float = 0.03) -> Dict:
    """
    Calculate DCF (Discounted Cash Flow) valuation.
    
    Args:
        free_cash_flows: List of projected free cash flows
        terminal_value: Terminal value at end of projection period
        discount_rate: WACC or discount rate
        terminal_growth_rate: Terminal growth rate (perpetuity)
        
    Returns:
        Dictionary with valuation metrics
    """
    # Discount free cash flows
    discounted_fcf = []
    for i, fcf in enumerate(free_cash_flows, 1):
        pv = fcf / ((1 + discount_rate) ** i)
        discounted_fcf.append(pv)
    
    # Discount terminal value
    n_periods = len(free_cash_flows)
    terminal_pv = terminal_value / ((1 + discount_rate) ** n_periods)
    
    # Enterprise value
    enterprise_value = sum(discounted_fcf) + terminal_pv
    
    return {
        'enterprise_value': enterprise_value,
        'discounted_fcf': discounted_fcf,
        'terminal_value_pv': terminal_pv,
        'total_fcf_pv': sum(discounted_fcf)
    }


def calculate_financial_ratios(income_statement: pd.DataFrame, 
                              balance_sheet: pd.DataFrame,
                              cash_flow: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate key financial ratios.
    
    Args:
        income_statement: DataFrame with income statement data
        balance_sheet: DataFrame with balance sheet data
        cash_flow: DataFrame with cash flow data
        
    Returns:
        DataFrame with calculated ratios
    """
    ratios = pd.DataFrame()
    
    # Profitability ratios
    if 'Revenue' in income_statement.columns and 'Net Income' in income_statement.columns:
        ratios['Net Profit Margin'] = income_statement['Net Income'] / income_statement['Revenue']
    
    if 'Total Assets' in balance_sheet.columns:
        ratios['ROA'] = income_statement['Net Income'] / balance_sheet['Total Assets']
    
    if 'Total Equity' in balance_sheet.columns:
        ratios['ROE'] = income_statement['Net Income'] / balance_sheet['Total Equity']
    
    # Liquidity ratios
    if 'Current Assets' in balance_sheet.columns and 'Current Liabilities' in balance_sheet.columns:
        ratios['Current Ratio'] = balance_sheet['Current Assets'] / balance_sheet['Current Liabilities']
    
    # Leverage ratios
    if 'Total Debt' in balance_sheet.columns and 'Total Equity' in balance_sheet.columns:
        ratios['Debt to Equity'] = balance_sheet['Total Debt'] / balance_sheet['Total Equity']
    
    # Efficiency ratios
    if 'Revenue' in income_statement.columns and 'Total Assets' in balance_sheet.columns:
        ratios['Asset Turnover'] = income_statement['Revenue'] / balance_sheet['Total Assets']
    
    return ratios


def monte_carlo_valuation(base_value: float, volatility: float, n_simulations: int = 10000,
                          confidence_levels: List[float] = [0.05, 0.95]) -> Dict:
    """
    Perform Monte Carlo simulation for valuation uncertainty.
    
    Args:
        base_value: Base valuation estimate
        volatility: Volatility of valuation (as decimal)
        n_simulations: Number of simulations
        confidence_levels: Confidence levels for percentiles
        
    Returns:
        Dictionary with simulation results
    """
    # Generate random valuations
    random_shocks = np.random.normal(0, 1, n_simulations)
    valuations = base_value * np.exp(volatility * random_shocks)
    
    # Calculate statistics
    mean_val = np.mean(valuations)
    median_val = np.median(valuations)
    std_val = np.std(valuations)
    
    # Percentiles
    percentiles = {}
    for cl in confidence_levels:
        percentiles[f'{int(cl*100)}th_percentile'] = np.percentile(valuations, cl * 100)
    
    return {
        'mean': mean_val,
        'median': median_val,
        'std': std_val,
        'percentiles': percentiles,
        'simulations': valuations
    }


def calculate_wacc(equity_value: float, debt_value: float, cost_of_equity: float,
                  cost_of_debt: float, tax_rate: float) -> float:
    """
    Calculate Weighted Average Cost of Capital (WACC).
    
    Args:
        equity_value: Market value of equity
        debt_value: Market value of debt
        cost_of_equity: Cost of equity (required return)
        cost_of_debt: Cost of debt (interest rate)
        tax_rate: Corporate tax rate
        
    Returns:
        WACC as decimal
    """
    total_value = equity_value + debt_value
    equity_weight = equity_value / total_value
    debt_weight = debt_value / total_value
    
    wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt * (1 - tax_rate))
    return wacc


if __name__ == "__main__":
    # Example: DCF Valuation
    fcf_projections = [100, 110, 120, 130, 140]  # 5 years
    terminal_val = 2000
    wacc = 0.10
    
    dcf_result = dcf_valuation(fcf_projections, terminal_val, wacc)
    print(f"Enterprise Value: ${dcf_result['enterprise_value']:,.2f}")
    print(f"Present Value of FCF: ${dcf_result['total_fcf_pv']:,.2f}")
    print(f"Present Value of Terminal Value: ${dcf_result['terminal_value_pv']:,.2f}")
    
    # Example: Monte Carlo valuation
    mc_result = monte_carlo_valuation(1000, 0.2, 10000)
    print(f"\nMonte Carlo Valuation:")
    print(f"  Mean: ${mc_result['mean']:,.2f}")
    print(f"  Median: ${mc_result['median']:,.2f}")
    print(f"  5th Percentile: ${mc_result['percentiles']['5th_percentile']:,.2f}")
    print(f"  95th Percentile: ${mc_result['percentiles']['95th_percentile']:,.2f}")
    
    # Example: WACC
    wacc_val = calculate_wacc(equity_value=800, debt_value=200, 
                              cost_of_equity=0.12, cost_of_debt=0.06, tax_rate=0.25)
    print(f"\nWACC: {wacc_val:.2%}")
