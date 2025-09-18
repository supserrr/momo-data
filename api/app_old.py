"""
FastAPI Application for MoMo Data Processing
Team 11 - Enterprise Web Development
"""

import logging
import subprocess
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from .db import MySQLDatabaseManager
from .schemas import (
    Transaction, TransactionCreate, TransactionUpdate, TransactionFilters,
    DashboardData, AnalyticsData, ETLProcessLog, DatabaseStats,
    SearchQuery, ETLRunRequest, ETLRunResponse, APIResponse, ErrorResponse
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MoMo Data Processing API",
    description="API for processing and analyzing MoMo SMS transaction data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database manager
db_manager = MySQLDatabaseManager()

# Database dependency
def get_db_manager():
    return db_manager

# Mount static files for frontend
app.mount("/web", StaticFiles(directory="web"), name="web")
app.mount("/data", StaticFiles(directory="data"), name="data")

@app.get("/", response_class=FileResponse)
async def serve_frontend():
    """Serve main dashboard."""
    return FileResponse("index.html")

@app.get("/health")
async def health_check():
    """Health check."""
    try:
        stats = db_manager.get_database_stats()
        return APIResponse(
            success=True,
            message="API is healthy",
            data={"database_connected": True, "stats": stats}
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return APIResponse(
            success=False,
            message="API health check failed",
            data={"database_connected": False, "error": str(e)}
        )

# Transaction endpoints
@app.get("/api/transactions", response_model=List[Transaction])
async def get_transactions(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Get transactions with filters."""
    try:
        transactions = db.get_transactions(
            limit=limit,
            offset=offset,
            category=category,
            status=status,
            phone=phone
        )
        return transactions
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction(
    transaction_id: int,
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Get specific transaction by ID."""
    try:
        transaction = db.get_transaction_by_id(transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction {transaction_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard-data", response_model=DashboardData)
async def get_dashboard_data(db: MySQLDatabaseManager = Depends(get_db_manager)):
    """Get dashboard data."""
    try:
        data = db.get_dashboard_data()
        return DashboardData(**data)
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics", response_model=AnalyticsData)
async def get_analytics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Get analytics data."""
    try:
        data = db.get_analytics(start_date=start_date, end_date=end_date)
        return AnalyticsData(**data)
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories", response_model=List[dict])
async def get_categories(db: MySQLDatabaseManager = Depends(get_db_manager)):
    """Get category stats."""
    try:
        categories = db.get_category_stats()
        return categories
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monthly-transactions")
async def get_monthly_transactions(db: MySQLDatabaseManager = Depends(get_db_manager)):
    """Get monthly transactions for volume chart."""
    try:
        monthly_data = db.get_monthly_transaction_data()
        return monthly_data
    except Exception as e:
        logger.error(f"Error getting monthly transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search", response_model=List[Transaction])
async def search_transactions(
    query: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(50, ge=1, le=1000),
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Search transactions by text."""
    try:
        transactions = db.search_transactions(query=query, limit=limit)
        return transactions
    except Exception as e:
        logger.error(f"Error searching transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/etl-logs", response_model=List[ETLProcessLog])
async def get_etl_logs(
    limit: int = Query(50, ge=1, le=1000),
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Get ETL process logs."""
    try:
        logs = db.get_etl_logs(limit=limit)
        return logs
    except Exception as e:
        logger.error(f"Error getting ETL logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/transaction-types-by-amount")
async def get_transaction_types_by_amount(db: MySQLDatabaseManager = Depends(get_db_manager)):
    """Get transaction types by amount for donut chart."""
    try:
        data = db.get_transaction_types_by_amount()
        return data
    except Exception as e:
        logger.error(f"Error getting transaction types by amount: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/database-stats", response_model=DatabaseStats)
async def get_database_stats(db: MySQLDatabaseManager = Depends(get_db_manager)):
    """Get database stats."""
    try:
        stats = db.get_database_stats()
        return DatabaseStats(**stats)
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ETL endpoints
@app.post("/api/run-etl", response_model=ETLRunResponse)
async def run_etl(
    request: ETLRunRequest,
    background_tasks: BackgroundTasks,
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Run ETL process."""
    try:
        # Import here to avoid circular imports
        from etl.run import run_enhanced_etl_pipeline
        
        xml_file = Path(request.xml_file) if request.xml_file else Path("data/raw/momo.xml")
        
        if not xml_file.exists():
            raise HTTPException(status_code=404, detail=f"XML file not found: {xml_file}")
        
        # Run ETL in background
        def run_etl_background():
            try:
                result = run_enhanced_etl_pipeline(xml_file, export_json=request.export_json)
                logger.info(f"ETL completed: {result}")
            except Exception as e:
                logger.error(f"ETL failed: {e}")
        
        background_tasks.add_task(run_etl_background)
        
        return ETLRunResponse(
            status="started",
            message="ETL process started in background",
            duration_seconds=None,
            total_processed=None,
            final_loaded=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting ETL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export-json")
async def export_json(db: MySQLDatabaseManager = Depends(get_db_manager)):
    """Export dashboard data as JSON."""
    try:
        # Import here to avoid circular imports
        from etl.loader import MySQLDatabaseLoader
        
        with MySQLDatabaseLoader() as db_loader:
            dashboard_data = db_loader.export_dashboard_json()
        
        # Create temporary file
        import tempfile
        import json
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(dashboard_data, f, indent=2, default=str)
            temp_file = f.name
        
        return FileResponse(
            temp_file,
            media_type='application/json',
            filename=f'momo-dashboard-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
        )
        
    except Exception as e:
        logger.error(f"Error exporting JSON: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            message="Resource not found",
            error_code="NOT_FOUND"
        ).dict()
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="Internal server error",
            error_code="INTERNAL_ERROR"
        ).dict()
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting MoMo Data Processing API")
    
    # Ensure required directories exist
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(parents=True, exist_ok=True)
    
    # Test database connection
    try:
        stats = db_manager.get_database_stats()
        logger.info(f"Database connected. Stats: {stats}")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down MoMo Data Processing API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
