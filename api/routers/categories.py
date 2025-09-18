"""
Categories Router
Team 11 - Enterprise Web Development
"""

from fastapi import APIRouter, Depends, HTTPException
from ..db import MySQLDatabaseManager

router = APIRouter(prefix="/categories", tags=["categories"])

def get_db_manager():
    return MySQLDatabaseManager()

@router.get("/")
async def get_categories(
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Get category statistics."""
    try:
        categories = db.get_category_stats()
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
