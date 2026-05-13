from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Enum, JSON, BigInteger, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum

class Base(DeclarativeBase):
    pass

class AccountType(str, enum.Enum):
    DEMO = "demo"
    LIVE = "live"

class TradeStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    CANCELED = "canceled"
    PENDING = "pending"

class TradeSide(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"

class SignalAction(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"
    CLOSE = "close"
    HOLD = "hold"

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    broker: Mapped[str] = mapped_column(String(100))
    login: Mapped[str] = mapped_column(String(50))
    account_type: Mapped[AccountType] = mapped_column(Enum(AccountType))
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    equity: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    leverage: Mapped[int] = mapped_column(Integer, default=1)
    
    trades: Mapped[List["Trade"]] = relationship(back_populates="account")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    symbol: Mapped[str] = mapped_column(String(20))
    side: Mapped[TradeSide] = mapped_column(Enum(TradeSide))
    volume: Mapped[float] = mapped_column(Float)
    entry_price: Mapped[float] = mapped_column(Float)
    exit_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sl: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[TradeStatus] = mapped_column(Enum(TradeStatus))
    strategy_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    signal_id: Mapped[Optional[str]] = mapped_column(ForeignKey("signals.id"), nullable=True)
    
    open_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    close_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    commission: Mapped[float] = mapped_column(Float, default=0.0)
    swap: Mapped[float] = mapped_column(Float, default=0.0)
    profit: Mapped[float] = mapped_column(Float, default=0.0)
    
    account: Mapped["Account"] = relationship(back_populates="trades")
    signal: Mapped[Optional["Signal"]] = relationship(back_populates="trades")

class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    strategy_id: Mapped[str] = mapped_column(String(100))
    symbol: Mapped[str] = mapped_column(String(20))
    action: Mapped[SignalAction] = mapped_column(Enum(SignalAction))
    confidence: Mapped[float] = mapped_column(Float) # 0.0 to 1.0
    ai_reasoning: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    trades: Mapped[List["Trade"]] = relationship(back_populates="signal")

class OHLCV(Base):
    __tablename__ = "ohlcv_data"

    # For TimescaleDB, we usually have a composite primary key or a specific time column.
    # SQLAlchemy needs a primary key. In TimescaleDB, time and symbol are often the composite PK.
    time: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    timeframe: Mapped[str] = mapped_column(String(10), primary_key=True)
    
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[float] = mapped_column(Float)

    __table_args__ = (
        Index("ix_ohlcv_time_symbol", "time", "symbol"),
    )

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    level: Mapped[str] = mapped_column(String(20)) # INFO, WARNING, ERROR, CRITICAL
    module: Mapped[str] = mapped_column(String(100))
    message: Mapped[str] = mapped_column(String(1000))
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
