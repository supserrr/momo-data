"""
Database Operations for MoMo Data
Team 11 - Enterprise Web Development
"""

import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from .config import DATABASE_FILE, DASHBOARD_JSON_FILE

logger = logging.getLogger(__name__)

class DatabaseLoader:
    """Load categorized transactions into SQLite database."""
    
    def __init__(self, db_path: Path = DATABASE_FILE):
        self.db_path = db_path
        self.connection = None
        self.loaded_count = 0
        self.error_count = 0
        self.errors = []
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def connect(self):
        """Connect to SQLite database."""
        try:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            logger.info(f"Connected to database: {self.db_path}")
            
            # Create tables
            self.create_tables()
            
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def create_tables(self):
        """Create database tables if they don't exist."""
        try:
            cursor = self.connection.cursor()
            
            # Main transactions table with all processed data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    phone TEXT NOT NULL,
                    date TEXT,
                    reference TEXT,
                    type TEXT,
                    status TEXT,
                    category TEXT,
                    category_confidence REAL,
                    original_data TEXT,
                    raw_data TEXT,
                    xml_tag TEXT,
                    xml_attributes TEXT,
                    cleaned_at TEXT,
                    categorized_at TEXT,
                    loaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(phone, amount, date, reference)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_phone ON transactions(phone)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_amount ON transactions(amount)")
            
            # ETL logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS etl_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    process_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    records_processed INTEGER,
                    records_successful INTEGER,
                    records_failed INTEGER,
                    start_time TEXT,
                    end_time TEXT,
                    error_message TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Category statistics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS category_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    count INTEGER NOT NULL,
                    total_amount REAL,
                    avg_amount REAL,
                    min_amount REAL,
                    max_amount REAL,
                    last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(category)
                )
            """)
            
            self.connection.commit()
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def load_transactions(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Load transactions into database.
        
        Args:
            transactions: List of categorized transaction dictionaries
            
        Returns:
            Summary of loading results
        """
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            
            for i, transaction in enumerate(transactions):
                try:
                    self._insert_transaction(cursor, transaction)
                    self.loaded_count += 1
                except Exception as e:
                    self.error_count += 1
                    error_msg = f"Transaction {i}: {str(e)}"
                    self.errors.append(error_msg)
                    logger.error(error_msg)
            
            # Update category statistics
            self._update_category_stats(cursor)
            
            # Log ETL process
            self._log_etl_process(cursor, len(transactions))
            
            self.connection.commit()
            
            logger.info(f"Loaded {self.loaded_count} transactions, {self.error_count} errors")
            
            return self.get_loading_summary()
            
        except Exception as e:
            logger.error(f"Error loading transactions: {e}")
            self.connection.rollback()
            raise
    
    def _insert_transaction(self, cursor, transaction: Dict[str, Any]):
        """Insert a single transaction into database."""
        # Prepare data for insertion
        data = {
            'amount': transaction.get('amount'),
            'phone': transaction.get('phone'),
            'date': transaction.get('date'),
            'reference': transaction.get('reference'),
            'type': transaction.get('type'),
            'status': transaction.get('status'),
            'category': transaction.get('category'),
            'category_confidence': transaction.get('category_confidence'),
            'original_data': transaction.get('original_data'),
            'raw_data': transaction.get('raw_data'),
            'xml_tag': transaction.get('xml_tag'),
            'xml_attributes': json.dumps(transaction.get('xml_attributes', {})) if transaction.get('xml_attributes') else None,
            'cleaned_at': transaction.get('cleaned_at'),
            'categorized_at': transaction.get('categorized_at'),
            'loaded_at': datetime.now().isoformat()
        }
        
        # Check for existing transaction before inserting
        # This handles the case where reference might be NULL
        cursor.execute("""
            SELECT id FROM transactions 
            WHERE phone = :phone 
            AND amount = :amount 
            AND date = :date 
            AND (reference = :reference OR (reference IS NULL AND :reference IS NULL))
        """, data)
        
        existing = cursor.fetchone()
        if existing:
            # Transaction already exists, skip insertion
            logger.debug(f"Duplicate transaction skipped: {data['phone']}, {data['amount']}, {data['date']}")
            return
        
        # Insert new transaction
        cursor.execute("""
            INSERT INTO transactions (
                amount, phone, date, reference, type, status, category,
                category_confidence, original_data, raw_data, xml_tag,
                xml_attributes, cleaned_at, categorized_at, loaded_at
            ) VALUES (
                :amount, :phone, :date, :reference, :type, :status, :category,
                :category_confidence, :original_data, :raw_data, :xml_tag,
                :xml_attributes, :cleaned_at, :categorized_at, :loaded_at
            )
        """, data)
    
    def _update_category_stats(self, cursor):
        """Update category statistics."""
        try:
            # Clear existing stats
            cursor.execute("DELETE FROM category_stats")
            
            # Calculate new stats
            cursor.execute("""
                INSERT INTO category_stats (
                    category, count, total_amount, avg_amount, min_amount, max_amount
                )
                SELECT 
                    category,
                    COUNT(*) as count,
                    SUM(amount) as total_amount,
                    AVG(amount) as avg_amount,
                    MIN(amount) as min_amount,
                    MAX(amount) as max_amount
                FROM transactions 
                WHERE category IS NOT NULL
                GROUP BY category
            """)
            
        except Exception as e:
            logger.error(f"Error updating category stats: {e}")
    
    def _log_etl_process(self, cursor, total_records: int):
        """Log ETL process information."""
        try:
            log_data = {
                'process_name': 'load_transactions',
                'status': 'completed' if self.error_count == 0 else 'completed_with_errors',
                'records_processed': total_records,
                'records_successful': self.loaded_count,
                'records_failed': self.error_count,
                'start_time': datetime.now().isoformat(),
                'end_time': datetime.now().isoformat(),
                'error_message': '; '.join(self.errors[:5]) if self.errors else None
            }
            
            cursor.execute("""
                INSERT INTO etl_logs (
                    process_name, status, records_processed, records_successful,
                    records_failed, start_time, end_time, error_message
                ) VALUES (
                    :process_name, :status, :records_processed, :records_successful,
                    :records_failed, :start_time, :end_time, :error_message
                )
            """, log_data)
            
        except Exception as e:
            logger.error(f"Error logging ETL process: {e}")
    
    def export_dashboard_json(self) -> Dict[str, Any]:
        """
        Export data for dashboard visualization.
        
        Returns:
            Dashboard data dictionary
        """
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            
            # Get summary statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(amount) as total_amount,
                    AVG(amount) as avg_amount,
                    COUNT(CASE WHEN status = 'SUCCESS' THEN 1 END) as successful_transactions
                FROM transactions
            """)
            summary = dict(cursor.fetchone())
            
            # Calculate success rate
            if summary['total_transactions'] > 0:
                summary['success_rate'] = (summary['successful_transactions'] / summary['total_transactions']) * 100
            else:
                summary['success_rate'] = 0
            
            summary['last_updated'] = datetime.now().isoformat()
            
            # Get recent transactions
            cursor.execute("""
                SELECT date, amount, type, status, phone
                FROM transactions
                ORDER BY date DESC
                LIMIT 100
            """)
            transactions = [dict(row) for row in cursor.fetchall()]
            
            # Get category distribution
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM transactions
                WHERE category IS NOT NULL
                GROUP BY category
                ORDER BY count DESC
            """)
            category_distribution = {row['category']: row['count'] for row in cursor.fetchall()}
            
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
            amount_distribution = {row['amount_range']: row['count'] for row in cursor.fetchall()}
            
            # Compile dashboard data
            dashboard_data = {
                'summary': summary,
                'transactions': transactions,
                'analytics': {
                    'amountDistribution': amount_distribution,
                    'transactionTypes': category_distribution
                },
                'exported_at': datetime.now().isoformat()
            }
            
            # Save to JSON file
            DASHBOARD_JSON_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(DASHBOARD_JSON_FILE, 'w') as f:
                json.dump(dashboard_data, f, indent=2, default=str)
            
            logger.info(f"Dashboard data exported to {DASHBOARD_JSON_FILE}")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error exporting dashboard data: {e}")
            raise
    
    def get_loading_summary(self) -> Dict[str, Any]:
        """Get summary of loading results."""
        return {
            'total_processed': self.loaded_count + self.error_count,
            'successfully_loaded': self.loaded_count,
            'loading_errors': self.error_count,
            'error_rate': self.error_count / (self.loaded_count + self.error_count) if (self.loaded_count + self.error_count) > 0 else 0,
            'errors': self.errors[:10],  # First 10 errors
            'loaded_at': datetime.now().isoformat()
        }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            
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
                'database_size_mb': round(db_size / (1024 * 1024), 2),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
