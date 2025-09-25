"""
MySQL Database Manager for API
Team 11 - Enterprise Web Development
"""

import mysql.connector
from mysql.connector import Error
import json
import logging
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from .config import settings

logger = logging.getLogger(__name__)

class MySQLDatabaseManager:
    """MySQL database manager for API operations."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize database manager with configuration."""
        self.config = config or settings.database_config
        self.connection_pool = None
        self._initialize_connection_pool()
    
    def _initialize_connection_pool(self):
        """Initialize connection pool for better performance."""
        try:
            if settings.is_production:
                # Use connection pooling in production
                self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name="momo_pool",
                    pool_size=settings.MAX_CONNECTIONS,
                    pool_reset_session=True,
                    **self.config
                )
                logger.info(f"Database connection pool initialized with {settings.MAX_CONNECTIONS} connections")
        except Error as e:
            logger.warning(f"Could not initialize connection pool: {e}. Using direct connections.")
            self.connection_pool = None
    
    @contextmanager
    def get_connection(self):
        """Get MySQL database connection with proper cleanup."""
        conn = None
        try:
            if self.connection_pool:
                # Use connection from pool
                conn = self.connection_pool.get_connection()
            else:
                # Use direct connection
                conn = mysql.connector.connect(**self.config)
            yield conn
        except Error as e:
            if conn:
                conn.rollback()
            logger.error(f"MySQL database error: {e}")
            raise
        finally:
            if conn and conn.is_connected():
                if self.connection_pool:
                    # Return connection to pool
                    conn.close()
                else:
                    # Close direct connection
                    conn.close()
    
    def get_transactions(
        self, 
        limit: int = 100, 
        offset: int = 0,
        category: Optional[str] = None,
        status: Optional[str] = None,
        phone: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        transaction_type: Optional[str] = None,
        sort_by: str = "date",
        sort_order: str = "DESC"
    ) -> List[Dict[str, Any]]:
        """Get transactions with optional filters."""
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Build query with filters
            query = """
                SELECT 
                    t.transaction_id as id,
                    t.external_transaction_id,
                    t.financial_transaction_id,
                    t.amount,
                    t.fee,
                    t.currency,
                    t.transaction_date as date,
                    t.status,
                    t.reference_number as reference,
                    t.description as type,
                    t.transaction_type,
                    t.direction,
                    t.sender_name,
                    t.sender_phone,
                    t.recipient_name,
                    t.recipient_phone,
                    t.momo_code,
                    t.sender_momo_id,
                    t.agent_momo_number,
                    t.business_name,
                    t.new_balance,
                    t.confidence_score,
                    t.raw_sms_data as original_data,
                    t.original_message,
                    t.xml_attributes,
                    t.processing_metadata,
                    su.phone_number as phone,
                    ru.phone_number as recipient_phone,
                    tc.category_name as category,
                    tc.description as category_description,
                    t.created_at as loaded_at
                FROM transactions t
                LEFT JOIN users su ON t.sender_user_id = su.user_id
                LEFT JOIN users ru ON t.receiver_user_id = ru.user_id
                LEFT JOIN transaction_categories tc ON t.category_id = tc.category_id
                WHERE 1=1
            """
            params = []
            
            # Basic filters
            if category:
                query += " AND tc.category_name = %s"
                params.append(category)
            
            if status:
                query += " AND t.status = %s"
                params.append(status)
            
            if phone:
                query += " AND (su.phone_number LIKE %s OR ru.phone_number LIKE %s)"
                phone_pattern = f"%{phone}%"
                params.extend([phone_pattern, phone_pattern])
            
            # Advanced filters
            if start_date:
                query += " AND DATE(t.transaction_date) >= %s"
                params.append(start_date)
            
            if end_date:
                query += " AND DATE(t.transaction_date) <= %s"
                params.append(end_date)
            
            if min_amount is not None:
                query += " AND t.amount >= %s"
                params.append(min_amount)
            
            if max_amount is not None:
                query += " AND t.amount <= %s"
                params.append(max_amount)
            
            if transaction_type:
                query += " AND t.transaction_type = %s"
                params.append(transaction_type)
            
            # Sorting
            valid_sort_fields = ["date", "amount", "status", "category", "phone"]
            if sort_by in valid_sort_fields:
                if sort_by == "date":
                    sort_field = "t.transaction_date"
                elif sort_by == "amount":
                    sort_field = "t.amount"
                elif sort_by == "status":
                    sort_field = "t.status"
                elif sort_by == "category":
                    sort_field = "tc.category_name"
                elif sort_by == "phone":
                    sort_field = "su.phone_number"
                
                sort_direction = "ASC" if sort_order.upper() == "ASC" else "DESC"
                query += f" ORDER BY {sort_field} {sort_direction}"
            else:
                query += " ORDER BY t.transaction_date DESC"
            
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert datetime objects to strings and parse JSON fields
            transactions = []
            for row in rows:
                transaction = dict(row)
                # Convert datetime to string
                if transaction.get('date'):
                    transaction['date'] = transaction['date'].isoformat()
                if transaction.get('loaded_at'):
                    transaction['loaded_at'] = transaction['loaded_at'].isoformat()
                
                # Parse JSON fields
                if transaction.get('xml_attributes') and isinstance(transaction['xml_attributes'], str):
                    try:
                        transaction['xml_attributes'] = json.loads(transaction['xml_attributes'])
                    except (json.JSONDecodeError, TypeError):
                        transaction['xml_attributes'] = {}
                
                if transaction.get('processing_metadata') and isinstance(transaction['processing_metadata'], str):
                    try:
                        transaction['processing_metadata'] = json.loads(transaction['processing_metadata'])
                    except (json.JSONDecodeError, TypeError):
                        transaction['processing_metadata'] = {}
                
                transactions.append(transaction)
            
            cursor.close()
            return transactions
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific transaction by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    t.transaction_id as id,
                    t.external_transaction_id,
                    t.financial_transaction_id,
                    t.amount,
                    t.fee,
                    t.currency,
                    t.transaction_date as date,
                    t.status,
                    t.reference_number as reference,
                    t.description as type,
                    t.transaction_type,
                    t.direction,
                    t.sender_name,
                    t.sender_phone,
                    t.recipient_name,
                    t.recipient_phone,
                    t.momo_code,
                    t.sender_momo_id,
                    t.agent_momo_number,
                    t.business_name,
                    t.new_balance,
                    t.confidence_score,
                    t.raw_sms_data as original_data,
                    t.original_message,
                    t.xml_attributes,
                    t.processing_metadata,
                    su.phone_number as phone,
                    su.display_name as sender_name,
                    ru.phone_number as recipient_phone,
                    ru.display_name as receiver_name,
                    tc.category_name as category,
                    t.created_at as loaded_at,
                    GROUP_CONCAT(tag.tag_name SEPARATOR ', ') as tags
                FROM transactions t
                LEFT JOIN users su ON t.sender_user_id = su.user_id
                LEFT JOIN users ru ON t.receiver_user_id = ru.user_id
                LEFT JOIN transaction_categories tc ON t.category_id = tc.category_id
                LEFT JOIN transaction_tags tt ON t.transaction_id = tt.transaction_id
                LEFT JOIN tags tag ON tt.tag_id = tag.tag_id
                WHERE t.transaction_id = %s
                GROUP BY t.transaction_id
            """
            
            cursor.execute(query, (transaction_id,))
            row = cursor.fetchone()
            
            if row:
                transaction = dict(row)
                
                # Convert datetime to string
                if transaction.get('date'):
                    transaction['date'] = transaction['date'].isoformat()
                if transaction.get('loaded_at'):
                    transaction['loaded_at'] = transaction['loaded_at'].isoformat()
                
                # Parse JSON fields
                if transaction.get('xml_attributes') and isinstance(transaction['xml_attributes'], str):
                    try:
                        transaction['xml_attributes'] = json.loads(transaction['xml_attributes'])
                    except (json.JSONDecodeError, TypeError):
                        transaction['xml_attributes'] = {}
                
                if transaction.get('processing_metadata') and isinstance(transaction['processing_metadata'], str):
                    try:
                        transaction['processing_metadata'] = json.loads(transaction['processing_metadata'])
                    except (json.JSONDecodeError, TypeError):
                        transaction['processing_metadata'] = {}
                
                cursor.close()
                return transaction
            
            cursor.close()
            return None
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard summary data."""
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get summary statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(CASE WHEN status != 'FAILED' THEN amount ELSE 0 END) as total_amount,
                    AVG(CASE WHEN status != 'FAILED' THEN amount ELSE NULL END) as avg_amount,
                    COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) as successful_transactions,
                    COUNT(CASE WHEN status = 'FAILED' THEN 1 END) as failed_transactions
                FROM transactions
            """)
            summary = cursor.fetchone()
            
            # Calculate success rate
            if summary['total_transactions'] > 0:
                summary['success_rate'] = (summary['successful_transactions'] / summary['total_transactions']) * 100
            else:
                summary['success_rate'] = 0
            
            # Get category distribution
            cursor.execute("""
                SELECT 
                    tc.category_name as category, 
                    COUNT(*) as count, 
                    SUM(CASE WHEN t.status != 'FAILED' THEN t.amount ELSE 0 END) as total_amount,
                    AVG(CASE WHEN t.status != 'FAILED' THEN t.amount ELSE NULL END) as avg_amount,
                    MIN(CASE WHEN t.status != 'FAILED' THEN t.amount ELSE NULL END) as min_amount,
                    MAX(CASE WHEN t.status != 'FAILED' THEN t.amount ELSE NULL END) as max_amount,
                    NOW() as last_updated
                FROM transactions t
                LEFT JOIN transaction_categories tc ON t.category_id = tc.category_id
                WHERE tc.category_name IS NOT NULL
                GROUP BY tc.category_name
                ORDER BY count DESC
            """)
            categories = []
            for row in cursor.fetchall():
                category = dict(row)
                # Ensure all required fields are present with proper types
                category['avg_amount'] = float(category['avg_amount']) if category['avg_amount'] else 0.0
                category['min_amount'] = float(category['min_amount']) if category['min_amount'] else 0.0
                category['max_amount'] = float(category['max_amount']) if category['max_amount'] else 0.0
                category['total_amount'] = float(category['total_amount']) if category['total_amount'] else 0.0
                category['count'] = int(category['count']) if category['count'] else 0
                # Convert datetime to string for API compatibility
                if 'last_updated' in category and category['last_updated']:
                    category['last_updated'] = category['last_updated'].strftime('%Y-%m-%d %H:%M:%S')
                categories.append(category)
            
            # Get amount distribution with more granular ranges
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN amount < 1000 THEN '0-1K'
                        WHEN amount < 5000 THEN '1K-5K'
                        WHEN amount < 10000 THEN '5K-10K'
                        WHEN amount < 25000 THEN '10K-25K'
                        WHEN amount < 50000 THEN '25K-50K'
                        WHEN amount < 100000 THEN '50K-100K'
                        WHEN amount < 250000 THEN '100K-250K'
                        WHEN amount < 500000 THEN '250K-500K'
                        ELSE '500K+'
                    END as amount_range,
                    COUNT(*) as count
                FROM transactions
                GROUP BY amount_range
                ORDER BY 
                    CASE 
                        WHEN amount_range = '0-1K' THEN 1
                        WHEN amount_range = '1K-5K' THEN 2
                        WHEN amount_range = '5K-10K' THEN 3
                        WHEN amount_range = '10K-25K' THEN 4
                        WHEN amount_range = '25K-50K' THEN 5
                        WHEN amount_range = '50K-100K' THEN 6
                        WHEN amount_range = '100K-250K' THEN 7
                        WHEN amount_range = '250K-500K' THEN 8
                        ELSE 9
                    END
            """)
            amount_distribution = [dict(row) for row in cursor.fetchall()]
            
            # Get recent transactions (for table display)
            cursor.execute("""
                SELECT 
                    t.transaction_id as id,
                    t.transaction_date as date,
                    t.amount,
                    t.description as type,
                    t.status,
                    su.phone_number as phone,
                    tc.category_name as category,
                    t.reference_number as reference,
                    t.raw_sms_data as original_data,
                    t.xml_attributes,
                    t.created_at as loaded_at
                FROM transactions t
                LEFT JOIN users su ON t.sender_user_id = su.user_id
                LEFT JOIN transaction_categories tc ON t.category_id = tc.category_id
                ORDER BY t.transaction_date DESC
                LIMIT 10
            """)
            recent_transactions = []
            for row in cursor.fetchall():
                transaction = dict(row)
                # Convert datetime to string
                if transaction.get('date'):
                    transaction['date'] = transaction['date'].isoformat()
                if transaction.get('loaded_at'):
                    transaction['loaded_at'] = transaction['loaded_at'].isoformat()
                
                # Parse xml_attributes from JSON string to dict
                if transaction.get('xml_attributes'):
                    try:
                        transaction['xml_attributes'] = json.loads(transaction['xml_attributes'])
                    except (json.JSONDecodeError, TypeError):
                        transaction['xml_attributes'] = {}
                else:
                    transaction['xml_attributes'] = {}
                recent_transactions.append(transaction)
            
            cursor.close()
            
            return {
                'summary': summary,
                'categories': categories,
                'amount_distribution': amount_distribution,
                'recent_transactions': recent_transactions
            }
    
    def get_monthly_transaction_data(self) -> Dict[str, Any]:
        """Get all transactions grouped by month for volume chart."""
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get monthly aggregated data
            cursor.execute("""
                SELECT 
                    DATE_FORMAT(transaction_date, '%Y-%m') as month,
                    COUNT(*) as count,
                    SUM(CASE WHEN status != 'FAILED' THEN amount ELSE 0 END) as volume,
                    AVG(CASE WHEN status != 'FAILED' THEN amount ELSE NULL END) as avg_amount
                FROM transactions
                WHERE amount > 0
                GROUP BY DATE_FORMAT(transaction_date, '%Y-%m')
                ORDER BY month
            """)
            monthly_stats = []
            for row in cursor.fetchall():
                month_data = dict(row)
                month_data['volume'] = float(month_data['volume']) if month_data['volume'] else 0.0
                month_data['avg_amount'] = float(month_data['avg_amount']) if month_data['avg_amount'] else 0.0
                monthly_stats.append(month_data)
            
            # Get hourly pattern from all transactions
            cursor.execute("""
                SELECT 
                    HOUR(transaction_date) as hour,
                    COUNT(*) as count,
                    SUM(CASE WHEN status != 'FAILED' THEN amount ELSE 0 END) as volume
                FROM transactions
                WHERE amount > 0
                GROUP BY HOUR(transaction_date)
                ORDER BY hour
            """)
            hourly_pattern = []
            for row in cursor.fetchall():
                hour_data = dict(row)
                hour_data['hour'] = int(hour_data['hour'])
                hour_data['volume'] = float(hour_data['volume']) if hour_data['volume'] else 0.0
                hourly_pattern.append(hour_data)
            
            cursor.close()
            
            return {
                'monthly_stats': monthly_stats,
                'hourly_pattern': hourly_pattern
            }
    
    def get_analytics(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get analytics data for date range."""
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Build date filter
            date_filter = ""
            params = []
            if start_date:
                date_filter += " AND transaction_date >= %s"
                params.append(start_date)
            if end_date:
                date_filter += " AND transaction_date <= %s"
                params.append(end_date)
            
            # Daily transaction amounts
            cursor.execute(f"""
                SELECT 
                    DATE(transaction_date) as date, 
                    SUM(amount) as daily_amount, 
                    COUNT(*) as daily_count
                FROM transactions
                WHERE 1=1 {date_filter}
                GROUP BY DATE(transaction_date)
                ORDER BY date DESC
                LIMIT 30
            """, params)
            daily_data = []
            for row in cursor.fetchall():
                daily_item = dict(row)
                if daily_item.get('date'):
                    daily_item['date'] = daily_item['date'].isoformat()
                daily_data.append(daily_item)
            
            # Category performance
            cursor.execute(f"""
                SELECT 
                    tc.category_name as category,
                    COUNT(*) as count,
                    SUM(t.amount) as total_amount,
                    AVG(t.amount) as avg_amount,
                    COUNT(CASE WHEN t.status = 'SUCCESS' THEN 1 END) as successful_count
                FROM transactions t
                LEFT JOIN transaction_categories tc ON t.category_id = tc.category_id
                WHERE tc.category_name IS NOT NULL {date_filter}
                GROUP BY tc.category_name
                ORDER BY count DESC
            """, params)
            category_performance = [dict(row) for row in cursor.fetchall()]
            
            # Phone number analysis
            cursor.execute(f"""
                SELECT 
                    su.phone_number as phone,
                    COUNT(*) as transaction_count,
                    SUM(t.amount) as total_amount,
                    AVG(t.amount) as avg_amount
                FROM transactions t
                LEFT JOIN users su ON t.sender_user_id = su.user_id
                WHERE su.phone_number IS NOT NULL {date_filter}
                GROUP BY su.phone_number
                ORDER BY transaction_count DESC
                LIMIT 20
            """, params)
            phone_analysis = [dict(row) for row in cursor.fetchall()]
            
            cursor.close()
            
            return {
                'daily_data': daily_data,
                'category_performance': category_performance,
                'phone_analysis': phone_analysis
            }
    
    def get_category_stats(self) -> List[Dict[str, Any]]:
        """Get category statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    tc.category_name as category,
                    COUNT(t.transaction_id) as count,
                    SUM(t.amount) as total_amount,
                    AVG(t.amount) as avg_amount,
                    MIN(t.amount) as min_amount,
                    MAX(t.amount) as max_amount,
                    COUNT(CASE WHEN t.status = 'SUCCESS' THEN 1 END) as successful_count
                FROM transaction_categories tc
                LEFT JOIN transactions t ON tc.category_id = t.category_id
                GROUP BY tc.category_id, tc.category_name
                ORDER BY count DESC
            """)
            stats = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            return stats
    
    def get_etl_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent ETL process logs."""
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    log_id as id,
                    process_name,
                    log_level as status,
                    message,
                    records_processed,
                    records_successful,
                    records_failed,
                    execution_time_seconds,
                    created_at,
                    details
                FROM system_logs 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (limit,))
            logs = []
            for row in cursor.fetchall():
                log = dict(row)
                if log.get('created_at'):
                    log['created_at'] = log['created_at'].isoformat()
                if log.get('details') and isinstance(log['details'], str):
                    try:
                        log['details'] = json.loads(log['details'])
                    except (json.JSONDecodeError, TypeError):
                        log['details'] = {}
                logs.append(log)
            cursor.close()
            return logs
    
    def search_transactions(
        self, 
        query: str, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search transactions by text query."""
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            search_term = f"%{query}%"
            
            cursor.execute("""
                SELECT 
                    t.transaction_id as id,
                    t.external_transaction_id,
                    t.amount,
                    t.transaction_date as date,
                    t.status,
                    t.reference_number as reference,
                    t.description as type,
                    su.phone_number as phone,
                    tc.category_name as category,
                    t.raw_sms_data as original_data
                FROM transactions t
                LEFT JOIN users su ON t.sender_user_id = su.user_id
                LEFT JOIN transaction_categories tc ON t.category_id = tc.category_id
                WHERE su.phone_number LIKE %s 
                   OR t.reference_number LIKE %s
                   OR t.raw_sms_data LIKE %s
                   OR t.description LIKE %s
                ORDER BY t.transaction_date DESC
                LIMIT %s
            """, (search_term, search_term, search_term, search_term, limit))
            
            transactions = []
            for row in cursor.fetchall():
                transaction = dict(row)
                if transaction.get('date'):
                    transaction['date'] = transaction['date'].isoformat()
                transactions.append(transaction)
            
            cursor.close()
            return transactions
    
    def get_transaction_types_by_amount(self) -> List[Dict[str, Any]]:
        """Get transaction types by amount for donut chart."""
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get transaction types with their amounts and percentages
            cursor.execute("""
                SELECT 
                    COALESCE(transaction_type, 'UNKNOWN') as transaction_type,
                    COUNT(*) as count,
                    SUM(CASE WHEN status != 'FAILED' THEN amount ELSE 0 END) as total_amount,
                    AVG(CASE WHEN status != 'FAILED' THEN amount ELSE NULL END) as avg_amount
                FROM transactions
                WHERE amount > 0
                GROUP BY transaction_type
                ORDER BY total_amount DESC
            """)
            
            results = []
            total_amount = 0
            
            # First pass to get total amount
            for row in cursor.fetchall():
                total_amount += row['total_amount']
                results.append(dict(row))
            
            # Second pass to calculate percentages
            for result in results:
                result['percentage'] = (result['total_amount'] / total_amount * 100) if total_amount > 0 else 0
                result['total_amount'] = float(result['total_amount'])
                result['avg_amount'] = float(result['avg_amount'])
                result['count'] = int(result['count'])
            
            cursor.close()
            return results

    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get table counts
            tables = ['users', 'transaction_categories', 'tags', 'transactions', 
                     'transaction_tags', 'user_preferences', 'system_logs', 'transaction_statistics']
            
            stats = {}
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f'{table}_count'] = cursor.fetchone()[0]
            
            # Get database size (approximate)
            cursor.execute("""
                SELECT 
                    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size_mb
                FROM information_schema.tables 
                WHERE table_schema = %s
            """, (self.config['database'],))
            result = cursor.fetchone()
            stats['database_size_mb'] = result[0] if result[0] else 0
            
            cursor.close()
            
            return stats

    def get_hourly_pattern(self) -> List[Dict[str, Any]]:
        """Get hourly transaction pattern data."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                # Initialize hourly data with zeros
                hourly_data = []
                for hour in range(24):
                    hourly_data.append({
                        "hour": hour,
                        "count": 0,
                        "volume": 0
                    })
                
                # Get actual hourly data from transactions
                cursor.execute("""
                    SELECT 
                        HOUR(transaction_date) as hour,
                        COUNT(*) as count,
                        SUM(amount) as volume
                    FROM transactions 
                    WHERE transaction_date IS NOT NULL
                    GROUP BY HOUR(transaction_date)
                    ORDER BY hour
                """)
                
                results = cursor.fetchall()
                
                # Update hourly data with actual values
                for result in results:
                    hour = result['hour']
                    if 0 <= hour <= 23:
                        hourly_data[hour]['count'] = result['count']
                        hourly_data[hour]['volume'] = float(result['volume'] or 0)
                
                cursor.close()
                return hourly_data
        except Exception as e:
            logger.error(f"Error getting hourly pattern: {e}")
            return []

    def get_amount_distribution(self) -> List[Dict[str, Any]]:
        """Get amount distribution data for charts."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                # Define amount ranges
                amount_ranges = [
                    {"range": "0-1,000", "min": 0, "max": 1000},
                    {"range": "1,000-5,000", "min": 1000, "max": 5000},
                    {"range": "5,000-10,000", "min": 5000, "max": 10000},
                    {"range": "10,000-25,000", "min": 10000, "max": 25000},
                    {"range": "25,000-50,000", "min": 25000, "max": 50000},
                    {"range": "50,000+", "min": 50000, "max": 999999999}
                ]
                
                distribution = []
                
                for range_info in amount_ranges:
                    if range_info["max"] == 999999999:  # 50,000+ range
                        cursor.execute("""
                            SELECT COUNT(*) as count
                            FROM transactions 
                            WHERE amount >= %s
                        """, (range_info["min"],))
                    else:
                        cursor.execute("""
                            SELECT COUNT(*) as count
                            FROM transactions 
                            WHERE amount >= %s AND amount < %s
                        """, (range_info["min"], range_info["max"]))
                    
                    result = cursor.fetchone()
                    distribution.append({
                        "amount_range": range_info["range"],
                        "count": result['count']
                    })
                
                cursor.close()
                return distribution
        except Exception as e:
            logger.error(f"Error getting amount distribution: {e}")
            return []
