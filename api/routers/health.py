"""
Health Router
Team 11 - Enterprise Web Development
"""

from fastapi import APIRouter, Depends, HTTPException
from ..db import MySQLDatabaseManager

router = APIRouter(prefix="/health", tags=["health"])

def get_db_manager():
    return MySQLDatabaseManager()

@router.get("/")
async def health_check(
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Health check endpoint."""
    try:
        # Test database connection
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "message": "All systems operational"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")
