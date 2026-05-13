from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class TradeSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class TradeType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"

class TradeRequest(BaseModel):
    account_id: str
    symbol: str
    side: TradeSide
    volume: float
    type: TradeType = TradeType.MARKET
    price: Optional[float] = None
    sl: Optional[float] = None
    tp: Optional[float] = None
    comment: Optional[str] = None
    magic: Optional[int] = None

class TradeResponse(BaseModel):
    id: str
    success: bool
    message: Optional[str] = None
    order_id: Optional[str] = None
    entry_price: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TradeUpdate(BaseModel):
    id: str
    account_id: str
    symbol: str
    side: TradeSide
    volume: float
    entry_price: float
    current_price: Optional[float] = None
    sl: Optional[float] = None
    tp: Optional[float] = None
    profit: float = 0.0
    status: str
    open_time: datetime
    close_time: Optional[datetime] = None
