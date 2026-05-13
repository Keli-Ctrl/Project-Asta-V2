from typing import Optional, Dict
import logging
from src.asta_brain.core.domain.trade import TradeRequest

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.kill_switch_engaged = False
        self.max_exposure_per_symbol = self.config.get("max_exposure_per_symbol", 0.1) # 10% of equity
        self.max_drawdown_limit = self.config.get("max_drawdown_limit", 0.2) # 20%
        self.default_lot_size = self.config.get("default_lot_size", 0.01)

    def engage_kill_switch(self):
        logger.warning("RiskManager: Engagement of Global Kill-switch!")
        self.kill_switch_engaged = True

    def disengage_kill_switch(self):
        logger.info("RiskManager: Disengagement of Global Kill-switch.")
        self.kill_switch_engaged = False

    async def validate_trade(self, request: TradeRequest, account_summary: dict) -> (bool, str):
        """
        Validates a trade request against risk parameters.
        Returns (True, "") if valid, (False, reason) otherwise.
        """
        if self.kill_switch_engaged:
            return False, "Global kill-switch is engaged."

        equity = account_summary.get("equity", 0)
        balance = account_summary.get("balance", 0)
        
        if equity <= 0:
            return False, "Insufficient equity."

        # Check max drawdown
        if balance > 0 and (balance - equity) / balance > self.max_drawdown_limit:
            self.engage_kill_switch()
            return False, f"Max drawdown limit exceeded: {(balance - equity) / balance:.2%}"

        # Static position sizing check (simple for now)
        # In a real system, we'd check contract size, margin requirements, etc.
        if request.volume <= 0:
            return False, "Invalid volume size."

        # Check exposure (dummy implementation for now)
        # exposure = (request.volume * current_price) / equity
        # if exposure > self.max_exposure_per_symbol:
        #     return False, f"Exposure too high for {request.symbol}"

        return True, ""

    def calculate_static_size(self, symbol: str) -> float:
        """
        Returns a static lot size.
        """
        return self.default_lot_size

    def wrap_execution(self, execution_func):
        """
        A decorator/wrapper to ensure risk validation before execution.
        """
        async def wrapper(request: TradeRequest, account_summary: dict, *args, **kwargs):
            is_valid, reason = await self.validate_trade(request, account_summary)
            if not is_valid:
                logger.error(f"Trade validation failed: {reason}")
                return {"success": False, "error": reason}
            
            return await execution_func(request, *args, **kwargs)
        
        return wrapper

# Global instance
risk_manager = RiskManager()
