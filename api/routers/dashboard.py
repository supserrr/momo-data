"""
Dashboard Router
"""

from fastapi import APIRouter, Depends, HTTPException
from ..db import MySQLDatabaseManager

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

def get_db_manager():
    return MySQLDatabaseManager()

@router.get("/data")
async def get_dashboard_data(
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Get dashboard summary data."""
    try:
        dashboard_data = db.get_dashboard_data()
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
