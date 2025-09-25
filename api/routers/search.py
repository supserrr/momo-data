"""
Search Router
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from ..db import MySQLDatabaseManager
from ..auth import get_current_user

router = APIRouter(prefix="/search", tags=["search"])

def get_db_manager():
    return MySQLDatabaseManager()

@router.get("/")
async def search_transactions(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=1000),
    db: MySQLDatabaseManager = Depends(get_db_manager),
    current_user: str = Depends(get_current_user)
):
    """Search transactions by text query."""
    try:
        results = db.search_transactions(q, limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
