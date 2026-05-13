import asyncio
import os
import sys
from datetime import datetime, timedelta
import random
import uuid
from typing import List, Dict, Any
from unittest.mock import MagicMock, AsyncMock

# Ensure imports work regardless of how script is called
project_root = "/home/team/shared/project-asta"
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

# MOCKING METAAPI SDK BEFORE IMPORTS
m = MagicMock()
sys.modules["metaapi_cloud_sdk"] = m
sys.modules["metaapi_cloud_sdk.clients"] = MagicMock()
sys.modules["metaapi_cloud_sdk.clients.metaapi"] = MagicMock()
sys.modules["metaapi_cloud_sdk.clients.metaapi.metatrader_account_model"] = MagicMock()

class MockRpcConnection:
    async def connect(self): pass
    async def wait_synchronized(self): pass
    async def create_market_order(self, symbol, side, volume, sl, tp, options):
        from loguru import logger
        logger.info(f"MOCK EXECUTION: {side} {volume} {symbol} at market price")
        return {'orderId': str(random.randint(100000, 999999)), 'price': 1.1050}
    async def close(self): pass
    async def get_positions(self): return []

class MockStreamingConnection:
    async def connect(self): pass
    async def wait_synchronized(self): pass
    def add_terminal_state_listener(self, listener): pass
    async def subscribe_to_market_data(self, symbol): pass
    async def close(self): pass

class MockAccount:
    def __init__(self, account_id):
        self.id = account_id
        self.state = 'DEPLOYED'
    async def deploy(self): pass
    async def wait_connected(self): pass
    def get_rpc_connection(self): return MockRpcConnection()
    def get_streaming_connection(self): return MockStreamingConnection()

class MockMetaApi:
    def __init__(self, token):
        self.metatrader_account_api = MagicMock()
        self.metatrader_account_api.get_account = AsyncMock(side_effect=lambda aid: MockAccount(aid))

m.MetaApi = MockMetaApi

# Now import system components
from loguru import logger
from asta_brain.infrastructure.adapters.metaapi import MetaApiManager
from asta_brain.strategies.registry import StrategyRegistry
from asta_brain.strategies.ema_trend import EMATrendStrategy
from asta_brain.strategies.rsi_momentum import RSIMomentumStrategy
from asta_brain.risk.manager import RiskManager
from asta_brain.ai.reasoning import AIReasoningLayer
from src.asta_brain.core.interfaces.strategy import MarketData, SignalAction
from asta_brain.infrastructure.schemas.market import OHLCV
from asta_brain.infrastructure.schemas.trade import TradeRequest, TradeSide, TradeType

