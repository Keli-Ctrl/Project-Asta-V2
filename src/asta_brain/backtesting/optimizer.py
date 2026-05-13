import asyncio
import uuid
from typing import List, Dict, Any, Type, Callable
import pandas as pd
import itertools
from src.asta_brain.core.interfaces.strategy import BaseStrategy
from src.asta_brain.backtesting.engine import BacktestingEngine, BacktestResult

class ParameterOptimizer:
    def __init__(self, strategy_class: Type[BaseStrategy], data: pd.DataFrame, engine: BacktestingEngine):
        self.strategy_class = strategy_class
        self.data = data
        self.engine = engine

    async def grid_search(self, param_grid: Dict[str, List[Any]]) -> List[BacktestResult]:
        """
        Runs backtests for all combinations of parameters in the grid.
        """
        keys = param_grid.keys()
        values = param_grid.values()
        combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
        
        results = []
        for params in combinations:
            strategy = self.strategy_class(strategy_id=f"opt_{uuid.uuid4().hex[:8]}", config=params)
            result = await self.engine.run(strategy, self.data)
            results.append(result)
            
        return results

    async def walk_forward(self, param_grid: Dict[str, List[Any]], train_size: int, test_size: int) -> List[BacktestResult]:
        """
        Performs walk-forward optimization.
        """
        # Divide data into rolling windows
        total_len = len(self.data)
        results = []
        
        start = 0
        while start + train_size + test_size <= total_len:
            train_data = self.data.iloc[start : start + train_size]
            test_data = self.data.iloc[start + train_size : start + train_size + test_size]
            
            # 1. Find best params on train_data
            best_result = None
            keys = param_grid.keys()
            values = param_grid.values()
            for v in itertools.product(*values):
                params = dict(zip(keys, v))
                strategy = self.strategy_class(strategy_id="temp", config=params)
                res = await self.engine.run(strategy, train_data)
                if best_result is None or res.final_balance > best_result.final_balance:
                    best_result = res
                    best_params = params
            
            # 2. Run best params on test_data
            strategy = self.strategy_class(strategy_id=f"wf_{start}", config=best_params)
            test_res = await self.engine.run(strategy, test_data)
            results.append(test_res)
            
            start += test_size
            
        return results

    def monte_carlo(self, result: BacktestResult, simulations: int = 1000) -> Dict[str, Any]:
        """
        Runs Monte Carlo simulations by shuffling trade outcomes.
        """
        import numpy as np
        
        trade_profits = [t.profit for t in result.trades]
        if not trade_profits:
            return {}
            
        final_balances = []
        max_drawdowns = []
        
        for _ in range(simulations):
            shuffled = np.random.choice(trade_profits, size=len(trade_profits), replace=True)
            equity = [result.initial_balance]
            curr = result.initial_balance
            for p in shuffled:
                curr += p
                equity.append(curr)
            
            final_balances.append(curr)
            
            # Calculate DD
            peak = result.initial_balance
            mdd = 0
            for v in equity:
                if v > peak: peak = v
                dd = (peak - v) / peak
                if dd > mdd: mdd = dd
            max_drawdowns.append(mdd)
            
        return {
            "avg_final_balance": sum(final_balances) / simulations,
            "median_final_balance": sorted(final_balances)[simulations // 2],
            "95th_percentile_dd": sorted(max_drawdowns)[int(simulations * 0.95)],
            "risk_of_ruin": len([b for b in final_balances if b <= 0]) / simulations
        }
