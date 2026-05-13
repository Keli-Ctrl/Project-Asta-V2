import numpy as np
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from loguru import logger

class PerformanceMetrics:
    """
    Calculates institutional-grade performance metrics.
    """
    
    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """
        Calculates the annualized Sharpe Ratio.
        """
        if returns.empty or returns.std() == 0:
            return 0.0
        # Assuming daily returns, 252 trading days
        excess_returns = returns - (risk_free_rate / 252)
        return (excess_returns.mean() / returns.std()) * np.sqrt(252)

    @staticmethod
    def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
        """
        Calculates the annualized Sortino Ratio (downside risk only).
        """
        if returns.empty:
            return 0.0
        downside_returns = returns[returns < 0]
        if downside_returns.empty or downside_returns.std() == 0:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / 252)
        return (excess_returns.mean() / downside_returns.std()) * np.sqrt(252)

    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> float:
        """
        Calculates the maximum drawdown from an equity curve.
        """
        if equity_curve.empty:
            return 0.0
        rolling_max = equity_curve.cummax()
        drawdowns = (equity_curve - rolling_max) / rolling_max
        return float(drawdowns.min())

    @staticmethod
    def calculate_profit_factor(trades: List[Dict[str, Any]]) -> float:
        """
        Calculates the Profit Factor (Gross Profit / Gross Loss).
        """
        gross_profit = sum(t['profit'] for t in trades if t['profit'] > 0)
        gross_loss = abs(sum(t['profit'] for t in trades if t['profit'] < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return gross_profit / gross_loss

    def get_summary_metrics(self, trade_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Returns a comprehensive summary of performance metrics.
        """
        if not trade_history:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0
            }

        df = pd.DataFrame(trade_history)
        df['close_time'] = pd.to_datetime(df['close_time'])
        df = df.sort_values('close_time')
        
        # Win rate
        winning_trades = len(df[df['profit'] > 0])
        win_rate = winning_trades / len(df)
        
        # Daily returns for Sharpe/Sortino
        # This is a simplification; ideally use daily account equity snapshots
        df.set_index('close_time', inplace=True)
        daily_profit = df['profit'].resample('D').sum()
        # For simplicity, we'll assume a starting balance of 10k if balance isn't provided
        # In a real system, we'd use the actual equity curve
        
        return {
            "total_trades": len(df),
            "win_rate": float(win_rate),
            "profit_factor": self.calculate_profit_factor(trade_history),
            "max_drawdown": self.calculate_max_drawdown(df['profit'].cumsum() + 10000), # Mock base
            "total_net_profit": float(df['profit'].sum())
        }
