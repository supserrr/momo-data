"""
Database connection and query helpers for the API.
"""

import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from contextlib import contextmanager
from etl.config import DATABASE_FILE

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for API operations."""
    
    def __init__(self, db_path: Path = DATABASE_FILE):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper cleanup."""
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def get_transactions(
        self, 
        limit: int = 100, 
        offset: int = 0,
        category: Optional[str] = None,
        status: Optional[str] = None,
        phone: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get transactions with optional filters."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build query with filters
            query = "SELECT * FROM transactions WHERE 1=1"
            params = []
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if phone:
                query += " AND phone LIKE ?"
                params.append(f"%{phone}%")
            
            query += " ORDER BY date DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific transaction by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
            row = cursor.fetchone()
            
            return dict(row) if row else None
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard summary data."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get summary statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(amount) as total_amount,
                    AVG(amount) as avg_amount,
                    COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) as successful_transactions,
                    COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed_transactions
                FROM transactions
            """)
            summary = dict(cursor.fetchone())
            
            # Calculate success rate
            if summary['total_transactions'] > 0:
                summary['success_rate'] = (summary['successful_transactions'] / summary['total_transactions']) * 100
            else:
                summary['success_rate'] = 0
            
            # Get category distribution
            cursor.execute("""
                SELECT category, COUNT(*) as count, SUM(amount) as total_amount
                FROM transactions
                WHERE category IS NOT NULL
                GROUP BY category
                ORDER BY count DESC
            """)
            categories = [dict(row) for row in cursor.fetchall()]
            
            # Get amount distribution
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN amount < 10000 THEN '0-10000'
                        WHEN amount < 50000 THEN '10000-50000'
                        WHEN amount < 100000 THEN '50000-100000'
                        ELSE '100000+'
                    END as amount_range,
                    COUNT(*) as count
                FROM transactions
                GROUP BY amount_range
                ORDER BY 
                    CASE 
                        WHEN amount_range = '0-10000' THEN 1
                        WHEN amount_range = '10000-50000' THEN 2
                        WHEN amount_range = '50000-100000' THEN 3
                        ELSE 4
                    END
            """)
            amount_distribution = [dict(row) for row in cursor.fetchall()]
            
            # Get recent transactions
            cursor.execute("""
                SELECT date, amount, type, status, phone, category
                FROM transactions
                ORDER BY date DESC
                LIMIT 10
            """)
            recent_transactions = [dict(row) for row in cursor.fetchall()]
            
            return {
                'summary': summary,
                'categories': categories,
                'amount_distribution': amount_distribution,
                'recent_transactions': recent_transactions
            }
    
    def get_analytics(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get analytics data for date range."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build date filter
            date_filter = ""
            params = []
            if start_date:
                date_filter += " AND date >= ?"
                params.append(start_date)
            if end_date:
                date_filter += " AND date <= ?"
                params.append(end_date)
            
            # Daily transaction amounts
            cursor.execute(f"""
                SELECT date, SUM(amount) as daily_amount, COUNT(*) as daily_count
                FROM transactions
                WHERE 1=1 {date_filter}
                GROUP BY date
                ORDER BY date DESC
                LIMIT 30
            """, params)
            daily_data = [dict(row) for row in cursor.fetchall()]
            
            # Category performance
            cursor.execute(f"""
                SELECT 
                    category,
                    COUNT(*) as count,
                    SUM(amount) as total_amount,
                    AVG(amount) as avg_amount,
                    COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) as successful_count
                FROM transactions
                WHERE category IS NOT NULL {date_filter}
                GROUP BY category
                ORDER BY count DESC
            """, params)
            category_performance = [dict(row) for row in cursor.fetchall()]
            
            # Phone number analysis
            cursor.execute(f"""
                SELECT 
                    phone,
                    COUNT(*) as transaction_count,
                    SUM(amount) as total_amount,
                    AVG(amount) as avg_amount
                FROM transactions
                WHERE 1=1 {date_filter}
                GROUP BY phone
                ORDER BY transaction_count DESC
                LIMIT 20
            """, params)
            phone_analysis = [dict(row) for row in cursor.fetchall()]
            
            return {
                'daily_data': daily_data,
                'category_performance': category_performance,
                'phone_analysis': phone_analysis
            }
    
    def get_category_stats(self) -> List[Dict[str, Any]]:
        """Get category statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM category_stats ORDER BY count DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_etl_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent ETL process logs."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM etl_logs 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def search_transactions(
        self, 
        query: str, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search transactions by text query."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            search_term = f"%{query}%"
            
            cursor.execute("""
                SELECT * FROM transactions
                WHERE phone LIKE ? 
                   OR reference LIKE ?
                   OR original_data LIKE ?
                   OR raw_data LIKE ?
                ORDER BY date DESC
                LIMIT ?
            """, (search_term, search_term, search_term, search_term, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get table counts
            cursor.execute("SELECT COUNT(*) FROM transactions")
            transaction_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM etl_logs")
            log_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM category_stats")
            stats_count = cursor.fetchone()[0]
            
            # Get database file size
            db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
            
            return {
                'transaction_count': transaction_count,
                'log_count': log_count,
                'stats_count': stats_count,
                'database_size_bytes': db_size,
                'database_size_mb': round(db_size / (1024 * 1024), 2)
            }
