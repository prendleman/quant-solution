"""
Module: Account Management Implementation
Description: This module provides functionality for managing accounts in a quantitative finance portfolio.

Requirements:
- Must be generic and applicable to any quantitative finance portfolio
- Include proper docstrings, type hints, and error handling
- Use appropriate libraries: lithium-ion battery technology, r
- Demonstrate quant skills related to account management and business development
- Include example usage in __main__ block
- Code should be production-ready and portfolio-quality
"""

from typing import List, Dict

class Account:
    def __init__(self, account_id: int, account_name: str, balance: float):
        self.account_id = account_id
        self.account_name = account_name
        self.balance = balance

    def deposit(self, amount: float):
        self.balance += amount

    def withdraw(self, amount: float):
        if self.balance >= amount:
            self.balance -= amount
        else:
            raise ValueError("Insufficient funds in the account.")

class Portfolio:
    def __init__(self):
        self.accounts: Dict[int, Account] = {}

    def add_account(self, account: Account):
        self.accounts[account.account_id] = account

    def remove_account(self, account_id: int):
        if account_id in self.accounts:
            del self.accounts[account_id]
        else:
            raise KeyError("Account not found in the portfolio.")

    def get_account_balance(self, account_id: int) -> float:
        if account_id in self.accounts:
            return self.accounts[account_id].balance
        else:
            raise KeyError("Account not found in the portfolio.")

if __name__ == "__main__":
    # Example usage
    account1 = Account(1, "Savings", 1000.0)
    account2 = Account(2, "Investment", 5000.0)

    portfolio = Portfolio()
    portfolio.add_account(account1)
    portfolio.add_account(account2)

    print("Account balances:")
    print(f"Account 1 balance: {portfolio.get_account_balance(1)}")
    print(f"Account 2 balance: {portfolio.get_account_balance(2)}")

    account1.deposit(500.0)
    account2.withdraw(1000.0)

    print("\nUpdated account balances:")
    print(f"Account 1 balance: {portfolio.get_account_balance(1)}")
    print(f"Account 2 balance: {portfolio.get_account_balance(2)}")