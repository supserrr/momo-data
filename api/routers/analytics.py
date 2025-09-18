"""
Analytics Router
Team 11 - Enterprise Web Development
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from ..db import MySQLDatabaseManager

router = APIRouter(prefix="/analytics", tags=["analytics"])

def get_db_manager():
    return MySQLDatabaseManager()

@router.get("/")
async def get_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Get analytics data for date range."""
    try:
        analytics_data = db.get_analytics(start_date, end_date)
        return analytics_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monthly")
async def get_monthly_data(
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Get monthly transaction data."""
    try:
        monthly_data = db.get_monthly_transaction_data()
        return monthly_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transaction-types-by-amount")
async def get_transaction_types_by_amount(
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Get transaction types by amount for charts."""
    try:
        transaction_types = db.get_transaction_types_by_amount()
        return transaction_types
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
