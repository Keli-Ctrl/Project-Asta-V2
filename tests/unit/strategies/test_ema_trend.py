import pytest
from datetime import datetime
from src.asta_brain.strategies.ema_trend import EMATrendStrategy
from src.asta_brain.core.interfaces.strategy import MarketData, SignalAction

@pytest.mark.asyncio
async def test_ema_trend_buy_signal():
    # Setup data where Fast EMA (20) crosses above Slow EMA (50)
    # We want the crossover to happen at the very last bar.
    # Start price low, then increase it until they cross.
    ohlcv = []
    price = 100.0
    for i in range(200):
        if i < 150:
            price = 100.0
        else:
            price += 0.5 # Gradually increase
            
        ohlcv.append({
            "time": datetime.utcnow(),
            "open": price,
            "high": price + 0.1,
            "low": price - 0.1,
            "close": price,
            "volume": 1000
        })
    
    strategy = EMATrendStrategy(config={"fast_period": 10, "slow_period": 30})
    
    # We will iterate through the data to find the exact crossover point
    found_signal = False
    for i in range(50, 201):
        market_data = MarketData(
            symbol="EURUSD",
            timeframe="H1",
            ohlcv=ohlcv[:i]
        )
        signals = await strategy.analyze(market_data)
        if any(s.action == SignalAction.BUY for s in signals):
            found_signal = True
            break
            
    assert found_signal

@pytest.mark.asyncio
async def test_ema_trend_sell_signal():
    ohlcv = []
    price = 100.0
    for i in range(200):
        if i < 150:
            price = 100.0
        else:
            price -= 0.5 # Gradually decrease
            
        ohlcv.append({
            "time": datetime.utcnow(),
            "open": price,
            "high": price + 0.1,
            "low": price - 0.1,
            "close": price,
            "volume": 1000
        })
    
    strategy = EMATrendStrategy(config={"fast_period": 10, "slow_period": 30})
    
    found_signal = False
    for i in range(50, 201):
        market_data = MarketData(
            symbol="EURUSD",
            timeframe="H1",
            ohlcv=ohlcv[:i]
        )
        signals = await strategy.analyze(market_data)
        if any(s.action == SignalAction.SELL for s in signals):
            found_signal = True
            break
            
    assert found_signal
