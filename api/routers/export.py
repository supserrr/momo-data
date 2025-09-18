"""
Export Router
"""

from fastapi import APIRouter, Depends, HTTPException
from ..db import MySQLDatabaseManager

router = APIRouter(prefix="/export", tags=["export"])

def get_db_manager():
    return MySQLDatabaseManager()

@router.get("/stats")
async def get_database_stats(
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Get database statistics."""
    try:
        stats = db.get_database_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
