"""
ETL Router
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from ..db import MySQLDatabaseManager

router = APIRouter(prefix="/etl", tags=["etl"])

def get_db_manager():
    return MySQLDatabaseManager()

@router.get("/logs")
async def get_etl_logs(
    limit: int = Query(50, ge=1, le=1000),
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Get recent ETL process logs."""
    try:
        logs = db.get_etl_logs(limit)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
