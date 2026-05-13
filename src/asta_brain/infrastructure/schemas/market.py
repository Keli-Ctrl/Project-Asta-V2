from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class Tick(BaseModel):
    symbol: str
    ask: float
    bid: float
    time: datetime = Field(default_factory=datetime.utcnow)
    broker_time: Optional[datetime] = None

class OHLCV(BaseModel):
    symbol: str
    timeframe: str
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

class MarketDataSubscription(BaseModel):
    symbol: str
    timeframe: Optional[str] = None
    type: str # "tick" or "ohlcv"
