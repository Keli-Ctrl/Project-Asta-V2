import asyncio
import logging
from typing import Dict, Any
from src.asta_brain.infrastructure.adapters.metaapi import MetaApiManager

logger = logging.getLogger(__name__)

class MetaApiHAProxy:
    """
    Wraps MetaApiManager to provide high-availability monitoring and failover logic.
    """
    def __init__(self, manager: MetaApiManager, check_interval: int = 30):
        self.manager = manager
        self.check_interval = check_interval
        self.is_running = False
        self._monitoring_task = None
        self.connection_states: Dict[str, bool] = {}

    async def start_monitoring(self):
        self.is_running = True
        self._monitoring_task = asyncio.create_task(self._monitor_loop())
        logger.info("MetaApi HA Monitoring started.")

    async def stop_monitoring(self):
        self.is_running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
        logger.info("MetaApi HA Monitoring stopped.")

    async def _monitor_loop(self):
        while self.is_running:
            try:
                for account_id in list(self.manager.accounts.keys()):
                    connection = self.manager.accounts[account_id]
                    # Check if connection is synchronized
                    is_synchronized = connection.synchronized
                    
                    if not is_synchronized:
                        logger.warning(f"Account {account_id} lost synchronization. Attempting recovery...")
                        try:
                            # Re-initialize or wait for SDK auto-reconnect
                            # If it stays down too long, we could trigger a kill-switch
                            pass 
                        except Exception as e:
                            logger.error(f"Recovery failed for {account_id}: {e}")
                    
                    self.connection_states[account_id] = is_synchronized

                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in HA monitor loop: {e}")
                await asyncio.sleep(self.check_interval)

    async def execute_with_failover(self, func_name: str, *args, **kwargs):
        """
        Executes a manager function with a simple retry/failover logic.
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                func = getattr(self.manager, func_name)
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failover execution failed after {max_retries} attempts: {e}")
                    raise
                logger.warning(f"Attempt {attempt + 1} failed, retrying... Error: {e}")
                await asyncio.sleep(1)
