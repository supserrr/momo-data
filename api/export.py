"""
Export functionality for MoMo Data Processing System
Supports multiple formats: JSON, CSV, Excel
"""

import json
import csv
import io
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import pandas as pd
from .db import MySQLDatabaseManager
from .config import settings

logger = logging.getLogger(__name__)

class DataExporter:
    """Data export functionality for various formats."""
    
    def __init__(self, db_manager: MySQLDatabaseManager):
        self.db = db_manager
    
    def export_transactions(
        self, 
        format_type: str = "json",
        limit: int = None,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Export transactions in specified format.
        
        Args:
            format_type: Export format (json, csv, xlsx)
            limit: Maximum number of records
            offset: Starting offset
            filters: Optional filters
            
        Returns:
            Dict containing export data and metadata
        """
        try:
            # Get data from database
            transactions = self.db.get_transactions(
                limit=limit or settings.EXPORT_MAX_RECORDS,
                offset=offset,
                category=filters.get('category') if filters else None,
                status=filters.get('status') if filters else None,
                phone=filters.get('phone') if filters else None
            )
            
            if not transactions:
                return {
                    "success": False,
                    "message": "No transactions found for export",
                    "data": None
                }
            
            # Export based on format
            if format_type.lower() == "json":
                return self._export_json(transactions, "transactions")
            elif format_type.lower() == "csv":
                return self._export_csv(transactions, "transactions")
            elif format_type.lower() == "xlsx":
                return self._export_excel(transactions, "transactions")
            else:
                return {
                    "success": False,
                    "message": f"Unsupported format: {format_type}",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Error exporting transactions: {e}")
            return {
                "success": False,
                "message": f"Export failed: {str(e)}",
                "data": None
            }
    
    def export_analytics(
        self, 
        format_type: str = "json",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export analytics data in specified format.
        
        Args:
            format_type: Export format (json, csv, xlsx)
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Dict containing export data and metadata
        """
        try:
            # Get analytics data
            analytics_data = self.db.get_analytics(start_date, end_date)
            
            if not analytics_data:
                return {
                    "success": False,
                    "message": "No analytics data found for export",
                    "data": None
                }
            
            # Export based on format
            if format_type.lower() == "json":
                return self._export_json(analytics_data, "analytics")
            elif format_type.lower() == "csv":
                return self._export_csv(analytics_data, "analytics")
            elif format_type.lower() == "xlsx":
                return self._export_excel(analytics_data, "analytics")
            else:
                return {
                    "success": False,
                    "message": f"Unsupported format: {format_type}",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Error exporting analytics: {e}")
            return {
                "success": False,
                "message": f"Export failed: {str(e)}",
                "data": None
            }
    
    def export_dashboard_data(self, format_type: str = "json") -> Dict[str, Any]:
        """
        Export dashboard data in specified format.
        
        Args:
            format_type: Export format (json, csv, xlsx)
            
        Returns:
            Dict containing export data and metadata
        """
        try:
            # Get dashboard data
            dashboard_data = self.db.get_dashboard_data()
            
            if not dashboard_data:
                return {
                    "success": False,
                    "message": "No dashboard data found for export",
                    "data": None
                }
            
            # Export based on format
            if format_type.lower() == "json":
                return self._export_json(dashboard_data, "dashboard")
            elif format_type.lower() == "csv":
                return self._export_csv(dashboard_data, "dashboard")
            elif format_type.lower() == "xlsx":
                return self._export_excel(dashboard_data, "dashboard")
            else:
                return {
                    "success": False,
                    "message": f"Unsupported format: {format_type}",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Error exporting dashboard data: {e}")
            return {
                "success": False,
                "message": f"Export failed: {str(e)}",
                "data": None
            }
    
    def _export_json(self, data: Any, data_type: str) -> Dict[str, Any]:
        """Export data as JSON."""
        try:
            export_data = {
                "export_info": {
                    "type": data_type,
                    "format": "json",
                    "timestamp": datetime.now().isoformat(),
                    "record_count": len(data) if isinstance(data, list) else 1
                },
                "data": data
            }
            
            return {
                "success": True,
                "message": f"Successfully exported {data_type} data as JSON",
                "data": export_data,
                "content_type": "application/json"
            }
        except Exception as e:
            logger.error(f"Error exporting JSON: {e}")
            return {
                "success": False,
                "message": f"JSON export failed: {str(e)}",
                "data": None
            }
    
    def _export_csv(self, data: Any, data_type: str) -> Dict[str, Any]:
        """Export data as CSV."""
        try:
            output = io.StringIO()
            
            if isinstance(data, list) and data:
                # Handle list of dictionaries
                if isinstance(data[0], dict):
                    fieldnames = data[0].keys()
                    writer = csv.DictWriter(output, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
                else:
                    # Handle list of simple values
                    writer = csv.writer(output)
                    writer.writerow(["value"])
                    writer.writerows([[item] for item in data])
            elif isinstance(data, dict):
                # Handle dictionary data
                writer = csv.writer(output)
                for key, value in data.items():
                    if isinstance(value, (list, dict)):
                        writer.writerow([key, json.dumps(value)])
                    else:
                        writer.writerow([key, value])
            else:
                # Handle other data types
                writer = csv.writer(output)
                writer.writerow(["data"])
                writer.writerow([str(data)])
            
            csv_content = output.getvalue()
            output.close()
            
            return {
                "success": True,
                "message": f"Successfully exported {data_type} data as CSV",
                "data": csv_content,
                "content_type": "text/csv"
            }
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            return {
                "success": False,
                "message": f"CSV export failed: {str(e)}",
                "data": None
            }
    
    def _export_excel(self, data: Any, data_type: str) -> Dict[str, Any]:
        """Export data as Excel."""
        try:
            output = io.BytesIO()
            
            if isinstance(data, list) and data:
                # Handle list of dictionaries
                if isinstance(data[0], dict):
                    df = pd.DataFrame(data)
                else:
                    # Handle list of simple values
                    df = pd.DataFrame(data, columns=["value"])
            elif isinstance(data, dict):
                # Handle dictionary data - create multiple sheets if needed
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    for key, value in data.items():
                        if isinstance(value, list) and value:
                            if isinstance(value[0], dict):
                                df = pd.DataFrame(value)
                            else:
                                df = pd.DataFrame(value, columns=["value"])
                        else:
                            df = pd.DataFrame([{"key": key, "value": str(value)}])
                        
                        # Clean sheet name (Excel has restrictions)
                        sheet_name = str(key)[:31].replace("/", "_").replace("\\", "_")
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                # Handle other data types
                df = pd.DataFrame([{"data": str(data)}])
                df.to_excel(output, index=False)
            
            # If we didn't use ExcelWriter, write to output
            if not isinstance(data, dict):
                df.to_excel(output, index=False)
            
            excel_content = output.getvalue()
            output.close()
            
            return {
                "success": True,
                "message": f"Successfully exported {data_type} data as Excel",
                "data": excel_content,
                "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            }
        except Exception as e:
            logger.error(f"Error exporting Excel: {e}")
            return {
                "success": False,
                "message": f"Excel export failed: {str(e)}",
                "data": None
            }
    
    def get_export_formats(self) -> List[str]:
        """Get list of supported export formats."""
        return settings.EXPORT_FORMATS
    
    def get_export_limits(self) -> Dict[str, int]:
        """Get export limits and constraints."""
        return {
            "max_records": settings.EXPORT_MAX_RECORDS,
            "supported_formats": settings.EXPORT_FORMATS
        }
