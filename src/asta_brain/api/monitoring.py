from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
import logging

from src.asta_brain.core.use_cases.monitoring import MonitoringService
from src.asta_brain.core.use_cases.audit_trail import AuditTrailService
# Placeholder for DB dependency
# from src.asta_brain.api.dependencies import get_db

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

# In a real app, this would be injected or retrieved from app state
monitoring_service = MonitoringService(db_session_factory=None)
audit_trail_service = AuditTrailService(db_session_factory=None)

@router.get("/health")
async def get_health():
    """
    Returns comprehensive system health status.
    """
    return await monitoring_service.get_system_health()

@router.get("/accounts")
async def get_accounts_status(db: AsyncSession = None):
    """
    Returns connectivity and balance status for all trading accounts.
    """
    # This would normally use the 'db' session dependency
    return await monitoring_service.get_account_connectivity(db)

@router.get("/strategies")
async def get_strategies_performance(db: AsyncSession = None):
    """
    Returns performance metrics for all active strategies.
    """
    return await monitoring_service.get_strategy_performance(db)

@router.get("/logs")
async def get_audit_logs(limit: int = 50, db: AsyncSession = None):
    """
    Returns the most recent system audit logs.
    """
    return await audit_trail_service.get_recent_logs(db, limit)
