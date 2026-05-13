from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from src.asta_brain.core.interfaces.strategy import StrategySignal
from src.asta_brain.core.domain.trade import TradeSide

class BacktestTrade(BaseModel):
    id: str
    symbol: str
    side: TradeSide
    entry_price: float
    exit_price: Optional[float] = None
    volume: float
    entry_time: datetime
    exit_time: Optional[datetime] = None
    sl: Optional[float] = None
    tp: Optional[float] = None
    profit: float = 0.0
    commission: float = 0.0
    swap: float = 0.0
    status: str = "open" # "open", "closed"

class BacktestResult(BaseModel):
    strategy_id: str
    start_time: datetime
    end_time: datetime
    initial_balance: float
    final_balance: float
    total_trades: int
    win_rate: float
    profit_factor: float
    max_drawdown: float
    sharpe_ratio: float
    equity_curve: List[float]
    trades: List[BacktestTrade]
