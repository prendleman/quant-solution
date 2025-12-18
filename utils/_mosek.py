"""
Module: portfolio_optimization

This module implements portfolio optimization using MOSEK for quantitative finance portfolios.

Requirements:
- Python 3.x
- MOSEK
- numpy
- pandas
- matplotlib
"""

import numpy as np
import pandas as pd
from mosek.fusion import Model, Domain, Expr, ObjectiveSense

def optimize_portfolio(returns: pd.DataFrame, risk_free_rate: float) -> pd.Series:
    """
    Optimize the portfolio allocation based on historical returns and risk-free rate.

    Args:
    returns (pd.DataFrame): Historical returns of assets
    risk_free_rate (float): Risk-free rate for the optimization

    Returns:
    pd.Series: Optimized portfolio allocation
    """
    num_assets = len(returns.columns)
    with Model("Portfolio Optimization") as M:
        x = M.variable("x", num_assets, Domain.unbounded())
        M.constraint("budget", Expr.sum(x), Domain.equalsTo(1.0))
        expected_return = Expr.dot(returns.mean().values, x)
        variance = Expr.vstack(
            Expr.constTerm(0.5),
            Expr.sub(returns.values @ x, expected_return)
        ).mul(x)
        risk = M.constraint("risk", variance, Domain.lessThan(returns.cov().values))
        M.objective("objective", ObjectiveSense.Maximize, expected_return - risk_free_rate * Expr.sum(x))
        M.solve()
        return pd.Series(x.level(), index=returns.columns)

if __name__ == "__main__":
    # Example usage
    np.random.seed(123)
    returns = pd.DataFrame(np.random.randn(100, 5), columns=["Asset1", "Asset2", "Asset3", "Asset4", "Asset5"])
    risk_free_rate = 0.02
    optimized_portfolio = optimize_portfolio(returns, risk_free_rate)
    print(optimized_portfolio)