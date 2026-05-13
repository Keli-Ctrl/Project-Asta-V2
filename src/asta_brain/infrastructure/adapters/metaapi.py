import asyncio
from typing import Dict, List, Optional, Callable, Any
from metaapi_cloud_sdk import MetaApi
from metaapi_cloud_sdk.clients.metaapi.metatrader_account_model import MetatraderAccountModel
from loguru import logger
from datetime import datetime

from asta_brain.infrastructure.schemas.market import Tick, OHLCV
from asta_brain.infrastructure.schemas.trade import TradeRequest, TradeResponse, TradeUpdate, TradeSide

class MetaApiManager:
    """
    Institutional-grade MetaApi Manager.
    Handles multiple accounts, streaming data, and trade orchestration.
    """
    def __init__(self, token: str):
        self.api = MetaApi(token)
        self.accounts: Dict[str, Any] = {} # account_id -> rpc_connection
        self.streaming_connections: Dict[str, Any] = {} # account_id -> streaming_connection
        self.price_callbacks: Dict[str, List[Callable]] = {} # symbol -> callbacks
        self.trade_callbacks: List[Callable] = []

    async def add_account(self, account_id: str):
        """
        Adds and synchronizes a MetaTrader account.
        """
        try:
            account = await self.api.metatrader_account_api.get_account(account_id)
            if account.state != 'DEPLOYED':
                logger.info(f"Deploying account {account_id}...")
                await account.deploy()
            
            await account.wait_connected()
            
            # RPC Connection for commands
            connection = account.get_rpc_connection()
            await connection.connect()
            await connection.wait_synchronized()
            self.accounts[account_id] = connection
            
            # Streaming Connection for events
            streaming_connection = account.get_streaming_connection()
            await streaming_connection.connect()
            await streaming_connection.wait_synchronized()
            self.streaming_connections[account_id] = streaming_connection
            
            # Register listeners
            self._setup_listeners(account_id, streaming_connection)
            
            logger.info(f"Account {account_id} fully synchronized and ready.")
            return account
        except Exception as e:
            logger.error(f"Failed to add account {account_id}: {e}")
            raise

    def _setup_listeners(self, account_id: str, streaming_connection: Any):
        """
        Sets up terminal and synchronization listeners.
        """
        class TerminalListener:
            def __init__(self, manager: 'MetaApiManager', acc_id: str):
                self.manager = manager
                self.acc_id = acc_id

            async def on_symbol_price(self, instance_index: str, price: Any):
                symbol = price['symbol']
                tick = Tick(
                    symbol=symbol,
                    ask=price['ask'],
                    bid=price['bid'],
                    broker_time=price['time']
                )
                if symbol in self.manager.price_callbacks:
                    for cb in self.manager.price_callbacks[symbol]:
                        try:
                            await cb(tick)
                        except Exception as e:
                            logger.error(f"Error in price callback for {symbol}: {e}")

            async def on_candle(self, instance_index: str, candle: Any):
                # Handle OHLCV updates
                pass

            async def on_order_filled(self, instance_index: str, order: Any):
                logger.info(f"Order filled on {self.acc_id}: {order['id']}")
                # Trigger trade callbacks if needed

            async def on_position_updated(self, instance_index: str, position: Any):
                logger.debug(f"Position updated on {self.acc_id}: {position['id']}")

        listener = TerminalListener(self, account_id)
        streaming_connection.add_terminal_state_listener(listener)

    async def subscribe_symbols(self, account_id: str, symbols: List[str], callback: Callable):
        """
        Subscribes to multiple symbols with a callback.
        """
        streaming_connection = self.streaming_connections.get(account_id)
        if not streaming_connection:
            raise ValueError(f"Account {account_id} streaming connection not found")

        for symbol in symbols:
            if symbol not in self.price_callbacks:
                self.price_callbacks[symbol] = []
            self.price_callbacks[symbol].append(callback)
            await streaming_connection.subscribe_to_market_data(symbol)
            logger.info(f"Subscribed to {symbol} on {account_id}")

    async def execute_market_order(self, request: TradeRequest) -> TradeResponse:
        """
        Executes a market order with SL/TP.
        """
        connection = self.accounts.get(request.account_id)
        if not connection:
            return TradeResponse(id="0", success=False, message="Account connection missing")

        try:
            # MetaApi SDK uses uppercase for side: BUY, SELL
            result = await connection.create_market_order(
                request.symbol,
                request.side.upper(),
                request.volume,
                request.sl,
                request.tp,
                {'comment': request.comment, 'magic': request.magic} if request.comment or request.magic else None
            )
            
            logger.info(f"Market order executed: {result}")
            return TradeResponse(
                id=result['orderId'],
                success=True,
                order_id=result['orderId'],
                entry_price=result.get('price'),
                message="Success"
            )
        except Exception as e:
            logger.error(f"Market order failed: {e}")
            return TradeResponse(id="0", success=False, message=str(e))

    async def close_position(self, account_id: str, position_id: str) -> bool:
        """
        Closes an open position.
        """
        connection = self.accounts.get(account_id)
        if not connection:
            return False
        try:
            await connection.close_position(position_id)
            logger.info(f"Closed position {position_id} on {account_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to close position {position_id}: {e}")
            return False

    async def close_all_positions(self, account_id: str):
        """
        Emergency kill-switch: closes all positions for an account.
        """
        connection = self.accounts.get(account_id)
        if not connection:
            return
        try:
            positions = await connection.get_positions()
            for p in positions:
                await connection.close_position(p['id'])
            logger.warning(f"All positions closed for account {account_id}")
        except Exception as e:
            logger.error(f"Emergency close failed for {account_id}: {e}")

    async def shutdown(self):
        """
        Graceful shutdown of all connections.
        """
        for acc_id, conn in self.accounts.items():
            await conn.close()
        for acc_id, conn in self.streaming_connections.items():
            await conn.close()
        logger.info("MetaApi Manager connections closed.")
