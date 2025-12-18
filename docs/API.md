# API Documentation

This document provides a comprehensive reference for the Quantitative Finance Portfolio API.

## Table of Contents

- [Risk Management](#risk-management)
- [Derivatives Pricing](#derivatives-pricing)
- [Portfolio Optimization](#portfolio-optimization)
- [Volatility Models](#volatility-models)
- [Factor Models](#factor-models)
- [Trading Strategies](#trading-strategies)
- [Data Analysis](#data-analysis)
- [Financial Modeling](#financial-modeling)

---

## Risk Management

**Module**: `analysis.risk_management_`

### `calculate_var(returns, confidence_level=0.05)`

Calculate Value at Risk (VaR) using historical method.

**Parameters:**
- `returns` (pd.Series): Series of returns
- `confidence_level` (float): Confidence level (e.g., 0.05 for 95% VaR)

**Returns:**
- `float`: VaR value

**Example:**
```python
from analysis.risk_management_ import calculate_var
import pandas as pd

returns = pd.Series([0.01, -0.02, 0.015, -0.01, 0.005, -0.03])
var_95 = calculate_var(returns, confidence_level=0.05)
```

### `calculate_cvar(returns, confidence_level=0.05)`

Calculate Conditional Value at Risk (CVaR), also known as Expected Shortfall.

**Parameters:**
- `returns` (pd.Series): Series of returns
- `confidence_level` (float): Confidence level

**Returns:**
- `float`: CVaR value

### `calculate_max_drawdown(prices)`

Calculate maximum drawdown from a price series.

**Parameters:**
- `prices` (pd.Series): Price series

**Returns:**
- `float`: Maximum drawdown (negative value)

---

## Derivatives Pricing

**Module**: `utils.derivatives_`

### `black_scholes_price(S, K, T, r, sigma, option_type='call')`

Calculate Black-Scholes option price.

**Parameters:**
- `S` (float): Current stock price
- `K` (float): Strike price
- `T` (float): Time to expiration (in years)
- `r` (float): Risk-free interest rate
- `sigma` (float): Volatility (annualized)
- `option_type` (str): 'call' or 'put'

**Returns:**
- `float`: Option price

**Example:**
```python
from utils.derivatives_ import black_scholes_price

price = black_scholes_price(S=100, K=100, T=1.0, r=0.05, sigma=0.2, option_type='call')
```

### `calculate_greeks(S, K, T, r, sigma, option_type='call')`

Calculate option Greeks (Delta, Gamma, Theta, Vega, Rho).

**Parameters:**
- Same as `black_scholes_price`

**Returns:**
- `dict`: Dictionary with keys 'delta', 'gamma', 'theta', 'vega', 'rho'

### `monte_carlo_option_price(S, K, T, r, sigma, n_simulations, option_type='call')`

Price option using Monte Carlo simulation.

**Parameters:**
- Same as `black_scholes_price`, plus:
- `n_simulations` (int): Number of Monte Carlo simulations

**Returns:**
- `float`: Option price

---

## Portfolio Optimization

**Module**: `models.portfolio_optimization`

### `mean_variance_optimization(returns, risk_free_rate=0.02, target_return=None, risk_aversion=1.0)`

Mean-variance portfolio optimization (Markowitz).

**Parameters:**
- `returns` (pd.DataFrame): DataFrame of asset returns (columns = assets, rows = time)
- `risk_free_rate` (float): Risk-free rate
- `target_return` (float, optional): Target portfolio return (if None, maximizes Sharpe ratio)
- `risk_aversion` (float): Risk aversion parameter (higher = more risk averse)

**Returns:**
- `dict`: Dictionary with 'weights', 'expected_return', 'volatility', 'sharpe_ratio'

**Example:**
```python
from models.portfolio_optimization import mean_variance_optimization
import pandas as pd

returns = pd.DataFrame({
    'Asset1': [...],
    'Asset2': [...],
    'Asset3': [...]
})

result = mean_variance_optimization(returns, risk_free_rate=0.02)
print(f"Optimal weights: {result['weights']}")
print(f"Sharpe ratio: {result['sharpe_ratio']}")
```

### `risk_parity_optimization(returns)`

Risk parity portfolio optimization.

**Parameters:**
- `returns` (pd.DataFrame): DataFrame of asset returns

**Returns:**
- `dict`: Dictionary with 'weights', 'expected_return', 'volatility'

### `minimum_variance_portfolio(returns)`

Calculate minimum variance portfolio.

**Parameters:**
- `returns` (pd.DataFrame): DataFrame of asset returns

**Returns:**
- `dict`: Dictionary with 'weights', 'expected_return', 'volatility'

### `efficient_frontier(returns, n_points=50, risk_free_rate=0.02)`

Generate efficient frontier.

**Parameters:**
- `returns` (pd.DataFrame): DataFrame of asset returns
- `n_points` (int): Number of points on the frontier
- `risk_free_rate` (float): Risk-free rate

**Returns:**
- `pd.DataFrame`: DataFrame with 'return' and 'volatility' columns

---

## Volatility Models

**Module**: `models.volatility_models`

### `estimate_garch(returns, p=1, q=1)`

Estimate GARCH(p,q) volatility model.

**Parameters:**
- `returns` (pd.Series): Series of returns
- `p` (int): GARCH order for ARCH terms
- `q` (int): GARCH order for GARCH terms

**Returns:**
- `dict`: Dictionary with GARCH parameters

### `calculate_ewma_volatility(returns, lambda_param=0.94)`

Calculate EWMA (Exponentially Weighted Moving Average) volatility.

**Parameters:**
- `returns` (pd.Series): Series of returns
- `lambda_param` (float): Decay factor (typically 0.94)

**Returns:**
- `pd.Series`: Series of EWMA volatilities

### `calculate_realized_volatility(returns, window=20)`

Calculate realized volatility using rolling window.

**Parameters:**
- `returns` (pd.Series): Series of returns
- `window` (int): Rolling window size

**Returns:**
- `pd.Series`: Series of realized volatilities

---

## Factor Models

**Module**: `models.factor_models`

### `fama_french_regression(returns, market_factor, smb_factor=None, hml_factor=None, rmw_factor=None, cma_factor=None)`

Run Fama-French factor model regression.

**Parameters:**
- `returns` (pd.Series): Asset/portfolio returns
- `market_factor` (pd.Series): Market excess returns (Mkt-Rf)
- `smb_factor` (pd.Series, optional): Small minus Big factor
- `hml_factor` (pd.Series, optional): High minus Low factor
- `rmw_factor` (pd.Series, optional): Robust minus Weak profitability
- `cma_factor` (pd.Series, optional): Conservative minus Aggressive investment

**Returns:**
- `dict`: Dictionary with 'alpha', 'factor_loadings', 'r_squared', 't_statistics', 'residuals', 'fitted_values'

**Example:**
```python
from models.factor_models import fama_french_regression

# 3-factor model
result = fama_french_regression(
    returns=asset_returns,
    market_factor=market_returns,
    smb_factor=smb_returns,
    hml_factor=hml_returns
)

print(f"Alpha: {result['alpha']}")
print(f"Market beta: {result['factor_loadings']['Market']}")
print(f"R-squared: {result['r_squared']}")
```

---

## Trading Strategies

**Module**: `strategies.statistical_arbitrage`

### `pairs_trading_strategy(price1, price2, lookback=60, entry_threshold=2.0, exit_threshold=0.5)`

Pairs trading strategy based on cointegration.

**Parameters:**
- `price1` (pd.Series): Price series of first asset
- `price2` (pd.Series): Price series of second asset
- `lookback` (int): Lookback period for z-score calculation
- `entry_threshold` (float): Z-score threshold for entry
- `exit_threshold` (float): Z-score threshold for exit

**Returns:**
- `dict`: Dictionary with 'signals', 'positions', 'hedge_ratio', 'z_scores'

---

## Data Analysis

**Module**: `analysis.data_analysis_`

### `analyze_returns(returns)`

Comprehensive return analysis.

**Parameters:**
- `returns` (pd.Series): Series of returns

**Returns:**
- `dict`: Dictionary with statistical metrics

### `correlation_analysis(returns_df)`

Correlation analysis for multiple assets.

**Parameters:**
- `returns_df` (pd.DataFrame): DataFrame of returns

**Returns:**
- `pd.DataFrame`: Correlation matrix

---

## Financial Modeling

**Module**: `models.financial_modeling_`

### `dcf_valuation(cash_flows, discount_rate, terminal_value=None, terminal_growth_rate=0.0)`

Discounted Cash Flow (DCF) valuation.

**Parameters:**
- `cash_flows` (list or pd.Series): Projected cash flows
- `discount_rate` (float): Discount rate (WACC)
- `terminal_value` (float, optional): Terminal value
- `terminal_growth_rate` (float): Terminal growth rate

**Returns:**
- `float`: Present value

### `calculate_wacc(equity_value, debt_value, cost_of_equity, cost_of_debt, tax_rate)`

Calculate Weighted Average Cost of Capital (WACC).

**Parameters:**
- `equity_value` (float): Market value of equity
- `debt_value` (float): Market value of debt
- `cost_of_equity` (float): Cost of equity
- `cost_of_debt` (float): Cost of debt
- `tax_rate` (float): Corporate tax rate

**Returns:**
- `float`: WACC

---

For more examples, see the `examples/portfolio_demo.py` file.
