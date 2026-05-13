import pandas as pd
import numpy as np
from typing import List, Optional
from datetime import datetime
import uuid

from src.asta_brain.core.interfaces.strategy import BaseStrategy, MarketData, StrategySignal, SignalAction

class RSIMomentumStrategy(BaseStrategy):
    """
    RSI Momentum Strategy: Uses RSI to identify overbought/oversold conditions and momentum.
    Signals:
    - BUY: RSI crosses above the oversold threshold.
    - SELL: RSI crosses below the overbought threshold.
    """
    
    def __init__(self, strategy_id: str = "rsi_momentum", config: Optional[dict] = None):
        super().__init__(strategy_id, config)
        self.rsi_period = self.config.get("rsi_period", 14)
        self.oversold_threshold = self.config.get("oversold_threshold", 30)
        self.overbought_threshold = self.config.get("overbought_threshold", 70)

    def calculate_rsi(self, series: pd.Series, period: int) -> pd.Series:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    async def analyze(self, market_data: MarketData) -> List[StrategySignal]:
        if not self.enabled:
            return []

        if len(market_data.ohlcv) < self.rsi_period + 1:
            return []

        df = pd.DataFrame(market_data.ohlcv)
        df['close'] = df['close'].astype(float)
        
        # Calculate RSI
        df['rsi'] = self.calculate_rsi(df['close'], self.rsi_period)
        
        if df['rsi'].isnull().all():
            return []

        # Check for signals
        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]
        
        if np.isnan(last_row['rsi']) or np.isnan(prev_row['rsi']):
            return []

        signals = []
        
        # Cross above oversold (Buy signal)
        if prev_row['rsi'] <= self.oversold_threshold and last_row['rsi'] > self.oversold_threshold:
            signals.append(StrategySignal(
                id=str(uuid.uuid4()),
                strategy_id=self.strategy_id,
                symbol=market_data.symbol,
                action=SignalAction.BUY,
                confidence=0.7,
                price=last_row['close'],
                timestamp=datetime.utcnow(),
                metadata={"rsi": last_row['rsi']}
            ))
            
        # Cross below overbought (Sell signal)
        elif prev_row['rsi'] >= self.overbought_threshold and last_row['rsi'] < self.overbought_threshold:
            signals.append(StrategySignal(
                id=str(uuid.uuid4()),
                strategy_id=self.strategy_id,
                symbol=market_data.symbol,
                action=SignalAction.SELL,
                confidence=0.7,
                price=last_row['close'],
                timestamp=datetime.utcnow(),
                metadata={"rsi": last_row['rsi']}
            ))
            
        return signals
