import asyncio
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Type
import pandas as pd
from src.asta_brain.core.interfaces.strategy import BaseStrategy, MarketData, StrategySignal
from src.asta_brain.core.domain.trade import TradeSide
from src.asta_brain.backtesting.models import BacktestTrade, BacktestResult

class BacktestingEngine:
    def __init__(self, initial_balance: float = 10000.0, commission: float = 0.0, spread: float = 0.0001, slippage: float = 0.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.commission = commission
        self.spread = spread
        self.slippage = slippage
        self.trades: List[BacktestTrade] = []
        self.equity_curve: List[float] = [initial_balance]

    async def run(self, strategy: BaseStrategy, data: pd.DataFrame) -> BacktestResult:
        """
        Replays historical OHLCV data and executes strategy analysis.
        Expects data to be a pandas DataFrame with columns: ['time', 'open', 'high', 'low', 'close', 'volume']
        """
        self.balance = self.initial_balance
        self.trades = []
        self.equity_curve = [self.initial_balance]
        
        # Sort data by time
        data = data.sort_values('time')
        
        # Current active trades
        active_trades: List[BacktestTrade] = []

        for index, row in data.iterrows():
            current_time = row['time']
            current_close = row['close']
            
            # 1. Update active trades (SL/TP check)
            for trade in active_trades[:]:
                if trade.side == TradeSide.BUY:
                    if trade.sl and row['low'] <= trade.sl:
                        self._close_trade(trade, trade.sl, current_time)
                        active_trades.remove(trade)
                    elif trade.tp and row['high'] >= trade.tp:
                        self._close_trade(trade, trade.tp, current_time)
                        active_trades.remove(trade)
                elif trade.side == TradeSide.SELL:
                    if trade.sl and row['high'] >= trade.sl:
                        self._close_trade(trade, trade.sl, current_time)
                        active_trades.remove(trade)
                    elif trade.tp and row['low'] <= trade.tp:
                        self._close_trade(trade, trade.tp, current_time)
                        active_trades.remove(trade)

            # 2. Strategy Analysis
            # In a real backtest, we might pass a window of historical data
            market_data = MarketData(
                symbol=data.iloc[0]['symbol'] if 'symbol' in data.columns else "UNKNOWN",
                timeframe="D1", # Placeholder
                ohlcv=data.iloc[:index+1].tail(100).to_dict('records'), # Last 100 bars
                timestamp=current_time
            )
            
            signals = await strategy.analyze(market_data)
            
            # 3. Execution (Market orders for now)
            for signal in signals:
                if signal.action == "buy":
                    entry_price = current_close + self.spread + self.slippage
                    self._open_trade(signal, entry_price, current_time, TradeSide.BUY, active_trades)
                elif signal.action == "sell":
                    entry_price = current_close - self.spread - self.slippage
                    self._open_trade(signal, entry_price, current_time, TradeSide.SELL, active_trades)
                elif signal.action == "close":
                    # Close all trades for this symbol
                    for trade in active_trades[:]:
                        self._close_trade(trade, current_close, current_time)
                        active_trades.remove(trade)

            # 4. Update equity curve
            unrealized_profit = sum([self._calculate_profit(t, current_close) for t in active_trades])
            self.equity_curve.append(self.balance + unrealized_profit)

        # Close any remaining trades at the end
        if active_trades:
            last_price = data.iloc[-1]['close']
            last_time = data.iloc[-1]['time']
            for trade in active_trades[:]:
                self._close_trade(trade, last_price, last_time)
                active_trades.remove(trade)

        return self._calculate_results(strategy.strategy_id, data)

    def _open_trade(self, signal: StrategySignal, price: float, time: datetime, side: TradeSide, active_trades: List[BacktestTrade]):
        # Simple volume calculation (fixed for now, should use RiskManager)
        volume = 0.01 
        
        trade = BacktestTrade(
            id=str(uuid.uuid4()),
            symbol=signal.symbol,
            side=side,
            entry_price=price,
            volume=volume,
            entry_time=time,
            sl=signal.sl,
            tp=signal.tp,
            status="open"
        )
        active_trades.append(trade)
        self.trades.append(trade)
        # Apply commission at entry
        self.balance -= self.commission

    def _close_trade(self, trade: BacktestTrade, price: float, time: datetime):
        trade.exit_price = price
        trade.exit_time = time
        trade.status = "closed"
        trade.profit = self._calculate_profit(trade, price)
        self.balance += trade.profit
        # Apply commission at exit
        self.balance -= self.commission

    def _calculate_profit(self, trade: BacktestTrade, current_price: float) -> float:
        # Simplified profit calculation (assuming 1 unit = 1 currency)
        # In FX, this would depend on pip value and leverage
        if trade.side == TradeSide.BUY:
            return (current_price - trade.entry_price) * trade.volume * 100000 # Standard lot size factor
        else:
            return (trade.entry_price - current_price) * trade.volume * 100000

    def _calculate_results(self, strategy_id: str, data: pd.DataFrame) -> BacktestResult:
        total_trades = len(self.trades)
        wins = [t for t in self.trades if t.profit > 0]
        win_rate = len(wins) / total_trades if total_trades > 0 else 0
        
        gross_profit = sum([t.profit for t in wins])
        gross_loss = abs(sum([t.profit for t in self.trades if t.profit < 0]))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Max drawdown
        peak = self.initial_balance
        max_dd = 0
        for val in self.equity_curve:
            if val > peak:
                peak = val
            dd = (peak - val) / peak
            if dd > max_dd:
                max_dd = dd
        
        # Sharpe ratio (simplified, daily data assumed)
        returns = pd.Series(self.equity_curve).pct_change().dropna()
        sharpe = (returns.mean() / returns.std()) * (252**0.5) if returns.std() > 0 else 0

        return BacktestResult(
            strategy_id=strategy_id,
            start_time=data.iloc[0]['time'],
            end_time=data.iloc[-1]['time'],
            initial_balance=self.initial_balance,
            final_balance=self.balance,
            total_trades=total_trades,
            win_rate=win_rate,
            profit_factor=profit_factor,
            max_drawdown=max_dd,
            sharpe_ratio=sharpe,
            equity_curve=self.equity_curve,
            trades=self.trades
        )
