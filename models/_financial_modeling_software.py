"""
Module: financial_modeling

This module contains functions for financial modeling using financial modeling software.
"""

from typing import List, Dict
import financial_modeling_software as fms
import data_analysis_tools as dat

def build_portfolio(portfolio_data: Dict[str, List[float]]) -> fms.Portfolio:
    """
    Build a portfolio object using the given portfolio data.

    Args:
    - portfolio_data: A dictionary where keys are stock tickers and values are lists of stock prices.

    Returns:
    - A Portfolio object representing the portfolio.
    """
    try:
        portfolio = fms.Portfolio()
        for ticker, prices in portfolio_data.items():
            stock = fms.Stock(ticker, prices)
            portfolio.add_stock(stock)
        return portfolio
    except Exception as e:
        raise ValueError(f"Error building portfolio: {str(e)}")

def forecast_portfolio_performance(portfolio: fms.Portfolio, num_days: int) -> Dict[str, float]:
    """
    Forecast the performance of a portfolio for the next 'num_days' days.

    Args:
    - portfolio: A Portfolio object representing the portfolio.
    - num_days: Number of days to forecast performance for.

    Returns:
    - A dictionary where keys are stock tickers and values are forecasted prices.
    """
    try:
        forecasted_prices = {}
        for stock in portfolio.stocks:
            forecasted_price = fms.forecast_stock_price(stock, num_days)
            forecasted_prices[stock.ticker] = forecasted_price
        return forecasted_prices
    except Exception as e:
        raise ValueError(f"Error forecasting portfolio performance: {str(e)}")

if __name__ == "__main__":
    portfolio_data = {
        "AAPL": [150.0, 152.0, 155.0, 160.0, 158.0],
        "GOOGL": [2500.0, 2550.0, 2600.0, 2650.0, 2700.0]
    }

    portfolio = build_portfolio(portfolio_data)
    forecasted_prices = forecast_portfolio_performance(portfolio, 5)
    print(f"Forecasted prices for the next 5 days: {forecasted_prices}")