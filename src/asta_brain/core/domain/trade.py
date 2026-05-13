from pydantic import BaseModel
from typing import Optional
from enum import Enum

class TradeSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class TradeRequest(BaseModel):
    symbol: str
    side: TradeSide
    volume: float
    price: Optional[float] = None
    sl: Optional[float] = None
    tp: Optional[float] = None
    strategy_id: Optional[str] = None
    signal_id: Optional[str] = None
    account_id: str

class TradeResponse(BaseModel):
    success: bool
    order_id: Optional[str] = None
    error_message: Optional[str] = None
    request: TradeRequest
