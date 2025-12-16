"""
Portfolio Demonstration Script

Shows how to use various modules in the quant portfolio.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import portfolio modules
from utils.time_series_ import analyze_time_series, calculate_returns
from analysis.risk_management_ import calculate_var, calculate_cvar, calculate_max_drawdown
from utils.derivatives_ import black_scholes_price, calculate_greeks, monte_carlo_option_price
from utils.machine_learning_ import prepare_features, train_price_prediction_model, generate_ml_signals
from models.financial_modeling_ import dcf_valuation, monte_carlo_valuation, calculate_wacc
from analysis.data_analysis_ import analyze_returns, correlation_analysis, rolling_statistics


def main():
    """
    Main demonstration function.
    """
    print("=" * 80)
    print("QUANTITATIVE FINANCE PORTFOLIO DEMONSTRATION")
    print("=" * 80)
    
    # Generate sample data
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    prices = 100 + np.cumsum(np.random.randn(500) * 0.5)
    price_data = pd.DataFrame({'Close': prices}, index=dates)
    
    print("\n1. TIME SERIES ANALYSIS")
    print("-" * 80)
    returns = calculate_returns(price_data['Close'])
    ts_analysis = analyze_time_series(returns, window=30)
    print(f"Mean return: {ts_analysis['mean']:.4f}")
    print(f"Std deviation: {ts_analysis['std']:.4f}")
    print(f"Skewness: {ts_analysis['skewness']:.4f}")
    
    print("\n2. RISK MANAGEMENT")
    print("-" * 80)
    var_95 = calculate_var(returns, 0.05)
    cvar_95 = calculate_cvar(returns, 0.05)
    max_dd = calculate_max_drawdown(price_data['Close'])
    print(f"VaR (95%): {var_95:.4f}")
    print(f"CVaR (95%): {cvar_95:.4f}")
    print(f"Max Drawdown: {max_dd:.2%}")
    
    print("\n3. DERIVATIVES PRICING")
    print("-" * 80)
    S, K, T, r, sigma = 100, 105, 0.25, 0.05, 0.2
    call_price = black_scholes_price(S, K, T, r, sigma, 'call')
    greeks = calculate_greeks(S, K, T, r, sigma, 'call')
    print(f"Call option price: ${call_price:.2f}")
    print(f"Delta: {greeks['delta']:.4f}, Gamma: {greeks['gamma']:.4f}")
    print(f"Theta: {greeks['theta']:.4f}, Vega: {greeks['vega']:.4f}")
    
    print("\n4. MACHINE LEARNING")
    print("-" * 80)
    X, y = prepare_features(price_data)
    ml_results = train_price_prediction_model(X, y, model_type='random_forest')
    print(f"ML Model R²: {ml_results['test_r2']:.4f}")
    signals = generate_ml_signals(price_data, ml_results)
    print(f"Trading signals generated: {signals[signals != 0].count()} signals")
    
    print("\n5. FINANCIAL MODELING")
    print("-" * 80)
    fcf = [100, 110, 120, 130, 140]
    dcf_result = dcf_valuation(fcf, 2000, 0.10)
    print(f"DCF Enterprise Value: ${dcf_result['enterprise_value']:,.2f}")
    wacc = calculate_wacc(800, 200, 0.12, 0.06, 0.25)
    print(f"WACC: {wacc:.2%}")
    
    print("\n6. DATA ANALYSIS")
    print("-" * 80)
    return_analysis = analyze_returns(returns)
    print(f"Sharpe Ratio: {return_analysis['sharpe_ratio']:.4f}")
    print(f"Positive days: {return_analysis['positive_days']}")
    print(f"Negative days: {return_analysis['negative_days']}")
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
