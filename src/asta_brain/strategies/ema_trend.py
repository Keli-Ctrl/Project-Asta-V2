import pandas as pd
import numpy as np
from typing import List, Optional
from datetime import datetime
import uuid

from src.asta_brain.core.interfaces.strategy import BaseStrategy, MarketData, StrategySignal, SignalAction

class EMATrendStrategy(BaseStrategy):
    """
    EMA Trend Strategy: Uses fast and slow EMAs to identify trend direction.
    Signals:
    - BUY: Fast EMA crosses above Slow EMA.
    - SELL: Fast EMA crosses below Slow EMA.
    """
    
    def __init__(self, strategy_id: str = "ema_trend", config: Optional[dict] = None):
        super().__init__(strategy_id, config)
        self.fast_period = self.config.get("fast_period", 20)
        self.slow_period = self.config.get("slow_period", 50)

    async def analyze(self, market_data: MarketData) -> List[StrategySignal]:
        if not self.enabled:
            return []

        if len(market_data.ohlcv) < self.slow_period + 1:
            return []

        df = pd.DataFrame(market_data.ohlcv)
        df['close'] = df['close'].astype(float)
        
        # Calculate EMAs
        df['ema_fast'] = df['close'].ewm(span=self.fast_period, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=self.slow_period, adjust=False).mean()
        
        # Check for crossover
        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]
        
        signals = []
        
        # Crossover Up (Buy)
        if prev_row['ema_fast'] <= prev_row['ema_slow'] and last_row['ema_fast'] > last_row['ema_slow']:
            signals.append(StrategySignal(
                id=str(uuid.uuid4()),
                strategy_id=self.strategy_id,
                symbol=market_data.symbol,
                action=SignalAction.BUY,
                confidence=0.8,
                price=last_row['close'],
                timestamp=datetime.utcnow(),
                metadata={"ema_fast": last_row['ema_fast'], "ema_slow": last_row['ema_slow']}
            ))
            
        # Crossover Down (Sell)
        elif prev_row['ema_fast'] >= prev_row['ema_slow'] and last_row['ema_fast'] < last_row['ema_slow']:
            signals.append(StrategySignal(
                id=str(uuid.uuid4()),
                strategy_id=self.strategy_id,
                symbol=market_data.symbol,
                action=SignalAction.SELL,
                confidence=0.8,
                price=last_row['close'],
                timestamp=datetime.utcnow(),
                metadata={"ema_fast": last_row['ema_fast'], "ema_slow": last_row['ema_slow']}
            ))
            
        return signals
