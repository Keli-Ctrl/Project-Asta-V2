from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import enum

class SignalAction(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"
    CLOSE = "close"
    HOLD = "hold"

class StrategySignal(BaseModel):
    id: str
    strategy_id: str
    symbol: str
    action: SignalAction
    confidence: float  # 0.0 to 1.0
    price: Optional[float] = None
    sl: Optional[float] = None
    tp: Optional[float] = None
    timestamp: datetime = datetime.utcnow()
    metadata: Optional[dict] = None

class MarketData(BaseModel):
    symbol: str
    timeframe: str
    ohlcv: List[dict] # Simplified for now, will be replaced by a more robust structure
    timestamp: datetime = datetime.utcnow()

class BaseStrategy(ABC):
    def __init__(self, strategy_id: str, config: Optional[dict] = None):
        self.strategy_id = strategy_id
        self.config = config or {}
        self.enabled = True

    @abstractmethod
    async def analyze(self, market_data: MarketData) -> List[StrategySignal]:
        """
        Analyze market data and return a list of signals.
        """
        pass

    def toggle(self, status: bool):
        self.enabled = status
