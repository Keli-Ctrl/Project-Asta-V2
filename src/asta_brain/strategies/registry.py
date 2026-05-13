from typing import Dict, List, Type
from src.asta_brain.core.interfaces.strategy import BaseStrategy, MarketData, StrategySignal

class StrategyRegistry:
    def __init__(self):
        self._strategies: Dict[str, BaseStrategy] = {}
        self._weights: Dict[str, float] = {}

    def register(self, strategy: BaseStrategy, weight: float = 1.0):
        self._strategies[strategy.strategy_id] = strategy
        self._weights[strategy.strategy_id] = weight

    def unregister(self, strategy_id: str):
        if strategy_id in self._strategies:
            del self._strategies[strategy_id]
            del self._weights[strategy_id]

    def set_weight(self, strategy_id: str, weight: float):
        if strategy_id in self._weights:
            self._weights[strategy_id] = weight

    def get_strategy(self, strategy_id: str) -> BaseStrategy:
        return self._strategies.get(strategy_id)

    def list_strategies(self) -> List[str]:
        return list(self._strategies.keys())

    async def run_all(self, market_data: MarketData) -> List[StrategySignal]:
        all_signals = []
        for strategy_id, strategy in self._strategies.items():
            if strategy.enabled:
                signals = await strategy.analyze(market_data)
                # Apply weights to confidence
                for signal in signals:
                    signal.confidence *= self._weights.get(strategy_id, 1.0)
                all_signals.extend(signals)
        return all_signals

# Global instance
registry = StrategyRegistry()
