"""
Visualization utilities for quantitative analysis.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Optional


class QuantVisualizer:
    """Create visualizations for quantitative analysis."""
    
    def __init__(self, style: str = 'seaborn-v0_8'):
        """Initialize visualizer with style."""
        plt.style.use(style)
        sns.set_palette("husl")
    
    def plot_equity_curve(self, 
                         equity: pd.Series, 
                         title: str = "Equity Curve",
                         figsize: tuple = (12, 6)) -> plt.Figure:
        """
        Plot equity curve over time.
        
        Args:
            equity: Series of portfolio values
            title: Plot title
            figsize: Figure size
            
        Returns:
            matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(equity.index, equity.values, linewidth=2)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Portfolio Value ($)')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig
    
    def plot_returns_distribution(self, 
                                  returns: pd.Series,
                                  title: str = "Returns Distribution",
                                  figsize: tuple = (10, 6)) -> plt.Figure:
        """
        Plot distribution of returns.
        
        Args:
            returns: Series of returns
            title: Plot title
            figsize: Figure size
            
        Returns:
            matplotlib Figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Histogram
        ax1.hist(returns, bins=50, alpha=0.7, edgecolor='black')
        ax1.axvline(returns.mean(), color='red', linestyle='--', 
                   label=f'Mean: {returns.mean():.4f}')
        ax1.set_title('Returns Histogram')
        ax1.set_xlabel('Returns')
        ax1.set_ylabel('Frequency')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Q-Q plot
        from scipy import stats
        stats.probplot(returns, dist="norm", plot=ax2)
        ax2.set_title('Q-Q Plot')
        ax2.grid(True, alpha=0.3)
        
        fig.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        return fig
    
    def plot_drawdown(self,
                     equity: pd.Series,
                     title: str = "Drawdown Analysis",
                     figsize: tuple = (12, 6)) -> plt.Figure:
        """
        Plot drawdown over time.
        
        Args:
            equity: Series of portfolio values
            title: Plot title
            figsize: Figure size
            
        Returns:
            matplotlib Figure
        """
        # Calculate running maximum
        running_max = equity.expanding().max()
        drawdown = (equity - running_max) / running_max * 100
        
        fig, ax = plt.subplots(figsize=figsize)
        ax.fill_between(drawdown.index, drawdown.values, 0, 
                       alpha=0.3, color='red')
        ax.plot(drawdown.index, drawdown.values, linewidth=1, color='darkred')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Drawdown (%)')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig

