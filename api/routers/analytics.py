"""
Analytics Router
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from ..db import MySQLDatabaseManager
from ..auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])

def get_db_manager():
    return MySQLDatabaseManager()

@router.get("/")
async def get_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: MySQLDatabaseManager = Depends(get_db_manager),
    current_user: str = Depends(get_current_user)
):
    """Get analytics data for date range."""
    try:
        analytics_data = db.get_analytics(start_date, end_date)
        return analytics_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monthly")
async def get_monthly_data(
    db: MySQLDatabaseManager = Depends(get_db_manager),
    current_user: str = Depends(get_current_user)
):
    """Get monthly transaction data."""
    try:
        monthly_data = db.get_monthly_transaction_data()
        return monthly_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transaction-types-by-amount")
async def get_transaction_types_by_amount(
    db: MySQLDatabaseManager = Depends(get_db_manager),
    current_user: str = Depends(get_current_user)
):
    """Get transaction types by amount for charts."""
    try:
        transaction_types = db.get_transaction_types_by_amount()
        return transaction_types
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hourly-pattern")
async def get_hourly_pattern(
    db: MySQLDatabaseManager = Depends(get_db_manager),
    current_user: str = Depends(get_current_user)
):
    """Get hourly transaction pattern data."""
    try:
        hourly_data = db.get_hourly_pattern()
        return hourly_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/amount-distribution")
async def get_amount_distribution(
    db: MySQLDatabaseManager = Depends(get_db_manager),
    current_user: str = Depends(get_current_user)
):
    """Get amount distribution data for charts."""
    try:
        amount_data = db.get_amount_distribution()
        return amount_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
