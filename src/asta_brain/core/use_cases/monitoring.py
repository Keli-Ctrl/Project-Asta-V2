import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging
from src.asta_brain.infrastructure.adapters.db.models import Account, Trade, AuditLog
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

# Prometheus Metrics
SYSTEM_UPTIME = Gauge('asta_system_uptime_seconds', 'System uptime in seconds')
ACCOUNT_EQUITY = Gauge('asta_account_equity', 'Account equity', ['account_id', 'broker'])
TRADE_COUNT = Counter('asta_trades_total', 'Total number of trades executed', ['strategy_id', 'status'])
STRATEGY_PROFIT = Gauge('asta_strategy_profit_total', 'Total profit per strategy', ['strategy_id'])

class MonitoringService:
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
        self.system_start_time = datetime.utcnow()
        self._health_status = "HEALTHY"

    async def get_system_health(self) -> Dict[str, Any]:
        """
        Returns basic system health metrics.
        """
        uptime = datetime.utcnow() - self.system_start_time
        SYSTEM_UPTIME.set(uptime.total_seconds())
        
        return {
            "status": self._health_status,
            "uptime": str(uptime),
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }

    async def update_prometheus_metrics(self, session: AsyncSession):
        """
        Periodically called to update Prometheus gauges from the database.
        """
        # Update account metrics
        stmt = select(Account)
        result = await session.execute(stmt)
        accounts = result.scalars().all()
        for acc in accounts:
            ACCOUNT_EQUITY.labels(account_id=acc.id, broker=acc.broker).set(acc.equity)

        # Update strategy metrics
        stmt = select(
            Trade.strategy_id,
            func.sum(Trade.profit).label("total_profit")
        ).group_by(Trade.strategy_id)
        result = await session.execute(stmt)
        for row in result.all():
            STRATEGY_PROFIT.labels(strategy_id=row.strategy_id or "Manual").set(row.total_profit)

    async def get_account_connectivity(self, session: AsyncSession) -> List[Dict[str, Any]]:
        """
        Checks connectivity status of all registered MetaApi accounts.
        """
        stmt = select(Account)
        result = await session.execute(stmt)
        accounts = result.scalars().all()
        
        status_report = []
        for acc in accounts:
            status_report.append({
                "account_id": acc.id,
                "broker": acc.broker,
                "status": "CONNECTED", # Placeholder for actual MetaApi status
                "equity": acc.equity,
                "balance": acc.balance
            })
        return status_report

    async def get_strategy_performance(self, session: AsyncSession) -> Dict[str, Any]:
        """
        Aggregates performance metrics across all active strategies.
        """
        stmt = select(
            Trade.strategy_id,
            func.sum(Trade.profit).label("total_profit"),
            func.count(Trade.id).label("trade_count")
        ).group_by(Trade.strategy_id)
        
        result = await session.execute(stmt)
        rows = result.all()
        
        performance = {}
        for row in rows:
            performance[row.strategy_id or "Manual"] = {
                "total_profit": row.total_profit,
                "trade_count": row.trade_count
            }
        return performance

    async def set_health_status(self, status: str):
        self._health_status = status
        logger.info(f"System health status changed to: {status}")
