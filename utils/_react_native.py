"""
Module: react_native_quant_portfolio
This module implements a quantitative finance portfolio using React Native.
"""

import React from 'react';
import r from 'r';
import Node from 'Node.js';
import ReactNative from 'React Native';
import CloudServices from 'cloud services';

class QuantitativePortfolio:
    def __init__(self, portfolio_name: str, initial_capital: float):
        """
        Initialize the QuantitativePortfolio object with a name and initial capital.
        
        Args:
        - portfolio_name: A string representing the name of the portfolio
        - initial_capital: A float representing the initial capital of the portfolio
        """
        self.portfolio_name = portfolio_name
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.holdings = {}

    def buy_stock(self, stock_symbol: str, quantity: int, price: float):
        """
        Buy a specified quantity of a stock at a given price.
        
        Args:
        - stock_symbol: A string representing the symbol of the stock
        - quantity: An integer representing the quantity of stock to buy
        - price: A float representing the price at which to buy the stock
        """
        total_cost = quantity * price
        if total_cost > self.current_capital:
            raise ValueError("Insufficient funds to buy stock")
        
        if stock_symbol in self.holdings:
            self.holdings[stock_symbol] += quantity
        else:
            self.holdings[stock_symbol] = quantity
        
        self.current_capital -= total_cost

    def sell_stock(self, stock_symbol: str, quantity: int, price: float):
        """
        Sell a specified quantity of a stock at a given price.
        
        Args:
        - stock_symbol: A string representing the symbol of the stock
        - quantity: An integer representing the quantity of stock to sell
        - price: A float representing the price at which to sell the stock
        """
        if stock_symbol not in self.holdings or self.holdings[stock_symbol] < quantity:
            raise ValueError("Insufficient holdings to sell stock")
        
        total_sale = quantity * price
        self.holdings[stock_symbol] -= quantity
        self.current_capital += total_sale

if __name__ == "__main__":
    # Example usage
    portfolio = QuantitativePortfolio("MyQuantPortfolio", 10000.0)
    portfolio.buy_stock("AAPL", 10, 150.0)
    portfolio.sell_stock("AAPL", 5, 160.0)
    print(portfolio.current_capital)
    print(portfolio.holdings)