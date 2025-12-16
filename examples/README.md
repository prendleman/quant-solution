# Portfolio Examples

This directory contains example scripts demonstrating how to use the quant portfolio modules.

## Available Examples

### `portfolio_demo.py`
Comprehensive demonstration showing:
- Time series analysis
- Risk management (VaR, CVaR, max drawdown)
- Derivatives pricing (Black-Scholes, Greeks)
- Machine learning for price prediction
- Financial modeling (DCF, WACC)
- Data analysis and statistics

## Running Examples

```bash
# Run the main demonstration
python examples/portfolio_demo.py
```

## Usage

Each module can also be imported and used independently:

```python
from utils.derivatives_ import black_scholes_price
from analysis.risk_management_ import calculate_var

# Calculate option price
price = black_scholes_price(S=100, K=105, T=0.25, r=0.05, sigma=0.2, option_type='call')

# Calculate VaR
var = calculate_var(returns, confidence_level=0.05)
```
