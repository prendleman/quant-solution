"""
Alternative Data Analysis

Analysis of non-traditional data sources for quantitative trading:
sentiment analysis, satellite data, web scraping, social media, etc.

Requirements:
- Python 3.8+
- Libraries: pandas, numpy, scikit-learn
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation


def sentiment_score(text_data: pd.Series, method: str = 'simple') -> pd.Series:
    """
    Calculate sentiment scores from text data.
    
    Args:
        text_data: Series of text strings
        method: 'simple' (keyword-based) or 'tfidf' (TF-IDF based)
        
    Returns:
        Series of sentiment scores (-1 to 1)
    """
    if method == 'simple':
        # Simple keyword-based sentiment
        positive_words = ['good', 'great', 'excellent', 'positive', 'up', 'bullish', 'buy', 'strong']
        negative_words = ['bad', 'poor', 'negative', 'down', 'bearish', 'sell', 'weak', 'crash']
        
        scores = []
        for text in text_data:
            if pd.isna(text):
                scores.append(0.0)
                continue
            
            text_lower = str(text).lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            total = positive_count + negative_count
            if total > 0:
                score = (positive_count - negative_count) / total
            else:
                score = 0.0
            scores.append(score)
        
        return pd.Series(scores, index=text_data.index)
    
    else:
        # Placeholder for more sophisticated methods
        return pd.Series(0.0, index=text_data.index)


def satellite_data_analysis(activity_indicators: pd.Series, 
                           price_data: pd.Series,
                           correlation_window: int = 20) -> Dict[str, float]:
    """
    Analyze correlation between satellite activity indicators and asset prices.
    Common use cases: parking lot activity, shipping traffic, oil storage levels.
    
    Args:
        activity_indicators: Series of activity indicators (e.g., car counts, ship counts)
        price_data: Series of asset prices
        correlation_window: Rolling window for correlation calculation
        
    Returns:
        Dictionary with correlation metrics
    """
    # Align data
    aligned_data = pd.DataFrame({
        'activity': activity_indicators,
        'price': price_data
    }).dropna()
    
    if len(aligned_data) < correlation_window:
        return {
            'correlation': 0.0,
            'rolling_correlation_mean': 0.0,
            'lead_lag_correlation': 0.0
        }
    
    # Calculate correlation
    correlation = aligned_data['activity'].corr(aligned_data['price'])
    
    # Rolling correlation
    rolling_corr = aligned_data['activity'].rolling(window=correlation_window).corr(
        aligned_data['price'].rolling(window=correlation_window)
    )
    
    # Lead-lag analysis (activity leads price by 1 period)
    activity_lead = aligned_data['activity'].shift(-1)
    lead_lag_corr = activity_lead.corr(aligned_data['price'])
    
    return {
        'correlation': correlation,
        'rolling_correlation_mean': rolling_corr.mean() if not rolling_corr.empty else 0.0,
        'lead_lag_correlation': lead_lag_corr,
        'signal_strength': abs(correlation) if not np.isnan(correlation) else 0.0
    }


def web_traffic_analysis(traffic_data: pd.Series, returns: pd.Series,
                        lookback: int = 5) -> Dict[str, float]:
    """
    Analyze relationship between web traffic metrics and stock returns.
    
    Args:
        traffic_data: Series of web traffic metrics (visits, page views, etc.)
        returns: Series of asset returns
        lookback: Lookback period for traffic aggregation
        
    Returns:
        Dictionary with analysis results
    """
    # Aggregate traffic over lookback period
    traffic_ma = traffic_data.rolling(window=lookback).mean()
    
    # Align data
    aligned = pd.DataFrame({
        'traffic': traffic_ma,
        'returns': returns
    }).dropna()
    
    if len(aligned) < 10:
        return {
            'correlation': 0.0,
            'traffic_momentum': 0.0,
            'predictive_power': 0.0
        }
    
    # Correlation
    correlation = aligned['traffic'].corr(aligned['returns'])
    
    # Traffic momentum (change in traffic)
    traffic_momentum = aligned['traffic'].pct_change().mean()
    
    # Predictive power (traffic leads returns)
    traffic_lead = aligned['traffic'].shift(-1)
    predictive_corr = traffic_lead.corr(aligned['returns'])
    
    return {
        'correlation': correlation,
        'traffic_momentum': traffic_momentum,
        'predictive_power': predictive_corr if not np.isnan(predictive_corr) else 0.0
    }


def social_media_sentiment(mention_counts: pd.Series, sentiment_scores: pd.Series,
                          returns: pd.Series) -> Dict[str, float]:
    """
    Analyze social media sentiment and mention frequency vs. returns.
    
    Args:
        mention_counts: Series of social media mention counts
        sentiment_scores: Series of sentiment scores
        returns: Series of asset returns
        
    Returns:
        Dictionary with sentiment analysis results
    """
    data = pd.DataFrame({
        'mentions': mention_counts,
        'sentiment': sentiment_scores,
        'returns': returns
    }).dropna()
    
    if len(data) < 10:
        return {
            'sentiment_correlation': 0.0,
            'mention_correlation': 0.0,
            'combined_signal': 0.0
        }
    
    # Individual correlations
    sentiment_corr = data['sentiment'].corr(data['returns'])
    mention_corr = data['mentions'].corr(data['returns'])
    
    # Combined signal (weighted)
    combined_signal = (sentiment_corr * 0.7 + mention_corr * 0.3) if not (np.isnan(sentiment_corr) or np.isnan(mention_corr)) else 0.0
    
    return {
        'sentiment_correlation': sentiment_corr if not np.isnan(sentiment_corr) else 0.0,
        'mention_correlation': mention_corr if not np.isnan(mention_corr) else 0.0,
        'combined_signal': combined_signal
    }


def credit_card_transaction_analysis(transaction_volumes: pd.Series,
                                    stock_returns: pd.Series,
                                    company_name: str = "") -> Dict[str, float]:
    """
    Analyze credit card transaction data as leading indicator for retail stocks.
    
    Args:
        transaction_volumes: Series of transaction volumes
        stock_returns: Series of stock returns
        company_name: Company name (for context)
        
    Returns:
        Dictionary with analysis results
    """
    data = pd.DataFrame({
        'transactions': transaction_volumes,
        'returns': stock_returns
    }).dropna()
    
    if len(data) < 10:
        return {
            'correlation': 0.0,
            'leading_indicator': 0.0,
            'transaction_growth': 0.0
        }
    
    # Correlation
    correlation = data['transactions'].corr(data['returns'])
    
    # Leading indicator (transactions lead returns)
    transactions_lead = data['transactions'].shift(-1)
    leading_corr = transactions_lead.corr(data['returns'])
    
    # Transaction growth rate
    transaction_growth = data['transactions'].pct_change().mean()
    
    return {
        'correlation': correlation if not np.isnan(correlation) else 0.0,
        'leading_indicator': leading_corr if not np.isnan(leading_corr) else 0.0,
        'transaction_growth': transaction_growth if not np.isnan(transaction_growth) else 0.0
    }


def news_sentiment_analysis(news_headlines: pd.Series, returns: pd.Series) -> Dict[str, float]:
    """
    Analyze news headline sentiment and its relationship to returns.
    
    Args:
        news_headlines: Series of news headlines
        returns: Series of asset returns
        
    Returns:
        Dictionary with sentiment analysis results
    """
    # Calculate sentiment scores
    sentiment_scores = sentiment_score(news_headlines, method='simple')
    
    # Align with returns
    data = pd.DataFrame({
        'sentiment': sentiment_scores,
        'returns': returns
    }).dropna()
    
    if len(data) < 10:
        return {
            'sentiment_correlation': 0.0,
            'sentiment_momentum': 0.0,
            'news_impact': 0.0
        }
    
    # Correlation
    correlation = data['sentiment'].corr(data['returns'])
    
    # Sentiment momentum
    sentiment_momentum = data['sentiment'].diff().mean()
    
    # News impact (sentiment leads returns)
    sentiment_lead = data['sentiment'].shift(-1)
    news_impact = sentiment_lead.corr(data['returns'])
    
    return {
        'sentiment_correlation': correlation if not np.isnan(correlation) else 0.0,
        'sentiment_momentum': sentiment_momentum if not np.isnan(sentiment_momentum) else 0.0,
        'news_impact': news_impact if not np.isnan(news_impact) else 0.0
    }


def alternative_data_signal_combination(signals: Dict[str, pd.Series],
                                       returns: pd.Series,
                                       weights: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    """
    Combine multiple alternative data signals into a composite signal.
    
    Args:
        signals: Dictionary of signal name -> signal series
        returns: Series of asset returns
        weights: Optional weights for each signal (default: equal weights)
        
    Returns:
        Dictionary with combined signal metrics
    """
    if weights is None:
        weights = {name: 1.0 / len(signals) for name in signals.keys()}
    
    # Normalize signals
    normalized_signals = {}
    for name, signal in signals.items():
        if len(signal.dropna()) > 0:
            normalized = (signal - signal.mean()) / (signal.std() + 1e-8)
            normalized_signals[name] = normalized
    
    # Combine signals
    combined_signal = pd.Series(0.0, index=returns.index)
    for name, signal in normalized_signals.items():
        weight = weights.get(name, 0.0)
        combined_signal += weight * signal
    
    # Align with returns
    data = pd.DataFrame({
        'combined_signal': combined_signal,
        'returns': returns
    }).dropna()
    
    if len(data) < 10:
        return {
            'combined_correlation': 0.0,
            'signal_strength': 0.0,
            'sharpe_ratio': 0.0
        }
    
    # Calculate metrics
    correlation = data['combined_signal'].corr(data['returns'])
    signal_strength = abs(correlation)
    
    # Sharpe-like metric
    signal_returns = data['combined_signal'] * data['returns']
    sharpe = signal_returns.mean() / (signal_returns.std() + 1e-8) * np.sqrt(252)
    
    return {
        'combined_correlation': correlation if not np.isnan(correlation) else 0.0,
        'signal_strength': signal_strength,
        'sharpe_ratio': sharpe if not np.isnan(sharpe) else 0.0,
        'signal_components': list(signals.keys())
    }


if __name__ == "__main__":
    # Example usage
    print("Alternative Data Analysis Demo")
    print("=" * 50)
    
    # Generate sample data
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    sentiment = pd.Series(np.random.uniform(-1, 1, 100), index=dates)
    returns = pd.Series(np.random.randn(100) * 0.01, index=dates)
    
    # News sentiment analysis
    news_result = news_sentiment_analysis(sentiment, returns)
    print("\nNews Sentiment Analysis:")
    for key, value in news_result.items():
        print(f"  {key}: {value:.4f}")