async def run_integration_demo():
    logger.remove()
    logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")
    
    logger.info("==========================================================")
    logger.info("PROJECT ASTA: END-TO-END SYSTEM INTEGRATION DEMO")
    logger.info("==========================================================")

    # 1. Initialize MetaApi Manager (Mocked)
    logger.info("Step 1: Initializing MetaApi Manager...")
    meta_manager = MetaApiManager(token="mock_token")
    account_id = "mock_account_123"
    await meta_manager.add_account(account_id)

    # 2. Register Strategies
    logger.info("Step 2: Registering strategies in Registry...")
    registry = StrategyRegistry()
    registry.register(EMATrendStrategy(config={"fast_period": 5, "slow_period": 10}))
    registry.register(RSIMomentumStrategy(config={"rsi_period": 14}))
    logger.info(f"Registered strategies: {registry.list_strategies()}")

    # 3. Setup Risk Manager
    logger.info("Step 3: Initializing Risk Manager...")
    risk_manager = RiskManager(config={
        "max_exposure_per_symbol": 0.05, 
        "default_lot_size": 0.1,
        "max_drawdraw_limit": 0.1
    })

    # 4. Setup AI Reasoning Layer
    logger.info("Step 4: Initializing AI Reasoning Layer (Anthropic Claude)...")
    # Note: AI Layer will return default reasoning if API key is not present
    ai_layer = AIReasoningLayer()

    # 5. Simulate Market Data Stream (OHLCV)
    symbol = "EURUSD"
    logger.info(f"Step 5: Simulating market data stream for {symbol}...")
    
    # Generate mock OHLCV history
    ohlcv_history: List[Dict[str, Any]] = []
    base_price = 1.1000
    for i in range(100):
        # Create a clearer trend reversal
        if i < 70:
            base_price -= 0.0001 # Long steady downtrend
        elif i < 85:
            base_price += 0.0008 # Sharp spike up to trigger RSI overbought and EMA crossover
        else:
            base_price -= 0.0004 # Pullback to trigger RSI exit or SELL signal

        ohlcv_history.append({
            "symbol": symbol,
            "timeframe": "M1",
            "time": datetime.utcnow() - timedelta(minutes=100-i),
            "open": base_price,
            "high": base_price + 0.0002,
            "low": base_price - 0.0002,
            "close": base_price + random.uniform(-0.0001, 0.0001),
            "volume": 100.0
        })

    # 6. Main Execution Cycle
    logger.info("Step 6: Starting execution cycle...")
    
    # We will simulate the last 20 bars of the "stream" to find a signal
    found_any_signal = False
    for i in range(80, 101):
        market_data = MarketData(
            symbol=symbol,
            timeframe="M1",
            ohlcv=ohlcv_history[:i]
        )

        # 6.1 Trigger Strategy Analysis
        signals = await registry.run_all(market_data)
        if signals:
            found_any_signal = True
            logger.info(f"Iteration {i}: Strategies generated {len(signals)} signals.")

            for signal in signals:
                logger.info(f"--- Processing Signal: {signal.strategy_id} ---")
                logger.info(f"Action: {signal.action.upper()} | Confidence: {signal.confidence}")

                # 6.2 AI Reasoning Layer
                logger.info("Consulting AI Reasoning Layer for market context validation...")
                recent_ohlcv = [OHLCV(**d) for d in ohlcv_history[i-10:i]]
                side = TradeSide.BUY if signal.action == SignalAction.BUY else TradeSide.SELL
                
                ai_result = await ai_layer.analyze_signal(
                    symbol=symbol,
                    side=side,
                    market_context={"market_regime": "volatile", "news_impact": "none"},
                    recent_ohlcv=recent_ohlcv
                )
                
                # Apply AI Confidence Multiplier
                final_confidence = signal.confidence * ai_result['confidence_multiplier']
                logger.info(f"AI Reasoning: {ai_result['reasoning']}")
                logger.info(f"Final Adjusted Confidence: {final_confidence:.2f}")

                # 6.3 Risk Management Validation
                if final_confidence >= 0.5:
                    logger.info("Confidence threshold met. Validating with RiskManager...")
                    trade_request = TradeRequest(
                        account_id=account_id,
                        symbol=symbol,
                        side=side,
                        volume=risk_manager.calculate_static_size(symbol),
                        type=TradeType.MARKET,
                        comment=f"Asta Demo: {signal.strategy_id}",
                        magic=20240512
                    )
                    
                    account_summary = {"balance": 10000.0, "equity": 10000.0}
                    is_valid, reason = await risk_manager.validate_trade(trade_request, account_summary)
                    
                    if is_valid:
                        logger.info("Risk validation PASSED.")
                        # 6.4 Execution via Execution Bridge
                        logger.info(f"Executing {side.upper()} order via MetaApi Execution Bridge...")
                        response = await meta_manager.execute_market_order(trade_request)
                        
                        if response.success:
                            logger.success(f"TRADE EXECUTED SUCCESSFULLY!")
                            logger.info(f"Order ID: {response.order_id} | Fill Price: {response.entry_price}")
                        else:
                            logger.error(f"Execution Failed: {response.message}")
                    else:
                        logger.warning(f"Risk validation FAILED: {reason}")
                else:
                    logger.warning(f"Signal REJECTED: Final confidence {final_confidence:.2f} below threshold (0.5)")
            
            # Stop after first successful demonstration of signals
            break
    
    if not found_any_signal:
        logger.warning("No signals were generated during the simulated stream.")

    # 7. Shutdown
    logger.info("Step 7: Shutting down connections...")
    await meta_manager.shutdown()
    logger.info("==========================================================")
    logger.info("DEMO COMPLETED SUCCESSFULLY")
    logger.info("==========================================================")

if __name__ == "__main__":
    try:
        asyncio.run(run_integration_demo())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.exception(f"Demo failed with error: {e}")
