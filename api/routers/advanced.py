"""
Advanced API Router for Enhanced Features
Includes export, advanced filtering, and real-time updates
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict, Any
import json
import io
from ..db import MySQLDatabaseManager
from ..auth import get_current_user_with_auto_auth
from ..export import DataExporter
from ..config import settings

router = APIRouter(prefix="/advanced", tags=["advanced"])

def get_db_manager():
    return MySQLDatabaseManager()

def get_exporter():
    return DataExporter(get_db_manager())

@router.get("/transactions/advanced")
async def get_transactions_advanced(
    request: Request,
    limit: int = Query(100, ge=1, le=10000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    phone: Optional[str] = Query(None, description="Filter by phone number"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum amount"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum amount"),
    transaction_type: Optional[str] = Query(None, description="Filter by transaction type"),
    sort_by: str = Query("date", description="Sort field"),
    sort_order: str = Query("DESC", description="Sort order (ASC/DESC)"),
    db: MySQLDatabaseManager = Depends(get_db_manager),
    current_user: str = Depends(get_current_user_with_auto_auth)
):
    """Get transactions with advanced filtering and sorting."""
    try:
        transactions = db.get_transactions(
            limit=limit,
            offset=offset,
            category=category,
            status=status,
            phone=phone,
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount,
            transaction_type=transaction_type,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return {
            "success": True,
            "data": transactions,
            "metadata": {
                "count": len(transactions),
                "limit": limit,
                "offset": offset,
                "filters": {
                    "category": category,
                    "status": status,
                    "phone": phone,
                    "start_date": start_date,
                    "end_date": end_date,
                    "min_amount": min_amount,
                    "max_amount": max_amount,
                    "transaction_type": transaction_type
                },
                "sorting": {
                    "sort_by": sort_by,
                    "sort_order": sort_order
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/transactions")
async def export_transactions(
    request: Request,
    format_type: str = Query("json", description="Export format (json, csv, xlsx)"),
    limit: int = Query(None, ge=1, le=10000, description="Maximum records to export"),
    offset: int = Query(0, ge=0, description="Starting offset"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    phone: Optional[str] = Query(None, description="Filter by phone number"),
    start_date: Optional[str] = Query(None, description="Start date filter"),
    end_date: Optional[str] = Query(None, description="End date filter"),
    min_amount: Optional[float] = Query(None, description="Minimum amount filter"),
    max_amount: Optional[float] = Query(None, description="Maximum amount filter"),
    transaction_type: Optional[str] = Query(None, description="Transaction type filter"),
    exporter: DataExporter = Depends(get_exporter),
    current_user: str = Depends(get_current_user_with_auto_auth)
):
    """Export transactions in various formats."""
    try:
        filters = {
            "category": category,
            "status": status,
            "phone": phone,
            "start_date": start_date,
            "end_date": end_date,
            "min_amount": min_amount,
            "max_amount": max_amount,
            "transaction_type": transaction_type
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        result = exporter.export_transactions(
            format_type=format_type,
            limit=limit,
            offset=offset,
            filters=filters
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        # Return appropriate response based on format
        if format_type.lower() == "json":
            return result["data"]
        else:
            # For CSV and Excel, return as streaming response
            content_type = result.get("content_type", "application/octet-stream")
            filename = f"transactions_export.{format_type}"
            
            if format_type.lower() == "csv":
                return StreamingResponse(
                    io.StringIO(result["data"]),
                    media_type=content_type,
                    headers={"Content-Disposition": f"attachment; filename={filename}"}
                )
            else:  # Excel
                return StreamingResponse(
                    io.BytesIO(result["data"]),
                    media_type=content_type,
                    headers={"Content-Disposition": f"attachment; filename={filename}"}
                )
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/analytics")
async def export_analytics(
    request: Request,
    format_type: str = Query("json", description="Export format (json, csv, xlsx)"),
    start_date: Optional[str] = Query(None, description="Start date filter"),
    end_date: Optional[str] = Query(None, description="End date filter"),
    exporter: DataExporter = Depends(get_exporter),
    current_user: str = Depends(get_current_user_with_auto_auth)
):
    """Export analytics data in various formats."""
    try:
        result = exporter.export_analytics(
            format_type=format_type,
            start_date=start_date,
            end_date=end_date
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        # Return appropriate response based on format
        if format_type.lower() == "json":
            return result["data"]
        else:
            # For CSV and Excel, return as streaming response
            content_type = result.get("content_type", "application/octet-stream")
            filename = f"analytics_export.{format_type}"
            
            if format_type.lower() == "csv":
                return StreamingResponse(
                    io.StringIO(result["data"]),
                    media_type=content_type,
                    headers={"Content-Disposition": f"attachment; filename={filename}"}
                )
            else:  # Excel
                return StreamingResponse(
                    io.BytesIO(result["data"]),
                    media_type=content_type,
                    headers={"Content-Disposition": f"attachment; filename={filename}"}
                )
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/dashboard")
async def export_dashboard(
    request: Request,
    format_type: str = Query("json", description="Export format (json, csv, xlsx)"),
    exporter: DataExporter = Depends(get_exporter),
    current_user: str = Depends(get_current_user_with_auto_auth)
):
    """Export dashboard data in various formats."""
    try:
        result = exporter.export_dashboard_data(format_type=format_type)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        # Return appropriate response based on format
        if format_type.lower() == "json":
            return result["data"]
        else:
            # For CSV and Excel, return as streaming response
            content_type = result.get("content_type", "application/octet-stream")
            filename = f"dashboard_export.{format_type}"
            
            if format_type.lower() == "csv":
                return StreamingResponse(
                    io.StringIO(result["data"]),
                    media_type=content_type,
                    headers={"Content-Disposition": f"attachment; filename={filename}"}
                )
            else:  # Excel
                return StreamingResponse(
                    io.BytesIO(result["data"]),
                    media_type=content_type,
                    headers={"Content-Disposition": f"attachment; filename={filename}"}
                )
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export/formats")
async def get_export_formats(
    request: Request,
    exporter: DataExporter = Depends(get_exporter),
    current_user: str = Depends(get_current_user_with_auto_auth)
):
    """Get supported export formats and limits."""
    try:
        formats = exporter.get_export_formats()
        limits = exporter.get_export_limits()
        
        return {
            "success": True,
            "data": {
                "supported_formats": formats,
                "limits": limits
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/transactions")
async def search_transactions(
    request: Request,
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum results"),
    db: MySQLDatabaseManager = Depends(get_db_manager),
    current_user: str = Depends(get_current_user_with_auto_auth)
):
    """Advanced search for transactions."""
    try:
        # Use the existing search functionality
        results = db.search_transactions(q, limit)
        
        return {
            "success": True,
            "data": results,
            "metadata": {
                "query": q,
                "count": len(results),
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/summary")
async def get_advanced_stats(
    request: Request,
    start_date: Optional[str] = Query(None, description="Start date filter"),
    end_date: Optional[str] = Query(None, description="End date filter"),
    db: MySQLDatabaseManager = Depends(get_db_manager),
    current_user: str = Depends(get_current_user_with_auto_auth)
):
    """Get advanced statistics and summary."""
    try:
        # Get various statistics
        dashboard_data = db.get_dashboard_data()
        analytics_data = db.get_analytics(start_date, end_date)
        category_stats = db.get_category_stats()
        
        # Calculate additional metrics
        total_transactions = dashboard_data.get("summary", {}).get("total_transactions", 0)
        total_amount = dashboard_data.get("summary", {}).get("total_amount", 0)
        success_rate = dashboard_data.get("summary", {}).get("success_rate", 0)
        
        # Get hourly pattern
        hourly_pattern = db.get_hourly_pattern()
        
        # Get amount distribution
        amount_distribution = db.get_amount_distribution()
        
        return {
            "success": True,
            "data": {
                "summary": {
                    "total_transactions": total_transactions,
                    "total_amount": total_amount,
                    "success_rate": success_rate,
                    "average_transaction": total_amount / total_transactions if total_transactions > 0 else 0
                },
                "analytics": analytics_data,
                "category_breakdown": category_stats,
                "hourly_pattern": hourly_pattern,
                "amount_distribution": amount_distribution,
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
