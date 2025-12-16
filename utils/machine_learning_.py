"""
Machine Learning for Quantitative Finance

ML models for price prediction, signal generation, and risk modeling.
Generated as part of quant portfolio development.
"""

from typing import Optional, Tuple, List
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score


def prepare_features(data: pd.DataFrame, lookback: int = 5) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Prepare features for ML model from price data.
    
    Args:
        data: DataFrame with price data (must have 'Close' column)
        lookback: Number of periods to look back for features
        
    Returns:
        Tuple of (features_df, target_series)
    """
    df = data.copy()
    
    # Calculate returns
    df['returns'] = df['Close'].pct_change()
    
    # Technical indicators as features
    df['sma_5'] = df['Close'].rolling(5).mean()
    df['sma_20'] = df['Close'].rolling(20).mean()
    df['volatility'] = df['returns'].rolling(20).std()
    df['rsi'] = calculate_rsi(df['Close'], 14)
    
    # Lagged features
    for i in range(1, lookback + 1):
        df[f'return_lag_{i}'] = df['returns'].shift(i)
        df[f'close_lag_{i}'] = df['Close'].shift(i)
    
    # Target: next period return
    df['target'] = df['returns'].shift(-1)
    
    # Drop NaN rows
    df = df.dropna()
    
    # Select feature columns
    feature_cols = [col for col in df.columns if col not in ['Close', 'returns', 'target']]
    X = df[feature_cols]
    y = df['target']
    
    return X, y


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
        prices: Price series
        period: RSI period
        
    Returns:
        RSI series
    """
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def train_price_prediction_model(X: pd.DataFrame, y: pd.Series, 
                                 model_type: str = 'random_forest',
                                 test_size: float = 0.2) -> dict:
    """
    Train ML model for price prediction.
    
    Args:
        X: Feature matrix
        y: Target variable (returns)
        model_type: 'random_forest', 'gradient_boosting', 'linear', or 'ridge'
        test_size: Proportion of data for testing
        
    Returns:
        Dictionary with model, metrics, and predictions
    """
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, shuffle=False)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Select model
    if model_type == 'random_forest':
        model = RandomForestRegressor(n_estimators=100, random_state=42)
    elif model_type == 'gradient_boosting':
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
    elif model_type == 'linear':
        model = LinearRegression()
    elif model_type == 'ridge':
        model = Ridge(alpha=1.0)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    # Train
    model.fit(X_train_scaled, y_train)
    
    # Predictions
    y_pred_train = model.predict(X_train_scaled)
    y_pred_test = model.predict(X_test_scaled)
    
    # Metrics
    train_mse = mean_squared_error(y_train, y_pred_train)
    test_mse = mean_squared_error(y_test, y_pred_test)
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    
    return {
        'model': model,
        'scaler': scaler,
        'train_mse': train_mse,
        'test_mse': test_mse,
        'train_r2': train_r2,
        'test_r2': test_r2,
        'y_pred_test': y_pred_test,
        'y_test': y_test
    }


def generate_ml_signals(data: pd.DataFrame, model_dict: dict, threshold: float = 0.001) -> pd.Series:
    """
    Generate trading signals from ML model predictions.
    
    Args:
        data: Price data
        model_dict: Dictionary from train_price_prediction_model
        threshold: Minimum predicted return to generate signal
        
    Returns:
        Series of signals (1 = buy, -1 = sell, 0 = hold)
    """
    X, _ = prepare_features(data)
    X_scaled = model_dict['scaler'].transform(X)
    predictions = model_dict['model'].predict(X_scaled)
    
    signals = pd.Series(0, index=X.index)
    signals[predictions > threshold] = 1  # Buy
    signals[predictions < -threshold] = -1  # Sell
    
    return signals


if __name__ == "__main__":
    # Example usage
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    prices = 100 + np.cumsum(np.random.randn(500) * 0.5)
    data = pd.DataFrame({'Close': prices}, index=dates)
    
    # Prepare features
    X, y = prepare_features(data)
    print(f"Prepared {len(X)} samples with {len(X.columns)} features")
    
    # Train model
    results = train_price_prediction_model(X, y, model_type='random_forest')
    print(f"\nModel Performance:")
    print(f"  Train R²: {results['train_r2']:.4f}")
    print(f"  Test R²: {results['test_r2']:.4f}")
    print(f"  Test MSE: {results['test_mse']:.6f}")
    
    # Generate signals
    signals = generate_ml_signals(data, results)
    print(f"\nGenerated {signals[signals != 0].count()} trading signals")
