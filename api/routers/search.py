"""
Search Router
Team 11 - Enterprise Web Development
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from ..db import MySQLDatabaseManager

router = APIRouter(prefix="/search", tags=["search"])

def get_db_manager():
    return MySQLDatabaseManager()

@router.get("/")
async def search_transactions(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=1000),
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Search transactions by text query."""
    try:
        results = db.search_transactions(q, limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
