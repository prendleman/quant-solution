# Quantitative Finance Portfolio

A comprehensive portfolio demonstrating quantitative finance skills, algorithms, and implementations.

## Overview

This portfolio contains implementations of various quantitative finance concepts, trading strategies, risk management tools, and data analysis techniques. All code is production-ready and demonstrates professional quant skills.

## Structure

- **models/**: Financial models and algorithms
- **strategies/**: Trading strategies and backtesting frameworks
- **analysis/**: Risk management and data analysis tools
- **utils/**: Utility functions and helper modules
- **examples/**: Example usage and demonstrations
- **tests/**: Unit tests and validation

## Features

### Risk Management
- Value at Risk (VaR) calculation
- Conditional Value at Risk (CVaR)
- Maximum drawdown analysis

### Derivatives Pricing
- Black-Scholes option pricing model
- Greeks calculation (Delta, Gamma, Theta, Vega, Rho)
- Monte Carlo option pricing

### Trading Strategies
- High-frequency trading framework
- Strategy backtesting engine
- Signal generation systems
- Machine learning-based signal generation
- Statistical arbitrage (pairs trading, mean reversion)
- Cointegration testing
- Hedge ratio calculation

### Portfolio Optimization
- Mean-variance optimization (Markowitz)
- Risk parity portfolio
- Minimum variance portfolio
- Efficient frontier generation
- Portfolio performance metrics

### Volatility Modeling
- GARCH(p,q) volatility models
- EWMA (Exponentially Weighted Moving Average) volatility
- Realized volatility estimation
- Volatility forecasting
- Volatility clustering tests

### Factor Models
- Fama-French factor models (3-factor, 5-factor)
- Factor exposure calculation
- Factor attribution analysis
- Style analysis with constraints

### Performance Attribution
- Return decomposition
- Alpha and beta calculation
- Information ratio and tracking error
- Win rate analysis
- Calmar ratio
- Rolling performance metrics

### Machine Learning
- Price prediction models (Random Forest, Gradient Boosting, Linear, Ridge)
- Feature engineering for financial data
- Technical indicators (RSI, moving averages)
- Trading signal generation from ML predictions

### Financial Modeling
- DCF (Discounted Cash Flow) valuation
- Financial ratios calculation
- Monte Carlo valuation simulation
- WACC (Weighted Average Cost of Capital) calculation

### Data Analysis
- Comprehensive return analysis
- Correlation analysis
- Outlier detection (IQR and Z-score methods)
- Rolling statistics
- Stationarity testing (ADF test)
- Data quality reporting
- Time series analysis
- Statistical modeling

### Advanced Options Pricing
- Binomial tree pricing
- American option pricing (Longstaff-Schwartz)
- Implied volatility calculation
- Barrier option pricing

### Momentum Strategies
- Price momentum signals
- Cross-sectional momentum
- Earnings momentum
- RSI-based momentum
- Momentum factor analysis

### Risk Budgeting
- Risk parity optimization
- Risk budget allocation
- Kelly Criterion position sizing
- Volatility targeting
- Risk decomposition

### Technical Indicators
- Moving averages (SMA, EMA, WMA)
- Bollinger Bands
- MACD
- Stochastic Oscillator
- ATR and ADX
- Williams %R
- CCI
- Fibonacci retracements

### Data Processing
- Financial data cleaning
- Winsorization
- Normalization methods
- Structural break detection
- Data alignment utilities

### Statistical Analysis
- Hypothesis testing (t-test, Mann-Whitney)
- Normality tests (Shapiro-Wilk, Jarque-Bera)
- Correlation tests
- Bootstrap confidence intervals
- Chi-square tests

### Quantitative Research
- Signal-to-noise ratio
- Information Coefficient (IC)
- Factor analysis (PCA)
- Regime detection
- Sharpe ratio testing
- Research backtesting
- Feature importance analysis

### Execution Algorithms
- TWAP (Time-Weighted Average Price) execution
- VWAP (Volume-Weighted Average Price) execution
- Implementation Shortfall optimization
- Adaptive execution strategies
- Optimal execution (Almgren-Chriss model)
- Execution quality evaluation

### Fixed Income Models
- Bond pricing and valuation
- Yield to maturity calculation
- Macaulay and Modified duration
- Bond convexity
- Yield curve bootstrapping
- Duration matching for ALM

### Foreign Exchange (FX) Models
- Forward rate calculation
- Carry trade analysis
- FX volatility smile/skew
- Triangular arbitrage detection
- Purchasing Power Parity (PPP)
- Currency basket hedging

### Market Microstructure
- Order book imbalance analysis
- Effective spread calculation
- Kyle's Lambda (price impact)
- Amihud illiquidity measure
- Roll spread estimation
- Market impact functions
- Price impact curve fitting

### Reinforcement Learning Trading
- DQN (Deep Q-Network) trading agent
- Trading environment simulation
- Experience replay and training
- Policy optimization for trading

### Alternative Data Analysis
- Sentiment analysis from text
- Satellite data correlation
- Web traffic analysis
- Social media sentiment
- Credit card transaction analysis
- News sentiment analysis
- Multi-signal combination

### Technologies
- Python with pandas, numpy, scipy
- Machine learning (scikit-learn, PyTorch)
- Data visualization and analysis tools

## Getting Started

### Installation

**Option 1: Install from source**
```bash
git clone https://github.com/yourusername/quant-portfolio.git
cd quant-portfolio
pip install -r requirements.txt
pip install -e .
```

**Option 2: Install dependencies only**
```bash
pip install -r requirements.txt
```

**Option 3: Install with development dependencies**
```bash
pip install -e ".[dev]"
```

### Usage

Each module can be run independently or imported as a library:

```python
from analysis.risk_management_ import calculate_var, calculate_cvar
from strategies.high_frequency_trading_ import TradingStrategy
import pandas as pd

# Example: Calculate VaR
returns = pd.Series([0.01, -0.02, 0.015, -0.01, 0.005, -0.03])
var_95 = calculate_var(returns, confidence_level=0.05)
print(f"VaR (95%): {var_95:.4f}")
```

See `examples/portfolio_demo.py` for comprehensive usage examples.

### Running Tests

```bash
pytest tests/ -v
```

With coverage:
```bash
pytest tests/ -v --cov=. --cov-report=html
```

## Documentation

- **API Reference**: See [docs/API.md](docs/API.md) for detailed API documentation
- **Examples**: See `examples/portfolio_demo.py` for usage examples
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines

## Portfolio Evolution

This portfolio is continuously improved based on quantitative job market requirements. New features are added automatically to demonstrate the latest quant skills and technologies in demand.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
