"""
Categories Router
"""

from fastapi import APIRouter, Depends, HTTPException
from ..db import MySQLDatabaseManager
from ..auth import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])

def get_db_manager():
    return MySQLDatabaseManager()

@router.get("/")
async def get_categories(
    db: MySQLDatabaseManager = Depends(get_db_manager),
    current_user: str = Depends(get_current_user)
):
    """Get category statistics."""
    try:
        categories = db.get_category_stats()
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
