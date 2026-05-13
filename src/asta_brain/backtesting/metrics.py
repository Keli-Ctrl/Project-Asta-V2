import pandas as pd
import numpy as np
from typing import Dict, Any, List
from src.asta_brain.backtesting.models import BacktestResult, BacktestTrade

def calculate_detailed_metrics(result: BacktestResult) -> Dict[str, Any]:
    """
    Calculates institutional-grade metrics for a backtest result.
    """
    trades = result.trades
    if not trades:
        return {"error": "No trades to analyze"}

    df_trades = pd.DataFrame([t.model_dump() for t in trades])
    
    # basic stats
    win_trades = df_trades[df_trades['profit'] > 0]
    loss_trades = df_trades[df_trades['profit'] <= 0]
    
    # Sortino Ratio (needs daily returns)
    equity_series = pd.Series(result.equity_curve)
    returns = equity_series.pct_change().dropna()
    downside_returns = returns[returns < 0]
    sortino = (returns.mean() / downside_returns.std()) * (252**0.5) if not downside_returns.empty and downside_returns.std() > 0 else 0
    
    # Recovery Factor
    recovery_factor = (result.final_balance - result.initial_balance) / (result.initial_balance * result.max_drawdown) if result.max_drawdown > 0 else float('inf')
    
    # Expectancy
    # (Avg Win * Win Rate) - (Avg Loss * Loss Rate)
    win_rate = result.win_rate
    avg_win = win_trades['profit'].mean() if not win_trades.empty else 0
    avg_loss = abs(loss_trades['profit'].mean()) if not loss_trades.empty else 0
    expectancy = (avg_win * win_rate) - (avg_loss * (1 - win_rate))
    
    return {
        "win_rate": result.win_rate,
        "profit_factor": result.profit_factor,
        "sharpe_ratio": result.sharpe_ratio,
        "sortino_ratio": sortino,
        "max_drawdown": result.max_drawdown,
        "recovery_factor": recovery_factor,
        "expectancy": expectancy,
        "total_trades": result.total_trades,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_in_currency": result.final_balance - result.initial_balance
    }

def compare_strategies(results: List[BacktestResult]) -> pd.DataFrame:
    """
    Compares multiple strategy runs in a single DataFrame.
    """
    comparison = []
    for res in results:
        metrics = calculate_detailed_metrics(res)
        metrics['strategy_id'] = res.strategy_id
        comparison.append(metrics)
        
    return pd.DataFrame(comparison)
