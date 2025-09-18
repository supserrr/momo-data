"""
Modular FastAPI Application for MoMo Data Processing
Team 11 - Enterprise Web Development
"""

import logging
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Import configuration
from .config import settings, API_ROUTERS, RESPONSE_TEMPLATES, ERROR_CODES

# Import routers
from .routers import (
    transactions_router,
    analytics_router,
    dashboard_router,
    etl_router,
    categories_router,
    search_router,
    export_router,
    health_router
)

# Import database manager
from .db import MySQLDatabaseManager

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with configuration
app = FastAPI(
    title=settings.title,
    description=settings.description,
    version=settings.version,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_tags=[
        {"name": "transactions", "description": "Transaction management and operations"},
        {"name": "analytics", "description": "Analytics and reporting operations"},
        {"name": "dashboard", "description": "Dashboard data and widgets"},
        {"name": "etl", "description": "ETL process management and monitoring"},
        {"name": "categories", "description": "Transaction category management"},
        {"name": "search", "description": "Search and filtering operations"},
        {"name": "export", "description": "Data export operations"},
        {"name": "health", "description": "System health monitoring"},
    ]
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure for production
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Initialize database manager
db_manager = MySQLDatabaseManager()

# Database dependency
def get_db_manager():
    """Get database manager instance"""
    return db_manager

# Global exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            **RESPONSE_TEMPLATES["error"],
            "message": exc.detail,
            "error_code": exc.status_code,
            "path": str(request.url)
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc.errors()} - {request.url}")
    return JSONResponse(
        status_code=422,
        content={
            **RESPONSE_TEMPLATES["validation_error"],
            "errors": exc.errors(),
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)} - {request.url}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            **RESPONSE_TEMPLATES["error"],
            "message": "Internal server error",
            "error_code": 500,
            "path": str(request.url)
        }
    )

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = datetime.now()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    # Add timing header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Mount static files
app.mount("/web", StaticFiles(directory="web"), name="web")
app.mount("/data", StaticFiles(directory="data"), name="data")

# Root endpoint
@app.get("/", response_class=FileResponse)
async def serve_frontend():
    """Serve main dashboard"""
    return FileResponse("index.html")

# Include all routers
app.include_router(transactions_router, prefix=settings.api_prefix)
app.include_router(analytics_router, prefix=settings.api_prefix)
app.include_router(dashboard_router, prefix=settings.api_prefix)
app.include_router(etl_router, prefix=settings.api_prefix)
app.include_router(categories_router, prefix=settings.api_prefix)
app.include_router(search_router, prefix=settings.api_prefix)
app.include_router(export_router, prefix=settings.api_prefix)
app.include_router(health_router, prefix=settings.api_prefix)

# Legacy endpoints for backward compatibility
@app.get("/api/transactions", include_in_schema=False)
async def legacy_get_transactions(
    limit: int = 100,
    offset: int = 0,
    category: Optional[str] = None,
    status: Optional[str] = None,
    phone: Optional[str] = None,
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Legacy transaction endpoint for backward compatibility"""
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
        logger.error(f"Error fetching transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard-data", include_in_schema=False)
async def legacy_get_dashboard_data(
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Legacy dashboard data endpoint for backward compatibility"""
    try:
        dashboard_data = db.get_dashboard_data()
        return dashboard_data
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics", include_in_schema=False)
async def legacy_get_analytics(
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Legacy analytics endpoint for backward compatibility"""
    try:
        analytics_data = db.get_analytics_data()
        return analytics_data
    except Exception as e:
        logger.error(f"Error fetching analytics data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/transaction-types-by-amount", include_in_schema=False)
async def legacy_get_transaction_types_by_amount(
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Legacy transaction types by amount endpoint for backward compatibility"""
    try:
        transaction_types = db.get_transaction_types_by_amount()
        return transaction_types
    except Exception as e:
        logger.error(f"Error fetching transaction types by amount: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monthly-stats", include_in_schema=False)
async def legacy_get_monthly_stats(
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Legacy monthly stats endpoint for backward compatibility"""
    try:
        monthly_data = db.get_monthly_transaction_data()
        return monthly_data.get('monthly_stats', [])
    except Exception as e:
        logger.error(f"Error fetching monthly stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/category-distribution", include_in_schema=False)
async def legacy_get_category_distribution(
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Legacy category distribution endpoint for backward compatibility"""
    try:
        dashboard_data = db.get_dashboard_data()
        return dashboard_data.get('categories', [])
    except Exception as e:
        logger.error(f"Error fetching category distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hourly-pattern", include_in_schema=False)
async def legacy_get_hourly_pattern(
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Legacy hourly pattern endpoint for backward compatibility"""
    try:
        monthly_data = db.get_monthly_transaction_data()
        return monthly_data.get('hourly_pattern', [])
    except Exception as e:
        logger.error(f"Error fetching hourly pattern: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/amount-distribution", include_in_schema=False)
async def legacy_get_amount_distribution(
    db: MySQLDatabaseManager = Depends(get_db_manager)
):
    """Legacy amount distribution endpoint for backward compatibility"""
    try:
        dashboard_data = db.get_dashboard_data()
        return dashboard_data.get('amount_distribution', [])
    except Exception as e:
        logger.error(f"Error fetching amount distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting MoMo Data Processing API...")
    logger.info(f"API Version: {settings.version}")
    logger.info(f"Database: {settings.database_host}:{settings.database_port}/{settings.database_name}")
    
    # Test database connection
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        sys.exit(1)

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down MoMo Data Processing API...")

# API Information endpoint
@app.get("/api/info")
async def get_api_info():
    """Get API information and status"""
    return {
        "name": settings.title,
        "version": settings.version,
        "description": settings.description,
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "transactions": f"{settings.api_prefix}/transactions",
            "analytics": f"{settings.api_prefix}/analytics",
            "dashboard": f"{settings.api_prefix}/dashboard",
            "etl": f"{settings.api_prefix}/etl",
            "categories": f"{settings.api_prefix}/categories",
            "search": f"{settings.api_prefix}/search",
            "export": f"{settings.api_prefix}/export",
            "health": f"{settings.api_prefix}/health"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.app_new:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
