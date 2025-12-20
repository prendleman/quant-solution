"""
Advanced Machine Learning Models for Quantitative Finance

LSTM, Transformer, and ensemble models for time series prediction,
signal generation, and portfolio optimization.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scipy, sklearn, torch (optional)
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler


class LSTMPredictor:
    """
    Simplified LSTM-like predictor using linear models with lag features.
    For full LSTM, use PyTorch or TensorFlow.
    """
    
    def __init__(self, sequence_length: int = 10, n_features: int = 1):
        """
        Initialize LSTM predictor.
        
        Args:
            sequence_length: Length of input sequences
            n_features: Number of features
        """
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.model = None
        self.scaler = StandardScaler()
    
    def create_sequences(self, data: pd.Series) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for LSTM input.
        
        Args:
            data: Time series data
            
        Returns:
            (X, y) arrays
        """
        X, y = [], []
        for i in range(len(data) - self.sequence_length):
            X.append(data.iloc[i:i+self.sequence_length].values)
            y.append(data.iloc[i+self.sequence_length])
        return np.array(X), np.array(y)
    
    def fit(self, data: pd.Series):
        """Fit the model."""
        # Create sequences
        X, y = self.create_sequences(data)
        
        # Flatten for simple model (in real LSTM, keep 3D)
        X_flat = X.reshape(X.shape[0], -1)
        
        # Use ensemble model as proxy
        self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_flat, y)
    
    def predict(self, data: pd.Series) -> np.ndarray:
        """Make predictions."""
        if self.model is None:
            raise ValueError("Model not fitted")
        
        X, _ = self.create_sequences(data)
        X_flat = X.reshape(X.shape[0], -1)
        return self.model.predict(X_flat)


def transformer_attention_weights(returns: pd.DataFrame, n_heads: int = 4) -> pd.DataFrame:
    """
    Calculate attention-like weights for multi-asset returns.
    Simplified transformer attention mechanism.
    
    Args:
        returns: DataFrame of asset returns
        n_heads: Number of attention heads
        
    Returns:
        DataFrame of attention weights
    """
    # Correlation-based attention
    corr_matrix = returns.corr()
    
    # Normalize to attention weights
    attention_weights = corr_matrix.abs()
    attention_weights = attention_weights.div(attention_weights.sum(axis=1), axis=0)
    
    return attention_weights


def ensemble_prediction(models: List, X: np.ndarray, method: str = 'mean') -> np.ndarray:
    """
    Ensemble predictions from multiple models.
    
    Args:
        models: List of fitted models
        X: Input features
        method: 'mean', 'median', or 'weighted'
        
    Returns:
        Ensemble predictions
    """
    predictions = np.array([model.predict(X) for model in models])
    
    if method == 'mean':
        return predictions.mean(axis=0)
    elif method == 'median':
        return np.median(predictions, axis=0)
    elif method == 'weighted':
        # Weight by inverse variance
        weights = 1 / (predictions.std(axis=0) + 1e-8)
        weights = weights / weights.sum()
        return np.average(predictions, axis=0, weights=weights)
    else:
        return predictions.mean(axis=0)


def feature_importance_shap(returns: pd.DataFrame, target: pd.Series,
                            model=None) -> pd.Series:
    """
    Calculate feature importance using permutation importance.
    Simplified version of SHAP.
    
    Args:
        returns: Feature DataFrame
        target: Target series
        model: Fitted model (if None, uses RandomForest)
        
    Returns:
        Series of feature importances
    """
    if model is None:
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(returns, target)
    
    # Permutation importance
    baseline_score = model.score(returns, target)
    importances = {}
    
    for feature in returns.columns:
        returns_permuted = returns.copy()
        returns_permuted[feature] = np.random.permutation(returns_permuted[feature])
        permuted_score = model.score(returns_permuted, target)
        importances[feature] = baseline_score - permuted_score
    
    return pd.Series(importances).sort_values(ascending=False)


def deep_factor_model(returns: pd.DataFrame, n_factors: int = 5) -> Dict[str, pd.DataFrame]:
    """
    Deep factor model using PCA and non-linear transformations.
    
    Args:
        returns: Asset returns
        n_factors: Number of factors to extract
        
    Returns:
        Dictionary with factors and loadings
    """
    from sklearn.decomposition import PCA
    
    # PCA factors
    pca = PCA(n_components=n_factors)
    factors = pca.fit_transform(returns.fillna(0))
    factor_loadings = pca.components_.T
    
    # Factor returns
    factor_returns = pd.DataFrame(
        factors,
        index=returns.index,
        columns=[f'Factor_{i+1}' for i in range(n_factors)]
    )
    
    # Loadings
    loadings_df = pd.DataFrame(
        factor_loadings,
        index=returns.columns,
        columns=[f'Factor_{i+1}' for i in range(n_factors)]
    )
    
    return {
        'factor_returns': factor_returns,
        'factor_loadings': loadings_df,
        'explained_variance': pd.Series(pca.explained_variance_ratio_,
                                       index=[f'Factor_{i+1}' for i in range(n_factors)])
    }


def reinforcement_learning_portfolio_optimization(returns: pd.DataFrame,
                                                 risk_free_rate: float = 0.02) -> pd.Series:
    """
    RL-inspired portfolio optimization using reward-based selection.
    
    Args:
        returns: Asset returns
        risk_free_rate: Risk-free rate
        
    Returns:
        Optimal portfolio weights
    """
    # Calculate Sharpe ratios as rewards
    sharpe_ratios = (returns.mean() - risk_free_rate / 252) / (returns.std() + 1e-8) * np.sqrt(252)
    
    # Softmax weights (temperature parameter)
    temperature = 1.0
    exp_sharpe = np.exp(sharpe_ratios / temperature)
    weights = exp_sharpe / exp_sharpe.sum()
    
    return pd.Series(weights, index=returns.columns)


if __name__ == "__main__":
    # Example usage
    print("Advanced ML Models Demo")
    print("=" * 50)
    
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    returns = pd.Series(np.random.randn(100) * 0.01, index=dates)
    
    # LSTM predictor
    lstm = LSTMPredictor(sequence_length=10)
    lstm.fit(returns)
    predictions = lstm.predict(returns)
    print(f"\nLSTM Predictions (first 5): {predictions[:5]}")
