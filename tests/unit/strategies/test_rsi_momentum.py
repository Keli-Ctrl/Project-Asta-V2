import pytest
from datetime import datetime
from src.asta_brain.strategies.rsi_momentum import RSIMomentumStrategy
from src.asta_brain.core.interfaces.strategy import MarketData, SignalAction

@pytest.mark.asyncio
async def test_rsi_momentum_buy_signal():
    # Setup data where RSI crosses above 30
    ohlcv = []
    # Drop price significantly to get RSI below 30, then recover
    prices = [100.0] * 50 + [100.0 - i * 2 for i in range(20)] + [60.0 + i * 2 for i in range(20)]
    for p in prices:
        ohlcv.append({
            "time": datetime.utcnow(),
            "open": p,
            "high": p + 0.1,
            "low": p - 0.1,
            "close": p,
            "volume": 1000
        })
    
    strategy = RSIMomentumStrategy(config={"rsi_period": 14, "oversold_threshold": 30})
    
    found_signal = False
    for i in range(30, len(ohlcv) + 1):
        market_data = MarketData(
            symbol="GBPUSD",
            timeframe="M15",
            ohlcv=ohlcv[:i]
        )
        signals = await strategy.analyze(market_data)
        if any(s.action == SignalAction.BUY for s in signals):
            found_signal = True
            break
            
    assert found_signal

@pytest.mark.asyncio
async def test_rsi_momentum_sell_signal():
    # Setup data where RSI crosses below 70
    ohlcv = []
    # Pump price to get RSI above 70, then drop
    prices = [100.0] * 50 + [100.0 + i * 2 for i in range(20)] + [140.0 - i * 2 for i in range(20)]
    for p in prices:
        ohlcv.append({
            "time": datetime.utcnow(),
            "open": p,
            "high": p + 0.1,
            "low": p - 0.1,
            "close": p,
            "volume": 1000
        })
    
    strategy = RSIMomentumStrategy(config={"rsi_period": 14, "overbought_threshold": 70})
    
    found_signal = False
    for i in range(30, len(ohlcv) + 1):
        market_data = MarketData(
            symbol="GBPUSD",
            timeframe="M15",
            ohlcv=ohlcv[:i]
        )
        signals = await strategy.analyze(market_data)
        if any(s.action == SignalAction.SELL for s in signals):
            found_signal = True
            break
            
    assert found_signal
