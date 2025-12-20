"""
Kalman Filter for State Estimation

Kalman filter implementation for dynamic state estimation in quantitative finance:
tracking hidden variables, parameter estimation, and signal extraction.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd


class KalmanFilter:
    """
    Simple Kalman Filter for state estimation.
    """
    
    def __init__(self, initial_state: float, initial_uncertainty: float,
                 process_noise: float, measurement_noise: float):
        """
        Initialize Kalman Filter.
        
        Args:
            initial_state: Initial state estimate
            initial_uncertainty: Initial uncertainty (covariance)
            process_noise: Process noise (Q)
            measurement_noise: Measurement noise (R)
        """
        self.state = initial_state
        self.uncertainty = initial_uncertainty
        self.process_noise = process_noise
        self.measurement_noise = measurement_noise
    
    def predict(self) -> Tuple[float, float]:
        """
        Predict next state (prediction step).
        
        Returns:
            (predicted_state, predicted_uncertainty)
        """
        # State prediction (assuming no control input)
        predicted_state = self.state
        
        # Uncertainty prediction
        predicted_uncertainty = self.uncertainty + self.process_noise
        
        return predicted_state, predicted_uncertainty
    
    def update(self, measurement: float) -> Tuple[float, float]:
        """
        Update state estimate with measurement (update step).
        
        Args:
            measurement: Observed measurement
            
        Returns:
            (updated_state, updated_uncertainty)
        """
        # Prediction
        predicted_state, predicted_uncertainty = self.predict()
        
        # Kalman gain
        kalman_gain = predicted_uncertainty / (predicted_uncertainty + self.measurement_noise)
        
        # Update state
        self.state = predicted_state + kalman_gain * (measurement - predicted_state)
        
        # Update uncertainty
        self.uncertainty = (1 - kalman_gain) * predicted_uncertainty
        
        return self.state, self.uncertainty
    
    def filter(self, measurements: pd.Series) -> pd.DataFrame:
        """
        Apply Kalman filter to series of measurements.
        
        Args:
            measurements: Series of measurements
            
        Returns:
            DataFrame with filtered states and uncertainties
        """
        filtered_states = []
        filtered_uncertainties = []
        
        for measurement in measurements:
            state, uncertainty = self.update(measurement)
            filtered_states.append(state)
            filtered_uncertainties.append(uncertainty)
        
        return pd.DataFrame({
            'filtered_state': filtered_states,
            'uncertainty': filtered_uncertainties,
            'measurement': measurements.values
        }, index=measurements.index)


def estimate_volatility_kalman(returns: pd.Series, initial_vol: float = 0.02) -> pd.Series:
    """
    Estimate time-varying volatility using Kalman filter.
    
    Args:
        returns: Series of returns
        initial_vol: Initial volatility estimate
        
    Returns:
        Series of filtered volatility estimates
    """
    # Use squared returns as noisy measurements of volatility
    squared_returns = returns ** 2
    
    # Initialize Kalman filter
    kf = KalmanFilter(
        initial_state=initial_vol ** 2,
        initial_uncertainty=0.001,
        process_noise=0.0001,
        measurement_noise=0.01
    )
    
    # Filter
    result = kf.filter(squared_returns)
    
    # Return volatility (square root of variance)
    return np.sqrt(result['filtered_state'])


def estimate_trend_kalman(prices: pd.Series) -> pd.DataFrame:
    """
    Estimate trend component using Kalman filter.
    
    Args:
        prices: Series of prices
        
    Returns:
        DataFrame with filtered trend and residuals
    """
    # Initialize filter
    kf = KalmanFilter(
        initial_state=prices.iloc[0],
        initial_uncertainty=1.0,
        process_noise=0.1,
        measurement_noise=1.0
    )
    
    # Filter prices
    result = kf.filter(prices)
    
    # Calculate residuals
    result['residuals'] = prices.values - result['filtered_state'].values
    
    return result


def dynamic_beta_estimation(stock_returns: pd.Series, market_returns: pd.Series) -> pd.Series:
    """
    Estimate time-varying beta using Kalman filter.
    
    Args:
        stock_returns: Series of stock returns
        market_returns: Series of market returns
        
    Returns:
        Series of filtered beta estimates
    """
    # Align data
    aligned = pd.DataFrame({
        'stock': stock_returns,
        'market': market_returns
    }).dropna()
    
    if len(aligned) < 10:
        return pd.Series(1.0, index=stock_returns.index)
    
    # Initialize beta estimate
    initial_beta = aligned['stock'].cov(aligned['market']) / aligned['market'].var()
    
    # Kalman filter for beta
    kf = KalmanFilter(
        initial_state=initial_beta,
        initial_uncertainty=0.1,
        process_noise=0.01,
        measurement_noise=0.1
    )
    
    # Filter: use rolling regression residuals as measurements
    betas = []
    window = 20
    
    for i in range(len(aligned)):
        if i < window:
            # Use initial estimate
            betas.append(initial_beta)
        else:
            # Rolling regression
            window_data = aligned.iloc[i-window:i]
            beta_est = window_data['stock'].cov(window_data['market']) / window_data['market'].var()
            if not np.isnan(beta_est):
                state, _ = kf.update(beta_est)
                betas.append(state)
            else:
                betas.append(betas[-1] if betas else initial_beta)
    
    return pd.Series(betas, index=aligned.index)


if __name__ == "__main__":
    # Example usage
    print("Kalman Filter Demo")
    print("=" * 50)
    
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    noisy_signal = 100 + np.cumsum(np.random.randn(100) * 0.5) + np.random.randn(100) * 2
    signal_series = pd.Series(noisy_signal, index=dates)
    
    # Trend estimation
    trend_result = estimate_trend_kalman(signal_series)
    print(f"\nTrend Estimation:")
    print(f"  Final filtered state: {trend_result['filtered_state'].iloc[-1]:.2f}")
    print(f"  Final uncertainty: {trend_result['uncertainty'].iloc[-1]:.4f}")
